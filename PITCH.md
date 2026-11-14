# Pitch TrialRevive — 5 minutes (+ 3 min de questions)

Chiffres ci-dessous = ceux de la démo actuelle (104 essais publics, 6 retenus, 98 écartés, 400 faux patients -> 252 complets (échelle S0 à S4)). Les relire à l'écran avant de parler.

| Temps | Qui | Contenu |
|-------|-----|---------|
| 0:00-0:45 | Pitch | **Problème.** Des centaines d'essais cliniques existent, mais personne ne sait vite lesquels peuvent répondre à une nouvelle question scientifique. Monter un nouvel essai coûte des années. Beaucoup d'anciens essais contiennent déjà la réponse : ils n'ont pas été conçus pour elle. |
| 0:45-1:15 | Pitch | **Idée.** On pose une question, TrialRevive rend un dossier de faisabilité : quels essais, quelle force de preuve, quel gain, avec les sources. Cas réel : le panitumumab et KRAS, dont on connaît la bonne réponse. |
| 1:15-3:45 | Démo (bouton « Cas de démo ») | 1. La question. 2. Onglet **retenus** : 6 essais sur 104 (dont PRIME). 3. Onglet **écartés** : 98 rejets, chacun avec sa raison. Montrer le point fort : 26 essais récents recrutent seulement des KRAS sauvages, donc ne peuvent pas comparer ; les essais pivots, conçus avant KRAS, le peuvent par réanalyse. 4. Onglet **patients** : 400 -> 252 complets sur l'essai interne fictif, sans que les données sortent. 5. **Dossier** : force de la preuve, gain, sources cliquables. |
| 3:45-4:30 | Pitch | **Comparaison** avec une IA généraliste (onglet Comparaison, à remplir) : elle ne compte pas les patients et ses sources doivent être vérifiées une à une. |
| 4:30-5:00 | Pitch | **Ce que ça change** : transformer des essais passés en réponses pour de nouvelles questions. Suite : plus de pathologies, vraies données hospitalières en environnement sécurisé. L'équipe. |

## Phrases à dire absolument
- « Données publiques ou fabriquées uniquement, aucun patient réel. »
- « Toute affirmation a une source cliquable. Ce qui n'est pas vérifié est marqué "à vérifier". »
- « Le tri est déterministe, sans IA : même question, même résultat. L'IA n'intervient que pour lire les documents. »

## Questions probables et réponses honnêtes
- **D'où viennent les données ?** ClinicalTrials.gov (API publique) + réanalyses publiées. L'essai interne est fabriqué.
- **Ça marche sur d'autres cas ?** Oui pour tout couple médicament anti-EGFR / marqueur (KRAS, NRAS, BRAF) ; pour d'autres classes, il faut ajouter des règles. Pas encore évalué sur 5 à 10 cas.
- **Risque de fausse information ?** Le dossier est produit par gabarit à partir des chiffres du moteur ; aucune phrase générée librement. Les réanalyses publiées sont encore à vérifier par un clinicien (le dire).
- **Limites ?** Règles à base de mots-clés sur le texte du registre ; lecture IA sur peu d'essais ; la méta-analyse elle-même n'est pas calculée, seulement proposée.
- **Confidentialité ?** Rien de réel ne quitte le système ; l'essai interne est local.

## Avant de monter sur scène
- [ ] Lancer `python -m streamlit run app.py` sur le PC de la présentation, tester sans wifi
- [ ] Enregistrer une vidéo de la démo (secours)
- [ ] Répéter 2 fois en chronométrant
- [ ] Remplir la comparaison IA (data/baseline/LISEZ_MOI.md)
- [ ] Faire vérifier `src/reanalyses.py` par la personne Science puis mettre `verifie=True` pour les lignes confirmées
