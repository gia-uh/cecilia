"""Cecilia: landing page and the instruction-collection form.

One FastAPI process serves both pages, the static assets and the single
POST that stores a submission. Replaces the Streamlit app in apps/.

Submissions keep the exact on-disk shape the Streamlit version wrote —
one JSON per example under CECILIA_DATA_DIR — so data/stats.py and any
downstream script keep working untouched.
"""

import json
import os
import pathlib
import time
import uuid
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator, model_validator

HERE = pathlib.Path(__file__).parent
STATIC = HERE / "static"

DATA_DIR = pathlib.Path(
    os.environ.get("CECILIA_DATA_DIR", "data/instructions/submitted")
)

# Kept identical to the Streamlit UI so existing submissions stay comparable.
TAGS = [
    "arte", "ciencia", "cultura", "deporte", "economía",
    "historia", "política", "salud", "casual", "otros",
]
EXAMPLE_TYPES = ["Pregunta", "Instrucción", "Conversación"]


class ContactInfo(BaseModel):
    name: str
    institution: str
    email: str

    @field_validator("name", "institution", "email")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("campo obligatorio")
        return v.strip()


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

    @field_validator("content")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("el mensaje no puede estar vacío")
        return v.strip()


class Submission(BaseModel):
    contact_info: ContactInfo
    example_type: Literal["Pregunta", "Instrucción", "Conversación"]
    tags: list[str] = Field(min_length=1)
    context: str = ""
    messages: list[Message]

    @field_validator("tags")
    @classmethod
    def known_tags(cls, v: list[str]) -> list[str]:
        unknown = [t for t in v if t not in TAGS]
        if unknown:
            raise ValueError(f"etiquetas desconocidas: {unknown}")
        return v

    @model_validator(mode="after")
    def well_formed_conversation(self):
        n = len(self.messages)
        if n < 2:
            raise ValueError("hacen falta al menos dos mensajes")
        if n % 2 != 0:
            raise ValueError("cada mensaje del usuario necesita una respuesta")
        for i, message in enumerate(self.messages):
            expected = "user" if i % 2 == 0 else "assistant"
            if message.role != expected:
                raise ValueError("los turnos deben alternar, empezando por el usuario")
        return self


app = FastAPI(title="Cecilia")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/training", include_in_schema=False)
def training():
    return FileResponse(STATIC / "training.html")


# Los PDF se sirven desde donde viven en el repo. Copiarlos aquí crearía una
# tercera copia (docs/ ya tiene la suya, que es la que necesita GitHub Pages)
# y tres copias de un binario divergen.
REPO = HERE.parent
DOCUMENTS = {
    "report.pdf": REPO / "report" / "report.pdf",
    "paper.pdf": REPO / "papers" / "uciencia25" / "paper.pdf",
}


@app.get("/{name}.pdf", include_in_schema=False)
def document(name: str):
    path = DOCUMENTS.get(f"{name}.pdf")
    if path is None or not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="application/pdf")


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


@app.post("/api/examples", status_code=201)
def submit(submission: Submission):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    example_id = str(uuid.uuid4())

    record = {
        "id": example_id,
        "contact_info": submission.contact_info.model_dump(),
        "example_type": submission.example_type,
        "tags": submission.tags,
        "context": submission.context,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "messages": [m.model_dump() for m in submission.messages],
    }

    path = DATA_DIR / f"{example_id}.json"
    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=4), encoding="utf-8"
    )
    return {"id": example_id}
