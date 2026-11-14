from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_demo_button_runs_and_shows_tabs():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    next(b for b in at.button if b.label == "Cas de démo").click().run()
    assert not at.exception and not at.error
    assert len(at.tabs) == 5


def test_empty_or_unknown_question_does_not_crash():
    for text in ["", "Quel temps fait-il ?"]:
        at = AppTest.from_file(APP, default_timeout=30).run()
        at.text_area[0].set_value(text).run()
        next(b for b in at.button if b.label == "Analyser").click().run()
        assert not at.exception and len(at.error) == 1


APP_UI = str(Path(__file__).resolve().parent.parent / "app_ui.py")


def _btn(at, label):
    for b in list(at.button) + list(at.sidebar.button):
        if label in b.label:
            return b
    raise AssertionError(f"bouton introuvable : {label}")


def _html(at):
    return " ".join(m.value for m in at.markdown)


def test_ui_demo_then_each_page_renders():
    at = AppTest.from_file(APP_UI, default_timeout=30).run()
    assert not at.exception
    _btn(at, "Cas de démo").click().run()
    assert not at.exception and not at.error
    assert "104" in _html(at) and "E4" in _html(at)  # tableau de bord : indicateurs + verdict
    for page, expected in [("Essais retenus", "NCT00364013"), ("Essais écartés", "pas randomisé"),
                           ("Patients", "FICTIVES"), ("Comparaison", "TrialRevive")]:
        _btn(at, page).click().run()
        assert not at.exception and expected in _html(at), page
    _btn(at, "Dossier").click().run()
    assert not at.exception and "Dossier de faisabilité" in _html(at)


def test_ui_pages_without_analysis_show_empty_state():
    at = AppTest.from_file(APP_UI, default_timeout=30).run()
    _btn(at, "Patients").click().run()
    assert not at.exception and "Aucune analyse" in _html(at)


def test_ui_bad_question_shows_error_not_crash():
    at = AppTest.from_file(APP_UI, default_timeout=30).run()
    at.text_area[0].set_value("Quel temps fait-il ?").run()
    _btn(at, "Analyser").click().run()
    assert not at.exception and len(at.error) == 1


def test_ui_has_no_emoji():
    src = Path(APP_UI).read_text(encoding="utf-8")
    emojis = [c for c in src if ord(c) >= 0x1F300 and ord(c) <= 0x1FAFF]
    assert not emojis, f"emojis restants : {set(emojis)}"


def test_ui_comparison_selects_each_record_and_preserves_full_answer(monkeypatch):
    from src import compare, question

    records = [{"question": question.CAS_VEDETTE_TEXTE, "reponse_ia": "A" * 800 + "FIN REPONSE",
                "modele": "Test A", "date": "2026-11-14"},
               {"question": "Autre question", "reponse_ia": "Seconde réponse",
                "modele": "Test B", "date": "2026-11-14"}]
    monkeypatch.setattr(compare, "load_baselines", lambda directory: (records, ["invalide.json : erreur de test"]))
    at = AppTest.from_file(APP_UI, default_timeout=30).run()
    _btn(at, "Cas de démo").click().run()
    _btn(at, "Comparaison").click().run()
    assert not at.exception
    assert at.text_area[1].value.endswith("FIN REPONSE")
    assert "invalide.json" in at.warning[0].value
    at.selectbox[0].select(1).run()
    assert not at.exception and at.text_area[1].value == "Seconde réponse"
    assert any("diffère" in w.value for w in at.warning)


def test_dashboard_demo_without_network(monkeypatch):
    import socket

    real_connect = socket.socket.connect

    def no_external_network(self, address, *args, **kwargs):
        # Windows (asyncio) ouvre une connexion locale en interne : seul le réseau externe est interdit.
        host = address[0] if isinstance(address, tuple) else address
        if host not in ("127.0.0.1", "::1", "localhost"):
            raise AssertionError(f"Appel réseau externe pendant la démo hors ligne : {address}")
        return real_connect(self, address, *args, **kwargs)
    monkeypatch.setattr(socket.socket, "connect", no_external_network)
    at = AppTest.from_file(APP_UI, default_timeout=10).run()
    _btn(at, "Cas de démo").click().run()
    assert not at.exception and not at.error
    assert "252" in _html(at)


def test_ui_other_treatment_explains_missing_internal_arm():
    at = AppTest.from_file(APP_UI, default_timeout=30).run()
    at.text_area[0].set_value("Le statut KRAS change-t-il l'effet du cetuximab ?").run()
    _btn(at, "Analyser").click().run()
    assert not at.exception and not at.error
    _btn(at, "Patients").click().run()
    assert not at.exception
    assert any("aucun bras cetuximab" in c.value for c in at.caption)
    _btn(at, "Dossier").click().run()
    assert not at.exception and "INDÉTERMINÉ" in _html(at)
