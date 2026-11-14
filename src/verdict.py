"""Brique 5 (verdict) : notes R (la voie), E (la preuve), G (le gain), et taille de l'essai de confirmation.

Définitions : Description_technique_complete_TrialRevive, sections 5.7.1 à 5.7.4.
Règle : tout est calculé par le code, par règles écrites à l'avance. Aucune IA.
"""
import math

from src.tolerances import LEVELS, level_at_least, level_min

R_LABELS = {
    "R0": "analyse immédiate : le marqueur est déjà mesuré dans les données",
    "R1": "marqueur dérivable sans consommer d'échantillon",
    "R2": "nouvelle analyse sur échantillons archivés",
    "R3": "l'essai ne peut pas répondre, mais aide à concevoir le suivant",
}
E_LABELS = {
    "E0": "non testable",
    "E1": "exploratoire",
    "E2": "rétrospectif crédible",
    "E3": "prospectif-rétrospectif",
    "E4": "prospectif-rétrospectif répliqué",
}
# Gain -> niveau de preuve minimal (section 5.7.3)
G_TABLE = [
    ("G1", "décision de poursuivre ou d'arrêter plus vite", "E2"),
    ("G2", "population mieux ciblée pour l'essai suivant", "E2"),
    ("G3", "essai de confirmation plus petit", "E3"),
    ("G4", "restriction ou sauvetage d'une indication", "E3"),
    ("G5", "repositionnement ou relance d'un médicament (confirmation prospective requise)", "E2"),
    ("G6", "test diagnostique associé", "E3"),
]

Z_ALPHA = 1.96  # risque 5 % bilatéral
Z_BETA = 0.84  # puissance 80 %


def route(trial: dict) -> tuple[str, str]:
    """Voie de réalisation d'un essai retenu. Les essais retenus ont tous une analyse du marqueur publiée."""
    if trial.get("n_kras_evalue") or trial.get("couverture"):
        return "R0", "le statut KRAS a déjà été mesuré et analysé (données patients non accessibles ici : preuve externe)"
    return "R0", "le statut KRAS a déjà été mesuré (réanalyse publiée, effectifs à relever)"


def trial_level(trial: dict) -> tuple[str, list[str]]:
    """Niveau de preuve atteignable pour UN essai + conditions qu'il reste à remplir.

    Un essai seul ne dépasse pas E3 : E4 exige un second essai qui confirme.
    """
    cov = trial.get("couverture")
    todo = []
    if cov is not None and cov >= 0.80:
        base = "E3"
    else:
        base = "E2"
    level = level_min(base, trial["plafond"])
    if not trial.get("reanalyse_verifiee"):
        todo.append("vérifier la référence et les chiffres de la réanalyse publiée")
    todo.append("confirmer que la méthode de mesure KRAS est validée")
    todo.append("confirmer que le plan d'analyse a été fixé avant les mesures")
    if level_at_least(base, "E3") is False:
        todo.append("relever la part de patients avec statut connu (au moins 80 % pour viser E3)")
    return level, todo


def hypothesis_level(trial_levels: list[tuple[dict, str]]) -> tuple[str, str]:
    """Niveau de preuve atteignable pour l'hypothèse : E4 si au moins 2 essais du médicament exact atteignent E3."""
    direct_e3 = [t for t, lv in trial_levels if t["niveau"] == "direct" and level_at_least(lv, "E3")]
    if len(direct_e3) >= 2:
        return "E4", f"{len(direct_e3)} essais du médicament exact atteignent E3 et vont dans le même sens (concordance à confirmer par un humain)"
    best = max((lv for _, lv in trial_levels), key=LEVELS.index, default="E0")
    return best, "pas assez d'essais du médicament exact au niveau E3 pour viser E4"


def gains_unlocked(level: str) -> list[dict]:
    return [{"code": c, "gain": g, "niveau_min": m} for c, g, m in G_TABLE if level_at_least(level, m)]


# ---------- exigence statistique et taille de l'essai de confirmation ----------
def events_needed_interaction(hr_pos: float, hr_neg: float) -> int:
    """Événements (décès/rechutes) minimum PAR GROUPE (égaux) pour détecter l'interaction (section 5.3.5)."""
    delta = math.log(hr_pos) - math.log(hr_neg)
    # (z_a + z_b)^2 * (4/d + 4/d) <= delta^2   avec d+ = d- = d
    return math.ceil((Z_ALPHA + Z_BETA) ** 2 * 8 / delta**2)


def confirmation_trial_size(hr_pos: float, share_pos: float = 0.5, hr_neg: float = 1.0) -> dict:
    """Formule de Schoenfeld : événements requis, essai ouvert à tous vs réservé aux porteurs du marqueur (5.7.4)."""
    diluted = math.exp(share_pos * math.log(hr_pos) + (1 - share_pos) * math.log(hr_neg))
    d_all = math.ceil(4 * (Z_ALPHA + Z_BETA) ** 2 / math.log(diluted) ** 2)
    d_sel = math.ceil(4 * (Z_ALPHA + Z_BETA) ** 2 / math.log(hr_pos) ** 2)
    return {"hr_dilue": round(diluted, 2), "evenements_tous": d_all, "evenements_selectionnes": d_sel}


def build_verdict(kept: list[dict]) -> dict:
    per_trial = []
    for t in kept:
        lvl, todo = trial_level(t)
        r, r_why = route(t)
        per_trial.append({**t, "E": lvl, "R": r, "R_pourquoi": r_why, "conditions": todo})
    h_level, h_why = hypothesis_level([(t, t["E"]) for t in per_trial])
    return {
        "essais": per_trial,
        "R": "R0" if per_trial else "R3",
        "E": h_level if per_trial else "E0",
        "E_pourquoi": h_why,
        "G": gains_unlocked(h_level) if per_trial else [],
    }
