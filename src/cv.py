"""Brique 2 : le "CV" de chaque essai = une fiche structurée.

Deux modes :
  - règles (mots-clés) pour TOUS les essais  -> python -m src.cv
  - IA Claude pour 2-3 essais (texte public)  -> python -m src.cv --ai NCT00614393 NCT...

Règle d'or : si une info n'est pas dans le texte, la valeur est None. Rien n'est inventé.
Chaque champ déduit garde un extrait de texte ("preuves") qui le justifie.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "trials.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS cv (
    nct_id TEXT PRIMARY KEY,
    traitement TEXT,
    comparateur TEXT,
    randomise INTEGER,
    biomarqueur_mesure INTEGER,
    biomarqueur_nom TEXT,
    population_biomarqueur TEXT,
    biomarqueur_methode TEXT,
    sous_groupe_possible INTEGER,
    critere_principal TEXT,
    nb_patients INTEGER,
    extraction TEXT,
    preuves TEXT,
    lien TEXT,
    n_kras_evalue INTEGER,
    reanalyse_verifiee INTEGER
);
"""

RE_PANI = re.compile(r"panitumumab|vectibix", re.I)
RE_CETUX = re.compile(r"cetuximab|erbitux", re.I)
RE_MARKER = re.compile(r"(?<![A-Za-z])(?:wt|m)?(KRAS|NRAS|HRAS|BRAF|RAS)\b", re.I)
RE_MIXED = re.compile(
    r"regardless|irrespective|(mutant|mutated)\s*(or|and|/)\s*wild|wild[\s-]?type\s*(or|and|/)\s*(mutant|mutated)", re.I
)
RE_WT = re.compile(r"wild[\s-]?type|\bwt\b|\bwt[-\s]?(KRAS|RAS)|(KRAS|RAS)[\s-]?wt|non[-\s]?mutated|without mutation", re.I)
RE_MUT = re.compile(r"mutant|mutated|mutation", re.I)


def _snippet(text: str, match: re.Match, width: int = 90) -> str:
    start, end = max(0, match.start() - width), min(len(text), match.end() + width)
    return " ".join(text[start:end].split())


def _split_criteria(text: str) -> tuple[str, str]:
    """Sépare critères d'inclusion / d'exclusion."""
    m = re.search(r"exclusion criteria", text, re.I)
    return (text[: m.start()], text[m.start():]) if m else (text, "")


def detect_treatment(bras: str, titre: str) -> tuple[str | None, str | None]:
    blob = f"{titre or ''} {bras or ''}"
    found = []
    m1, m2 = RE_PANI.search(blob), RE_CETUX.search(blob)
    if m1:
        found.append("panitumumab")
    if m2:
        found.append("cetuximab")
    return (" + ".join(found) or None), (_snippet(blob, m1 or m2) if (m1 or m2) else None)


def detect_comparator(bras: str) -> str | None:
    """Comparateur = bras de type ACTIVE_COMPARATOR / PLACEBO_COMPARATOR / NO_INTERVENTION (si présent)."""
    if not bras:
        return None
    parts = [b.strip() for b in bras.split(" | ") if re.search(r"\((ACTIVE_COMPARATOR|PLACEBO_COMPARATOR|SHAM_COMPARATOR|NO_INTERVENTION)\)", b)]
    return " | ".join(parts) or None


def detect_biomarker(criteria: str, titre: str) -> dict:
    """Détecte KRAS/RAS et dit si la population est restreinte à un statut (wild-type seulement, etc.).

    Le tri par sous-groupe n'est possible que si les deux statuts (muté / sauvage) sont inclus.
    """
    criteria, titre = criteria or "", titre or ""
    inc, exc = _split_criteria(criteria)
    names, evidence = [], []
    for part, label in ((titre, "titre"), (inc, "inclusion"), (exc, "exclusion")):
        for m in RE_MARKER.finditer(part):
            n = m.group(1).upper()
            if n not in names:
                names.append(n)
                evidence.append(f"[{label}] {_snippet(part, m)}")
    if not names:
        return {"mesure": False, "noms": None, "population": None, "sous_groupe": False, "preuves": []}

    # Restriction de population : regarder les phrases qui mentionnent un marqueur RAS/KRAS
    def sentences(txt):
        return [s for s in re.split(r"[\n.;]", txt) if RE_MARKER.search(s)]

    wt_inc = any(RE_WT.search(s) for s in sentences(inc + " " + titre))
    mut_inc = any(RE_MUT.search(s) and not RE_WT.search(s) for s in sentences(inc + " " + titre))
    mut_exc = any(RE_MUT.search(s) for s in sentences(exc))

    mixed = any(RE_MIXED.search(s) for s in sentences(inc + " " + titre))
    if mixed:
        pop, sous = "mixte ou non précisé", True
    elif wt_inc or mut_exc:
        pop, sous = "sauvage seulement", False
    elif mut_inc:
        pop, sous = "muté seulement", False
    else:
        pop, sous = "mixte ou non précisé", True
    return {"mesure": True, "noms": ", ".join(names), "population": pop, "sous_groupe": sous, "preuves": evidence[:4]}


def build_cv_from_rules(row: dict) -> dict:
    treat, treat_ev = detect_treatment(row["bras"], row["titre"])
    bio = detect_biomarker(row["inclusion_exclusion"], row["titre"])
    preuves = []
    if treat_ev:
        preuves.append(f"[traitement] {treat_ev}")
    preuves += bio["preuves"]
    return {
        "nct_id": row["nct_id"],
        "traitement": treat,
        "comparateur": detect_comparator(row["bras"]),
        "randomise": 1 if row["allocation"] == "RANDOMIZED" else (0 if row["allocation"] else None),
        "biomarqueur_mesure": int(bio["mesure"]),
        "biomarqueur_nom": bio["noms"],
        "population_biomarqueur": bio["population"],
        "biomarqueur_methode": None,  # nécessite de lire protocole/publication (mode IA ou manuel)
        "sous_groupe_possible": int(bio["sous_groupe"]),
        "critere_principal": row["critere_principal"],
        "nb_patients": row["nb_patients"],
        "extraction": "regles",
        "preuves": json.dumps(preuves, ensure_ascii=False),
        "lien": row["lien"],
    }


def apply_reanalysis(cv: dict) -> dict:
    """Essais conçus avant KRAS : une réanalyse publiée rend l'analyse par sous-groupe possible."""
    from src.reanalyses import REANALYSES

    info = REANALYSES.get(cv["nct_id"])
    cv.setdefault("n_kras_evalue", None)
    cv.setdefault("reanalyse_verifiee", None)
    if not info:
        return cv
    preuves = json.loads(cv["preuves"] or "[]")
    preuves.append(f"[réanalyse publiée] {info['publication']} -> {info['conclusion']}")
    cv.update(
        biomarqueur_mesure=1,
        biomarqueur_nom=cv["biomarqueur_nom"] or "KRAS",
        population_biomarqueur="mixte (réanalyse rétrospective)",
        sous_groupe_possible=1,
        n_kras_evalue=info["n_kras_evalue"],
        reanalyse_verifiee=int(info["verifie"]),
        extraction="regles+reanalyse",
        preuves=json.dumps(preuves, ensure_ascii=False),
    )
    return cv


def save_cv(cv: dict, con: sqlite3.Connection) -> None:
    cv = apply_reanalysis(dict(cv))
    cols = list(cv)
    con.execute(
        f"INSERT OR REPLACE INTO cv ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})", cv
    )


# ---------- Mode IA (2-3 essais, textes PUBLICS uniquement) ----------
AI_PROMPT = """Tu lis la fiche PUBLIQUE d'un essai clinique. Remplis un JSON avec exactement ces clés :
biomarqueur_nom (str|null), population_biomarqueur ("sauvage seulement"|"muté seulement"|"mixte ou non précisé"|null),
biomarqueur_methode (str|null : méthode ou exons testés, si écrit), sous_groupe_possible (true|false|null),
preuves (liste de courts extraits COPIÉS du texte).
Règle : si l'information n'est pas dans le texte, mets null. N'invente rien. Réponds avec le JSON seul.

TITRE: {titre}
BRAS: {bras}
CRITÈRES: {criteres}
CRITÈRE PRINCIPAL: {primaire}
"""


def extract_with_ai(row: dict, base_cv: dict) -> dict:
    from anthropic import Anthropic
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY manquante dans .env")
    client = Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=800,
        messages=[{"role": "user", "content": AI_PROMPT.format(
            titre=row["titre"], bras=row["bras"], criteres=(row["inclusion_exclusion"] or "")[:6000],
            primaire=row["critere_principal"])}],
    )
    text = msg.content[0].text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    data = json.loads(text)
    allowed = {"biomarqueur_nom", "population_biomarqueur", "biomarqueur_methode", "sous_groupe_possible", "preuves"}
    cv = dict(base_cv)
    for k in allowed & data.keys():
        v = data[k]
        if k == "sous_groupe_possible" and v is not None:
            v = int(bool(v))
        if k == "preuves":
            v = json.dumps(v, ensure_ascii=False)
        cv[k] = v
    if cv.get("biomarqueur_nom"):
        cv["biomarqueur_mesure"] = 1
    cv["extraction"] = "ia"
    return cv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ai", nargs="*", metavar="NCT", help="extraction IA pour ces essais")
    args = ap.parse_args()

    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        con.execute(SCHEMA)
        for col in ("n_kras_evalue INTEGER", "reanalyse_verifiee INTEGER"):
            try:
                con.execute(f"ALTER TABLE cv ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass
        rows = [dict(r) for r in con.execute("SELECT * FROM trials")]
        if not rows:
            sys.exit("Table trials vide : lancez d'abord python -m src.fetch")

        by_id = {r["nct_id"]: r for r in rows}
        if args.ai is not None:
            for nct in args.ai:
                if nct not in by_id:
                    print(f"{nct} absent de la base, ignoré")
                    continue
                cv = extract_with_ai(by_id[nct], build_cv_from_rules(by_id[nct]))
                save_cv(cv, con)
                print(f"IA OK : {nct}")
        else:
            ai_done = {r[0] for r in con.execute("SELECT nct_id FROM cv WHERE extraction='ia'")}
            for r in rows:
                if r["nct_id"] not in ai_done:  # ne pas écraser une fiche IA validée
                    save_cv(build_cv_from_rules(r), con)
            n = con.execute("SELECT COUNT(*) FROM cv").fetchone()[0]
            print(f"{n} fiches dans la table cv")


if __name__ == "__main__":
    main()
