# Directives de Développement

## Principes généraux

### Simplicité avant tout
- Privilégier la lisibilité à la performance
- Éviter la sur-ingénierie
- Code auto-documenté avec noms explicites

### Fiabilité des calculs
- Vérifier toutes les formules avec sources officielles
- Tester avec des cas d'usage réels
- Documenter les hypothèses et limitations

## Standards de code Python

### Style et formatage
```python
# Utiliser des type hints
def calcul_is(benefice: float) -> float:
    """Calcule l'Impôt sur les Sociétés selon le barème 2024."""
    pass

# Constantes en MAJUSCULES
IS_TAUX_REDUIT = 0.15
IS_SEUIL_REDUIT = 42500

# Noms de variables explicites
remuneration_nette_mensuelle = 4000
charges_sociales_sasu = remuneration_nette * CHARGES_SASU_TAUX
```

### Structure des fonctions
- Une fonction = une responsabilité
- Paramètres avec valeurs par défaut quand approprié
- Docstrings avec Args et Returns
- Gestion des cas limites (valeurs négatives, nulles)

### Gestion des erreurs
```python
def calcul_ir(revenu: float, parts: float = 1.0) -> float:
    """Calcule l'IR avec validation des entrées."""
    if revenu < 0:
        raise ValueError("Le revenu ne peut pas être négatif")
    if parts <= 0:
        raise ValueError("Le nombre de parts doit être positif")
    # ... calcul
```

## Interface Streamlit

### Organisation des composants
- Sidebar pour tous les paramètres d'entrée
- Zone principale pour résultats et visualisations
- Sections clairement délimitées avec headers

### UX/UI
- Valeurs par défaut réalistes
- Tooltips explicatifs sur paramètres complexes
- Formatage monétaire cohérent (espaces comme séparateurs)
- Métriques visuelles pour résultats clés

### Performance
- Éviter les recalculs inutiles
- Mise en cache des résultats si nécessaire
- Interface réactive même avec gros volumes

## Données fiscales

### Sources officielles
- Service-public.fr
- URSSAF
- Impots.gouv.fr
- Code général des impôts

### Mise à jour annuelle
1. Vérifier nouveaux barèmes (janvier)
2. Mettre à jour constantes dans app.py
3. Tester avec cas de référence : `uv run pytest tests/`
4. Documenter changements dans CHANGELOG

### Traçabilité
```python
# Barème IR 2024 (revenus 2023)
# Source: https://www.impots.gouv.fr/particulier/bareme-de-limpot-sur-le-revenu
TRANCHES_IR = [
    (11294, 0.00),  # Tranche 0%
    (28797, 0.11),  # Tranche 11%
    # ...
]
```

## Tests et validation

### Cas de test obligatoires
- Revenus très faibles (proche de 0)
- Revenus moyens (30-50k€)
- Revenus élevés (>100k€)
- Cas limites (pas de dividendes, capital minimal)

### Validation croisée
- Comparer avec simulateurs officiels
- Vérifier cohérence SASU vs EURL
- Tester différentes configurations familiales

### Tests de régression
- Sauvegarder résultats de référence
- Vérifier après chaque modification
- Alerter sur écarts significatifs

## Documentation

### Code
- Docstrings pour toutes les fonctions publiques
- Commentaires pour logique complexe
- Exemples d'usage dans docstrings

### Utilisateur
- README à jour avec captures d'écran
- FAQ pour questions fréquentes
- Avertissements clairs sur limitations

### Développeur
- Architecture dans CONTRIBUTING.md
- Processus de mise à jour des taux
- Guide de déploiement si applicable