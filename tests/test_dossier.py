from src import dossier, engine, fake_data, question


def run():
    q = question.parse_question(question.CAS_VEDETTE_TEXTE)
    scr = engine.screen_trials(q, engine.load_cvs())
    u = engine.count_usable(fake_data.load(), q)
    return dossier.build_dossier(q, scr, engine.rejection_summary(scr), u, engine.group_summary(u["data"], q)), scr, u


def test_numbers_match_engine():
    d, scr, u = run()
    assert d["utilisables"] == u["utilisables"] == d["entonnoir"][-1]["n"]
    assert len(d["retenus"]) == sum(r["retenu"] for r in scr)
    md = dossier.to_markdown(d)
    assert str(u["utilisables"]) in md


def test_sources_are_real_links_and_unverified_is_flagged():
    d, _, _ = run()
    assert d["sources"] and all(s["lien"].startswith("https://clinicaltrials.gov/study/NCT") for s in d["sources"])
    assert d["verdict"]["preuve_verifiee"] is False  # tant que les réanalyses ne sont pas vérifiées
    md = dossier.to_markdown(d)
    assert "à vérifier" in md and "FICTIF" in md.upper()


def test_verdict_and_sizes_in_dossier():
    d, _, _ = run()
    v = d["verdict"]
    assert v["R"] == "R0" and v["E"] in ("E3", "E4") and v["G"]
    assert d["essai_confirmation"]["evenements_selectionnes"] < d["essai_confirmation"]["evenements_tous"]
    md = dossier.to_markdown(d)
    assert "ATTEIGNABLE" in md and "à confirmer" in md and "Schoenfeld" in md
