import pandas as pd
import pytest

from src import engine, fake_data, question

Q = question.parse_question(question.CAS_VEDETTE_TEXTE)


def cv(**kw):
    base = {"nct_id": "NCT1", "titre": "t", "lien": "u", "nb_patients": 500, "randomise": 1,
            "traitement": "panitumumab", "biomarqueur_mesure": 1, "sous_groupe_possible": 1,
            "population_biomarqueur": "mixte", "reanalyse_verifiee": 0, "n_kras_evalue": 400}
    base.update(kw)
    return base


def test_question_parsing():
    assert Q["traitement"] == "panitumumab" and Q["biomarqueur"] == "KRAS" and Q["traitements_classe"] == ["cetuximab"]
    with pytest.raises(ValueError):
        question.parse_question("Quel temps fait-il ?")


def test_every_rejection_has_reason():
    cases = [(dict(randomise=0), 1), (dict(traitement="chimio"), 2), (dict(biomarqueur_mesure=0), 3),
             (dict(sous_groupe_possible=0, population_biomarqueur="sauvage seulement"), 4), (dict(nb_patients=50), 5)]
    for kw, step in cases:
        r = engine.screen_trial(Q, cv(**kw))
        assert not r["retenu"] and r["etape_rejet"] == step and r["raison"]


def test_keep_direct_and_class():
    assert engine.screen_trial(Q, cv())["niveau"] == "direct"
    assert engine.screen_trial(Q, cv(traitement="cetuximab"))["niveau"] == "classe"


def test_funnel_is_consistent_and_deterministic():
    df = fake_data.generate()
    a, b = engine.count_usable(df, Q), engine.count_usable(df, Q)
    ns = [s["n"] for s in a["entonnoir"]]
    assert ns[0] == 400 and ns == sorted(ns, reverse=True) and a["utilisables"] == ns[-1] == b["utilisables"]
    assert 0 < a["utilisables"] < 400


def test_fake_data_proportions_and_seed():
    df = fake_data.generate()
    assert len(df) == 400 and df.equals(fake_data.generate())
    p = df["kras_statut"].value_counts(normalize=True)
    assert abs(p["muté"] - 0.40) < 0.06 and abs(p["sauvage"] - 0.50) < 0.06 and abs(p["inconnu"] - 0.10) < 0.05
    assert df["patient_id"].str.startswith("FAKE-").all()


def test_km_median():
    assert engine.kaplan_meier_median(pd.Series([1, 2, 3, 4]), pd.Series([1, 1, 1, 1])) == 2.0
    assert engine.kaplan_meier_median(pd.Series([1, 2]), pd.Series([0, 0])) is None


def test_availability_scale_s0_to_s4():
    df = fake_data.generate()
    r = engine.count_usable(df, Q)
    ns = [s["n"] for s in r["entonnoir"]]
    assert len(ns) == 5 and ns[0] == 400 and ns == sorted(ns, reverse=True)
    assert r["utilisables"] == ns[-1] and r["statut"] == "calculé"


def test_unvalidated_key_gives_indeterminate_not_a_number():
    r = engine.count_usable(fake_data.generate(), Q, key_validated=False)
    assert r["utilisables"] is None and r["statut"] == "indéterminé" and len(r["entonnoir"]) == 4


def test_small_totals_are_masked():
    assert engine.mask(4) is None and engine.mask(5) == 5
    tiny = fake_data.generate().head(30)
    for g in engine.group_summary(engine.count_usable(tiny, Q)["data"], Q):
        for k in ("n_traite", "n_controle"):
            assert g[k] is None or g[k] >= 5


@pytest.mark.parametrize("marker", ["NRAS", "BRAF", "RAS", "KRAS et BRAF"])
def test_unsupported_or_ambiguous_markers_never_reuse_kras_data(marker):
    with pytest.raises(ValueError):
        question.parse_question(f"Le statut {marker} change-t-il l'effet du panitumumab ?")


def test_other_drug_has_no_internal_treatment_arm():
    q = question.parse_question("Le statut KRAS change-t-il l'effet du cetuximab ?")
    u = engine.count_usable(fake_data.load(), q)
    assert u["utilisables"] is None and u["statut"] == "indéterminé"
    assert u["data"].empty and "aucun bras cetuximab" in u["raison_indetermination"]
