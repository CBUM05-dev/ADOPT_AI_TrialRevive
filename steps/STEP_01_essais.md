# STEP 01 — Récupérer les essais publics (1h30)

## Prompt à donner à Claude
> Lis CLAUDE.md. Écris `src/fetch.py` : interroge l'API publique ClinicalTrials.gov v2 (`https://clinicaltrials.gov/api/v2/studies`) pour les essais randomisés phase 2/3 sur le cancer colorectal métastatique avec panitumumab ou cetuximab (anti-EGFR). Récupère 30 à 50 essais, sauvegarde le JSON brut dans `data/raw/`, puis range dans SQLite `data/trials.db` (table `trials` : nct_id, titre, phase, statut, bras, critères d'inclusion, critères d'exclusion, critère principal, nb patients, lien). Gère la pagination et les erreurs réseau. Ajoute un test.

## Paramètres utiles de l'API
- `query.cond=colorectal cancer`, `query.intr=panitumumab` (puis `cetuximab`)
- `filter.overallStatus`, `pageSize=50`
- Champs : `protocolSection.identificationModule`, `eligibilityModule`, `armsInterventionsModule`, `outcomesModule`, `designModule`

## Plan B
Si l'API bloque : télécharger quelques fiches à la main (export JSON depuis le site) et les mettre dans `data/raw/`.

## Vérification
- [ ] `SELECT COUNT(*) FROM trials` donne entre 30 et 50
- [ ] Chaque ligne a un `nct_id` et un lien cliquable valide
- [ ] Aucun champ clé vide sur plus de 10 % des lignes
