# STEP 08 — Comparaison avec une IA généraliste (45 min)

## But
Montrer que TrialRevive compte réellement les patients et cite des sources vérifiables, contrairement à une IA généraliste.

## À faire
- [ ] Poser les MÊMES 5 à 10 questions à une IA généraliste (question publique, sans rien de confidentiel)
- [ ] Sauvegarder les réponses brutes dans `data/baseline/` (date, modèle utilisé)
- [ ] Tableau : question | TrialRevive | IA généraliste | critères : compte patients ? sources vérifiables ? raisons des rejets ?
- [ ] Vérifier une à une les sources citées par l'IA généraliste (existent-elles ?) et noter le résultat honnêtement

## Prompt à donner à Claude
> Lis CLAUDE.md. Crée `src/compare.py` qui charge `data/baseline/*.json` et produit un tableau comparatif pour l'interface. Ne triche pas : si l'IA généraliste est meilleure sur un critère, l'afficher.

## Vérification
- [ ] Réponses brutes archivées (preuve)
- [ ] Au moins 3 sources de l'IA généraliste vérifiées à la main
- [ ] Comparaison honnête (le jury posera la question)
