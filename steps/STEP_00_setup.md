# STEP 00 — Setup (30 min)

## Prompt à donner à Claude
> Lis CLAUDE.md. Crée la structure de dossiers, un `requirements.txt` (streamlit, pandas, requests, numpy, anthropic, pytest), un environnement virtuel, et un `app.py` Streamlit avec un titre "TrialRevive" et une zone de texte pour la question. Ne fais rien d'autre.

## À faire
- [ ] `python -m venv .venv` puis activer, `pip install -r requirements.txt`
- [ ] Créer dossiers `data/raw`, `src`, `tests`
- [ ] `streamlit run app.py` fonctionne
- [ ] Mettre la clé API dans `.env` (jamais commitée), ajouter `.gitignore`

## Vérification
- La page s'ouvre dans le navigateur.
- `pytest` tourne (même sans test).
