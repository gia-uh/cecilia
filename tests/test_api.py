"""Contract tests for the submission endpoint.

The rules mirror what apps/pages/training.py enforced in the browser. The
difference is that these run on the server, so a hand-rolled POST cannot
get around them.
"""

import json
import os
import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("CECILIA_DATA_DIR", str(tmp_path))
    import web.main

    importlib = __import__("importlib")
    importlib.reload(web.main)
    return TestClient(web.main.app)


def valid_payload(**overrides):
    payload = {
        "contact_info": {
            "name": "Juana Pérez",
            "institution": "Universidad de La Habana",
            "email": "juana@uh.cu",
        },
        "example_type": "Pregunta",
        "tags": ["historia"],
        "context": "",
        "messages": [
            {"role": "user", "content": "¿Quién fue José Martí?"},
            {"role": "assistant", "content": "Fue el Apóstol de la independencia de Cuba."},
        ],
    }
    payload.update(overrides)
    return payload


# --- the happy path -------------------------------------------------------

def test_valid_submission_is_stored(client, tmp_path):
    r = client.post("/api/examples", json=valid_payload())
    assert r.status_code == 201, r.text

    written = list(tmp_path.glob("*.json"))
    assert len(written) == 1

    saved = json.loads(written[0].read_text(encoding="utf-8"))
    assert saved["id"] == written[0].stem
    uuid.UUID(saved["id"])
    assert saved["contact_info"]["name"] == "Juana Pérez"
    assert saved["example_type"] == "Pregunta"
    assert saved["tags"] == ["historia"]
    assert len(saved["messages"]) == 2
    assert saved["created_at"]
    assert r.json()["id"] == saved["id"]


def test_accents_survive_the_round_trip(client, tmp_path):
    client.post("/api/examples", json=valid_payload())
    raw = list(tmp_path.glob("*.json"))[0].read_text(encoding="utf-8")
    assert "Pérez" in raw and "\\u00e9" not in raw


def test_context_is_optional(client):
    assert client.post("/api/examples", json=valid_payload(context="")).status_code == 201


# --- rejections -----------------------------------------------------------

@pytest.mark.parametrize("field", ["name", "institution", "email"])
def test_blank_contact_field_is_rejected(client, field, tmp_path):
    payload = valid_payload()
    payload["contact_info"][field] = "   "
    assert client.post("/api/examples", json=payload).status_code == 422
    assert list(tmp_path.glob("*.json")) == []


def test_empty_conversation_is_rejected(client):
    assert client.post("/api/examples", json=valid_payload(messages=[])).status_code == 422


def test_single_message_is_rejected(client):
    payload = valid_payload(messages=[{"role": "user", "content": "hola"}])
    assert client.post("/api/examples", json=payload).status_code == 422


def test_odd_message_count_is_rejected(client):
    payload = valid_payload(messages=[
        {"role": "user", "content": "a"},
        {"role": "assistant", "content": "b"},
        {"role": "user", "content": "c"},
    ])
    assert client.post("/api/examples", json=payload).status_code == 422


def test_must_start_with_the_user(client):
    payload = valid_payload(messages=[
        {"role": "assistant", "content": "a"},
        {"role": "user", "content": "b"},
    ])
    assert client.post("/api/examples", json=payload).status_code == 422


def test_roles_must_alternate(client):
    payload = valid_payload(messages=[
        {"role": "user", "content": "a"},
        {"role": "user", "content": "b"},
        {"role": "assistant", "content": "c"},
        {"role": "assistant", "content": "d"},
    ])
    assert client.post("/api/examples", json=payload).status_code == 422


def test_empty_message_content_is_rejected(client):
    payload = valid_payload(messages=[
        {"role": "user", "content": "   "},
        {"role": "assistant", "content": "b"},
    ])
    assert client.post("/api/examples", json=payload).status_code == 422


def test_no_tags_is_rejected(client):
    assert client.post("/api/examples", json=valid_payload(tags=[])).status_code == 422


def test_unknown_tag_is_rejected(client):
    assert client.post("/api/examples", json=valid_payload(tags=["reguetón"])).status_code == 422


def test_unknown_example_type_is_rejected(client):
    assert client.post("/api/examples", json=valid_payload(example_type="Otro")).status_code == 422


# --- pages ----------------------------------------------------------------

@pytest.mark.parametrize("path", ["/", "/training"])
def test_pages_render(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_health(client):
    assert client.get("/health").status_code == 200
