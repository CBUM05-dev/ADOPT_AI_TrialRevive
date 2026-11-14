# STEP 07 — Interface Streamlit (1h30)

## Écrans (une seule page avec sections suffit)
1. Champ question + bouton "Analyser" (+ exemple pré-rempli : cas KRAS)
2. Résultat essais : onglets "Retenus" / "Écartés (avec raison)"
3. Données internes : graphique entonnoir (400 -> N utilisables)
4. Dossier final : rendu lisible + bouton "Télécharger (Markdown/PDF)"
5. Onglet "Comparaison IA généraliste" (étape 8)

## Prompt à donner à Claude
> Lis CLAUDE.md. Construis `app.py` avec les 5 sections ci-dessus en appelant `src/engine.py` et `src/dossier.py`. Mets en cache les résultats lourds. Bouton "Cas de démo" qui lance le cas vedette en un clic (indispensable pour le jour J). Messages d'erreur clairs.

## Vérification
- [ ] Le bouton "Cas de démo" donne un résultat complet en moins de 10 s
- [ ] Fonctionne SANS internet (tout en cache local) : plan B si le wifi de la salle plante
- [ ] Aucun crash si la question est vide ou inconnue
- [ ] Lisible sur un projecteur (grosse police)
