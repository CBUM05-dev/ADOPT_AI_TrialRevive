# Contrat entre le front (web/) et le backend

Le front (`web/`) ne connaît **que** ces routes JSON. Tout backend qui les respecte peut l'utiliser, quelle que soit sa logique interne. `server.py` en est l'implémentation de référence (Starlette), appuyée sur `src/`.

Les fichiers statiques sont servis sous `/assets/` (dossier `web/`), la page sur `/` (`web/index.html`). Les erreurs sont du JSON `{"error": "message lisible"}` avec un code HTTP 4xx ou 5xx : le front affiche ce message tel quel.

## Routes

| Route | Entrée | Sortie |
|---|---|---|
| `GET /api/info` | | `{ "exemple": "<question de démonstration>" }` |
| `POST /api/analyze` | `{ "question": "..." }` | `{ "dossier": <voir ci-dessous>, "markdown": "...", "exemple": "..." }` |
| `GET /api/dossier.md?question=...` | | fichier Markdown (en-tête `Content-Disposition: attachment`) |
| `GET /api/baselines` | | `{ "records": [<réponse IA>], "errors": ["..."] }` |
| `POST /api/baselines/validate` | `{ "text": "<JSON brut>" }` | `{ "record": <réponse IA> }` ou erreur 400 |
| `POST /api/baselines/archive` | `{ "record": <réponse IA> }` | `{ "archive": "<nom de fichier>" }` |
| `POST /api/compare` | `{ "question": "...", "record": <réponse IA> }` | `{ "rows": [...], "meme_question": bool, "nct": [...] }` |

**Réponse IA** (`record`) : `question`, `reponse_ia`, `modele`, `date` (AAAA-MM-JJ) obligatoires ; `contexte`, `compte_patients`, `sources_verifiables`, `explique_rejets` facultatifs (texte).

**`/api/compare`** : `rows` = liste de `{ "Critère", "TrialRevive", "IA généraliste (évaluation déclarée)" }` ; `nct` = liste de `{ "NCT cité", "Cache local", "Titre du registre", "Lien" }`.

## Le dossier (`dossier`)

Valeurs absentes : `null`. Le front gère `utilisables: null` (comptage indéterminé ou masqué).

```
question                       texte
retenus[]   (essais retenus, déjà classés du meilleur au moins bon)
  nct_id, titre, lien          texte
  retenu                       true
  niveau                       "direct" (médicament exact) ou "classe" (même classe)
  nb_patients                  entier
  couverture                   0 à 1, ou null (part des patients avec statut connu)
  score                        nombre
  plafond, E                   "E0" à "E4"  (E = preuve atteignable de cet essai)
  R, R_pourquoi                "R0".."R3" et une phrase
  ecarts[]                     phrases : compromis acceptés
  conditions[]                 phrases : à confirmer par un humain
ecartes[]   (essais écartés)
  nct_id, titre, lien, raison  texte
  retenu                       false
  etape_rejet                  1 à 6  (1 pas randomisé, 2 autre médicament, 3 marqueur non mesuré,
                                       4 un seul statut, 5 trop petit, 6 statut connu pour trop peu de patients)
rejection { total, retenus, ecartes_par_etape { "<libellé>": n } }
entonnoir[]  { etape: "S0 prévu : ...", n, n_publie }     5 marches S0 à S4 ; n_publie = null si < 5
utilisables                    entier ou null
raison_indetermination         texte ou null
groupes[]    { statut: "sauvage" | "muté", n_traite, n_controle, mediane_traite, mediane_controle, evenements, gain_mois }
verdict { R, R_texte, E, E_texte, E_pourquoi, preuve_verifiee (bool),
          G[] { code, gain, niveau_min } }
methode                        texte
statistique { evenements_necessaires_par_groupe, evenements_internes { sauvage, muté }, suffisant (bool), hr_hypothese }
essai_confirmation { hr_dilue, evenements_tous, evenements_selectionnes }
gain { pct_sauvage, gain_sauvage_mois, gain_mute_mois, note }
sources[]    { nct_id, lien, niveau, reanalyse, publication_lien, reanalyse_verifiee }
limites[]                      phrases
```

## Adapter un autre backend

Le plus simple : garder le front tel quel et écrire, côté backend, **une fonction qui transforme votre résultat dans ce format** (dans `server.py`, la fonction `analyse(text)` produit `{ question, dossier, markdown }`). Si un champ n'existe pas chez vous, mettez `null`, `[]` ou une phrase honnête (« non calculé ») plutôt que d'inventer une valeur : le front affiche ce qu'il reçoit.
