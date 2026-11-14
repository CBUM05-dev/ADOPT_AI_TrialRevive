# VERIFICATION — Checklist étape par étape

État vérifié le 14 novembre 2026. Une case cochée décrit uniquement la vérification indiquée ; les validations scientifiques, les mesures comparatives et les tâches de présentation restent distinctes des tests techniques.

## Commandes de base

```bash
python -m src.fetch --offline
python -m src.cv
python -m pytest -q
python -m streamlit run app_ui.py --browser.gatherUsageStats=false
python -m src.demo --output-dir outputs/demo
```

Résultat cloud : **51 tests réussis**, serveur HTTP 200, démo AppTest sans connexion réseau en 0,47 s (démarrage + clic). Refaire les mesures sur le PC de scène.

## Étape 0 — Setup

- [x] Environnement installé, serveur Streamlit et parcours fonctionnel vérifiés
- [x] `.env` ignoré par Git ; aucune clé nécessaire à la démo hors ligne

## Étape 1 — Essais

- [x] 104 essais uniques en base (objectif initial de 30–50 dépassé)
- [x] Chaque essai a un identifiant NCT et un lien de registre issus du cache
- [x] Données brutes sauvegardées dans `data/raw`, reconstruction hors ligne vérifiée
- [ ] Revalider les liens en ligne si le jeu de données est actualisé

## Étape 2 — CV des essais

- [x] 104 fiches pour 104 essais
- [x] Champs absents conservés inconnus, méthode non inventée (tests d'extraction)
- [x] Les six DOI/PMID sont présents dans les références des essais en cache
- [ ] Trois fiches relues à la main contre la source et leurs conclusions confirmées
- [ ] Effectifs KRAS des six réanalyses confirmés dans les publications : `docs/REVUE_SCIENTIFIQUE.md`

## Étape 3 — Question

- [ ] Fiche KRAS validée par la personne Science
- [x] Autre médicament pris en charge : question KRAS/cetuximab valide pour la recherche externe
- [x] NRAS/BRAF/RAS et questions ambiguës refusés, sans réutiliser le comptage KRAS
- [x] Pas de comptage interne affirmatif sans bras du traitement demandé

## Étape 4 — Faux patients

- [x] 400 lignes, reproductibles avec seed 42
- [x] Proportions testées, identifiants FAKE et mention FICTIF

## Étape 5 — Moteur

- [x] Raison lisible pour chaque essai écarté
- [x] Au moins trois essais retenus (six dans la démo)
- [x] Entonnoir cohérent et déterministe : 400 → 359 → 332 → 271 → 252
- [x] Lien non validé ou traitement absent : comptage indéterminé
- [ ] Scores et seuils relus par la personne Science/statistiques

## Étape 6 — Dossier

- [x] Chiffres du dossier contrôlés contre ceux du moteur
- [x] Sources NCT et publications liées ; rattachement des articles vérifié dans le cache
- [x] Statuts non validés, hypothèses et données fictives explicités
- [ ] Contenu scientifique et sources relus par un clinicien/Science

## Étape 7 — Interface

- [x] Cas de démo inférieur à 10 s dans AppTest cloud
- [x] Parcours testé sans accès réseau ; bibliothèque 3D locale
- [x] Pas de crash sur entrée vide, inconnue ou marqueur non pris en charge
- [x] Toutes les pages principales affichées dans les tests UI
- [ ] Vérification visuelle et sans wifi sur le PC de présentation

## Étape 8 — Comparaison

- [x] Import/validation JSON, sélection de toutes les réponses, réponse complète et archivage sans écrasement
- [x] Fichiers invalides signalés ; différence de question signalée ; absence du cache distincte d'un NCT inexistant
- [ ] Réponses réelles brutes archivées avec modèle, date et contexte
- [ ] Au moins trois sources de l'IA généraliste vérifiées dans les sources primaires
- [ ] Évaluation comparée réalisée honnêtement avec les mêmes entrées et critères

## Étape 9 — Pitch

- [x] Pitch et cinq diapositives rédigés, chiffres alignés sur la démo
- [x] Dossier statique de secours exporté (HTML, Markdown, chiffres JSON)
- [ ] Équipe et rôles renseignés dans la présentation finale
- [ ] Moins de 5 min vérifié lors de deux répétitions humaines chronométrées
- [ ] Vidéo de secours enregistrée
- [ ] Échéance et règles de dépôt confirmées, livrables déposés

## Vérification finale sur place

- [ ] Lancer la démo de zéro sur le PC utilisé
- [ ] Tester sans wifi
- [ ] Vérifier batterie, chargeur et adaptateur HDMI
- [ ] Copier le projet, l'export de secours et la vidéo sur une clé USB
