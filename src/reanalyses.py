"""Réanalyses KRAS publiées des essais pivots (analyses FAITES APRÈS COUP sur des essais conçus sans KRAS).

Les PMID et DOI ont été recoupés avec les références du cache ClinicalTrials.gov
(data/raw/pinned.json, 2026-11-14). Cela vérifie le rattachement bibliographique,
pas les effectifs ni l'interprétation clinique, initialement saisis de mémoire.
`verifie=False` tant qu'un humain
(personne Science) n'a pas vérifié la référence ET les chiffres dans la publication. Le dossier final affiche ce statut.
Valeur inconnue = None (jamais devinée).
"""

REANALYSES = {
    "NCT00113763": {
        "publication": "Amado et al., J Clin Oncol 2008 (panitumumab vs soins de support, analyse rétrospective KRAS)",
        "pmid": "18316791",
        "doi": "10.1200/JCO.2007.14.7116",
        "n_kras_evalue": 427,
        "conclusion": "Bénéfice du panitumumab chez les patients KRAS sauvage ; pas de bénéfice chez les KRAS mutés.",
        "verifie": False,
    },
    "NCT00364013": {
        "publication": "Douillard et al., J Clin Oncol 2010 (PRIME, analyse prospective-rétrospective KRAS)",
        "pmid": "20921465",
        "doi": "10.1200/JCO.2009.27.4860",
        "n_kras_evalue": 1096,
        "conclusion": "Bénéfice du panitumumab + FOLFOX4 chez les KRAS sauvage ; pas de bénéfice chez les KRAS mutés.",
        "verifie": False,
    },
    "NCT00339183": {
        "publication": "Peeters et al., J Clin Oncol 2010 (étude 20050181, analyse KRAS)",
        "pmid": "20921462",
        "doi": "10.1200/JCO.2009.27.6055",
        "n_kras_evalue": 1083,
        "conclusion": "Bénéfice du panitumumab + FOLFIRI chez les KRAS sauvage ; pas de bénéfice chez les KRAS mutés.",
        "verifie": False,
    },
    "NCT00079066": {
        "publication": "Karapetis et al., N Engl J Med 2008 (CO.17, cetuximab vs soins de support, analyse KRAS)",
        "pmid": "18946061",
        "doi": "10.1056/NEJMoa0804385",
        "n_kras_evalue": 394,
        "conclusion": "Bénéfice du cetuximab chez les KRAS sauvage ; pas de bénéfice chez les KRAS mutés (preuve de classe).",
        "verifie": False,
    },
    "NCT00154102": {
        "publication": "Van Cutsem et al., N Engl J Med 2009 (CRYSTAL, cetuximab + FOLFIRI, analyse KRAS)",
        "pmid": "19339720",
        "doi": "10.1056/NEJMoa0805019",
        "n_kras_evalue": None,
        "conclusion": "Bénéfice du cetuximab chez les KRAS sauvage ; pas chez les KRAS mutés (preuve de classe).",
        "verifie": False,
    },
    "NCT00125034": {
        "publication": "Bokemeyer et al., J Clin Oncol 2009 (OPUS, cetuximab + FOLFOX4, analyse KRAS)",
        "pmid": "19114683",
        "doi": "10.1200/JCO.2008.20.8397",
        "n_kras_evalue": None,
        "conclusion": "Bénéfice du cetuximab chez les KRAS sauvage ; pas chez les KRAS mutés (preuve de classe).",
        "verifie": False,
    },
}
