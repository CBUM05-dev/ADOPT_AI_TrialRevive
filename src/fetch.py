"""Brique 1 : récupérer des essais publics sur ClinicalTrials.gov (API v2) et les ranger en SQLite.

Usage :  python -m src.fetch            (télécharge puis range en base)
         python -m src.fetch --offline  (relit data/raw/*.json sans réseau)
"""
import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

import requests

try:  # utilise les certificats de Windows (utile derrière un antivirus/proxy qui intercepte le HTTPS)
    import truststore

    truststore.inject_into_ssl()
except Exception:
    pass

API = "https://clinicaltrials.gov/api/v2/studies"
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "trials.db"

# Médicaments anti-EGFR : le cas vedette est le panitumumab, le cetuximab donne des essais comparables
DRUGS = ["panitumumab", "cetuximab"]
CONDITION = "colorectal cancer"
MAX_TRIALS = 50

SCHEMA = """
CREATE TABLE IF NOT EXISTS trials (
    nct_id TEXT PRIMARY KEY,
    titre TEXT,
    phase TEXT,
    statut TEXT,
    allocation TEXT,
    bras TEXT,
    inclusion_exclusion TEXT,
    critere_principal TEXT,
    nb_patients INTEGER,
    lien TEXT
);
"""


def fetch_drug(drug: str, max_studies: int = MAX_TRIALS, session=None) -> list[dict]:
    """Télécharge les études pour un médicament, avec pagination et réessais."""
    http = session or requests
    studies, token = [], None
    while len(studies) < max_studies:
        params = {
            "query.cond": CONDITION,
            "query.intr": drug,
            "pageSize": min(50, max_studies - len(studies)),
            "format": "json",
        }
        if token:
            params["pageToken"] = token
        data = None
        for attempt in range(3):
            try:
                resp = http.get(API, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                break
            except requests.RequestException as exc:
                print(f"  [{drug}] essai {attempt + 1}/3 échoué : {exc}", file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        if data is None:
            raise RuntimeError(f"Impossible de joindre ClinicalTrials.gov pour {drug}")
        studies.extend(data.get("studies", []))
        token = data.get("nextPageToken")
        if not token:
            break
    return studies


# Essais pivots anti-EGFR (KRAS analysé après coup dans des publications) : à CONFIRMER par la personne Science
# via le titre affiché au téléchargement. Corriger/compléter cette liste si un NCT ne correspond pas.
PINNED_NCT = [
    "NCT00113763",  # panitumumab vs meilleurs soins de support (étude 20020408)
    "NCT00364013",  # PRIME : FOLFOX4 +/- panitumumab, 1re ligne
    "NCT00339183",  # étude 20050181 : FOLFIRI +/- panitumumab, 2e ligne
    "NCT00079066",  # CO.17 : cetuximab vs meilleurs soins de support
    "NCT00154102",  # CRYSTAL : FOLFIRI +/- cetuximab
    "NCT00125034",  # OPUS : FOLFOX4 +/- cetuximab
]


def fetch_pinned(nct_ids: list[str], session=None) -> list[dict]:
    """Télécharge des études précises par identifiant NCT. Un identifiant introuvable est signalé, pas fatal."""
    http = session or requests
    found = []
    for nct in nct_ids:
        try:
            resp = http.get(f"{API}/{nct}", params={"format": "json"}, timeout=30)
            resp.raise_for_status()
            found.append(resp.json())
        except requests.RequestException as exc:
            print(f"  [pinned] {nct} introuvable : {exc}", file=sys.stderr)
    return found


def parse_study(study: dict) -> dict:
    """Aplatit une étude brute en une ligne pour la base. Champ absent -> None (jamais inventé)."""
    p = study.get("protocolSection", {})
    ident = p.get("identificationModule", {})
    status = p.get("statusModule", {})
    design = p.get("designModule", {})
    arms = p.get("armsInterventionsModule", {})
    elig = p.get("eligibilityModule", {})
    outc = p.get("outcomesModule", {})

    nct = ident.get("nctId")
    bras = [
        f"{a.get('label', '?')} ({a.get('type', '?')}): {', '.join(a.get('interventionNames', []))}"
        for a in arms.get("armGroups", [])
    ]
    primary = [o.get("measure") for o in outc.get("primaryOutcomes", []) if o.get("measure")]
    return {
        "nct_id": nct,
        "titre": ident.get("briefTitle"),
        "phase": ", ".join(design.get("phases", [])) or None,
        "statut": status.get("overallStatus"),
        "allocation": design.get("designInfo", {}).get("allocation"),
        "bras": " | ".join(bras) or None,
        "inclusion_exclusion": elig.get("eligibilityCriteria"),
        "critere_principal": " ; ".join(primary) or None,
        "nb_patients": design.get("enrollmentInfo", {}).get("count"),
        "lien": f"https://clinicaltrials.gov/study/{nct}" if nct else None,
    }


def save_raw(drug: str, studies: list[dict]) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{drug}.json"
    path.write_text(json.dumps(studies, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def load_raw() -> list[dict]:
    studies = []
    for path in sorted(RAW_DIR.glob("*.json")):
        studies.extend(json.loads(path.read_text(encoding="utf-8")))
    return studies


def store(studies: list[dict], db_path: Path = DB_PATH) -> int:
    """Range les études dans SQLite (dédoublonnées par NCT). Retourne le nombre de lignes."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [r for r in (parse_study(s) for s in studies) if r["nct_id"]]
    with sqlite3.connect(db_path) as con:
        con.execute(SCHEMA)
        con.executemany(
            """INSERT OR REPLACE INTO trials
               (nct_id, titre, phase, statut, allocation, bras, inclusion_exclusion,
                critere_principal, nb_patients, lien)
               VALUES (:nct_id, :titre, :phase, :statut, :allocation, :bras,
                       :inclusion_exclusion, :critere_principal, :nb_patients, :lien)""",
            rows,
        )
        return con.execute("SELECT COUNT(*) FROM trials").fetchone()[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="relire data/raw sans réseau")
    args = ap.parse_args()

    if not args.offline:
        for drug in DRUGS:
            print(f"Téléchargement : {drug} ...")
            studies = fetch_drug(drug)
            path = save_raw(drug, studies)
            print(f"  {len(studies)} études -> {path.name}")
        print("Téléchargement : essais pivots (par NCT) ...")
        pinned = fetch_pinned(PINNED_NCT)
        save_raw("pinned", pinned)
        for s in pinned:
            row = parse_study(s)
            print(f"  {row['nct_id']} | {row['allocation']} | n={row['nb_patients']} | {row['titre']}")

    all_studies = load_raw()
    if not all_studies:
        sys.exit("Aucun JSON dans data/raw. Lancez sans --offline ou ajoutez des fichiers à la main.")
    count = store(all_studies)
    print(f"Base prête : {count} essais dans {DB_PATH}")


if __name__ == "__main__":
    main()
