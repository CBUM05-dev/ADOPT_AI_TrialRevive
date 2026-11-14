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
| `web/css/app.css` | Style complet, conforme à la charte graphique (`docs/charte/CHARTE_GRAPHIQUE.md`) : gris uniquement, Manrope, coins droits, sans ombre, dégradé ni 3D. |
| `web/brand/`, `web/fonts/` | Logos officiels (SVG) et police Manrope, fournis par la charte, utilisés sans modification. |
| `tests/test_charte.py` | Garde-fous automatiques : couleurs hors palette, coins arrondis, ombres, dégradés, polices ou ressources distantes font échouer le test. |
| `tests/test_server.py` | Tests de l'API (serveur réel, sans navigateur). |

## Ajouter une fonctionnalité

1. **Logique** dans `src/` (avec ses tests), comme avant.
2. **Route API** dans `server.py` : lire le JSON, appeler `src/`, renvoyer `Json({...})`. Erreurs : `bad("message clair")`.
3. **Vue** dans `web/js/app.js` : une fonction qui renvoie un élément (`h("div", {}, ...)`), puis l'ajouter dans `ROUTES` et dans la table de `render()`.
4. **Test** de la route dans `tests/test_server.py`.

## Règles à garder

- Le DOM est construit avec `h(...)` : les textes restent du texte. N'utilisez `innerHTML` (attribut `html`) que pour des constantes écrites dans le code, jamais pour des données.
- Aucune ressource distante : polices, logos et scripts sont dans `web/` (la démo doit marcher sans wifi).
- **Charte graphique** : Manrope, logo officiel, coins droits, ni ombre, ni dégradé, ni 3D. Utilisez les variables de `app.css` (`--tr-*` pour les gris, `--vert`, `--menthe`, `--ambre` pour l'accent), jamais une couleur en dur.
- **Écart assumé à la charte** : la charte est en gris uniquement, mais le tout gris faisait trop sombre pour un produit de santé. Le front ajoute un accent vert médical et de l'ambre pour les alertes. Les slides, le pitch et la vidéo doivent reprendre le même accent (ou la charte doit être mise à jour) pour garder une identité commune. Les couleurs autorisées sont listées dans `tests/test_charte.py`.
- Données publiques ou fictives uniquement. Aucune clé ni secret dans le dépôt (`.env` est ignoré).
- Les fichiers statiques ne sont pas mis en cache : rechargez la page après une modification.

## Pour éviter les conflits

Répartition suggérée : **UI/UX** (`web/css`, `illustration.js`, mise en page de `app.js`) d'un côté, **fonctionnalités** (`src/`, routes de `server.py`, `compare.py`, `demo.py`) de l'autre. Travaillez sur des branches et fusionnez souvent.
