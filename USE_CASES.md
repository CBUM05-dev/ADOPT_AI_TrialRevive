# Cas d'usage — Ce que l'utilisateur peut faire

Acteurs : **Chercheur / Clinicien** (utilisateur principal), **Jury** (voit la démo), **IA Claude** (système externe pour l'extraction).

## Diagramme

```mermaid
flowchart LR
    U([Chercheur / Clinicien])
    J([Jury - observateur])
    AI([API IA - extraction])
    CT([ClinicalTrials.gov])

    subgraph TrialRevive
        UC1(Poser une question scientifique)
        UC2(Lancer le cas de démo)
        UC3(Voir les essais retenus)
        UC4(Voir les essais écartés et la raison)
        UC5(Compter les patients utilisables - essai interne)
        UC6(Consulter le dossier de faisabilité)
        UC7(Vérifier les sources)
        UC8(Télécharger le dossier)
        UC9(Comparer avec une IA généraliste)
        UC10(Récupérer les essais publics)
        UC11(Générer la fiche d'un essai)
    end

    U --> UC1
    U --> UC2
    U --> UC3
    U --> UC4
    U --> UC5
    U --> UC6
    U --> UC7
    U --> UC8
    U --> UC9
    J --> UC2
    J --> UC9

    UC1 -.inclut.-> UC10
    UC1 -.inclut.-> UC11
    UC6 -.inclut.-> UC7
    UC10 --> CT
    UC11 --> AI
```

## Description des cas d'usage

| Cas | Acteur | Résultat |
|-----|--------|----------|
| Poser une question | Chercheur | La question est traduite en exigences précises |
| Lancer le cas de démo | Chercheur / Jury | Résultat complet du cas KRAS en un clic |
| Voir essais retenus | Chercheur | Liste des essais pouvant répondre, avec lien NCT |
| Voir essais écartés | Chercheur | Chaque rejet est expliqué |
| Compter patients utilisables | Chercheur | Entonnoir 400 -> N sur l'essai fictif, sans que les données sortent |
| Consulter le dossier | Chercheur | Méthode, force de preuve, gain, sources |
| Vérifier les sources | Chercheur | Chaque affirmation renvoie à un essai/publication réel |
| Télécharger le dossier | Chercheur | Export Markdown/PDF |
| Comparer avec IA généraliste | Chercheur / Jury | Tableau côte à côte honnête |

## Séquence de la démo (pour le pitch)
```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant A as App TrialRevive
    participant M as Moteur
    participant D as Données (essais + essai fictif)
    U->>A: Question (panitumumab + KRAS)
    A->>M: Fiche de la question
    M->>D: Trier ~40 essais publics
    D-->>M: Retenus / écartés + raisons
    M->>D: Compter patients utilisables (400 faux patients)
    D-->>M: N utilisables
    M-->>A: Résultats
    A-->>U: Dossier de faisabilité + sources
```
