"""Brique 4 : le moteur. Déterministe, SANS IA.

1) screen_trials : trie les essais en entonnoir, chaque rejet garde sa raison.
2) count_usable  : compte les patients utilisables de l'essai interne (entonnoir 400 -> N).
3) group_summary : médianes de survie par groupe (Kaplan-Meier), descriptif seulement.
"""
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from src.tolerances import COUVERTURE_IDEALE, COUVERTURE_MIN, LEVELS, TOLERANCES, level_min

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


def _coverage(cv: dict):
    n, tot = cv.get("n_kras_evalue"), cv.get("nb_patients")
    return (n / tot) if n and tot else None


def screen_trial(q: dict, cv: dict) -> dict:
    """Retourne {retenu, niveau, raison, etape_rejet, score, plafond, bonus, ecarts}.

    Obligatoire : un échec élimine. Toléré : le score baisse et la preuve est plafonnée. Idéal : bonus de classement.
    """
    ex = q["exigences"]
    out = {"nct_id": cv["nct_id"], "titre": cv["titre"], "lien": cv["lien"], "nb_patients": cv["nb_patients"]}

    def reject(step, reason):
        return {**out, "retenu": False, "niveau": None, "etape_rejet": step, "raison": reason}

    # --- OBLIGATOIRE ---
    if ex["randomise"] and not cv["randomise"]:
        return reject(1, "pas randomisé")
    tr = (cv["traitement"] or "").lower()
    if q["traitement"] in tr:
        niveau = "direct"
    elif any(d in tr for d in q["traitements_classe"]):
        niveau = "classe"
    else:
        return reject(2, f"traitement différent ({cv['traitement'] or 'aucun anti-EGFR détecté'})")
    if ex["biomarqueur_mesure"] and not cv["biomarqueur_mesure"]:
        return reject(3, f"{q['biomarqueur']} non mesuré (ni dans le registre, ni dans une réanalyse connue)")
    if ex["analyse_sous_groupe"] and not cv["sous_groupe_possible"]:
        return reject(4, f"population limitée à un seul statut ({cv['population_biomarqueur']}) : comparaison muté/sauvage impossible")
    if (cv["nb_patients"] or 0) < ex["taille_min"]:
        return reject(5, f"trop petit ({cv['nb_patients']} patients < {ex['taille_min']})")
    cov = _coverage(cv)
    if cov is not None and cov < COUVERTURE_MIN:
        return reject(6, f"statut {q['biomarqueur']} connu pour seulement {cov:.0%} des patients (minimum {COUVERTURE_MIN:.0%})")

    # --- TOLÉRÉ : chaque écart coûte un score et plafonne la preuve ---
    used = []
    if niveau == "classe":
        used.append("molecule_classe")
    if cov is None:
        used.append("couverture_inconnue")
    elif cov < COUVERTURE_IDEALE:
        used.append("couverture_60_80")
    prim = (cv.get("critere_principal") or "").lower()
    if re.search(r"respon|remission|orr", prim) and not re.search(r"surviv|overall|progression|os|pfs", prim):
        used.append("critere_substitue")

    score, plafond, ecarts = 1.0, "E4", []
    for key in used:
        t = TOLERANCES[key]
        score *= t["score"]
        plafond = level_min(plafond, t["plafond"])
        ecarts.append(t["phrase"])

    # --- IDÉAL : bonus de classement ---
    bonus = int(niveau == "direct") + int(cov is not None and cov >= COUVERTURE_IDEALE)

    return {
        **out,
        "retenu": True,
        "niveau": niveau,
        "etape_rejet": None,
        "raison": "répond à toutes les exigences obligatoires" + (f", avec {len(ecarts)} écart(s) toléré(s)" if ecarts else ""),
        "score": round(score, 2),
        "plafond": plafond,
        "bonus": bonus,
        "couverture": cov,
        "ecarts": ecarts,
        "reanalyse_verifiee": cv.get("reanalyse_verifiee"),
        "n_kras_evalue": cv.get("n_kras_evalue"),
    }


def screen_trials(q: dict, cvs: list[dict]) -> list[dict]:
    """Retenus classés : plafond de preuve, puis score, puis bonus, puis effectif (comme dans la description technique)."""
    res = [screen_trial(q, cv) for cv in cvs]
    kept = sorted(
        [r for r in res if r["retenu"]],
        key=lambda r: (-LEVELS.index(r["plafond"]), -r["score"], -r["bonus"], -(r["nb_patients"] or 0)),
    )
    return kept + [r for r in res if not r["retenu"]]


def rejection_summary(results: list[dict]) -> dict:
    steps = {1: "pas randomisé", 2: "traitement différent", 3: "biomarqueur non mesuré", 4: "un seul statut", 5: "trop petit", 6: "statut connu pour trop peu de patients"}
    counts = {label: 0 for label in steps.values()}
    for r in results:
        if not r["retenu"]:
            counts[steps[r["etape_rejet"]]] += 1
    kept = sum(r["retenu"] for r in results)
    return {"total": len(results), "retenus": kept, "ecartes_par_etape": counts}


# ---------- essai interne fictif ----------
MASK_BELOW = 5  # un total inférieur à 5 ne sort jamais (risque de réidentification)


def mask(n: int):
    """Total publiable : None si < 5."""
    return None if n < MASK_BELOW else int(n)


def count_usable(df: pd.DataFrame, q: dict, key_validated: bool = True) -> dict:
    """Échelle de disponibilité : chaque patient monte de S0 (prévu) à S4 (complet). Seuls les S4 comptent.

    S0 prévu -> S1 collecté -> S2 existant -> S3 utilisable -> S4 complet.
    Si le lien patient/bras/résultats n'est pas validé (key_validated=False) : résultat « indéterminé », jamais une estimation.
    """
    s0 = df
    s1 = s0[s0["kras_statut"].isin(["muté", "sauvage"])]                                  # un test a été fait
    s2 = s1[s1["echantillon_en_stock"] == 1]                                                # échantillon encore en stock
    s3 = s2[(s2["quantite_suffisante"] == 1) & (s2["consentement_ok"] == 1)
            & s2["methode_test"].isin(q["methodes_valides"])]                              # quantité, consentement, méthode valide
    s4 = s3[(s3["cle_liaison_valide"] == 1) & s3["traitement"].isin([q["traitement"], "controle"])
            & s3["survie_mois"].notna() & s3["evenement"].notna()]                         # relié au bras et au résultat
    names = [
        ("S0 prévu : patients de l'essai", s0),
        ("S1 collecté : statut du marqueur testé", s1),
        ("S2 existant : échantillon encore en stock", s2),
        ("S3 utilisable : quantité, consentement et méthode OK", s3),
        ("S4 complet : relié à son groupe et à son résultat", s4),
    ]
    funnel = [{"etape": name, "n": len(x), "n_publie": mask(len(x))} for name, x in names]
    missing_treatment = not (df["traitement"] == q["traitement"]).any()
    if not key_validated or missing_treatment:
        reason = (f"aucun bras {q['traitement']} dans l'essai interne fictif" if missing_treatment
                  else "le lien entre les données n'est pas validé")
        return {"entonnoir": funnel[:4], "utilisables": None, "statut": "indéterminé",
                "raison_indetermination": reason, "data": s4.iloc[0:0]}
    return {"entonnoir": funnel, "utilisables": mask(len(s4)), "statut": "calculé", "data": s4}


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
                "n_traite": mask(n_t),
                "n_controle": mask(n_c),
                "mediane_traite": m_t if n_t >= MASK_BELOW else None,
                "mediane_controle": m_c if n_c >= MASK_BELOW else None,
                "evenements": int(data[(data["kras_statut"] == status)]["evenement"].sum()),
                "gain_mois": None if (m_t is None or m_c is None or min(n_t, n_c) < MASK_BELOW) else round(m_t - m_c, 1),
            }
        )
    return rows
