"""Tests de l'API web (serveur réel lancé dans un fil, sans navigateur)."""
import threading
import time

import pytest
import requests
import uvicorn

import server
from src import question


@pytest.fixture(scope="module")
def base():
    port = 8791
    srv = uvicorn.Server(uvicorn.Config(server.app, host="127.0.0.1", port=port, log_level="error"))
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()
    for _ in range(50):
        try:
            requests.get(f"http://127.0.0.1:{port}/api/info", timeout=1)
            break
        except requests.ConnectionError:
            time.sleep(0.1)
    yield f"http://127.0.0.1:{port}"
    srv.should_exit = True
    t.join(timeout=5)


def test_home_and_assets_are_served_locally(base):
    page = requests.get(base + "/")
    assert page.status_code == 200 and "TrialRevive" in page.text
    for path in ("/assets/css/app.css", "/assets/js/app.js", "/assets/js/illustration.js", "/assets/fonts/Manrope-Variable.ttf",
                 "/assets/brand/TrialRevive_logo_horizontal_noir.svg", "/assets/brand/TrialRevive_icone_carree.png"):
        assert requests.get(base + path).status_code == 200, path
    assert "http" not in " ".join(
        line for line in page.text.splitlines() if "src=" in line or "href=" in line and "stylesheet" in line
    ).replace("http://www.w3.org", "")  # aucune ressource distante


def test_analyze_demo_matches_pipeline(base):
    r = requests.post(base + "/api/analyze", json={"question": question.CAS_VEDETTE_TEXTE})
    d = r.json()["dossier"]
    assert r.status_code == 200
    assert d["rejection"]["total"] == 104 and len(d["retenus"]) == 6 and d["utilisables"] == 252
    assert d["verdict"]["E"] in ("E3", "E4") and d["verdict"]["preuve_verifiee"] is False


def test_bad_input_gives_clear_errors(base):
    for body, expected in [({"question": ""}, "Écrivez"), ({"question": "Quel temps fait-il ?"}, "non reconnue"),
                           ({"question": "x" * 700}, "trop longue")]:
        r = requests.post(base + "/api/analyze", json=body)
        assert r.status_code == 400 and expected in r.json()["error"]
    assert requests.post(base + "/api/analyze", data="pas du json").status_code == 400


def test_comparison_endpoints_do_not_invent_and_validate(base):
    assert "records" in requests.get(base + "/api/baselines").json()
    rec = {"question": question.CAS_VEDETTE_TEXTE, "reponse_ia": "Voir NCT00364013 et NCT99999999 <script>x</script>",
           "modele": "Modèle de test", "date": "2026-11-14"}
    ok = requests.post(base + "/api/baselines/validate", json={"text": __import__("json").dumps(rec)})
    assert ok.status_code == 200 and ok.json()["record"]["reponse_ia"] == rec["reponse_ia"]
    bad = requests.post(base + "/api/baselines/validate", json={"text": "{ pas json"})
    assert bad.status_code == 400
    out = requests.post(base + "/api/compare", json={"question": question.CAS_VEDETTE_TEXTE, "record": rec}).json()
    assert out["meme_question"] is True and {n["NCT cité"] for n in out["nct"]} == {"NCT00364013", "NCT99999999"}
    present = {n["NCT cité"]: n["Cache local"] for n in out["nct"]}
    assert present["NCT00364013"] == "Présent" and present["NCT99999999"].startswith("Absent")


def test_markdown_download(base):
    r = requests.get(base + "/api/dossier.md")
    assert r.status_code == 200 and "attachment" in r.headers["content-disposition"] and "Dossier de faisabilité" in r.text
