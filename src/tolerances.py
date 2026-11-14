"""Bibliothèque de tolérances : ce qu'on accepte à contrecoeur, combien ça coûte, et jusqu'où ça plafonne la preuve.

Source des PLAFONDS (E2/E3) : Description_technique_complete_TrialRevive, section 5.3.4.
Les SCORES (0 à 1) sont des valeurs de travail de l'assistant : à valider par la personne Science.
"""

LEVELS = ["E0", "E1", "E2", "E3", "E4"]


def level_min(a: str, b: str) -> str:
    return a if LEVELS.index(a) <= LEVELS.index(b) else b


def level_at_least(level: str, minimum: str) -> bool:
    return LEVELS.index(level) >= LEVELS.index(minimum)


TOLERANCES = {
    "molecule_classe": {
        "score": 0.8,
        "plafond": "E3",
        "phrase": "autre médicament de la même classe : il faudra répéter avec le médicament exact avant la preuve maximale (E4)",
    },
    "couverture_60_80": {
        "score": 0.8,
        "plafond": "E2",
        "phrase": "le statut KRAS n'est connu que pour 60 à 80 % des patients tirés au sort",
    },
    "couverture_inconnue": {
        "score": 0.7,
        "plafond": "E2",
        "phrase": "part des patients avec statut KRAS inconnue (à relever dans la publication)",
    },
    "critere_substitue": {
        "score": 0.7,
        "plafond": "E2",
        "phrase": "critère de jugement de remplacement (taux de réponse au lieu de la survie)",
    },
}

COUVERTURE_MIN = 0.60  # en dessous : éliminé (obligatoire)
COUVERTURE_IDEALE = 0.80  # au-dessus : bonus (idéal)
