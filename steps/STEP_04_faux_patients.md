# STEP 04 — Essai interne fictif (1h)

400 FAUX patients. Données entièrement fabriquées.

## Colonnes
`patient_id, age, sexe, traitement (panitumumab/contrôle), kras_statut (muté/sauvage/inconnu), methode_test, survie_mois, evenement (0/1), date_inclusion`

## Règles de réalisme (pour que le comptage soit intéressant)
- ~40 % KRAS muté, ~50 % sauvage, ~10 % inconnu (donc inutilisables)
- Quelques patients avec méthode de test insuffisante (ex. exons incomplets) -> non utilisables
- Effet fabriqué : le panitumumab aide les KRAS sauvages, pas les mutés (pour illustrer l'interaction)
- Quelques valeurs manquantes volontaires

## Prompt à donner à Claude
> Lis CLAUDE.md. Écris `src/fake_data.py` avec seed fixe (reproductible) qui génère `data/internal_trial.csv` selon les règles ci-dessus. Ajoute en tête du fichier un commentaire "DONNÉES FICTIVES". Ajoute un test qui vérifie les proportions.

## Vérification
- [ ] 400 lignes, mêmes données à chaque exécution (seed)
- [ ] Proportions KRAS dans la cible (+/- 5 %)
- [ ] Le fichier ne contient aucun vrai nom ni vrai identifiant
