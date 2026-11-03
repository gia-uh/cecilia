"""Contract tests for /api/voces: participants, prompts, clips, votes.

Audio is made with ffmpeg, the same tool the server uses to check it, so
these tests need ffmpeg on PATH.
"""

import importlib
import pathlib
import subprocess
import time
import uuid

import pytest
from fastapi.testclient import TestClient

CONSENT = {"adult": True, "license": True, "deletion": True}


def tone(path: pathlib.Path, seconds: float, volume: float = 0.3) -> bytes:
    src = f"sine=frequency=220:duration={seconds}"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", src, "-af", f"volume={volume}",
         "-c:a", "libopus", "-b:a", "48k", str(path)],
        check=True,
    )
    return path.read_bytes()


@pytest.fixture(scope="session")
def audio(tmp_path_factory):
    d = tmp_path_factory.mktemp("audio")
    return {
        "ok": tone(d / "ok.webm", 3),
        "short": tone(d / "short.webm", 0.4),
        "silent": tone(d / "silent.webm", 3, volume=0.001),
        "loud": tone(d / "loud.webm", 3, volume=40.0),
    }


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("CECILIA_VOZ_DIR", str(tmp_path / "voz"))
    prompts = tmp_path / "prompts.tsv"
    prompts.write_text(
        "text\tkind\tsource\n"
        "Me monté en la guagua en Línea y G.\tfrase\ttest\n"
        "El agro de Diecinueve tenía boniato.\tfrase\ttest\n"
        "En Baracoa llueve casi todo el año.\tfrase\ttest\n",
        encoding="utf-8",
    )
    import web.voces
    import web.main

    importlib.reload(web.voces)
    monkeypatch.setattr(web.voces, "PROMPTS_FILE", prompts)
    importlib.reload(web.main)
    with TestClient(web.main.app) as c:
        yield c


def join(client, **profile) -> dict:
    r = client.post("/api/voces/participants", json={**CONSENT, **profile})
    assert r.status_code == 201, r.text
    return {"X-Voz-Code": r.json()["code"]}


def upload(client, who, prompt_id, data, clip_id=None):
    return client.post(
        "/api/voces/clips",
        headers=who,
        data={"id": clip_id or str(uuid.uuid4()), "prompt_id": prompt_id, "duration": 3},
        files={"audio": ("a.webm", data, "audio/webm")},
    )


# --- participants ------------------------------------------------------------

def test_consent_is_required(client):
    r = client.post("/api/voces/participants", json={**CONSENT, "license": False})
    assert r.status_code == 422


def test_code_is_readable_and_only_its_hash_is_stored(client, tmp_path):
    who = join(client)
    code = who["X-Voz-Code"]
    a, b, digits = code.split("-")
    assert a.isalpha() and b.isalpha() and len(digits) == 4
    db = (tmp_path / "voz" / "voz.sqlite").read_bytes()
    assert code.encode() not in db


def test_code_survives_case_and_spaces(client):
    code = join(client)["X-Voz-Code"]
    messy = "  " + code.upper().replace("-", " ") + " "
    r = client.get("/api/voces/participants/check", headers={"X-Voz-Code": messy})
    assert r.status_code == 200


def test_unknown_code_is_refused(client):
    r = client.get("/api/voces/me", headers={"X-Voz-Code": "caoba-tinajon-0000"})
    assert r.status_code == 401


def test_profile_keeps_only_known_values(client):
    who = join(client, province="Matanzas", age_range="18-29", gender="nadie")
    r = client.get("/api/voces/me", headers=who)
    assert r.json()["profile"]["province"] == "Matanzas"
    assert r.json()["profile"]["gender"] is None


# --- prompts and clips -------------------------------------------------------

def test_prompts_skip_what_i_recorded(client, audio):
    who = join(client)
    first = client.get("/api/voces/prompts?n=10", headers=who).json()
    assert len(first) == 3
    assert upload(client, who, first[0]["id"], audio["ok"]).status_code == 201
    ids = {p["id"] for p in client.get("/api/voces/prompts", headers=who).json()}
    assert first[0]["id"] not in ids and len(ids) == 2


def test_prompt_leaves_after_three_speakers(client, audio):
    pid = client.get("/api/voces/prompts", headers=join(client)).json()[0]["id"]
    for _ in range(3):
        assert upload(client, join(client), pid, audio["ok"]).status_code == 201
    ids = {p["id"] for p in client.get("/api/voces/prompts", headers=join(client)).json()}
    assert pid not in ids


def test_clip_is_stored_with_measured_duration(client, audio, tmp_path):
    who = join(client)
    pid = client.get("/api/voces/prompts", headers=who).json()[0]["id"]
    r = upload(client, who, pid, audio["ok"])
    assert r.status_code == 201, r.text
    assert abs(r.json()["duration"] - 3) < 0.2
    files = list((tmp_path / "voz" / "audio").rglob("*.webm"))
    assert len(files) == 1 and files[0].read_bytes() == audio["ok"]


def test_retry_with_the_same_id_does_not_duplicate(client, audio):
    who = join(client)
    pid = client.get("/api/voces/prompts", headers=who).json()[0]["id"]
    cid = str(uuid.uuid4())
    assert upload(client, who, pid, audio["ok"], cid).status_code == 201
    r = upload(client, who, pid, audio["ok"], cid)
    assert r.json()["duplicate"] is True
    assert client.get("/api/voces/me", headers=who).json()["clips"] == 1


@pytest.mark.parametrize("kind,why", [
    ("short", "durar"), ("silent", "no se oye"), ("loud", "saturado"),
])
def test_bad_takes_are_refused(client, audio, kind, why):
    who = join(client)
    pid = client.get("/api/voces/prompts", headers=who).json()[0]["id"]
    r = upload(client, who, pid, audio[kind])
    assert r.status_code == 422 and why in r.json()["detail"]


def test_unknown_audio_type_is_refused(client, audio):
    who = join(client)
    pid = client.get("/api/voces/prompts", headers=who).json()[0]["id"]
    r = client.post(
        "/api/voces/clips", headers=who,
        data={"id": str(uuid.uuid4()), "prompt_id": pid, "duration": 3},
        files={"audio": ("a.txt", b"hola", "text/plain")},
    )
    assert r.status_code == 415


def test_three_reports_retire_a_prompt(client):
    pid = client.get("/api/voces/prompts", headers=join(client)).json()[0]["id"]
    for _ in range(3):
        client.post(f"/api/voces/prompts/{pid}/report", headers=join(client))
    ids = {p["id"] for p in client.get("/api/voces/prompts", headers=join(client)).json()}
    assert pid not in ids


# --- validation --------------------------------------------------------------

def recorded(client, audio):
    who = join(client)
    pid = client.get("/api/voces/prompts", headers=who).json()[0]["id"]
    upload(client, who, pid, audio["ok"])
    return who


def test_nobody_reviews_their_own_clip(client, audio):
    who = recorded(client, audio)
    assert client.get("/api/voces/review", headers=who).json() is None


def test_yes_before_the_end_is_refused(client, audio):
    recorded(client, audio)
    v = join(client)
    item = client.get("/api/voces/review", headers=v).json()
    r = client.post("/api/voces/votes", headers=v, json={"ticket": item["ticket"], "vote": "yes"})
    assert r.status_code == 422
    r = client.post("/api/voces/votes", headers=v, json={"ticket": item["ticket"], "vote": "no"})
    assert r.status_code == 201


def test_audio_url_plays_and_expires(client, audio, monkeypatch):
    recorded(client, audio)
    item = client.get("/api/voces/review", headers=join(client)).json()
    r = client.get(item["audio_url"])
    assert r.status_code == 200 and r.content == audio["ok"]
    import web.voces
    monkeypatch.setattr(web.voces.time, "time", lambda: time.monotonic() + 1e10)
    assert client.get(item["audio_url"]).status_code == 403


def test_two_yes_validate_and_the_clip_leaves_review(client, audio, monkeypatch):
    recorded(client, audio)
    import web.voces
    tickets = []
    for _ in range(2):
        v = join(client)
        tickets.append((v, client.get("/api/voces/review", headers=v).json()["ticket"]))
    real = time.time
    monkeypatch.setattr(web.voces.time, "time", lambda: real() + 10)
    for v, t in tickets:
        r = client.post("/api/voces/votes", headers=v, json={"ticket": t, "vote": "yes"})
        assert r.status_code == 201, r.text
    assert client.get("/api/voces/review", headers=join(client)).json() is None
    web.voces._stats.clear()
    assert client.get("/api/voces/stats").json()["validated"] == 1


def test_a_ticket_is_personal(client, audio):
    recorded(client, audio)
    t = client.get("/api/voces/review", headers=join(client)).json()["ticket"]
    r = client.post("/api/voces/votes", headers=join(client), json={"ticket": t, "vote": "no"})
    assert r.status_code == 403


# --- my contribution ---------------------------------------------------------

def test_delete_removes_audio_and_code(client, audio, tmp_path):
    who = recorded(client, audio)
    assert client.delete("/api/voces/me", headers=who).json()["deleted"] == 1
    assert not list((tmp_path / "voz" / "audio").rglob("*.webm"))
    assert client.get("/api/voces/me", headers=who).status_code == 401


def test_stats_count_hours_speakers_and_provinces(client, audio):
    who = join(client, province="Holguín")
    pid = client.get("/api/voces/prompts", headers=who).json()[0]["id"]
    upload(client, who, pid, audio["ok"])
    s = client.get("/api/voces/stats").json()
    assert s["speakers"] == 1 and s["clips"] == 1
    assert s["provinces"]["Holguín"] > 0 and s["provinces"]["Matanzas"] == 0


def test_page_is_served(client):
    r = client.get("/voces")
    assert r.status_code == 200 and "CecilIA" in r.text
