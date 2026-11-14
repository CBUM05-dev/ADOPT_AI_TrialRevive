from src.cv import build_cv_from_rules, detect_biomarker, detect_treatment


def test_wild_type_only_blocks_subgroup():
    bio = detect_biomarker("Inclusion Criteria:\n* Confirmed wtKRAS CRC.\nExclusion Criteria:\n* none", "")
    assert bio["mesure"] and bio["population"] == "sauvage seulement" and not bio["sous_groupe"]


def test_exclusion_of_mutant_means_wild_type_only():
    bio = detect_biomarker("Inclusion Criteria:\n* mCRC\nExclusion Criteria:\n* KRAS mutation", "")
    assert bio["population"] == "sauvage seulement"


def test_mixed_population_allows_subgroup():
    bio = detect_biomarker("Inclusion Criteria:\n* KRAS status known (mutant or wild-type is allowed)", "")
    assert bio["mesure"] and bio["sous_groupe"]


def test_no_marker_means_not_measured_and_none():
    bio = detect_biomarker("Inclusion Criteria:\n* age over 18", "A trial")
    assert bio["mesure"] is False and bio["noms"] is None and bio["population"] is None


def test_treatment_detection():
    t, _ = detect_treatment("Arm A: Drug: Panitumumab | Arm B: Biological: Cetuximab", "x")
    assert t == "panitumumab + cetuximab"
    assert detect_treatment("Arm: chemo", "title")[0] is None


def test_cv_never_invents_method():
    row = {"nct_id": "NCT1", "titre": "t", "bras": "A (EXPERIMENTAL): Panitumumab", "inclusion_exclusion": "KRAS",
           "allocation": "RANDOMIZED", "critere_principal": "OS", "nb_patients": 100, "lien": "u"}
    cv = build_cv_from_rules(row)
    assert cv["biomarqueur_methode"] is None and cv["randomise"] == 1 and cv["extraction"] == "regles"
