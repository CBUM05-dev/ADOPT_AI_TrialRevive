# PROGRESS — Avancement TrialRevive

Dernière mise à jour : 2026-11-14 nuit (par Claude, pendant que l’utilisateur dormait)

## Tableau d'avancement
Statuts : ⬜ à faire · 🟨 en cours · ✅ fini et vérifié · ❌ bloqué · ✂️ coupé

| # | Étape | Statut | Responsable | Vérifié ? | Notes |
|---|-------|--------|-------------|-----------|-------|
| 0 | Setup | ✅ | | ☑ | Streamlit OK. pytest 9.2 bugue : épingler pytest<9 |
| 1 | Essais publics | ✅ | IA | ☑ | 104 essais (98 + 6 pivots épinglés, titres confirmés) |
| 2 | CV des essais | ✅ | IA | 🟨 | Règles + réanalyses publiées (À VÉRIFIER par humain). Extraction IA non faite (pas de clé API) |
| 3 | Fiche question | ✅ | IA | 🟨 | Codée, `validee_par_humain=False` : à relire par la personne Science |
| 4 | Faux patients | ✅ | IA | ☑ | 400 patients, seed 42, tests OK |
| 5 | Moteur | ✅ | IA | ☑ | 6 retenus / 98 écartés avec raison, 306 patients utilisables |
| 6 | Dossier | ✅ | IA | 🟨 | Par gabarit, sources liées. À relire par un clinicien |
| 7 | Interface | ✅ | IA | ☑ | Tests UI auto OK. À tester sur le PC de présentation |
| 8 | Comparaison IA | 🟨 | humain | ☐ | Besoin d’un humain : voir data/baseline/LISEZ_MOI.md |
| 9 | Pitch | 🟨 | humain | ☐ | Texte prêt dans PITCH.md ; répétition à faire |

## 🚩 Points à signaler (à remplir en continu)
### Blocages
- Git Bash/`!` : erreur SSL pip. Résolu : `truststore` activé dans src/fetch.py + venv recréé dans PowerShell.
- pytest 9.2 plantait : épinglé `pytest<9` (8.4.2 installé).

### À FAIRE PAR UN HUMAIN (je ne peux pas)
1. Vérifier src/reanalyses.py (références + chiffres, saisis de MÉMOIRE) puis `verifie=True`.
2. Faire relire la fiche de la question (src/question.py) par la personne Science.
3. Comparaison IA généraliste : data/baseline/LISEZ_MOI.md.
4. Tester `python -m streamlit run app.py` sans wifi sur le PC de présentation ; vidéo de secours ; répéter le pitch.
5. (Optionnel) clé dans .env puis `python -m src.cv --ai NCT00364013 NCT00339183` : extraction IA.

### Décisions prises
- (date, décision, qui)

### Risques
- API ClinicalTrials.gov lente ou bloquée -> données en cache local
- Wifi de la salle -> démo hors ligne
- Extraction IA incorrecte -> relecture humaine obligatoire
- Retard -> appliquer l'ordre de coupe dans BUILD_PLAN.md

### Questions pour Sami / jury / coachs
- 

### Conformité (à cocher avant le dépôt)
- [ ] Aucune donnée de santé réelle
- [ ] Rien de confidentiel dans une IA externe sans accord
- [ ] Code non publié sans accord
- [ ] Accord d'équipe signé (vendredi soir)
- [ ] Désactivation de l'entraînement sur mes conversations IA

## Journal
| Heure | Qui | Fait | Reste |
|-------|-----|------|-------|
| | | | |
