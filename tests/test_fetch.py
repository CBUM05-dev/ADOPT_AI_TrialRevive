import sqlite3

from src.fetch import parse_study, store

SAMPLE = {
    "protocolSection": {
        "identificationModule": {"nctId": "NCT00000001", "briefTitle": "Panitumumab test"},
        "statusModule": {"overallStatus": "COMPLETED"},
        "designModule": {
            "phases": ["PHASE3"],
            "designInfo": {"allocation": "RANDOMIZED"},
            "enrollmentInfo": {"count": 300},
        },
        "armsInterventionsModule": {
            "armGroups": [{"label": "A", "type": "EXPERIMENTAL", "interventionNames": ["Panitumumab"]}]
        },
        "eligibilityModule": {"eligibilityCriteria": "KRAS wild-type"},
        "outcomesModule": {"primaryOutcomes": [{"measure": "Overall survival"}]},
    }
}


def test_parse_complete():
    row = parse_study(SAMPLE)
    assert row["nct_id"] == "NCT00000001"
    assert row["lien"] == "https://clinicaltrials.gov/study/NCT00000001"
    assert row["allocation"] == "RANDOMIZED"
    assert row["nb_patients"] == 300


def test_parse_missing_fields_are_none():
    row = parse_study({"protocolSection": {"identificationModule": {"nctId": "NCT2"}}})
    assert row["phase"] is None and row["critere_principal"] is None and row["nb_patients"] is None


def test_store_deduplicates(tmp_path):
    db = tmp_path / "t.db"
    assert store([SAMPLE, SAMPLE], db) == 1
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM trials").fetchone()[0] == 1
