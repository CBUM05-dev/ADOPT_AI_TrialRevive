"""Brique 5 : assembler le dossier de faisabilité. Tout chiffre vient du moteur, toute affirmation a une source.

Aucune IA ici : le texte est produit par gabarit, donc impossible d'inventer un chiffre ou une source.
"""
from src import verdict
from src.reanalyses import REANALYSES

# Hypothèse de travail pour la taille de l'essai de confirmation : exemple du document (section 5.7.4).
# À remplacer par les effets issus des réanalyses vérifiées.
HR_PORTEURS_HYPOTHESE = 0.55


def build_dossier(q: dict, screening: list[dict], rejection: dict, usable: dict, groups: list[dict]) -> dict:
    kept = [r for r in screening if r["retenu"]]
    rejected = [r for r in screening if not r["retenu"]]
    v = verdict.build_verdict(kept)
    funnel = usable["entonnoir"]
    data = usable["data"]
    pct_wt = round(100 * (data["kras_statut"] == "sauvage").mean()) if len(data) else None
    wt = next((g for g in groups if g["statut"] == "sauvage"), None)
    mut = next((g for g in groups if g["statut"] == "muté"), None)

    need = verdict.events_needed_interaction(HR_PORTEURS_HYPOTHESE, 1.0)
    have = {g["statut"]: g["evenements"] for g in groups}
    power_ok = all(have.get(s, 0) >= need for s in ("sauvage", "muté")) if groups else False
    sizing = verdict.confirmation_trial_size(HR_PORTEURS_HYPOTHESE, (pct_wt or 50) / 100)

    sources = [
        {"nct_id": r["nct_id"], "lien": r["lien"], "niveau": r["niveau"],
         "reanalyse": REANALYSES.get(r["nct_id"], {}).get("publication"),
         "publication_lien": (f"https://doi.org/{REANALYSES[r['nct_id']]['doi']}"
                              if REANALYSES.get(r["nct_id"], {}).get("doi") else None),
         "reanalyse_verifiee": REANALYSES.get(r["nct_id"], {}).get("verifie")}
        for r in kept
    ]
    all_verified = bool(kept) and all(r.get("reanalyse_verifiee") for r in kept)
    indetermination = usable.get("raison_indetermination") or "effectif inférieur à 5 (masqué)"
    return {
        "question": q["question"],
        "retenus": v["essais"],
        "ecartes": rejected,
        "rejection": rejection,
        "entonnoir": funnel,
        "utilisables": usable["utilisables"],
        "statut_comptage": usable["statut"],
        "raison_indetermination": usable.get("raison_indetermination"),
        "groupes": groups,
        "verdict": {"R": v["R"], "R_texte": verdict.R_LABELS[v["R"]], "E": v["E"], "E_texte": verdict.E_LABELS[v["E"]],
                    "E_pourquoi": v["E_pourquoi"], "G": v["G"], "preuve_verifiee": all_verified},
        "methode": (
            f"Réunir les {len(kept)} essais retenus, extraire l'effet de {q['traitement']} chez les patients "
            f"{q['biomarqueur']} sauvage et muté, puis tester l'interaction traitement × {q['biomarqueur']}. "
            + (f"Confirmer sur les données internes : {usable['utilisables']} patients complets sur {funnel[0]['n']}."
               if usable["utilisables"] is not None
               else f"Comptage interne indéterminé : {indetermination}.")
        ),
        "statistique": {"evenements_necessaires_par_groupe": need, "evenements_internes": have, "suffisant": power_ok,
                        "hr_hypothese": HR_PORTEURS_HYPOTHESE},
        "essai_confirmation": sizing,
        "gain": {
            "pct_sauvage": pct_wt,
            "gain_sauvage_mois": wt["gain_mois"] if wt else None,
            "gain_mute_mois": mut["gain_mois"] if mut else None,
            "note": "Chiffres calculés sur l'essai interne FICTIF : illustration, pas un résultat clinique.",
        },
        "sources": sources,
        "limites": [
            "Prototype de hackathon : l'essai interne est entièrement fictif.",
            "Les références bibliographiques sont rattachées au cache du registre ; les effectifs KRAS et les conclusions, "
            "initialement saisis de mémoire, restent à vérifier dans les publications par la personne Science.",
            "La fiche de question et les règles cliniques ne sont pas encore validées par la personne Science.",
            "Les notes E (preuve) sont des niveaux ATTEIGNABLES : il reste des conditions à confirmer "
            "(méthode validée, plan d'analyse fixé à l'avance).",
            "Les points des tolérances (scores) sont des valeurs de travail à valider par la personne Science.",
            "Le tri s'appuie sur des règles appliquées au registre ClinicalTrials.gov ; aucune extraction par IA n'a été réalisée.",
            "Seul KRAS est pris en charge ; le comptage interne panitumumab ne doit pas être extrapolé à un autre traitement.",
        ],
    }


def to_markdown(d: dict) -> str:
    v = d["verdict"]
    L = ["# Dossier de faisabilité\n", f"**Question :** {d['question']}\n"]
    L.append("## Verdict en un coup d'oeil")
    L.append(f"- **R : {v['R']}** — {v['R_texte']}")
    L.append(f"- **E : {v['E']}** ({v['E_texte']}) — niveau ATTEIGNABLE, pas acquis : {v['E_pourquoi']}")
    L.append("- **G :** " + " ; ".join(f"{g['code']} {g['gain']}" for g in v["G"]))
    L.append("\n## 1. Essais retenus (classés)")
    for r in d["retenus"]:
        tag = "médicament exact" if r["niveau"] == "direct" else "même classe"
        L.append(f"- [{r['nct_id']}]({r['lien']}) — {r['titre']} — {r['nb_patients']} patients — {tag} "
                 f"— preuve {r['E']}, score {r['score']}")
        for e in r["ecarts"]:
            L.append(f"  - écart toléré : {e}")
        L.append(f"  - à confirmer : {' ; '.join(r['conditions'])}")
    rs = d["rejection"]
    L.append(f"\n## 2. Essais écartés ({rs['total'] - rs['retenus']} sur {rs['total']})")
    for label, n in rs["ecartes_par_etape"].items():
        L.append(f"- {label} : {n}")
    L.append("\n## 3. Données internes (FICTIVES) — du prévu au complet")
    for s in d["entonnoir"]:
        L.append(f"- {s['etape']} : {s['n_publie'] if s['n_publie'] is not None else '<5 (masqué)'}")
    if d["utilisables"] is None:
        L.append(f"\n**Patients complets : INDÉTERMINÉ ou masqué** ({d.get('raison_indetermination') or 'effectif inférieur à 5'})")
    else:
        L.append(f"\n**Patients complets : {d['utilisables']}**")
    st = d["statistique"]
    L.append(f"\n## 4. Comment obtenir la réponse\n{d['methode']}")
    L.append(f"\nExigence statistique : {st['evenements_necessaires_par_groupe']} événements par groupe "
             f"(hypothèse d'effet {st['hr_hypothese']}). Dans l'essai interne : {st['evenements_internes']} -> "
             f"{'suffisant' if st['suffisant'] else 'INSUFFISANT'}.")
    c = d["essai_confirmation"]
    L.append(f"\n**Essai de confirmation :** environ {c['evenements_tous']} événements si on teste tous les patients, "
             f"contre environ {c['evenements_selectionnes']} si on réserve l'essai aux KRAS sauvage "
             "(formule de Schoenfeld, hypothèse de travail).")
    L.append("\n## 5. Gain attendu")
    g = d["gain"]
    L.append(f"- Part de KRAS sauvage parmi les patients complets : {g['pct_sauvage']} %")
    L.append(f"- Gain de survie médiane (traité vs contrôle) : KRAS sauvage {g['gain_sauvage_mois']} mois ; "
             f"KRAS muté {g['gain_mute_mois']} mois")
    L.append(f"- _{g['note']}_")
    L.append("\n## 6. Sources")
    for s in d["sources"]:
        citation = f"[{s['reanalyse']}]({s['publication_lien']})" if s.get("publication_lien") else s["reanalyse"]
        extra = f" — {citation} ({'vérifiée' if s['reanalyse_verifiee'] else 'à vérifier'})" if s["reanalyse"] else ""
        L.append(f"- {s['lien']}{extra}")
    L.append("\n## 7. Limites")
    L += [f"- {x}" for x in d["limites"]]
    return "\n".join(L)
