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
    assert d["force_preuve"] != "forte"  # tant que les réanalyses ne sont pas vérifiées
    md = dossier.to_markdown(d)
    assert "à vérifier" in md and "FICTIF" in md.upper()
