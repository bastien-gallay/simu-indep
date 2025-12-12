# Implementation Plan - Intégration des Standards de Code et Tests

## Vue d'ensemble

Ce plan d'implémentation suit une approche **Test-Driven Development (TDD)** avec le cycle Red-Green-Refactor-Reflect pour transformer le simulateur monolithique en une architecture modulaire, testée et conforme aux standards CUPID.

## Tâches d'implémentation

- [-] 1. Configuration de l'environnement de développement et outils qualité
  - Configurer les outils de qualité de code (Black, Ruff, mypy)
  - Mettre à jour pyproject.toml avec les dépendances de test
  - Configurer pre-commit hooks pour automatiser les vérifications
  - Créer la structure de répertoires pour les modules
  - *Requirements: 5.1, 5.2, 5.3, 5.4, 5.5*

- [x] 1.1 Configurer pytest et coverage
  - Installer pytest, pytest-cov, hypothesis pour les tests de propriétés
  - Configurer pytest.ini avec les options de couverture
  - Créer les répertoires tests/ avec structure modulaire
  - *Requirements: 2.3, 5.4*

- [x] 1.2 Configurer les outils de qualité
  - Configurer Black avec line-length=100 selon CODING_STANDARDS.md
  - Configurer Ruff pour linting et import sorting
  - Configurer mypy pour vérification de types stricte
  - Tester que tous les outils fonctionnent sur le code existant
  - *Requirements: 5.1, 5.2, 5.3*

- [ ] 2. Phase TDD Red : Tests de caractérisation du comportement existant
  - Créer des tests qui capturent le comportement actuel du code monolithique
  - Tester les fonctions calcul_is, calcul_ir, simuler_sasu, simuler_eurl
  - Utiliser des cas de test variés (revenus faibles, moyens, élevés)
  - Documenter les résultats comme référence pour la non-régression
  - *Requirements: 1.3, 2.1, 2.5*

- [x] 2.1 Tests de caractérisation des calculs fiscaux
  - **Property 1: Behavioral Equivalence**
  - **Validates: Requirements 1.3**
  - Tester calcul_is avec différents bénéfices (seuils IS)
  - Tester calcul_ir avec différents revenus et parts fiscales
  - Capturer les résultats exacts pour validation future

- [ ] 2.2 Tests de caractérisation des simulations complètes
  - **Property 1: Behavioral Equivalence**
  - **Validates: Requirements 1.3**
  - Tester simuler_sasu avec paramètres variés
  - Tester simuler_eurl avec différents capitaux sociaux
  - Valider tous les champs de ResultatSimulation

- [ ] 3. Création des modèles de données typés (TDD Green)
  - Créer le module models/ avec dataclasses immutables
  - Implémenter TaxRates, SimulationParameters, résultats
  - Ajouter validation dans `__post_init__` des dataclasses
  - Utiliser Decimal pour tous les calculs monétaires
  - *Requirements: 6.1, 6.5, 7.1, 7.2, 7.4, 7.5*

- [ ] 3.1 Modèles fiscaux et paramètres
  - Créer TaxBracket, TaxRates avec validation des taux
  - Créer SimulationParameters avec validation métier
  - Implémenter get_2024_tax_rates() avec sources officielles
  - Ajouter docstrings complètes avec références légales
  - *Requirements: 6.1, 7.2, 8.2*

- [ ] 3.2 Tests unitaires des modèles de données
  - **Property 3: Monetary Value Consistency**
  - **Property 4: Rate Bounds Validation**
  - **Validates: Requirements 3.3, 3.4, 3.5, 6.5, 7.1, 7.2**
  - Tester validation des taux (0-100%)
  - Tester validation des valeurs monétaires (non-négatives)
  - Tester validation des règles métier (capital > 0, parts fiscales)

- [ ] 3.3 Modèles de résultats immutables
  - Créer SalaryCost, DividendResult, BaseSimulationResult
  - Créer SASUResult, EURLResult, ComparisonResult
  - Implémenter factory methods (ex: DividendResult.zero())
  - Ajouter properties calculées (monthly_net, etc.)
  - *Requirements: 6.1, 6.5*

- [ ] 4. Calculateurs fiscaux purs (TDD Green)
  - Créer le module calculators/ avec interfaces Protocol
  - Implémenter IncomeTaxCalculator avec méthode publique calculate_progressive_tax
  - Implémenter CorporateTaxCalculator
  - Toutes les méthodes publiques pour testabilité maximale
  - *Requirements: 1.1, 4.1, 6.4*

- [ ] 4.1 Calculateur d'impôt sur le revenu
  - Implémenter IncomeTaxCalculator.calculate() avec quotient familial
  - Implémenter calculate_progressive_tax() publique et testable
  - Gérer les cas limites (revenus négatifs, parts invalides)
  - Utiliser les TaxBracket pour la logique progressive
  - *Requirements: 2.4, 4.2, 7.3*

- [ ] 4.2 Tests unitaires du calculateur IR
  - **Property 2: Tax Calculation Monotonicity**
  - **Validates: Requirements 3.1**
  - Tester avec exemples officiels (service-public.fr)
  - Tester calculate_progressive_tax isolément
  - Vérifier monotonie : revenus croissants → impôts croissants
  - Tester cas limites et validation d'erreurs

- [ ] 4.3 Calculateur d'impôt sur les sociétés
  - Implémenter CorporateTaxCalculator.calculate()
  - Gérer taux réduit (15%) jusqu'à 42500€, puis 25%
  - Validation des bénéfices (non-négatifs)
  - Documentation avec références Code Général des Impôts
  - *Requirements: 2.4, 4.2, 8.2*

- [ ] 4.4 Tests unitaires du calculateur IS
  - Tester seuils IS (42500€) avec exemples précis
  - Tester cas limites (bénéfice = 0, très élevé)
  - Valider contre calculs manuels officiels
  - Vérifier monotonie des calculs

- [ ] 5. Calculateurs de charges sociales (TDD Green)
  - Créer SASUChargesCalculator et EURLChargesCalculator
  - Implémenter calculs spécifiques à chaque statut
  - Méthodes publiques pour testabilité (calculate_salary_cost, etc.)
  - Gérer les spécificités EURL (seuil 10% capital pour dividendes)
  - *Requirements: 1.1, 4.1, 6.2*

- [ ] 5.1 Calculateur charges SASU
  - Implémenter calculate_salary_cost() (82% charges sur net)
  - Pas de charges sociales sur dividendes
  - Retourner SalaryCost avec détail net/charges/total
  - Validation des montants et cohérence
  - *Requirements: 2.4, 4.2*

- [ ] 5.2 Tests unitaires charges SASU
  - Tester calcul charges salariales (82% du net)
  - Vérifier absence charges sur dividendes
  - Tester cas limites (salaire = 0, très élevé)
  - Valider structure SalaryCost retournée

- [ ] 5.3 Calculateur charges EURL
  - Implémenter calculate_salary_cost() (45% charges TNS)
  - Implémenter calculate_dividend_charges() avec seuil 10% capital
  - Gérer la logique complexe des dividendes EURL
  - Documentation des règles TNS et seuils
  - *Requirements: 2.4, 4.2, 7.4*

- [ ] 5.4 Tests unitaires charges EURL
  - Tester charges TNS (45% du net)
  - Tester seuil 10% capital pour charges dividendes
  - Tester avec différents montants de capital social
  - Valider calculs complexes dividendes

- [ ] 6. Checkpoint - Validation des calculateurs de base
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Simulateurs spécialisés (TDD Green)
  - Créer SASUSimulator et EURLSimulator
  - Composer les calculateurs sans état interne
  - Toutes les méthodes de calcul publiques pour testabilité
  - Fonctions pures sans effets de bord
  - *Requirements: 1.1, 1.2, 4.1, 6.2*

- [ ] 7.1 SASUSimulator avec méthodes publiques
  - Implémenter simulate() comme orchestration principale
  - Implémenter calculate_profit_before_salary() publique
  - Implémenter calculate_salary_cost() publique
  - Implémenter calculate_dividends() publique (spécifique SASU)
  - Implémenter calculate_income_tax() publique
  - Implémenter calculate_global_rate() publique
  - *Requirements: 1.4, 4.2, 4.4*

- [ ] 7.2 Tests unitaires SASUSimulator
  - **Property 5: Module Independence and Composability**
  - **Validates: Requirements 1.1, 4.1, 6.2**
  - Tester chaque méthode de calcul isolément
  - Tester simulate() complète avec validation résultat
  - Vérifier composition sans dépendances externes
  - Tester cas avec et sans dividendes

- [ ] 7.3 EURLSimulator avec méthodes publiques
  - Implémenter simulate() pour logique EURL
  - Adapter calculate_dividends() pour règles EURL (charges sociales)
  - Gérer spécificités capital social et seuils
  - Maintenir cohérence interface avec SASUSimulator
  - *Requirements: 1.4, 4.2, 4.4*

- [ ] 7.4 Tests unitaires EURLSimulator
  - **Property 5: Module Independence and Composability**
  - **Validates: Requirements 1.1, 4.1, 6.2**
  - Tester logique spécifique EURL (charges dividendes)
  - Tester différents montants de capital social
  - Valider cohérence avec interface SASU
  - Tester cas limites et validation

- [ ] 8. Validation et orchestrateur (TDD Green)
  - Créer InputValidator avec validation robuste
  - Créer SimulationOrchestrator pour composer les simulateurs
  - Gestion d'erreurs explicite avec messages clairs
  - Interface simple pour comparaison SASU vs EURL
  - *Requirements: 7.1, 7.3, 7.4, 7.5*

- [ ] 8.1 InputValidator complet
  - Valider tous les paramètres SimulationParameters
  - Messages d'erreur explicites et utiles
  - Validation des règles métier complexes
  - Utiliser TypeGuard si approprié pour validation runtime
  - *Requirements: 6.3, 7.3*

- [ ] 8.2 Tests de validation d'entrées
  - **Property 7: Input Validation Robustness**
  - **Validates: Requirements 7.3, 7.4, 7.5**
  - Tester rejet valeurs négatives avec messages clairs
  - Tester validation parts fiscales (limites légales)
  - Tester validation capital social positif
  - Tester validation cohérence CA/rémunération

- [ ] 8.3 SimulationOrchestrator
  - Implémenter compare_statuses() fonction pure
  - Composer SASUSimulator et EURLSimulator
  - Retourner ComparisonResult avec analyse
  - Pas d'état interne, composition pure
  - *Requirements: 1.1, 4.1*

- [ ] 8.4 Tests d'intégration orchestrateur
  - **Property 8: Simulation Parameter Consistency**
  - **Validates: Requirements 3.2**
  - Tester que SASU et EURL utilisent mêmes taux fiscaux
  - Valider ComparisonResult avec différents scénarios
  - Tester composition complète sans mocks

- [ ] 9. Tests de régression et équivalence comportementale
  - Valider que les nouveaux simulateurs produisent résultats identiques
  - Comparer résultat par résultat avec code original
  - Tests sur large gamme de paramètres d'entrée
  - Documenter et corriger toute divergence trouvée
  - *Requirements: 1.3, 2.5*

- [ ] 9.1 Tests de régression SASU
  - **Property 1: Behavioral Equivalence**
  - **Validates: Requirements 1.3**
  - Comparer SASUSimulator.simulate() vs simuler_sasu()
  - Tester sur 20+ combinaisons de paramètres
  - Tolérance < 1€ sur tous les montants
  - Documenter toute différence significative

- [ ] 9.2 Tests de régression EURL
  - **Property 1: Behavioral Equivalence**
  - **Validates: Requirements 1.3**
  - Comparer EURLSimulator.simulate() vs simuler_eurl()
  - Tester différents capitaux sociaux
  - Valider logique complexe dividendes EURL
  - Assurer équivalence parfaite

- [ ] 10. Tests de propriétés avec Hypothesis
  - Implémenter tests basés sur propriétés pour validation large
  - Utiliser générateurs Hypothesis pour paramètres aléatoires
  - Valider invariants métier sur milliers de cas
  - Minimum 100 itérations par test de propriété
  - *Requirements: 3.1, 3.2, 3.3, 3.4, 3.5*

- [ ] 10.1 Tests de propriétés fiscales
  - **Property 2: Tax Calculation Monotonicity**
  - **Property 3: Monetary Value Consistency**
  - **Property 4: Rate Bounds Validation**
  - **Validates: Requirements 3.1, 3.3, 3.4, 3.5, 6.5, 7.1, 7.2**
  - Générer revenus aléatoires, vérifier monotonie impôts
  - Vérifier tous résultats monétaires non-négatifs
  - Vérifier tous taux dans bornes valides (0-100%)

- [ ] 10.2 Tests de propriétés architecturales
  - **Property 5: Module Independence and Composability**
  - **Property 6: Type Annotation Completeness**
  - **Property 9: Code Quality Standards Compliance**
  - **Property 10: Data Model Structure Consistency**
  - **Validates: Requirements 1.1, 1.4, 1.5, 4.1, 4.2, 4.4, 4.5, 6.1, 6.2, 6.4**
  - Vérifier indépendance modules (pas imports UI)
  - Vérifier annotations types complètes
  - Vérifier utilisation dataclasses vs dict/tuple

- [ ] 11. Checkpoint - Validation complète des tests
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Refactoring de l'interface Streamlit
  - Séparer logique UI de la logique métier
  - Utiliser SimulationOrchestrator pour les calculs
  - Maintenir interface utilisateur identique
  - Améliorer gestion d'erreurs avec messages InputValidator
  - *Requirements: 1.1, 1.2, 7.3*

- [ ] 12.1 Extraction logique métier de app.py
  - Remplacer appels directs simuler_sasu/eurl par orchestrateur
  - Garder interface Streamlit identique pour utilisateur
  - Utiliser nouveaux modèles de données typés
  - Améliorer affichage erreurs avec messages explicites
  - *Requirements: 1.1, 1.2*

- [ ] 12.2 Tests d'intégration interface
  - Tester que interface produit mêmes résultats visuels
  - Valider gestion erreurs utilisateur
  - Tester cas limites interface (valeurs extrêmes)
  - Vérifier cohérence affichage avec nouveaux modèles

- [ ] 13. Documentation technique complète
  - Documenter architecture modulaire et dépendances
  - Créer guide de maintenance avec processus mise à jour taux
  - Documenter API publique avec exemples d'usage
  - Expliquer stratégie de tests (unitaires vs propriétés)
  - *Requirements: 8.1, 8.2, 8.3, 8.4, 8.5*

- [ ] 13.1 Documentation architecture et API
  - Diagrammes modules et dépendances
  - Documentation API avec exemples concrets
  - Guide utilisation calculateurs indépendants
  - Références sources officielles pour taux fiscaux
  - *Requirements: 8.1, 8.2, 8.3*

- [ ] 13.2 Guide de maintenance annuelle
  - Processus mise à jour taux fiscaux (janvier)
  - Checklist validation nouveaux taux
  - Tests de régression à exécuter
  - Documentation des changements légaux à surveiller
  - *Requirements: 8.5*

- [ ] 14. Checkpoint final - Validation complète
  - Ensure all tests pass, ask the user if questions arise.

## Notes d'implémentation

### Approche TDD Stricte

- Chaque fonctionnalité commence par un test qui échoue (Red)
- Implémentation minimale pour faire passer le test (Green)
- Refactoring avec tests verts (Refactor)
- Réflexion et adaptation du plan (Reflect)

### Testabilité Maximale

- Toutes les méthodes de calcul sont publiques
- Pas de méthodes privées pour la logique métier critique
- Fonctions pures sans effets de bord
- Composition explicite des dépendances

### Validation Continue

- Tests de régression après chaque module
- Comparaison systématique avec code original
- Couverture de code > 80% sur logique métier
- Validation avec sources officielles

### Principes CUPID Appliqués

- **Composable** : Modules indépendants et réutilisables
- **Unix Philosophy** : Une responsabilité par module
- **Predictable** : Fonctions pures, résultats déterministes
- **Idiomatic** : Conventions Python et dataclasses
- **Domain-based** : Vocabulaire métier explicite