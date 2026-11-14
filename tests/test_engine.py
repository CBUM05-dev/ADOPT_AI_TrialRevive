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
