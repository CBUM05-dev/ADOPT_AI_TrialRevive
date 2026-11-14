# Dossier de relecture — personne Science

État au 14 novembre 2026 : le rattachement des six articles aux essais a été recoupé automatiquement avec `data/raw/pinned.json` (références ClinicalTrials.gov). Cela **ne valide pas** les effectifs KRAS ni les conclusions. Tous les `verifie` restent `False` et la fiche de question reste non validée.

L'accès au service bibliographique Europe PMC (`www.ebi.ac.uk`) a renvoyé un refus du proxy (403). Aucun résumé ou texte intégral n'a pu être consulté par cette voie. La relecture clinique n'est pas faite.

| Essai | Article rattaché au cache | DOI | Effectif total du registre | Effectif KRAS actuellement saisi, non validé |
|-------|--------------------------|-----|---------------------------|---------------------------------------------|
| NCT00113763 | Amado 2008, [PMID 18316791](https://pubmed.ncbi.nlm.nih.gov/18316791/) | [10.1200/JCO.2007.14.7116](https://doi.org/10.1200/JCO.2007.14.7116) | 463 | 427 |
| NCT00364013 | Douillard 2010, [PMID 20921465](https://pubmed.ncbi.nlm.nih.gov/20921465/) | [10.1200/JCO.2009.27.4860](https://doi.org/10.1200/JCO.2009.27.4860) | 1183 | 1096 |
| NCT00339183 | Peeters 2010, [PMID 20921462](https://pubmed.ncbi.nlm.nih.gov/20921462/) | [10.1200/JCO.2009.27.6055](https://doi.org/10.1200/JCO.2009.27.6055) | 1186 | 1083 |
| NCT00079066 | Karapetis 2008, [PMID 18946061](https://pubmed.ncbi.nlm.nih.gov/18946061/) | [10.1056/NEJMoa0804385](https://doi.org/10.1056/NEJMoa0804385) | 572 | 394 |
| NCT00154102 | Van Cutsem 2009, [PMID 19339720](https://pubmed.ncbi.nlm.nih.gov/19339720/) | [10.1056/NEJMoa0805019](https://doi.org/10.1056/NEJMoa0805019) | 1221 | inconnu |
| NCT00125034 | Bokemeyer 2009, [PMID 19114683](https://pubmed.ncbi.nlm.nih.gov/19114683/) | [10.1200/JCO.2008.20.8397](https://doi.org/10.1200/JCO.2008.20.8397) | 344 | inconnu |

## Pour chaque essai

- [ ] Lire l'article ; confirmer l'identité NCT, le médicament et le comparateur.
- [ ] Relever le dénominateur de l'analyse KRAS et sa page/table. Distinguer une analyse initiale d'une mise à jour ou d'une analyse RAS étendue.
- [ ] Vérifier la méthode du test, les exons couverts, les statuts inclus et la chronologie du plan d'analyse.
- [ ] Vérifier le critère de jugement et l'interaction traitement × marqueur ; ne pas confondre deux tests de sous-groupes avec un test d'interaction.
- [ ] Confirmer ou corriger la conclusion, avec sa source exacte.
- [ ] Documenter le relecteur, la date et les pages ; passer `verifie=True` seulement après cette revue.

Une fois les données corrigées, relancer `python -m src.cv`, `python -m pytest -q` puis la démo. Un changement d'effectif peut changer la couverture, le classement et le niveau atteignable.

## Question, tolérances et dossier

- [ ] Valider la fiche KRAS (`src/question.py`) et ses exigences ; elle n'est pas une validation de toutes les questions contenant ces mots-clés.
- [ ] Valider les seuils et scores de `src/tolerances.py` ; ce sont des choix de prototype, pas une échelle clinique validée.
- [ ] Relire le dossier complet, les conditions d'accès aux données et l'exigence statistique.
- [ ] E4 reste un objectif conditionnel : confirmer la concordance, la qualité et l'indépendance des essais.
- [ ] Ne pas présenter le gain de survie des faux patients, ni l'hypothèse HR=0,55, comme des résultats cliniques.

Le prototype couvre KRAS avec panitumumab/cetuximab pour la recherche externe ; l'essai interne fictif ne contient qu'un bras panitumumab et un contrôle. Pour cetuximab, le comptage interne est donc indéterminé. NRAS/BRAF/RAS et les questions ambiguës sont refusés.
