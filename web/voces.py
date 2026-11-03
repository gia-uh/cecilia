"""CecilIA voces: a collaborative corpus of spoken Cuban Spanish.

People read prompts aloud in the browser and validate other people's
recordings. Metadata lives in one SQLite file and audio in plain files,
both under CECILIA_VOZ_DIR. Design: specs/2026-11-03-voz-design.html.

A participant is anonymous: the browser holds a readable code
(caoba-tinajon-4821) and sends it in X-Voz-Code; the server keeps only
its HMAC. Nothing that identifies a person is stored next to the audio,
not even the IP, which the rate limiter keeps in memory only.
"""

import array
import base64
import hashlib
import hmac
import json
import os
import pathlib
import secrets
import sqlite3
import subprocess
import time
import unicodedata
import uuid
from collections import defaultdict
from typing import Literal

from fastapi import APIRouter, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

HERE = pathlib.Path(__file__).parent
WORDS = (HERE / "voces_words.txt").read_text(encoding="utf-8").split()
PROMPTS_FILE = HERE / "voces_prompts.tsv"

CONSENT_VERSION = "2026-11-03"
GOAL_HOURS = 25

MIN_SECONDS, MAX_SECONDS = 1.0, 30.0
MAX_BYTES = 10 * 1024 * 1024
CLIPS_PER_DAY = 300
RECORDINGS_PER_PROMPT = 3
REPORTS_TO_RETIRE = 3
VOTES_TO_DECIDE = 2
AUDIO_URL_TTL = 3600
# Silence: the loudest 50 ms window stays under this RMS (full scale = 1).
SILENCE_RMS = 0.01
CLIPPED_FRACTION = 0.01

PROVINCES = [
    "Pinar del Río", "Artemisa", "La Habana", "Mayabeque", "Matanzas",
    "Cienfuegos", "Villa Clara", "Sancti Spíritus", "Ciego de Ávila",
    "Camagüey", "Las Tunas", "Holguín", "Granma", "Santiago de Cuba",
    "Guantánamo", "Isla de la Juventud",
]
AGE_RANGES = ["18-29", "30-44", "45-59", "60+"]
GENDERS = ["femenino", "masculino", "otro"]
ABROAD = ["no", "menos-5", "mas-5"]

AUDIO_TYPES = {"audio/webm": ".webm", "audio/ogg": ".ogg", "audio/mp4": ".m4a"}

SCHEMA = """
create table if not exists participants (
    id text primary key,
    code_hash text unique not null,
    created_at real not null,
    consent_version text not null,
    province text, municipality text, age_range text, gender text, abroad text
);
create table if not exists prompts (
    id integer primary key,
    text text unique not null,
    kind text not null,
    source text not null,
    active integer not null default 1
);
create table if not exists clips (
    id text primary key,
    participant_id text not null references participants(id),
    prompt_id integer not null references prompts(id),
    path text not null,
    mime text not null,
    duration real not null,
    bytes integer not null,
    created_at real not null
);
create index if not exists clips_prompt on clips(prompt_id);
create index if not exists clips_participant on clips(participant_id);
create table if not exists votes (
    clip_id text not null references clips(id),
    participant_id text not null references participants(id),
    vote text not null,
    created_at real not null,
    primary key (clip_id, participant_id)
);
create table if not exists reports (
    prompt_id integer not null references prompts(id),
    participant_id text not null references participants(id),
    primary key (prompt_id, participant_id)
);
"""

router = APIRouter()


# --- storage ---------------------------------------------------------------

def voz_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("CECILIA_VOZ_DIR", "data/voces"))


def secret() -> bytes:
    """Server key for code hashes, review tickets and audio URLs.

    Generated once next to the database, so a restore of CECILIA_VOZ_DIR
    keeps every participant's code working.
    """
    path = voz_dir() / "secret"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(secrets.token_hex(32))
    return path.read_text().strip().encode()


def db() -> sqlite3.Connection:
    root = voz_dir()
    root.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(root / "voz.sqlite", timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma journal_mode=wal")
    conn.execute("pragma foreign_keys=on")
    return conn


def init() -> None:
    """Create the schema and sync prompts from voces_prompts.tsv.

    The file is the source of truth for which prompts are offered: a line
    removed from it retires the prompt, recordings and all, from new
    sessions. Prompts retired by reports stay retired.
    """
    conn = db()
    conn.executescript(SCHEMA)
    rows = []
    if PROMPTS_FILE.exists():
        lines = PROMPTS_FILE.read_text(encoding="utf-8").splitlines()[1:]
        rows = [l.split("\t") for l in lines if l.strip()]
    texts = [r[0] for r in rows]
    with conn:
        conn.executemany(
            "insert or ignore into prompts (text, kind, source) values (?, ?, ?)", rows
        )
        conn.execute("create temp table keep (text text primary key)")
        conn.executemany("insert or ignore into keep values (?)", [(t,) for t in texts])
        conn.execute("update prompts set active = 0 where text not in (select text from keep)")
        conn.execute("drop table keep")
    conn.close()


# --- codes -----------------------------------------------------------------

def plain(s: str) -> str:
    s = unicodedata.normalize("NFD", s.strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def new_code() -> str:
    return f"{secrets.choice(WORDS)}-{secrets.choice(WORDS)}-{secrets.randbelow(10000):04d}"


def code_hash(code: str) -> str:
    normal = "-".join(plain(code).replace(" ", "-").split("-"))
    return hmac.new(secret(), normal.encode(), hashlib.sha256).hexdigest()


def participant(conn: sqlite3.Connection, code: str | None) -> sqlite3.Row:
    if not code:
        raise HTTPException(401, "falta el código de participante")
    row = conn.execute(
        "select * from participants where code_hash = ?", (code_hash(code),)
    ).fetchone()
    if row is None:
        raise HTTPException(401, "no conocemos ese código")
    return row


# --- signed tokens ---------------------------------------------------------

def sign(payload: dict) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    mac = hmac.new(secret(), body.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{body}.{mac}"


def unsign(token: str) -> dict:
    try:
        body, mac = token.rsplit(".", 1)
    except ValueError:
        raise HTTPException(400, "token mal formado")
    good = hmac.new(secret(), body.encode(), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(mac, good):
        raise HTTPException(400, "token no válido")
    return json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))



# --- rate limits (memory only) ---------------------------------------------

_counts: dict[tuple[str, str], int] = defaultdict(int)


def take(kind: str, key: str, limit: int) -> None:
    day = time.strftime("%Y-%m-%d")
    slot = (f"{day}:{kind}", key)
    if _counts[slot] >= limit:
        raise HTTPException(429, "ha llegado al límite de hoy; gracias, vuelva mañana")
    _counts[slot] += 1
    if len(_counts) > 100_000:
        for k in [k for k in _counts if not k[0].startswith(day)]:
            del _counts[k]


def client_ip(request: Request) -> str:
    # Caddy sets X-Forwarded-For; the app only listens on localhost.
    return request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
        request.client.host if request.client else "?"
    )


# --- audio checks ----------------------------------------------------------

def analyse(path: pathlib.Path) -> dict:
    """Decode with ffmpeg to 16 kHz mono and measure what the browser measured.

    Returns duration, the loudest 50 ms RMS and the clipped fraction.
    """
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000",
         "-f", "s16le", "-"],
        capture_output=True, timeout=60,
    )
    if out.returncode != 0 or not out.stdout:
        raise HTTPException(422, "no pudimos leer el audio")
    pcm = array.array("h")
    pcm.frombytes(out.stdout[: len(out.stdout) // 2 * 2])
    n = len(pcm)
    win = 800
    loudest = 0.0
    for i in range(0, max(n - win, 1), win):
        chunk = pcm[i:i + win]
        if chunk:
            loudest = max(loudest, (sum(s * s for s in chunk) / len(chunk)) ** 0.5 / 32768)
    clipped = sum(1 for s in pcm if s >= 32700 or s <= -32700) / max(n, 1)
    return {"duration": n / 16000, "rms": loudest, "clipped": clipped}


# --- API -------------------------------------------------------------------

class NewParticipant(BaseModel):
    adult: bool
    license: bool
    deletion: bool
    province: str | None = None
    municipality: str | None = None
    age_range: str | None = None
    gender: str | None = None
    abroad: str | None = None


class Profile(BaseModel):
    province: str | None = None
    municipality: str | None = None
    age_range: str | None = None
    gender: str | None = None
    abroad: str | None = None


def clean_profile(p: Profile | NewParticipant) -> dict:
    def pick(value, allowed):
        return value if value in allowed else None
    return {
        "province": pick(p.province, PROVINCES),
        "municipality": (p.municipality or "").strip()[:60] or None,
        "age_range": pick(p.age_range, AGE_RANGES),
        "gender": pick(p.gender, GENDERS),
        "abroad": pick(p.abroad, ABROAD),
    }


@router.post("/api/voces/participants", status_code=201)
def create_participant(body: NewParticipant, request: Request):
    if not (body.adult and body.license and body.deletion):
        raise HTTPException(422, "hace falta aceptar las tres condiciones")
    take("participants", client_ip(request), 20)
    conn = db()
    profile = clean_profile(body)
    for _ in range(5):
        code = new_code()
        try:
            with conn:
                conn.execute(
                    "insert into participants (id, code_hash, created_at, consent_version,"
                    " province, municipality, age_range, gender, abroad)"
                    " values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(uuid.uuid4()), code_hash(code), time.time(), CONSENT_VERSION,
                     *profile.values()),
                )
            return {"code": code}
        except sqlite3.IntegrityError:
            continue
    raise HTTPException(500, "no pudimos crear el código; inténtelo de nuevo")


@router.get("/api/voces/participants/check")
def check_code(request: Request, x_voz_code: str | None = Header(None)):
    take("check", client_ip(request), 60)
    participant(db(), x_voz_code)
    return {"ok": True}


@router.patch("/api/voces/participants/me")
def update_profile(body: Profile, x_voz_code: str | None = Header(None)):
    conn = db()
    me = participant(conn, x_voz_code)
    p = clean_profile(body)
    with conn:
        conn.execute(
            "update participants set province=?, municipality=?, age_range=?, gender=?,"
            " abroad=? where id=?", (*p.values(), me["id"]),
        )
    return p


@router.get("/api/voces/prompts")
def next_prompts(n: int = Query(10, ge=1, le=30), x_voz_code: str | None = Header(None)):
    conn = db()
    me = participant(conn, x_voz_code)
    rows = conn.execute(
        """
        select p.id, p.text, p.kind,
               (select count(distinct c.participant_id) from clips c where c.prompt_id = p.id) as done
        from prompts p
        where p.active = 1
          and not exists (select 1 from clips c where c.prompt_id = p.id and c.participant_id = :me)
          and not exists (select 1 from reports r where r.prompt_id = p.id and r.participant_id = :me)
        and (select count(distinct c.participant_id) from clips c where c.prompt_id = p.id) < :per
        order by done, random()
        limit :n
        """,
        {"me": me["id"], "per": RECORDINGS_PER_PROMPT, "n": n},
    ).fetchall()
    return [{"id": r["id"], "text": r["text"], "kind": r["kind"]} for r in rows]


@router.post("/api/voces/prompts/{prompt_id}/report")
def report_prompt(prompt_id: int, x_voz_code: str | None = Header(None)):
    conn = db()
    me = participant(conn, x_voz_code)
    with conn:
        conn.execute("insert or ignore into reports values (?, ?)", (prompt_id, me["id"]))
        n = conn.execute(
            "select count(*) from reports where prompt_id = ?", (prompt_id,)
        ).fetchone()[0]
        if n >= REPORTS_TO_RETIRE:
            conn.execute("update prompts set active = 0 where id = ?", (prompt_id,))
    return {"reports": n}


@router.post("/api/voces/clips", status_code=201)
async def upload_clip(
    request: Request,
    id: str = Form(...),
    prompt_id: int = Form(...),
    duration: float = Form(...),
    audio: UploadFile = File(...),
    x_voz_code: str | None = Header(None),
):
    try:
        clip_id = str(uuid.UUID(id))
    except ValueError:
        raise HTTPException(422, "id de grabación no válido")
    conn = db()
    me = participant(conn, x_voz_code)
    old = conn.execute("select participant_id from clips where id = ?", (clip_id,)).fetchone()
    if old is not None:
        if old["participant_id"] != me["id"]:
            raise HTTPException(409, "ese id ya existe")
        return {"id": clip_id, "duplicate": True}
    if conn.execute("select 1 from prompts where id = ?", (prompt_id,)).fetchone() is None:
        raise HTTPException(422, "no conocemos esa frase")

    mime = (audio.content_type or "").split(";")[0].strip()
    ext = AUDIO_TYPES.get(mime)
    if ext is None:
        raise HTTPException(415, f"formato de audio no admitido: {mime or 'desconocido'}")
    data = await audio.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "la grabación es demasiado grande")

    take("clips", me["id"], CLIPS_PER_DAY)
    take("clips-ip", client_ip(request), CLIPS_PER_DAY)

    rel = pathlib.Path("audio") / clip_id[:2] / f"{clip_id}{ext}"
    path = voz_dir() / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(ext + ".part")
    tmp.write_bytes(data)
    try:
        m = analyse(tmp)
        if not MIN_SECONDS <= m["duration"] <= MAX_SECONDS + 0.5:
            raise HTTPException(422, "la grabación debe durar entre 1 y 30 segundos")
        if m["rms"] < SILENCE_RMS:
            raise HTTPException(422, "casi no se oye nada; acérquese al micrófono")
        if m["clipped"] > CLIPPED_FRACTION:
            raise HTTPException(422, "el sonido sale saturado; aléjese un poco del micrófono")
    except HTTPException:
        tmp.unlink(missing_ok=True)
        raise
    tmp.rename(path)
    with conn:
        conn.execute(
            "insert into clips (id, participant_id, prompt_id, path, mime, duration, bytes,"
            " created_at) values (?, ?, ?, ?, ?, ?, ?, ?)",
            (clip_id, me["id"], prompt_id, str(rel), mime, round(m["duration"], 2),
             len(data), time.time()),
        )
    return {"id": clip_id, "duration": round(m["duration"], 2)}


@router.get("/api/voces/review")
def review(x_voz_code: str | None = Header(None)):
    conn = db()
    me = participant(conn, x_voz_code)
    row = conn.execute(
        """
        select c.id, c.duration, p.text,
               sum(v.vote = 'yes') as yes, sum(v.vote = 'no') as no, count(v.vote) as n
        from clips c join prompts p on p.id = c.prompt_id
        left join votes v on v.clip_id = c.id
        where c.participant_id != :me
          and not exists (select 1 from votes w where w.clip_id = c.id and w.participant_id = :me)
        group by c.id
        having coalesce(yes, 0) < :k and coalesce(no, 0) < :k
        order by n, random()
        limit 1
        """,
        {"me": me["id"], "k": VOTES_TO_DECIDE},
    ).fetchone()
    if row is None:
        return None
    now = time.time()
    exp = int(now) + AUDIO_URL_TTL
    return {
        "clip_id": row["id"],
        "text": row["text"],
        "duration": row["duration"],
        "audio_url": f"/api/voces/audio/{row['id']}?" + f"t={sign({'c': row['id'], 'e': exp})}",
        "ticket": sign({"c": row["id"], "p": me["id"], "t": now}),
    }


@router.get("/api/voces/audio/{clip_id}", include_in_schema=False)
def audio(clip_id: str, t: str):
    claim = unsign(t)
    if claim.get("c") != clip_id or claim.get("e", 0) < time.time():
        raise HTTPException(403, "enlace caducado")
    row = db().execute("select path, mime from clips where id = ?", (clip_id,)).fetchone()
    if row is None:
        raise HTTPException(404)
    return FileResponse(voz_dir() / row["path"], media_type=row["mime"])


class Vote(BaseModel):
    ticket: str
    vote: Literal["yes", "no", "skip"]


@router.post("/api/voces/votes", status_code=201)
def vote(body: Vote, x_voz_code: str | None = Header(None)):
    conn = db()
    me = participant(conn, x_voz_code)
    claim = unsign(body.ticket)
    if claim.get("p") != me["id"]:
        raise HTTPException(403, "ese voto no es suyo")
    clip = conn.execute(
        "select participant_id, duration from clips where id = ?", (claim["c"],)
    ).fetchone()
    if clip is None:
        raise HTTPException(404, "esa grabación ya no existe")
    if clip["participant_id"] == me["id"]:
        raise HTTPException(403, "no puede validar sus propias grabaciones")
    # A yes needs the whole recording heard: no earlier than its duration
    # after the review was handed out (a little slack for the network).
    if body.vote == "yes" and time.time() - claim["t"] < clip["duration"] - 0.5:
        raise HTTPException(422, "escuche la grabación completa antes de decir que sí")
    with conn:
        conn.execute(
            "insert or replace into votes values (?, ?, ?, ?)",
            (claim["c"], me["id"], body.vote, time.time()),
        )
    return {"ok": True}


@router.get("/api/voces/me")
def me(x_voz_code: str | None = Header(None)):
    conn = db()
    p = participant(conn, x_voz_code)
    clips = conn.execute(
        "select count(*), coalesce(sum(duration), 0) from clips where participant_id = ?",
        (p["id"],),
    ).fetchone()
    votes = conn.execute(
        "select count(*) from votes where participant_id = ? and vote != 'skip'", (p["id"],)
    ).fetchone()[0]
    return {
        "clips": clips[0],
        "seconds": round(clips[1], 1),
        "votes": votes,
        "profile": {k: p[k] for k in ("province", "municipality", "age_range", "gender", "abroad")},
    }


@router.delete("/api/voces/me")
def delete_me(x_voz_code: str | None = Header(None)):
    conn = db()
    p = participant(conn, x_voz_code)
    paths = [r[0] for r in conn.execute(
        "select path from clips where participant_id = ?", (p["id"],)
    )]
    with conn:
        conn.execute(
            "delete from votes where clip_id in (select id from clips where participant_id = ?)",
            (p["id"],),
        )
        conn.execute("delete from votes where participant_id = ?", (p["id"],))
        conn.execute("delete from reports where participant_id = ?", (p["id"],))
        conn.execute("delete from clips where participant_id = ?", (p["id"],))
        conn.execute("delete from participants where id = ?", (p["id"],))
    for rel in paths:
        (voz_dir() / rel).unlink(missing_ok=True)
    _stats.clear()
    return {"deleted": len(paths)}


_stats: dict = {}


@router.get("/api/voces/stats")
def stats():
    if _stats and _stats["at"] > time.time() - 60:
        return _stats["value"]
    conn = db()
    total = conn.execute("select coalesce(sum(duration), 0), count(*) from clips").fetchone()
    speakers = conn.execute("select count(distinct participant_id) from clips").fetchone()[0]
    validated = conn.execute(
        "select count(*) from (select clip_id from votes group by clip_id"
        " having sum(vote = 'yes') >= ? and sum(vote = 'no') < ?)",
        (VOTES_TO_DECIDE, VOTES_TO_DECIDE),
    ).fetchone()[0]
    by_province = dict.fromkeys(PROVINCES, 0.0)
    for prov, secs in conn.execute(
        "select p.province, sum(c.duration) from clips c join participants p"
        " on p.id = c.participant_id where p.province is not null group by p.province"
    ):
        by_province[prov] = round(secs / 3600, 3)
    value = {
        "hours": round(total[0] / 3600, 2),
        "goal_hours": GOAL_HOURS,
        "clips": total[1],
        "speakers": speakers,
        "validated": validated,
        "provinces": by_province,
    }
    _stats.update(at=time.time(), value=value)
    return value
