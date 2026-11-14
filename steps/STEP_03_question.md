# STEP 03 — La fiche de la question (1h)

Traduire "Le KRAS change-t-il l'effet du panitumumab ?" en exigences précises.

## Exigences types (à valider avec Eva / la personne Science)
```json
{
  "question": "...",
  "traitement": "panitumumab",
  "biomarqueur": "KRAS",
  "population": "cancer colorectal métastatique",
  "exigences": {
    "randomise": true,
    "biomarqueur_mesure": true,
    "analyse_sous_groupe": true,
    "taille_min": 100
  },
  "reponse_attendue": "effet du traitement différent selon KRAS (muté vs sauvage)"
}
```

## Prompt à donner à Claude
> Lis CLAUDE.md. Écris `src/question.py` : une fonction qui transforme la question en texte libre en fiche JSON ci-dessus. Pour le cas vedette, la fiche est codée en dur et validée ; pour les autres questions, utilise l'API Claude avec sortie JSON. Valide le schéma.

## Vérification
- [ ] La fiche du cas KRAS est relue et approuvée par la personne Science
- [ ] Une question différente (ex. BRAF) produit une fiche valide
- [ ] Chaque exigence est testable automatiquement par le moteur (étape 5)
