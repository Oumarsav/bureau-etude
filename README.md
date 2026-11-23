# Projet 1 — Bureau d'études : prédimensionnement

Application Python en console pour saisir/charger un petit projet, estimer les charges, effectuer un prédimensionnement pédagogique des poteaux et semelles, établir un devis simplifié et exporter un rapport.

> **Important — usage pédagogique uniquement.** Les calculs sont des estimations simplifiées destinées à un exercice. Ils ne constituent ni une note de calcul réglementaire ni une validation pour construire. Un ingénieur structure doit vérifier les hypothèses, les combinaisons d'actions, le sol, le ferraillage, le flambement, les dispositions constructives et les normes applicables.

## 1. Contenu

```text
bureau-etudes/
├── README.md
├── requirements.txt
├── .gitignore
├── donnees/
│   ├── projet_exemple.json
│   ├── materiaux.json
│   └── bordereau.csv
├── src/
│   ├── __init__.py
│   ├── elements.py
│   ├── charges.py
│   ├── predimensionnement.py
│   ├── devis.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_charges.py
└── rapports/
    └── .gitkeep
```

## 2. Prérequis

- Python 3.10 ou plus récent
- Aucune bibliothèque externe obligatoire

## 3. Lancer le programme

Ouvrir un terminal dans le dossier `bureau-etudes`, puis exécuter :

```bash
python -m src.main
```

Sous Windows, si `python` n'est pas reconnu, essayer :

```bash
py -m src.main
```

## 4. Menu

1. Saisir un nouveau projet
2. Charger un projet JSON
3. Calculer le poids propre estimatif
4. Effectuer la descente de charges simplifiée
5. Prédimensionner les poteaux et semelles
6. Générer le devis estimatif
7. Exporter le rapport texte
8. Quitter

Le programme conserve le projet actif en mémoire. La saisie et le chargement permettent d'enregistrer le projet au format JSON dans `donnees/`.

## 5. Hypothèses pédagogiques utilisées

- Poids propre d'une dalle : `épaisseur (m) × poids volumique du béton (kN/m³) × surface (m²)`.
- Charge permanente surfacique : poids propre de dalle + charges permanentes complémentaires.
- Charge d'exploitation : valeur saisie par l'utilisateur.
- Descente de charges simplifiée : `N_ELU = (1,35 G + 1,50 Q) × surface d'influence × nombre de niveaux` pour les poteaux ; `G + Q` est conservé pour le prédimensionnement des semelles.
- Section indicative de poteau : `A_min = N / contrainte_admissible_béton` ; côté carré arrondi au multiple supérieur de 5 cm, avec un minimum pédagogique de 20 cm.
- Semelle carrée indicative : `B_min = √(N_semelle / (q_sol − poids_propre_semelle_équivalent))`. Pour reproduire le tableau du sujet, le calcul par défaut utilise `q_sol = 200 kPa` et une marge forfaitaire de 12,5 kPa, soit `B ≥ √(N / 187,5)`.

Les coefficients et hypothèses sont affichés dans le rapport. Les résultats changent selon les données saisies.

## 6. Tests

À la racine du projet :

```bash
python -m unittest discover -s tests -v
```

## 7. Git (travail d'équipe)

Chaque membre peut travailler sur son module dans une branche dédiée, faire des commits descriptifs, puis ouvrir une pull request. Exemple :

```bash
git init
git add .
git commit -m "Initialise le projet bureau d'etudes"
```

Pensez à ajouter les autres membres comme collaborateurs du dépôt GitHub et à vérifier les calculs ensemble avant la présentation.
