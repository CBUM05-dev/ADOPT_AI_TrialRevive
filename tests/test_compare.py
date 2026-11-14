import json

import pytest

from src import compare, question


@pytest.fixture
def record():
    return {"question": question.CAS_VEDETTE_TEXTE,
            "reponse_ia": "  Réponse de test, pas une mesure de performance.\nNCT00364013 et NCT99999999.\n",
            "modele": "Modèle de test", "date": "2026-11-14"}


@pytest.mark.parametrize("payload", ['[]', 'null', '{', '{}',
    '{"question":"q","reponse_ia":"r","modele":"m","date":"hier"}'])
def test_invalid_records_are_reported(payload):
    with pytest.raises(ValueError):
        compare.parse_record(payload)


def test_loading_skips_bad_records_without_losing_good_ones(tmp_path, record):
    (tmp_path / "a.json").write_text(json.dumps(record))
    (tmp_path / "b.json").write_text('[]')
    (tmp_path / "c.json").write_text(json.dumps({**record, "modele": "Autre modèle"}))
    records, errors = compare.load_baselines(tmp_path)
    assert len(records) == 2 and len(errors) == 1
    assert "b.json" in errors[0]
    assert records[0]["reponse_ia"] == record["reponse_ia"]


def test_archive_is_lossless_repeatable_and_does_not_overwrite(tmp_path, record):
    path = compare.archive_record(record, tmp_path)
    assert compare.archive_record(record, tmp_path) == path
    assert json.loads(path.read_text(encoding="utf-8")) == record
    second = compare.archive_record({**record, "reponse_ia": "Autre réponse"}, tmp_path)
    assert second != path and len(list(tmp_path.glob("*.json"))) == 2
    assert json.loads(path.read_text(encoding="utf-8"))["reponse_ia"] == record["reponse_ia"]


def test_comparison_preserves_evaluation_and_does_not_assume_ia_failure(record):
    d = {"question": record["question"], "utilisables": 252, "ecartes": [{}]}
    record["sources_verifiables"] = "Toutes les références exactes après relecture"
    rows = compare.comparison_rows(d, record)
    assert rows[0]["IA généraliste (évaluation déclarée)"] == "Non évalué"
    assert "Toutes les références exactes" in rows[1]["IA généraliste (évaluation déclarée)"]
    assert "252" in rows[0]["TrialRevive"]
    other = {**record, "question": "Combien de patients KRAS avec panitumumab ?"}
    assert all(r["TrialRevive"] == "Non évalué sur cette question" for r in compare.comparison_rows(d, other))


def test_nct_cache_lookup_does_not_claim_absent_trial_is_fake():
    rows = compare.audit_nct_references("nct00364013, NCT00364013 et NCT99999999")
    assert len(rows) == 2
    assert rows[0]["Cache local"] == "Présent"
    assert "PRIME" in rows[0]["Titre du registre"]
    assert "non déterminée" in rows[1]["Cache local"]
