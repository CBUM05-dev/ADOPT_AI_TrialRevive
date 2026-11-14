"""Brique 4 : le moteur. Déterministe, SANS IA.

1) screen_trials : trie les essais en entonnoir, chaque rejet garde sa raison.
2) count_usable  : compte les patients utilisables de l'essai interne (entonnoir 400 -> N).
3) group_summary : médianes de survie par groupe (Kaplan-Meier), descriptif seulement.
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "trials.db"


def load_cvs(db_path: Path = DB_PATH) -> list[dict]:
    with sqlite3.connect(db_path) as con:
        con.row_factory = sqlite3.Row
        return [
            dict(r)
            for r in con.execute(
                "SELECT c.*, t.titre FROM cv c JOIN trials t ON t.nct_id = c.nct_id ORDER BY c.nct_id"
            )
        ]


def screen_trial(q: dict, cv: dict) -> dict:
    """Retourne {retenu, niveau ('direct'|'classe'|None), raison, etape_rejet}."""
    ex = q["exigences"]
    out = {"nct_id": cv["nct_id"], "titre": cv["titre"], "lien": cv["lien"], "nb_patients": cv["nb_patients"]}

    def reject(step, reason):
        return {**out, "retenu": False, "niveau": None, "etape_rejet": step, "raison": reason}

    # 1. randomisé
    if ex["randomise"] and not cv["randomise"]:
        return reject(1, "pas randomisé")
    # 2. traitement
    tr = (cv["traitement"] or "").lower()
    if q["traitement"] in tr:
        niveau = "direct"
    elif any(d in tr for d in q["traitements_classe"]):
        niveau = "classe"
    else:
        return reject(2, f"traitement différent ({cv['traitement'] or 'aucun anti-EGFR détecté'})")
    # 3. biomarqueur mesuré
    if ex["biomarqueur_mesure"] and not cv["biomarqueur_mesure"]:
        return reject(3, f"{q['biomarqueur']} non mesuré (ni dans le registre, ni dans une réanalyse connue)")
    # 4. analyse par sous-groupe possible
    if ex["analyse_sous_groupe"] and not cv["sous_groupe_possible"]:
        return reject(4, f"population limitée à un seul statut ({cv['population_biomarqueur']}) : comparaison muté/sauvage impossible")
    # 5. taille
    if (cv["nb_patients"] or 0) < ex["taille_min"]:
        return reject(5, f"trop petit ({cv['nb_patients']} patients < {ex['taille_min']})")

    return {
        **out,
        "retenu": True,
        "niveau": niveau,
        "etape_rejet": None,
        "raison": "répond à toutes les exigences" + (" (preuve de classe, autre médicament anti-EGFR)" if niveau == "classe" else ""),
        "reanalyse_verifiee": cv.get("reanalyse_verifiee"),
        "n_kras_evalue": cv.get("n_kras_evalue"),
    }


def screen_trials(q: dict, cvs: list[dict]) -> list[dict]:
    return [screen_trial(q, cv) for cv in cvs]


def rejection_summary(results: list[dict]) -> dict:
    steps = {1: "pas randomisé", 2: "traitement différent", 3: "biomarqueur non mesuré", 4: "un seul statut", 5: "trop petit"}
    counts = {label: 0 for label in steps.values()}
    for r in results:
        if not r["retenu"]:
            counts[steps[r["etape_rejet"]]] += 1
    kept = sum(r["retenu"] for r in results)
    return {"total": len(results), "retenus": kept, "ecartes_par_etape": counts}


# ---------- essai interne fictif ----------
def count_usable(df: pd.DataFrame, q: dict) -> dict:
    """Entonnoir : chaque étape retire des patients. Retourne l'entonnoir + le dataframe utilisable."""
    steps = [("Patients dans l'essai interne (fictif)", df)]
    d = df[df["traitement"].isin([q["traitement"], "controle"])]
    steps.append(("Traitement connu", d))
    d = d[d["kras_statut"].isin(["muté", "sauvage"])]
    steps.append((f"Statut {q['biomarqueur']} connu", d))
    d = d[d["methode_test"].isin(q["methodes_valides"])]
    steps.append(("Méthode de test valide", d))
    d = d[d["survie_mois"].notna() & d["evenement"].notna()]
    steps.append(("Données de survie complètes", d))
    funnel = [{"etape": name, "n": len(x)} for name, x in steps]
    return {"entonnoir": funnel, "utilisables": len(d), "data": d}


def kaplan_meier_median(time: pd.Series, event: pd.Series) -> float | None:
    """Médiane de survie de Kaplan-Meier (None si non atteinte)."""
    t = np.asarray(time, dtype=float)
    e = np.asarray(event, dtype=int)
    if len(t) == 0:
        return None
    order = np.argsort(t)
    t, e = t[order], e[order]
    at_risk, surv = len(t), 1.0
    for ti in np.unique(t):
        mask = t == ti
        d = e[mask].sum()
        if d:
            surv *= 1 - d / at_risk
            if surv <= 0.5:
                return float(ti)
        at_risk -= mask.sum()
    return None


def group_summary(data: pd.DataFrame, q: dict) -> list[dict]:
    """Médiane de survie par (statut du biomarqueur x traitement). DESCRIPTIF, pas un test statistique."""
    rows = []
    for status in ["sauvage", "muté"]:
        meds = {}
        for tr in [q["traitement"], "controle"]:
            sub = data[(data["kras_statut"] == status) & (data["traitement"] == tr)]
            meds[tr] = (kaplan_meier_median(sub["survie_mois"], sub["evenement"]), len(sub))
        (m_t, n_t), (m_c, n_c) = meds[q["traitement"]], meds["controle"]
        rows.append(
            {
                "statut": status,
                "n_traite": n_t,
                "n_controle": n_c,
                "mediane_traite": m_t,
                "mediane_controle": m_c,
                "gain_mois": None if m_t is None or m_c is None else round(m_t - m_c, 1),
            }
        )
    return rows
