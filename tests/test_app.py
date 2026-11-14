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
