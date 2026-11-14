# BUILD PLAN — TrialRevive (de zéro à la démo)

Principe : un pipeline de bout en bout très tôt, puis on l'améliore. Chaque étape a son fichier dans `steps/`.

| # | Étape | Fichier | Durée | Livrable testable |
|---|-------|---------|-------|-------------------|
| 0 | Setup projet | steps/STEP_00_setup.md | 30 min | `streamlit run app.py` affiche une page |
| 1 | Récupérer les essais publics | steps/STEP_01_essais.md | 1h30 | 30-50 essais dans la base |
| 2 | Fiche (CV) de chaque essai | steps/STEP_02_cv_essai.md | 2h | Fiches structurées, 2-3 par IA, reste manuel/règles |
| 3 | Fiche de la question | steps/STEP_03_question.md | 1h | Exigences en JSON pour le cas KRAS |
| 4 | Essai interne fictif | steps/STEP_04_faux_patients.md | 1h | 400 faux patients CSV |
| 5 | Moteur de tri + comptage | steps/STEP_05_moteur.md | 2h | Essais gardés/écartés avec raison + nb patients utilisables |
| 6 | Dossier final | steps/STEP_06_dossier.md | 1h30 | Dossier lisible avec sources |
| 7 | Interface Streamlit | steps/STEP_07_interface.md | 1h30 | Démo cliquable complète |
| 8 | Comparaison IA généraliste | steps/STEP_08_comparaison.md | 45 min | Tableau côte à côte |
| 9 | Pitch + répétition | steps/STEP_09_pitch.md | 1h30 | 5 min chronométrées |

Total ~13h de travail effectif. Le reste : marge, pauses, imprévus.

## Ordre si le temps manque (couper dans cet ordre)
1. Étape 8 : faire la comparaison à la main (captures d'écran).
2. Étape 2 : remplir les fiches à la main (pas d'IA) sauf 2 essais.
3. Étape 7 : interface minimale (3 boutons).
Ne JAMAIS couper : 1, 3, 4, 5, 6 (le cœur) et 9 (le pitch).

## Répartition suggérée (5 personnes)
- Science : choisir le cas, valider la crédibilité clinique, aide étapes 3 et 6
- Données : étapes 1-2
- Technique : étapes 5, 7
- Statistiques : étapes 4, 5 (comptage), 8 (évaluation)
- Pitch : étapes 8-9, tout au long du projet

## Point de jonction (à ne pas rater)
Dès la fin des étapes 1-5 en version "bête" : lancer UN run complet. Un pipeline moche qui marche vaut mieux que 5 briques parfaites non branchées.
