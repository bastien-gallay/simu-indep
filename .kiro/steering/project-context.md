# Contexte du Projet - Simulateur de Rémunération

## Vue d'ensemble

Ce projet est un simulateur de rémunération pour entrepreneurs français, permettant de comparer les statuts SASU et EURL à l'Impôt sur les Sociétés.

## Architecture technique

### Stack technologique
- **Python 3.8+** : Langage principal
- **Streamlit** : Framework d'interface web
- **Plotly** : Visualisations interactives
- **Pandas** : Manipulation de données

### Structure du code
- `app.py` : Application principale avec logique métier et interface
- Approche monolithique pour simplicité d'usage
- Calculs fiscaux centralisés dans des fonctions dédiées

## Domaine métier

### Statuts juridiques couverts
- **SASU** : Société par Actions Simplifiée Unipersonnelle
  - Président assimilé salarié
  - Charges sociales ~82% du net
  - Pas de charges sociales sur dividendes
  
- **EURL** : Entreprise Unipersonnelle à Responsabilité Limitée
  - Gérant TNS (Travailleur Non Salarié)
  - Charges sociales ~45% du net
  - Charges sociales sur dividendes > 10% du capital

### Calculs fiscaux
- **IS** : Impôt sur les Sociétés (15% puis 25%)
- **IR** : Impôt sur le Revenu (barème progressif 2024)
- **Flat Tax** : 30% sur dividendes (alternative au barème)
- **Quotient familial** : Pris en compte dans les calculs IR

## Contraintes et limitations

### Simplifications assumées
- Taux de charges moyens (varient selon situation réelle)
- Pas de prise en compte : ACRE, CSG déductible détaillée, prévoyance
- Cotisations TNS calculées sur année courante (réalité : N-2 avec régularisation)

### Avertissements utilisateur
- Résultats indicatifs uniquement
- Consultation expert-comptable recommandée
- Mise à jour annuelle des taux nécessaire

## Standards de développement

### Qualité du code
- Docstrings pour toutes les fonctions
- Type hints Python
- Noms de variables explicites
- Séparation logique métier / interface

### Tests et validation
- Validation avec cas réels
- Comparaison avec autres simulateurs
- Tests de régression sur changements de taux

### Documentation
- README détaillé avec instructions
- Commentaires dans le code pour calculs complexes
- CHANGELOG pour suivi des modifications