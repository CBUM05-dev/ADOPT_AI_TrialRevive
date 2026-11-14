# Guide du nouveau front (pour Adam)

Le site web remplace l'interface Streamlit pour la démo. La logique métier (`src/`) n'a pas changé : le site l'appelle par une petite API.

## Lancer

```powershell
python -m pip install -r requirements.txt
python -m pytest -q          # 56 tests doivent passer
python server.py             # puis http://localhost:8000   (ou double-clic sur lancer.bat)
```

Les interfaces Streamlit (`app_ui.py`, `app.py`) restent en secours.

## Où est quoi

| Fichier | Rôle |
|---|---|
| `server.py` | API (Starlette) : `/api/analyze`, `/api/baselines`, `/api/compare`, `/api/dossier.md`… Réutilise `src/` sans le modifier. |
| `web/index.html` | Coquille de la page (barre latérale, tiroir, infobulle). |
| `web/js/app.js` | Toutes les vues : accueil, aperçu, essais, écartés, patients, dossier, comparaison, guide. |
| `web/js/illustration.js` | Illustrations vectorielles (personnages, icônes) : accueil et bandeaux de pages. |
| `web/js/capsule.js` | Capsule 3D (three.js local). |
| `web/css/app.css` | Style complet (palette verte, noir, gris clair, d'après la maquette). |
| `tests/test_server.py` | Tests de l'API (serveur réel, sans navigateur). |

## Ajouter une fonctionnalité

1. **Logique** dans `src/` (avec ses tests), comme avant.
2. **Route API** dans `server.py` : lire le JSON, appeler `src/`, renvoyer `Json({...})`. Erreurs : `bad("message clair")`.
3. **Vue** dans `web/js/app.js` : une fonction qui renvoie un élément (`h("div", {}, ...)`), puis l'ajouter dans `ROUTES` et dans la table de `render()`.
4. **Test** de la route dans `tests/test_server.py`.

## Règles à garder

- Le DOM est construit avec `h(...)` : les textes restent du texte. N'utilisez `innerHTML` (attribut `html`) que pour des constantes écrites dans le code, jamais pour des données.
- Aucune ressource distante : polices, 3D et scripts sont dans `web/` (la démo doit marcher sans wifi).
- Données publiques ou fictives uniquement. Aucune clé ni secret dans le dépôt (`.env` est ignoré).
- Les fichiers statiques ne sont pas mis en cache : rechargez la page après une modification.

## Pour éviter les conflits

Répartition suggérée : **UI/UX** (`web/css`, `illustration.js`, mise en page de `app.js`) d'un côté, **fonctionnalités** (`src/`, routes de `server.py`, `compare.py`, `demo.py`) de l'autre. Travaillez sur des branches et fusionnez souvent.
