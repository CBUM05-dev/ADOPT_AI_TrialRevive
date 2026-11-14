# Pitch TrialRevive — cible 5 minutes, puis 3 minutes de questions

Chiffres reproduits le 14 novembre 2026 par `python -m src.demo` : **104 essais publics, 6 retenus, 98 écartés ; 400 patients fictifs → 252 complets**. Consulter `outputs/demo/chiffres.json` après toute mise à jour. Les temps ci-dessous sont des objectifs ; deux répétitions humaines restent à chronométrer.

| Temps cible | À dire et à montrer |
|-------------|--------------------|
| 0:00–0:45 | **Problème.** « Avant de lancer une nouvelle étude, peut-on retrouver des essais qui permettent déjà d'examiner notre question ? Un registre contient des études, mais leur pertinence dépend du traitement, du marqueur, des groupes comparables et des données effectivement disponibles. » |
| 0:45–1:15 | **Idée.** « TrialRevive transforme une question en dossier de faisabilité sourcé. Notre cas de démonstration est le panitumumab et KRAS dans le cancer colorectal. Nous utilisons uniquement des essais publics et des patients fabriqués : aucun patient réel. » |
| 1:15–1:45 | **Tableau de bord.** Cliquer sur **Cas de démo** dans `app_ui.py`. Lire la question puis les indicateurs : 104 essais, 6 retenus, 98 écartés. « Le tri est déterministe. L'objectif E4 affiché est conditionnel, il n'est pas une preuve déjà acquise. » |
| 1:45–2:20 | **Essais retenus puis écartés.** Montrer PRIME et les liens du registre. « Chaque rejet a une raison. Dans ce cache, 26 essais sont écartés car leur population ne permet pas de comparer les statuts muté et sauvage. Les références des réanalyses doivent encore être relues scientifiquement. » |
| 2:20–3:00 | **Patients.** « Avoir 400 lignes ne veut pas dire avoir 400 patients analysables. Ici, nous passons de 400 à 359 avec statut connu, 332 avec échantillon en stock, 271 utilisables puis 252 complets. Ce sont exclusivement des données fictives ; leurs résultats ne démontrent aucun bénéfice clinique. » |
| 3:00–3:45 | **Dossier.** Afficher le dossier et son téléchargement. Montrer les sources, les conditions restantes et l'exigence statistique. « Nous proposons une voie d'analyse ; nous ne calculons pas encore une méta-analyse ni une validation clinique. » |
| 3:45–4:30 | **Comparaison.** Si des réponses réelles ont été collectées et vérifiées, sélectionner l'archive et commenter uniquement les écarts observés, avec le contexte fourni à chaque outil. Sinon : « L'outil de comparaison est prêt, mais l'expérience n'a pas été menée ; nous n'annonçons pas de supériorité sur une IA généraliste. » |
| 4:30–5:00 | **Suite.** « La prochaine étape est de faire valider les références, les règles et la fiche de question, puis de mesurer la méthode sur d'autres cas. Le prototype actuel est limité à KRAS. » Présenter les membres réels de l'équipe et leurs rôles, sans noms ou engagements inventés. |

## Questions probables

- **D'où viennent les données ?** Des JSON publics ClinicalTrials.gov conservés sous `data/raw/`, des références bibliographiques et d'un CSV local explicitement fictif. Les DOI sont rattachés au cache du registre ; les effectifs KRAS et les conclusions restent à vérifier dans les articles.
- **Quel est le rôle de l'IA ?** Le tri, le comptage, le verdict et le dossier utilisent des règles et des gabarits. Un mode optionnel d'extraction par Claude existe, mais il n'a pas été exécuté dans cette démo. Aucun appel IA n'est nécessaire à son fonctionnement.
- **Que signifie E4 ?** Un niveau atteignable selon les règles de travail du prototype, sous conditions de qualité, de concordance et de relecture. Ce n'est pas une échelle clinique validée ni une validation acquise.
- **D'autres cas ?** La recherche externe accepte KRAS avec panitumumab ou cetuximab. Le CSV interne ne contient que panitumumab/contrôle : le comptage cetuximab est indéterminé. NRAS/BRAF/RAS sont refusés, car leurs données ne sont pas disponibles. Pas encore d'évaluation sur 5 à 10 cas.
- **Confidentialité ?** Cette démonstration traite uniquement des données publiques ou fictives, en local. Une architecture pour de vraies données de santé n'est pas déployée et ne doit pas être annoncée comme réalisée.
- **Que fait-on si le live échoue ?** Ouvrir le dossier statique `outputs/demo/dossier.html`. Une vidéo reste à enregistrer sur le PC de présentation.

## Avant de monter sur scène

- [ ] Désigner la personne qui parle et celle qui pilote ; renseigner les rôles de l'équipe.
- [ ] Faire la revue scientifique décrite dans `docs/REVUE_SCIENTIFIQUE.md`.
- [ ] Actualiser les chiffres avec `python -m src.demo`, copier tout `outputs/demo/` sur le PC de présentation et une clé USB.
- [ ] Lancer `python -m streamlit run app_ui.py --browser.gatherUsageStats=false` sur ce PC, puis tester sans wifi. Garder `app.py` en secours.
- [ ] Enregistrer la vidéo du parcours (question → retenus → écartés → patients → dossier), sans données réelles.
- [ ] Répéter deux fois avec un chronomètre ; relever la durée réelle ci-dessous et raccourcir si besoin.
- [ ] Collecter et relire les comparaisons réelles, ou utiliser explicitement la phrase « expérience non menée ».
- [ ] Vérifier les règles de dépôt, l'autorisation de publication et l'échéance annoncée par l'organisation ; déposer les livrables.

| Répétition | Date | Durée réelle | Corrections |
|------------|------|--------------|-------------|
| 1 | À faire | Non mesurée | |
| 2 | À faire | Non mesurée | |
