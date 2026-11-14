# STEP 05 — Le moteur (2h) — LE COEUR

## Entrées
Fiche de la question (étape 3) + CV des essais (étape 2) + essai interne (étape 4).

## Tri en entonnoir (chaque rejet garde sa RAISON)
1. Randomisé ? non -> écarté ("pas randomisé")
2. Traitement correspond ? non -> écarté
3. Biomarqueur mesuré ? non -> écarté ("KRAS non mesuré")
4. Analyse par sous-groupe possible ? non -> écarté
5. Taille suffisante ? non -> écarté
-> Reste : essais "retenus"

## Comptage sur l'essai interne
Patients utilisables = traitement connu ET kras_statut connu ET méthode de test valide ET données de survie complètes. Afficher l'entonnoir : 400 -> sans KRAS connu -> sans méthode valide -> ... -> N utilisables.

## Prompt à donner à Claude
> Lis CLAUDE.md. Écris `src/engine.py` : (1) `screen_trials(question, cvs)` retourne pour chaque essai {nct_id, retenu: bool, raison}; (2) `count_usable(df)` retourne le nombre de patients utilisables et l'entonnoir étape par étape. Déterministe, pas d'IA ici. Tests unitaires avec cas limites.

## Vérification
- [ ] Chaque essai écarté a une raison lisible
- [ ] Au moins 3 essais retenus pour le cas KRAS (sinon revoir exigences)
- [ ] L'entonnoir de comptage se recoupe à la main (somme cohérente, 400 au départ)
- [ ] Même entrée = même sortie
