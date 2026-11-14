"""Brique 3 : traduire une question scientifique en exigences précises (fiche de la question).

Le cas vedette est codé en dur (à faire valider par la personne Science).
Les autres questions passent par des règles simples (médicament + marqueur reconnus dans le texte).
"""
import re

# Médicaments de la même classe (anti-EGFR) : preuve "de classe", moins forte que le médicament lui-même
CLASSES = {
    "anti-EGFR": ["panitumumab", "cetuximab"],
}
MARKERS = ["KRAS", "NRAS", "BRAF", "RAS"]

# Méthodes de test que la question accepte (cohérent avec src/fake_data.py)
METHODES_VALIDES = ["KRAS exons 2-4 (complet)", "KRAS exon 2 seulement"]


def question_card(drug: str, marker: str, text: str) -> dict:
    drug = drug.lower()
    classe = next((c for c, ds in CLASSES.items() if drug in ds), None)
    classmates = [d for d in CLASSES.get(classe, []) if d != drug]
    return {
        "question": text,
        "traitement": drug,
        "traitements_classe": classmates,  # acceptés comme preuve de classe
        "classe": classe,
        "biomarqueur": marker.upper(),
        "population": "cancer colorectal métastatique",
        "exigences": {
            "randomise": True,
            "biomarqueur_mesure": True,
            "analyse_sous_groupe": True,
            "taille_min": 100,
        },
        "methodes_valides": METHODES_VALIDES,
        "reponse_attendue": f"effet de {drug} différent selon le statut {marker.upper()} (muté vs sauvage)",
        "validee_par_humain": False,
    }


CAS_VEDETTE_TEXTE = "Le statut KRAS change-t-il l'effet du panitumumab dans le cancer colorectal métastatique ?"


def parse_question(text: str) -> dict:
    """Retourne la fiche de la question, ou lève ValueError si le médicament/marqueur n'est pas reconnu."""
    drugs = [d for ds in CLASSES.values() for d in ds]
    drug = next((d for d in drugs if re.search(d, text, re.I)), None)
    marker = next((m for m in MARKERS if re.search(rf"\b{m}\b", text, re.I)), None)
    if not drug or not marker:
        raise ValueError(
            "Question non reconnue : mentionnez un médicament (panitumumab, cetuximab) et un biomarqueur (KRAS, NRAS, BRAF)."
        )
    card = question_card(drug, marker, text)
    if drug == "panitumumab" and marker == "KRAS":
        card["validee_par_humain"] = False  # passer à True quand la personne Science a relu
    return card
