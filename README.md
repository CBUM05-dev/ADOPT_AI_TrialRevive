# TrialRevive

Prototype de faisabilité sur des essais publics ClinicalTrials.gov et 400 patients **entièrement fictifs**. Cas de démonstration : panitumumab / KRAS dans le cancer colorectal. Les références et règles cliniques restent à valider par la personne Science ; la démo n'est pas un outil de décision clinique.

## Démarrage hors ligne après installation

Depuis la racine du dépôt, Python 3.11+ (3.12 vérifié) :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.fetch --offline
python -m src.cv
python -m pytest -q
python -m streamlit run app_ui.py --browser.gatherUsageStats=false
```

Sur Windows, activer avec `.venv\Scripts\Activate.ps1` dans PowerShell. L'installation nécessite le registre de paquets ; ensuite, la démo utilise les fichiers en cache, sans clé API ni accès Internet. `app.py` reste l'interface simple de secours. Éviter `src.fetch` sans `--offline` si l'on veut conserver les données brutes du dépôt.


## Site web (interface principale)

```bash
python server.py
# puis ouvrir http://localhost:8000
```

Site autonome (polices, 3D et scripts en local, aucun accès Internet nécessaire). Il réutilise la logique de `src/` sans la modifier. Les interfaces Streamlit (`app_ui.py`, `app.py`) restent disponibles en secours.

## Livrables et derniers préparatifs

```bash
python -m src.demo --output-dir outputs/demo
```

Cette commande produit les chiffres, le dossier Markdown et une page HTML autonome à ouvrir directement depuis le disque. La page n'utilise pas de serveur ni de bibliothèque distante ; ses liens scientifiques demandent Internet. Cet export est un secours statique, pas une vidéo.

- Comparaison IA : import JSON, archivage local, choix parmi toutes les réponses et examen des NCT dans les deux interfaces. [Protocole](data/baseline/LISEZ_MOI.md).
- [Pitch](PITCH.md), [cinq diapositives](docs/PRESENTATION.md), [revue scientifique](docs/REVUE_SCIENTIFIQUE.md).
- [Avancement et restes précis](PROGRESS.md), [vérifications](VERIFICATION.md).

Ne fournir à des services externes que des données publiques ou fictives ; ne pas publier les documents confidentiels de l'équipe. Les réponses IA réellement collectées ne sont pas encore présentes et aucune supériorité comparative n'est mesurée.

