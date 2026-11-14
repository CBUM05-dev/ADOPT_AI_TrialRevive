# STEP 02 — Le "CV" de chaque essai (2h)

Une fiche structurée par essai : de quoi décider s'il peut répondre à la question.

## Schéma de la fiche
```json
{
  "nct_id": "NCT...",
  "traitement": "panitumumab",
  "comparateur": "...",
  "population": "CCR métastatique",
  "biomarqueur_mesure": true,
  "biomarqueur_nom": "KRAS",
  "biomarqueur_methode": "exons 2 seulement / étendu",
  "analyse_sous_groupe_prevue": true,
  "randomise": true,
  "critere_principal": "survie globale",
  "nb_patients": 0,
  "sources": ["lien ou extrait"]
}
```

## Prompt à donner à Claude
> Lis CLAUDE.md. Écris `src/cv.py` : pour chaque essai de la base, produit la fiche selon le schéma ci-dessus. Deux modes : (a) règles simples (mots-clés KRAS/RAS dans critères et titre) pour tous les essais ; (b) extraction par API Claude pour 2-3 essais seulement, avec une réponse JSON validée. Chaque champ rempli doit garder l'extrait de texte qui le justifie. Sauve dans la table `cv`.

## Plan B
Remplir un CSV à la main pour 10-15 essais (la personne Science peut le faire en parallèle).

## Vérification
- [ ] Fiches pour tous les essais de la base
- [ ] Pour 3 essais choisis au hasard, un humain relit la fiche contre la source : correcte
- [ ] Aucun champ inventé : si l'info manque, valeur `null` (pas de supposition)
