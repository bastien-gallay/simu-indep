# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Non publié]

### Ajouté

- Documentation de contribution (CONTRIBUTING.md)
- Licence MIT
- Fichier .gitignore complet
- Configuration pyproject.toml pour uv
- Dépendances de développement (requirements-dev.txt)
- Documentation de contexte projet (.kiro/steering/)
- Configuration markdownlint (.markdownlint.json)
- Hooks pre-commit pour qualité de code
- Ce fichier CHANGELOG

### Modifié

- README.md amélioré avec instructions d'installation uv
- CONTRIBUTING.md mis à jour pour uv et correction titres dupliqués
- Correction du formatage Markdown dans tous les fichiers

## [1.0.0] - 2024-12-12

### Ajouté

- Simulateur de rémunération SASU vs EURL
- Interface Streamlit interactive
- Calculs fiscaux et sociaux 2024
- Comparaison visuelle avec graphiques
- Support de la flat tax et du barème progressif
- Gestion du quotient familial
- Calcul des charges sociales différenciées
- Tableau récapitulatif détaillé
- Visualisations Plotly interactives

### Fonctionnalités principales

- Calcul automatique des charges sociales (SASU: ~82%, EURL: ~45%)
- Gestion de l'Impôt sur les Sociétés (15% puis 25%)
- Calcul des dividendes avec charges spécifiques EURL
- Option barème IR vs flat tax 30%
- Interface responsive avec sidebar de paramètres
- Métriques clés et détails de calcul

### Hypothèses de calcul

- Taux de charges sociales moyens
- Barème IR 2024
- Abattement 10% sur salaires (plafonné)
- Charges sur dividendes EURL > 10% du capital
