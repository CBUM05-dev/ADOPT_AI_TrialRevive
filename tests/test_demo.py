import json
import socket

from src.demo import export_demo
from src.reanalyses import REANALYSES
from src.fetch import RAW_DIR


def test_offline_export_matches_pipeline_and_contains_full_dossier(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("La démo ne doit pas accéder au réseau")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    summary = export_demo(tmp_path)
    assert summary["essais_publics"] == summary["retenus"] + summary["ecartes"] == 104
    assert summary["patients_complets"] == 252
    assert summary["preuve_validee"] is False
    assert summary["question_validee_par_humain"] is False
    assert json.loads((tmp_path / "chiffres.json").read_text(encoding="utf-8")) == summary
    assert "FICTIVES" in (tmp_path / "dossier.md").read_text(encoding="utf-8")
    page = (tmp_path / "dossier.html").read_text(encoding="utf-8")
    assert "252" in page and "NCT00364013" in page
    assert "<script" not in page and '<link' not in page
    assert "non validée" in page


def test_bibliographic_links_match_the_cached_registry_not_human_validation():
    studies = json.loads((RAW_DIR / "pinned.json").read_text(encoding="utf-8"))
    by_id = {s["protocolSection"]["identificationModule"]["nctId"]: s["protocolSection"] for s in studies}
    for nct, info in REANALYSES.items():
        refs = by_id[nct]["referencesModule"]["references"]
        reference = next(r for r in refs if r.get("pmid") == info["pmid"])
        assert info["doi"] in reference["citation"]
        assert info["verifie"] is False
