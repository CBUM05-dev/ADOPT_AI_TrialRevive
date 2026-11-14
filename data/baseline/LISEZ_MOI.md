# Comparaison avec une IA généraliste (à faire par un humain, 15 min)

Je n'ai PAS fabriqué de réponses d'IA : une comparaison truquée ne résisterait pas aux questions du jury.

## À faire
1. Ouvrir une IA généraliste (ChatGPT, Gemini, Claude...) SANS rien de confidentiel.
2. Poser exactement ces questions (une conversation neuve chacune) :
   - « Le statut KRAS change-t-il l'effet du panitumumab dans le cancer colorectal métastatique ? Cite les essais cliniques avec leurs numéros NCT et le nombre de patients analysés. »
   - « Parmi mes 400 patients, combien ont un statut KRAS connu avec un test valide ? » (l'IA n'a pas les données : elle devrait le dire, ou inventer)
3. Copier la réponse COMPLÈTE dans un fichier `data/baseline/q1.json` (modèle ci-dessous).
4. Vérifier à la main chaque numéro NCT cité par l'IA sur https://clinicaltrials.gov (existe ? bon essai ? bon nombre de patients ?) et noter le résultat honnêtement.
5. Relancer l'app : l'onglet « Comparaison IA » s'affiche tout seul.

## Modèle de fichier `q1.json`
```json
{
  "question": "Le statut KRAS change-t-il l'effet du panitumumab ... ?",
  "reponse_ia": "COLLER ICI LA RÉPONSE COMPLÈTE",
  "modele": "nom exact du modèle",
  "date": "2026-11-15",
  "compte_patients": "non / oui mais inventé / ...",
  "sources_verifiables": "ex. 2 NCT sur 4 vérifiés exacts, 2 inexistants",
  "explique_rejets": "non"
}
```
Si l'IA généraliste est meilleure sur un critère, l'écrire quand même : le jury posera la question.
