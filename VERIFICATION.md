# VERIFICATION — Checklist étape par étape

Règle : une étape n'est ✅ dans PROGRESS.md que si TOUTES ses cases sont cochées.

## Commandes de base
```
pytest -q
streamlit run app.py
```

## Étape 0 — Setup
- [ ] Environnement installé, page Streamlit s'ouvre
- [ ] `.env` et clés ignorés par git

## Étape 1 — Essais
- [ ] 30-50 essais en base
- [ ] Chaque essai a un NCT et un lien valide
- [ ] Données brutes sauvegardées dans data/raw (reproductible hors ligne)

## Étape 2 — CV des essais
- [ ] Une fiche par essai
- [ ] 3 fiches relues à la main contre la source : correctes
- [ ] Champs manquants = null, jamais inventés

## Étape 3 — Question
- [ ] Fiche KRAS validée par la personne Science
- [ ] Une autre question produit une fiche valide

## Étape 4 — Faux patients
- [ ] 400 lignes, reproductible (seed)
- [ ] Proportions conformes, marqué "FICTIF"

## Étape 5 — Moteur
- [ ] Raison lisible pour chaque essai écarté
- [ ] >= 3 essais retenus
- [ ] Entonnoir de patients cohérent (calcul manuel identique)
- [ ] Déterministe

## Étape 6 — Dossier
- [ ] Toutes les sources existent
- [ ] Chiffres du dossier = chiffres du moteur
- [ ] Relu par un clinicien/Science

## Étape 7 — Interface
- [ ] "Cas de démo" < 10 s
- [ ] Marche hors ligne
- [ ] Pas de crash sur entrée vide

## Étape 8 — Comparaison
- [ ] Réponses brutes archivées
- [ ] Sources de l'IA vérifiées honnêtement

## Étape 9 — Pitch
- [ ] < 5 min chronométré, 2 répétitions
- [ ] Vidéo de secours enregistrée
- [ ] Livrables déposés avant dimanche 12h

## Vérification finale (avant le pitch)
- [ ] Lancer la démo de zéro sur le PC qui sera utilisé
- [ ] Tester sans wifi
- [ ] Batterie / chargeur / adaptateur HDMI
- [ ] Une copie du projet sur clé USB + une vidéo
