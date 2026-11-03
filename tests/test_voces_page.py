"""The /voces page end to end in Chromium, with a fake microphone.

One person records a prompt, once offline so the take waits in the queue,
and another person validates it. Needs ffmpeg and Playwright's Chromium
(`playwright install chromium`); skipped when Chromium is missing.
"""

import os
import socket
import subprocess
import sys
import time

import httpx
import pytest

sync_api = pytest.importorskip("playwright.sync_api")

SPOKEN_SECONDS = 3


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    root = tmp_path_factory.mktemp("page")
    port = free_port()
    env = {**os.environ, "CECILIA_VOZ_DIR": str(root / "voz"), "CECILIA_DATA_DIR": str(root / "ex")}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "web.main:app", "--port", str(port)],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            httpx.get(url + "/health")
            break
        except httpx.HTTPError:
            time.sleep(0.1)
    yield url
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="module")
def browser(tmp_path_factory):
    wav = tmp_path_factory.mktemp("mic") / "voice.wav"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=220:duration=60",
         "-af", "volume=2", "-ar", "48000", "-ac", "1", str(wav)],
        check=True,
    )
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch(args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-audio-capture={wav}",
                "--autoplay-policy=no-user-gesture-required",
            ])
        except Exception as e:  # Chromium not installed
            pytest.skip(f"Chromium no disponible: {e}")
        yield b
        b.close()


def consent(page, url, screen):
    page.goto(f"{url}/voces#{screen}")
    page.locator("#s-antes").wait_for()
    for box in page.locator(".req").all():
        box.check()
    page.select_option("#f-province", "Holguín")
    page.click("#consent-ok")
    page.locator(f"#s-{screen}").wait_for()


def record(page):
    page.click("#r-mic")
    page.wait_for_timeout(SPOKEN_SECONDS * 1000)
    page.click("#r-mic")
    page.locator("#r-after").wait_for()
    page.click("#r-next")


def test_record_offline_then_validate(server, browser):
    reader = browser.new_context(permissions=["microphone"])
    page = reader.new_page()
    consent(page, server, "leer")
    assert page.text_content("#r-text") != "Cargando frases…"

    record(page)
    page.wait_for_function("document.getElementById('q-text').textContent === 'Todo subido'")

    reader.set_offline(True)
    record(page)
    page.wait_for_function("document.getElementById('q-text').textContent.startsWith('1 grabación')")
    reader.set_offline(False)
    page.evaluate("window.dispatchEvent(new Event('online'))")
    page.wait_for_function("document.getElementById('q-text').textContent === 'Todo subido'")

    stats = httpx.get(server + "/api/voces/stats").json()
    assert stats["clips"] == 2 and stats["speakers"] == 1
    # Each take keeps half a second after «parar», so no last word is cut.
    code = page.evaluate("localStorage.getItem('voces.code')")
    seconds = httpx.get(server + "/api/voces/me", headers={"X-Voz-Code": code}).json()["seconds"]
    assert seconds >= 2 * (SPOKEN_SECONDS + 0.4)
    assert stats["provinces"]["Holguín"] > 0

    validator = browser.new_context().new_page()
    consent(validator, server, "validar")
    validator.locator("#c-text").wait_for()
    assert validator.is_disabled("#c-yes")
    validator.click("#c-play")
    validator.wait_for_function("!document.getElementById('c-yes').disabled", timeout=15000)
    with validator.expect_response("**/api/voces/votes") as vote:
        validator.click("#c-yes")
    assert vote.value.status == 201

    validator.goto(server + "/voces#aporte")
    validator.wait_for_function("document.getElementById('m-votes').textContent === '1'")
    assert validator.text_content("#m-code").count("-") == 2
