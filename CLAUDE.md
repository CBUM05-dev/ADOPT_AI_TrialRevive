# CLAUDE.md — Contexte permanent TrialRevive

## Projet
TrialRevive : une question scientifique entre -> un dossier de faisabilité sort.
Hackathon Adopt AI for Health, défi n°12. Démo finale : 5 min + 3 min de questions.

## Cas vedette
Panitumumab + mutation KRAS, cancer colorectal. Question : "Le statut KRAS change-t-il l'effet du panitumumab ?"

## Règles ABSOLUES
1. Aucune donnée de santé réelle. Uniquement données publiques (ClinicalTrials.gov) ou fabriquées.
2. Ne jamais mettre d'info confidentielle de la conception (dossier 04) dans le code publié ou un service externe sans accord de Sami.
3. Ne rien publier (GitHub public, etc.) sans accord.
4. Toute affirmation du dossier final doit avoir une SOURCE (NCT id, lien, citation).

## Stack (simple et rapide)
- Python 3.11+, SQLite (fichier `trialrevive.db`), pandas
- Interface : Streamlit (`app.py`)
- IA : API Claude pour l'extraction (2-3 essais seulement), le reste à la main si besoin
- Structure :
```
data/raw/        JSON bruts ClinicalTrials.gov
data/trials.db   base SQLite
src/fetch.py     brique 1 : récupération
src/cv.py        brique 2 : fiche (CV) d'essai
src/question.py  brique 3 : fiche de la question
src/engine.py    brique 4 : tri + comptage patients
src/fake_data.py essai interne fictif (400 patients)
src/dossier.py   brique 5 : dossier final
app.py           interface Streamlit
tests/           vérifications
```

## Façon de travailler
- Faire UNE étape à la fois (fichiers `steps/STEP_XX.md`).
- Après chaque étape : lancer les vérifications de `VERIFICATION.md`, puis mettre à jour `PROGRESS.md`.
- Petit et qui marche de bout en bout > grand et cassé. En cas de retard : couper, ne pas s'étendre.
- Si bloqué plus de 20 min : noter dans `PROGRESS.md` (section Blocages) et passer au plan B.
