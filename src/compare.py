"""Comparaison à partir de réponses réelles archivées, sans appel à une IA.

Les appréciations sont celles de l'évaluateur. Retrouver un NCT dans le cache
ne valide ni les chiffres cités, ni la conclusion scientifique d'une réponse.
"""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_DIR = ROOT / "data" / "baseline"
CRITERIA = {
    "compte_patients": "Compte les patients utilisables ?",
    "sources_verifiables": "Sources vérifiables ?",
    "explique_rejets": "Explique les rejets ?",
}


def validate_record(value) -> dict:
    if not isinstance(value, dict):
        raise ValueError("Le fichier doit contenir un objet JSON.")
    for field in ("question", "reponse_ia", "modele", "date"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ValueError(f"Champ {field} manquant ou vide.")
    try:
        if date.fromisoformat(value["date"]).isoformat() != value["date"]:
            raise ValueError("Format non canonique")
    except ValueError as exc:
        raise ValueError("Date attendue : AAAA-MM-JJ.") from exc
    for field in CRITERIA:
        if field in value and not isinstance(value[field], str):
            raise ValueError(f"Le champ {field} doit être du texte.")
    # Conserver la réponse intégrale, y compris ses espaces et sa ponctuation.
    return dict(value)


def parse_record(text: str) -> dict:
    try:
        return validate_record(json.loads(text))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON invalide (ligne {exc.lineno}).") from exc


def load_baselines(directory: Path = BASELINE_DIR) -> tuple[list[dict], list[str]]:
    records, errors = [], []
    for path in sorted(directory.glob("*.json")):
        try:
            records.append(parse_record(path.read_text(encoding="utf-8-sig")))
        except (ValueError, OSError) as exc:
            errors.append(f"{path.name} : {exc}")
    return records, errors


def archive_record(record: dict, directory: Path = BASELINE_DIR) -> Path:
    """Archive locale immuable : jamais de nom fourni par un fichier importé."""
    payload = json.dumps(validate_record(record), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"baseline-{digest}.json"
    try:
        with path.open("x", encoding="utf-8") as out:
            out.write(payload)
    except FileExistsError:
        if path.read_text(encoding="utf-8") != payload:
            raise ValueError("Une archive différente existe déjà à cet emplacement.")
    return path


def same_question(a: str, b: str) -> bool:
    # Une simple correspondance médicament/marqueur ne suffit pas : une question
    # sur l'effectif et une question sur l'effet clinique ne sont pas identiques.
    def normalise(text):
        return " ".join(text.casefold().split()).rstrip(" ?.!…")
    return normalise(a) == normalise(b)


def comparison_rows(d: dict, record: dict) -> list[dict]:
    matched = same_question(d["question"], record["question"])
    n = d["utilisables"]
    trialrevive = {
        "compte_patients": f"{n} patients FICTIFS complets" if n is not None else "Comptage indéterminé ou masqué",
        "sources_verifiables": "Liens NCT ; réanalyses à valider par la personne Science",
        "explique_rejets": f"{len(d['ecartes'])} essais écartés, avec une raison par essai",
    }
    return [{"Critère": label,
             "TrialRevive": trialrevive[key] if matched else "Non évalué sur cette question",
             "IA généraliste (évaluation déclarée)": record.get(key) or "Non évalué"}
            for key, label in CRITERIA.items()]


def audit_nct_references(answer: str) -> list[dict]:
    from src.fetch import load_raw, parse_study

    cached = {r["nct_id"]: r for r in map(parse_study, load_raw())}
    rows = []
    for nct in sorted({n.upper() for n in re.findall(r"\bNCT\d{8}\b", answer, flags=re.I)}):
        trial = cached.get(nct)
        rows.append({"NCT cité": nct,
                     "Cache local": "Présent" if trial else "Absent (existence non déterminée)",
                     "Titre du registre": trial["titre"] if trial else "À vérifier en ligne",
                     "Effectif total du registre": trial["nb_patients"] if trial else None,
                     "Lien": f"https://clinicaltrials.gov/study/{nct}"})
    return rows


def render_comparison(d: dict, directory: Path = BASELINE_DIR) -> None:
    """Vue commune aux deux interfaces ; aucune réponse ni note n'est fabriquée."""
    import streamlit as st

    st.subheader("Comparaison avec une IA généraliste")
    records, errors = load_baselines(directory)
    for error in errors:
        st.warning(error)
    uploaded = st.file_uploader("Importer une réponse réelle (JSON)", type=["json"])
    imported = None
    if uploaded is not None:
        try:
            imported = parse_record(uploaded.getvalue().decode("utf-8-sig"))
            records.append(imported)
        except (ValueError, UnicodeError) as exc:
            st.error(f"Import impossible : {exc}")
    if not records:
        st.info("Aucune réponse enregistrée. Importez une réponse réelle ; aucune comparaison n'a encore été effectuée.")
        st.caption("Format et protocole : data/baseline/LISEZ_MOI.md")
        return
    index = st.selectbox("Réponse à examiner", range(len(records)),
                          index=len(records) - 1 if imported else 0,
                          format_func=lambda i: f"{i + 1}. {records[i]['modele']} · {records[i]['date']} · {records[i]['question']}")
    record = records[index]
    st.markdown(f"**Question posée :** {record['question']}")
    st.caption(f"Modèle : {record['modele']} — Date : {record['date']}")
    if record.get("contexte"):
        st.write("Contexte de l'expérience :", str(record["contexte"]))
    if not same_question(d["question"], record["question"]):
        st.warning("La question archivée diffère de la question analysée. Les résultats TrialRevive ne sont pas comparables ; relancez exactement la même question si elle est prise en charge.")
    st.table(comparison_rows(d, record))
    st.text_area("Réponse brute intégrale", record["reponse_ia"], height=300, disabled=True)
    with st.expander("Examiner les NCT cités"):
        st.caption("Le cache permet de retrouver un essai, pas de valider la réponse. Un NCT absent du cache peut exister. L'effectif total du registre n'est pas l'effectif analysé pour KRAS.")
        rows = audit_nct_references(record["reponse_ia"])
        if rows:
            st.dataframe(rows, hide_index=True, column_config={"Lien": st.column_config.LinkColumn("Lien")})
        else:
            st.write("Aucun numéro NCT détecté ; les autres références restent à vérifier.")
    payload = json.dumps(record, ensure_ascii=False, indent=2)
    st.download_button("Télécharger l'archive JSON", payload, "comparaison_ia.json", "application/json")
    if imported is not None and record is imported:
        if st.button("Archiver cette réponse localement"):
            try:
                path = archive_record(record, directory)
                st.success(f"Réponse intégrale archivée : {path.name}")
            except (ValueError, OSError) as exc:
                st.error(f"Archivage impossible : {exc}")
