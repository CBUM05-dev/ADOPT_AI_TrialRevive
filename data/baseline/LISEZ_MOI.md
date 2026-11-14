# Comparaison avec une IA généraliste

L'outil est prêt ; aucune réponse réelle n'est encore archivée. Les réponses des tests automatiques sont des fixtures, pas des résultats de comparaison.

## Protocole

1. Ouvrir une conversation neuve et relever le nom exact du modèle, la date, les outils activés (navigation, code) et les documents fournis. N'utiliser que des données publiques ou fictives.
2. Poser **exactement la même question** aux deux outils. Pour la démo :

   > Le statut KRAS change-t-il l'effet du panitumumab dans le cancer colorectal métastatique ?

3. Pour comparer le comptage, fournir également à l'IA le CSV **fictif** `data/internal_trial.csv` et les mêmes règles S0 à S4 de `src/engine.py`. Noter cet accès dans `contexte`. Si l'IA n'a pas reçu les données ou les règles, le signaler : son refus de donner un nombre n'est pas une erreur. Le prototype ne sait pas traiter une question libre sur « mes 400 patients » ; ne pas la présenter comme un test symétrique de question scientifique.
4. Copier la réponse **intégrale** dans un JSON avec sa question, son modèle et sa date. Ne pas corriger la réponse originale. Compléter les trois critères seulement après examen ; un critère absent s'affiche « Non évalué ».
5. Dans **Comparaison**, importer ce JSON puis cliquer sur **Archiver cette réponse localement**. On peut aussi le placer directement sous `data/baseline/`. L'archive conserve la réponse brute, sans écraser une archive précédente. Le téléchargement JSON fournit une copie transportable.
6. Sélectionner chaque réponse enregistrée dans le menu. Une question différente affiche « Non évalué sur cette question » pour TrialRevive ; relancer cette question si elle est prise en charge. Les réponses ne sont jamais tronquées.

## Format JSON

Ce gabarit n'est pas une réponse ; remplacer les valeurs avant import. Utiliser la date réelle de l'expérience.

```json
{
  "question": "Le statut KRAS change-t-il l'effet du panitumumab dans le cancer colorectal métastatique ?",
  "reponse_ia": "Réponse réelle complète à coller ici, sans correction",
  "modele": "Nom exact du modèle utilisé",
  "date": "2026-11-14",
  "contexte": "Conversation neuve ; navigation activée ou non ; fichiers et règles fournis ou non",
  "compte_patients": "Évaluation à remplir après vérification",
  "sources_verifiables": "Évaluation à remplir après vérification",
  "explique_rejets": "Évaluation à remplir après vérification"
}
```

## Vérifier les sources

L'expandeur **Examiner les NCT cités** retrouve les identifiants dans les 104 essais en cache et affiche le titre et l'effectif total du registre. Un identifiant absent du cache n'est pas nécessairement inexistant. L'effectif du registre n'est pas l'effectif KRAS analysé dans une publication.

Vérifier au moins trois sources citées contre le registre et/ou la publication : existence, bon essai, bon médicament, population et effectif analysé. Conserver les liens, ce qui a été vérifié et les écarts dans `sources_verifiables` ou une note jointe. La présence d'un lien ne valide pas une conclusion scientifique. Ne pas supposer que TrialRevive est meilleur : rapporter aussi ses références non validées, ses questions non prises en charge et les avantages observés de l'IA.

L'objectif du plan est de répéter sur 5 à 10 questions **prises en charge**, avec les mêmes entrées et les mêmes critères. Aucune comparaison de performance ne doit être annoncée avant ces mesures et leur relecture.
