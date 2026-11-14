"""Brique 5 : assembler le dossier de faisabilité. Tout chiffre vient du moteur, toute affirmation a une source.

Aucune IA ici : le texte est produit par gabarit, donc impossible d'inventer un chiffre ou une source.
"""
from src.reanalyses import REANALYSES


def evidence_strength(kept: list[dict]) -> tuple[str, str]:
    """Règle simple et expliquée : nombre d'essais directs, taille totale, vérification des réanalyses."""
    direct = [r for r in kept if r["niveau"] == "direct"]
    total_n = sum(r["nb_patients"] or 0 for r in kept)
    verified = all(r.get("reanalyse_verifiee") for r in kept) if kept else False
    if len(direct) >= 3 and total_n >= 2000 and verified:
        level = "forte"
    elif len(direct) >= 2 and total_n >= 500:
        level = "moyenne"
    else:
        level = "faible"
    why = (
        f"{len(direct)} essai(s) randomisé(s) avec le médicament lui-même, {len(kept) - len(direct)} avec un médicament de la même classe, "
        f"{total_n} patients au total ; "
        + ("réanalyses vérifiées." if verified else "réanalyses publiées PAS ENCORE VÉRIFIÉES par un humain (la force est plafonnée à « moyenne »).")
    )
    return level, why


def build_dossier(q: dict, screening: list[dict], rejection: dict, usable: dict, groups: list[dict]) -> dict:
    kept = [r for r in screening if r["retenu"]]
    rejected = [r for r in screening if not r["retenu"]]
    level, why = evidence_strength(kept)

    wt = next((g for g in groups if g["statut"] == "sauvage"), None)
    mut = next((g for g in groups if g["statut"] == "muté"), None)
    funnel = usable["entonnoir"]
    pct_wt = None
    data = usable["data"]
    if len(data):
        pct_wt = round(100 * (data["kras_statut"] == "sauvage").mean())

    sources = [
        {"nct_id": r["nct_id"], "lien": r["lien"], "niveau": r["niveau"],
         "reanalyse": REANALYSES.get(r["nct_id"], {}).get("publication"),
         "reanalyse_verifiee": REANALYSES.get(r["nct_id"], {}).get("verifie")}
        for r in kept
    ]
    return {
        "question": q["question"],
        "retenus": kept,
        "ecartes": rejected,
        "rejection": rejection,
        "entonnoir": funnel,
        "utilisables": usable["utilisables"],
        "groupes": groups,
        "methode": (
            f"Réunir les {len(kept)} essais randomisés retenus, extraire l'effet de {q['traitement']} chez les patients "
            f"{q['biomarqueur']} sauvage et muté, puis tester l'interaction traitement × {q['biomarqueur']} (méta-analyse). "
            f"Confirmer sur les données internes : {usable['utilisables']} patients utilisables sur {funnel[0]['n']}."
        ),
        "force_preuve": level,
        "force_explication": why,
        "gain": {
            "pct_sauvage": pct_wt,
            "gain_sauvage_mois": wt["gain_mois"] if wt else None,
            "gain_mute_mois": mut["gain_mois"] if mut else None,
            "note": "Chiffres calculés sur l'essai interne FICTIF : illustration, pas un résultat clinique.",
        },
        "sources": sources,
        "limites": [
            "Prototype de hackathon : l'essai interne est entièrement fictif.",
            "Les réanalyses publiées ont été saisies de mémoire et ne sont pas encore vérifiées par un humain.",
            "Le tri s'appuie sur les textes du registre ClinicalTrials.gov ; la lecture par IA n'a été faite que sur peu d'essais.",
        ],
    }


def to_markdown(d: dict) -> str:
    L = [f"# Dossier de faisabilité\n", f"**Question :** {d['question']}\n"]
    L.append("## 1. Essais retenus")
    for r in d["retenus"]:
        tag = "médicament direct" if r["niveau"] == "direct" else "preuve de classe"
        L.append(f"- [{r['nct_id']}]({r['lien']}) — {r['titre']} — {r['nb_patients']} patients — {tag}")
    rs = d["rejection"]
    L.append(f"\n## 2. Essais écartés ({rs['total'] - rs['retenus']} sur {rs['total']})")
    for label, n in rs["ecartes_par_etape"].items():
        L.append(f"- {label} : {n}")
    L.append("\n## 3. Données internes (FICTIVES) — entonnoir de patients")
    for s in d["entonnoir"]:
        L.append(f"- {s['etape']} : {s['n']}")
    L.append(f"\n**Patients utilisables : {d['utilisables']}**")
    L.append("\n## 4. Comment obtenir la réponse\n" + d["methode"])
    L.append(f"\n## 5. Force de la preuve : {d['force_preuve'].upper()}\n{d['force_explication']}")
    g = d["gain"]
    L.append("\n## 6. Gain attendu pour le médicament")
    L.append(f"- Part de patients KRAS sauvage parmi les utilisables : {g['pct_sauvage']} %")
    L.append(f"- Gain de survie médiane (traité vs contrôle), KRAS sauvage : {g['gain_sauvage_mois']} mois ; KRAS muté : {g['gain_mute_mois']} mois")
    L.append(f"- _{g['note']}_")
    L.append("\n## 7. Sources")
    for s in d["sources"]:
        extra = f" — {s['reanalyse']} ({'vérifiée' if s['reanalyse_verifiee'] else 'à vérifier'})" if s["reanalyse"] else ""
        L.append(f"- {s['lien']}{extra}")
    L.append("\n## 8. Limites")
    L += [f"- {x}" for x in d["limites"]]
    return "\n".join(L)
