# STEP 06 — Le dossier de faisabilité (1h30)

## Contenu du dossier
1. La question
2. Essais retenus (liste + lien NCT) et essais écartés avec raison
3. Données internes : entonnoir de patients, nombre utilisable
4. Comment obtenir la réponse : méthode proposée (ex. méta-analyse des essais retenus + analyse d'interaction)
5. Force de la preuve : faible / moyenne / forte avec justification
6. Gain attendu : ce que le médicament gagnerait (population ciblée, bénéfice)
7. Sources (toutes vérifiables)
8. Limites et avertissement : "prototype, données fictives"

## Prompt à donner à Claude
> Lis CLAUDE.md. Écris `src/dossier.py` : assemble les résultats du moteur en dossier (dict + rendu Markdown). La force de preuve est calculée par règle simple et expliquée (nb d'essais, taille totale, cohérence). L'IA peut reformuler le texte mais ne doit JAMAIS ajouter un chiffre ou une source absente des données. Chaque phrase factuelle référence sa source.

## Vérification
- [ ] Toutes les sources sont des liens/NCT réels trouvés dans la base
- [ ] Les chiffres du dossier = chiffres du moteur (test automatique)
- [ ] Le "gain pour le médicament" est justifié, pas inventé
- [ ] Mention "données fictives" visible pour la partie interne
- [ ] Un clinicien (Science) relit : crédible
