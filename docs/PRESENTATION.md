# TrialRevive — cinq diapositives

Support à copier dans l'outil de présentation de l'équipe. Chiffres issus de `python -m src.demo`, cache du 14 novembre 2026. Noms de l'équipe à renseigner par les participants. Les temps sont des cibles, pas des répétitions effectuées.

## 1. Une question, des essais à examiner — 0:00 à 0:45

**Avant de relancer une étude, quels essais existants peuvent aider ?**

- Cas : effet du panitumumab selon le statut KRAS, cancer colorectal.
- Sélectionner les essais comparables, retrouver les sources et vérifier les données utilisables.
- Objectif du prototype : un dossier de faisabilité traçable.

Source : question `src/question.py`, registre en cache `data/raw/`.

---

## 2. Un pipeline explicable — 0:45 à 1:15

**Question → exigences → essais → données disponibles → dossier.**

- Règles déterministes pour le tri et le comptage.
- Sources publiques ClinicalTrials.gov ; patients internes entièrement fictifs.
- Aucun appel IA nécessaire dans cette démo. Extraction IA optionnelle non exécutée.

Source : `src/engine.py`, `src/fake_data.py`, `src/dossier.py`.

---

## 3. La démonstration — 1:15 à 3:00

**104 essais → 6 retenus, 98 écartés avec une raison.**

**400 patients fictifs → 359 → 332 → 271 → 252 complets.**

- Montrer le tableau de bord, PRIME, les motifs de rejet puis l'entonnoir.
- Le nombre de lignes ne remplace pas la vérification des échantillons, méthodes, consentements et liens aux résultats.

Source : export `outputs/demo/chiffres.json`, calculé depuis le cache et le CSV fictif. Aucun résultat clinique réel n'est mesuré.

---

## 4. Un dossier avec ses conditions — 3:00 à 4:30

- Essais classés, rejets motivés, sources NCT et DOI, dossier téléchargeable.
- E4 est un **objectif conditionnel**, pas une validation clinique acquise.
- Effectifs KRAS, réanalyses, fiche de question et scores encore à relire.
- Comparaison IA : import et archivage disponibles ; **aucune performance comparative mesurée à ce stade**. Ne remplacer cette phrase que par des observations réellement vérifiées.

Source : `src/verdict.py`, `src/tolerances.py`, `docs/REVUE_SCIENTIFIQUE.md`, `data/baseline/LISEZ_MOI.md`.

---

## 5. Prochaines validations et équipe — 4:30 à 5:00

- Valider les six réanalyses, la question et les règles avec la personne Science.
- Mesurer la méthode sur plusieurs cas, avec les mêmes entrées pour les outils comparés.
- Étendre les marqueurs et pathologies après validation ; KRAS uniquement aujourd'hui.
- Présenter les membres et rôles réels de l'équipe.

**Données publiques ou fictives uniquement. Prototype de faisabilité, pas un outil de décision clinique.**
