from src import engine, question, verdict

Q = question.parse_question(question.CAS_VEDETTE_TEXTE)


def kept():
    return [r for r in engine.screen_trials(Q, engine.load_cvs()) if r["retenu"]]


def test_document_example_sizes():
    # exemple du document : HR 0,55 chez porteurs, aucun effet chez non porteurs, 50 % de porteurs
    s = verdict.confirmation_trial_size(0.55, 0.5)
    assert s["hr_dilue"] == 0.74 and 345 <= s["evenements_tous"] <= 360 and 85 <= s["evenements_selectionnes"] <= 92


def test_interaction_events_formula():
    assert 170 <= verdict.events_needed_interaction(0.55, 1.0) <= 180  # ~175 par groupe


def test_caps_hold():
    v = verdict.build_verdict(kept())
    for t in v["essais"]:
        assert verdict.level_at_least(t["plafond"], t["E"])  # E jamais au-dessus du plafond
        if t["niveau"] == "classe":
            assert t["E"] in ("E2", "E3") and t["E"] != "E4"


def test_hypothesis_level_and_gains_follow_table():
    v = verdict.build_verdict(kept())
    assert v["E"] == "E4"
    codes = {g["code"] for g in v["gains"] if "gains" in v} if "gains" in v else {g["code"] for g in v["G"]}
    assert {"G1", "G2", "G3", "G6"} <= codes
    # sans essai : E0 et aucun gain
    empty = verdict.build_verdict([])
    assert empty["E"] == "E0" and empty["G"] == []


def test_e4_needs_two_direct_trials():
    one = [t for t in kept() if t["niveau"] == "direct"][:1]
    assert verdict.build_verdict(one)["E"] != "E4"
