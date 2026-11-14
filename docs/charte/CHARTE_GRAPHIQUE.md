# Charte graphique TrialRevive

*Version 1.0 · 14 novembre 2026. Ce fichier fait foi. Il est écrit pour être donné tel quel à une IA (Claude, ChatGPT, Cursor…) avant de lui demander un document, une présentation, une page web ou un visuel.*

## Instructions pour l'IA

Quand tu produis un livrable pour TrialRevive :

1. Utilise **uniquement les couleurs de la palette ci-dessous** : des nuances de gris, du noir au blanc. Aucune autre couleur, aucun dégradé, aucune ombre portée.
2. Utilise **la police Manrope** partout (repli : Arial). Pas d'autre police.
3. **Fond blanc par défaut.** Le fond noir est réservé aux moments forts (une slide clé, une couverture).
4. Place le **logo fourni** (dossier `logo/`), sans le redessiner, le déformer ni le recolorer en dehors du noir et du blanc.
5. Reste **sobre** : beaucoup d'espace, coins droits, filets fins, un seul élément mis en avant par page.
6. Ne change jamais le contenu qu'on te donne pour l'adapter au style.

## Palette

| Nom | Hex | Usage |
|---|---|---|
| Noir | `#0A0A0A` | Titres, logo, aplats forts (slide sombre, carte mise en avant), en-têtes de tableaux |
| Anthracite | `#262626` | Texte courant ; cartes sur fond noir |
| Graphite | `#4A4A4A` | Sous-titres, texte secondaire |
| Gris moyen | `#6E6E6E` | Légendes, surtitres, numéros de page |
| Gris clair | `#BDBDBD` | Icônes discrètes, flèches ; texte secondaire sur fond noir |
| Perle | `#E4E4E4` | Bordures, cartes |
| Brume | `#F5F5F5` | Fond des encadrés et des cartes |
| Blanc | `#FFFFFF` | Fond par défaut |
| Filet | `#D9D9D9` | Filets fins (sous les titres de section, en-tête, pied de page) |

Règles :

- Répartition visée : environ 60 % blanc et brume, 30 % gris, 10 % noir.
- Sur fond blanc, aucun texte plus clair que `#6E6E6E` (contraste 5,1:1).
- Sur fond noir : texte en blanc, texte secondaire en `#BDBDBD`.
- Dans un graphique, les séries se distinguent par la luminosité. La donnée clé est en noir, les autres en gris de plus en plus clairs.

## Typographie

Police unique : **Manrope** (Google Fonts, licence libre SIL OFL). Fichiers dans `polices/` : variable (toutes les graisses) et statiques Regular / Bold.

| Graisse | Usage |
|---|---|
| 200 (fine) | « Trial » du logo, accroches, grands chiffres clés |
| 400 | Texte courant |
| 500 | Surtitres en capitales |
| 700 / 800 | Titres, mots importants, « Revive » du logo |

Réglages :

- Titres : gras, approche serrée (−0,04 em, soit −1 pt dans Word).
- Surtitres : capitales, 13 pt, graisse 500, espacement +0,16 em, gris moyen.
- Hiérarchie : trois niveaux au plus par page.
- Texte aligné à gauche ; seuls les éléments isolés (logo, grand chiffre) se centrent.

Si Manrope n'est pas disponible (PowerPoint sur un poste sans la police), utiliser Arial et garder la même hiérarchie. Dans Word, la police peut être incorporée au fichier (Fichier > Options > Enregistrement > Incorporer les polices). Le modèle fourni le fait déjà.

## Logo

Fichiers dans `logo/`, en SVG (à préférer) et PNG transparent :

| Fichier | Quand l'utiliser |
|---|---|
| `TrialRevive_logo_horizontal_noir` / `_blanc` | Par défaut : en-tête de document, coin de slide, site web |
| `TrialRevive_logo_empile_noir` / `_blanc` | Couverture, page de titre, affiche (symbole au-dessus du nom) |
| `TrialRevive_symbole_noir` / `_blanc` | Petits espaces, favicon, pied de slide, filigrane |
| `TrialRevive_icone_carree.png` | Avatar, icône d'application (symbole blanc sur carré noir) |

Construction : un symbole de trois flèches fines formant un triangle (recyclage), et le nom écrit « Trial » en Manrope 200 puis « Revive » en Manrope 800, collés, approche −0,045 em.

Règles :

- Noir sur fond clair (blanc, brume, perle, gris clair) ; blanc sur fond noir, anthracite ou graphite.
- Zone de protection : la moitié de la largeur du symbole, tout autour.
- Taille minimale du symbole : 24 px (environ 6 mm).
- Interdit : déformer, changer les couleurs, ajouter une ombre, un contour ou un effet, réécrire le nom dans une autre police, séparer « Trial » et « Revive ».
- Le logo apparaît une fois par page ou par slide, en haut (à gauche dans un document, à droite sur une slide).

## Mise en page

### Documents (Word, PDF)

Modèle prêt à l'emploi : `modeles/Modele_document_TrialRevive.docx`. Aperçu : `apercus/document_modele.png`.

- A4, marges d'environ 2,5 cm, fond blanc.
- **En-tête** : logo horizontal noir (environ 4,5 cm de large) à gauche, filet fin `#D9D9D9` dessous.
- **Titre du document** : Manrope gras 26 pt, noir, filet noir de 1,5 pt dessous ; sous-titre en italique 9,5 pt, graphite.
- **Titres de section** : gras 15 pt, noir, filet fin `#D9D9D9` dessous, bel espace avant.
- **Sous-sections** : gras 11,5 pt, anthracite.
- **Texte** : 10 pt, anthracite, interligne 1,12.
- **Encadré** : fond brume `#F5F5F5`, barre noire épaisse (4,5 pt) à gauche, texte avec un mot clé en gras au début.
- **Tableaux** : ligne d'en-tête noire, texte blanc en gras ; cellules blanches, bordures `#D0D0D0`, marges intérieures généreuses.
- **Listes** : puces « • » noires.
- **Pied de page** : texte 8 pt gris moyen, aligné à droite, avec le numéro de page, filet fin au-dessus.

### Présentations (16:9)

Exemple : `modeles/Exemple_presentation_TrialRevive.pptx`. Aperçus : `apercus/slide_exemple_1.png` à `_3.png`.

- Format 13,33 × 7,5 pouces, marges latérales d'environ 0,9 pouce.
- Logo horizontal en haut à droite (environ 2,1 pouces de large), noir ou blanc selon le fond.
- Surtitre en capitales (13 pt, gris moyen), puis titre gras 34 pt, une idée par slide, sans point final.
- Contenu en cartes à coins droits : cartes blanches à bordure perle sur fond brume, cartes brume sur fond blanc, ou cartes anthracite sur fond noir.
- Une seule carte mise en avant par slide, en inversant ses couleurs (carte noire sur fond clair, carte blanche sur fond noir).
- Flèches de processus : chevrons gris clair entre les cartes.
- Icônes au trait fin, en anthracite (ou en blanc sur fond noir).
- Numéro de page « 1 / 3 » en bas à droite, 12 pt, gris moyen.
- Alterner fonds clairs et une slide noire pour le moment fort ; pas de bandeau ni de barre décorative.

### Web et visuels

Variables prêtes à l'emploi : `tokens/tokens.css` (CSS) et `tokens/tokens.json` (toute autre technologie).

- Grandes zones blanches, typographie qui porte le design.
- Contraste fort : titres très gras, accroches en graisse 200.
- Le symbole peut servir de grand filigrane très discret (`#171717` sur fond noir, `#EDEDED` sur fond blanc).

## À faire / à éviter

| À faire | À éviter |
|---|---|
| Fond blanc, beaucoup d'air | Couleurs vives, bleu « tech », dégradés |
| Noir pour l'élément le plus important | Plusieurs éléments mis en avant sur la même page |
| Filets fins gris | Ombres portées, coins arrondis, effets 3D |
| Manrope, trois niveaux de hiérarchie | Autres polices, texte centré en paragraphe |
| Logo fourni, en noir ou blanc | Logo redessiné, recoloré ou déformé |

## Contenu du dossier

```
08_Charte_graphique/
├── CHARTE_GRAPHIQUE.md     ← ce fichier (à donner à l'IA)
├── LISEZ-MOI.md            ← mode d'emploi rapide
├── logo/                   ← SVG et PNG : horizontal, empilé, symbole, icône
├── polices/                ← Manrope (variable, Regular, Bold) + licence OFL
├── tokens/                 ← tokens.css, tokens.json
├── modeles/                ← modèle Word, exemple PowerPoint
└── apercus/                ← images de référence (logo, slides, documents)
```
