# Design Document - Intégration des Standards de Code et Tests

## Overview

Ce document détaille l'architecture et l'approche technique pour transformer le simulateur de rémunération monolithique en une application modulaire, testée et conforme aux standards de code définis. L'objectif est d'améliorer la qualité, la maintenabilité et la fiabilité tout en préservant les fonctionnalités existantes.

## Architecture

### Structure Modulaire Cible

```
simulateur_remuneration/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── tax_models.py      # Modèles de données fiscales
│   ├── simulation.py      # Modèles de simulation
│   └── results.py         # Modèles de résultats
├── calculators/
│   ├── __init__.py
│   ├── base.py           # Interface commune
│   ├── tax_calculator.py # Calculs fiscaux (IS, IR)
│   ├── social_charges.py # Charges sociales
│   └── simulation_engine.py # Moteur de simulation
├── validators/
│   ├── __init__.py
│   └── input_validator.py # Validation des entrées
├── ui/
│   ├── __init__.py
│   └── streamlit_app.py  # Interface utilisateur
└── utils/
    ├── __init__.py
    └── formatters.py     # Utilitaires de formatage
```

### Séparation des Responsabilités

- **Models** : Structures de données typées et immutables
- **Calculators** : Logique métier pure, sans dépendances externes
- **Validators** : Validation des entrées et règles métier
- **UI** : Interface utilisateur Streamlit, orchestration
- **Utils** : Fonctions utilitaires réutilisables

## Components and Interfaces

### 1. Modèles de Données (models/)

#### TaxBrackets et TaxRates

```python
@dataclass(frozen=True)
class TaxBracket:
    """Tranche d'imposition"""
    threshold: Decimal
    rate: Decimal
    
    def __post_init__(self):
        if self.rate < 0 or self.rate > 1:
            raise ValueError("Tax rate must be between 0 and 1")

@dataclass(frozen=True)
class TaxRates:
    """Taux fiscaux pour une année donnée"""
    year: int
    income_tax_brackets: List[TaxBracket]
    corporate_tax_reduced_rate: Decimal
    corporate_tax_normal_rate: Decimal
    corporate_tax_threshold: Decimal
    flat_tax_rate: Decimal
    social_charges_sasu: Decimal
    social_charges_eurl_tns: Decimal
    social_charges_eurl_dividends: Decimal
```

#### SimulationParameters

```python
@dataclass(frozen=True)
class SimulationParameters:
    """Paramètres d'entrée pour une simulation"""
    annual_revenue: Decimal
    operating_expenses: Decimal
    target_net_salary: Decimal
    distribute_dividends: bool
    tax_parts: Decimal
    use_progressive_tax: bool
    share_capital: Decimal = Decimal('1000')
    
    def __post_init__(self):
        # Validation des paramètres
        if self.annual_revenue < 0:
            raise ValueError("Annual revenue cannot be negative")
        # ... autres validations
```

### 2. Calculateurs (calculators/)

#### Interface Commune

```python
from typing import Protocol

class TaxCalculator(Protocol):
    """Interface pour les calculateurs fiscaux"""
    def calculate(self, taxable_amount: Decimal, tax_rates: TaxRates) -> Decimal:
        """Calcule l'impôt sur un montant imposable"""
        ...

class SocialChargesCalculator(Protocol):
    """Interface pour les calculateurs de charges sociales"""
    def calculate_salary_charges(self, net_salary: Decimal) -> Decimal:
        """Calcule les charges sociales sur salaire"""
        ...
    
    def calculate_dividend_charges(self, dividends: Decimal, share_capital: Decimal) -> Decimal:
        """Calcule les charges sociales sur dividendes"""
        ...
```

#### Implémentations Concrètes

```python
class IncomeTaxCalculator:
    """Calculateur d'impôt sur le revenu avec quotient familial"""
    
    def calculate(self, taxable_income: Decimal, tax_parts: Decimal, tax_rates: TaxRates) -> Decimal:
        """Calcule l'IR avec le quotient familial - Interface principale"""
        income_per_part = taxable_income / tax_parts
        tax_per_part = self.calculate_progressive_tax(income_per_part, tax_rates.income_tax_brackets)
        return tax_per_part * tax_parts
    
    def calculate_progressive_tax(self, income: Decimal, brackets: List[TaxBracket]) -> Decimal:
        """
        Calcule l'impôt progressif par tranches - Fonction réutilisable et testable
        
        Cette méthode est publique pour permettre :
        - Tests unitaires directs de la logique du barème
        - Réutilisation par d'autres calculateurs (CSG, etc.)
        - Transparence des calculs fiscaux
        
        Args:
            income: Revenu imposable
            brackets: Liste des tranches d'imposition
            
        Returns:
            Montant de l'impôt calculé
        """
        if income <= 0:
            return Decimal('0')
        
        total_tax = Decimal('0')
        previous_threshold = Decimal('0')
        
        for bracket in brackets:
            if income <= bracket.threshold:
                # Dernière tranche applicable
                taxable_in_bracket = income - previous_threshold
                total_tax += taxable_in_bracket * bracket.rate
                break
            else:
                # Tranche complète
                taxable_in_bracket = bracket.threshold - previous_threshold
                total_tax += taxable_in_bracket * bracket.rate
                previous_threshold = bracket.threshold
        
        return total_tax

class CorporateTaxCalculator:
    """Calculateur d'impôt sur les sociétés"""
    
    def calculate(self, profit: Decimal, tax_rates: TaxRates) -> Decimal:
        """Calcule l'IS avec taux réduit jusqu'au seuil"""
        if profit <= tax_rates.corporate_tax_threshold:
            return profit * tax_rates.corporate_tax_reduced_rate
        
        reduced_part = tax_rates.corporate_tax_threshold * tax_rates.corporate_tax_reduced_rate
        normal_part = (profit - tax_rates.corporate_tax_threshold) * tax_rates.corporate_tax_normal_rate
        return reduced_part + normal_part
```

### 3. Simulateurs Spécialisés (calculators/)

#### Approche Composable et Fonctionnelle

Au lieu d'un moteur monolithique, nous utilisons des simulateurs spécialisés qui composent des calculateurs purs :

```python
class SASUSimulator:
    """Simulateur spécialisé pour le statut SASU"""
    
    def __init__(
        self,
        income_tax_calc: IncomeTaxCalculator,
        corporate_tax_calc: CorporateTaxCalculator,
        social_charges_calc: SASUChargesCalculator
    ):
        self._income_tax_calc = income_tax_calc
        self._corporate_tax_calc = corporate_tax_calc
        self._social_charges_calc = social_charges_calc
    
    def simulate(self, params: SimulationParameters, tax_rates: TaxRates) -> SASUResult:
        """Simulation SASU - fonction pure sans effets de bord"""
        # Étape 1: Calculs de base (fonctions pures)
        profit_before_salary = self.calculate_profit_before_salary(params)
        salary_cost = self.calculate_salary_cost(params, tax_rates)
        
        # Étape 2: Calculs fiscaux (fonctions pures)
        profit_after_salary = profit_before_salary - salary_cost.total_cost
        corporate_tax = self._corporate_tax_calc.calculate(profit_after_salary, tax_rates)
        net_company_result = profit_after_salary - corporate_tax
        
        # Étape 3: Dividendes (fonctions pures)
        dividend_result = self.calculate_dividends(net_company_result, params, tax_rates)
        
        # Étape 4: IR final (fonction pure)
        income_tax = self.calculate_income_tax(
            salary_cost.net_salary, dividend_result, params, tax_rates
        )
        
        # Assemblage du résultat (immutable)
        return SASUResult(
            status="SASU",
            annual_revenue=params.annual_revenue,
            operating_expenses=params.operating_expenses,
            profit_before_salary=profit_before_salary,
            net_salary=salary_cost.net_salary,
            social_charges_salary=salary_cost.social_charges,
            profit_after_salary=profit_after_salary,
            corporate_tax=corporate_tax,
            net_company_result=net_company_result,
            gross_dividends=dividend_result.gross_amount,
            dividend_tax=dividend_result.tax_amount,
            net_dividends=dividend_result.net_amount,
            income_tax=income_tax,
            net_available=salary_cost.net_salary + dividend_result.net_amount - income_tax,
            global_tax_rate=self.calculate_global_rate(params.annual_revenue, salary_cost, corporate_tax, dividend_result.tax_amount, income_tax)
        )
    
    def calculate_profit_before_salary(self, params: SimulationParameters) -> Decimal:
        """Fonction pure : calcul du bénéfice avant rémunération - Testable directement"""
        return params.annual_revenue - params.operating_expenses
    
    def calculate_salary_cost(self, params: SimulationParameters, tax_rates: TaxRates) -> SalaryCost:
        """Fonction pure : calcul du coût salarial - Testable directement"""
        return self._social_charges_calc.calculate_salary_cost(
            params.target_net_salary, tax_rates
        )
    
    def calculate_dividends(self, net_company_result: Decimal, params: SimulationParameters, tax_rates: TaxRates) -> DividendResult:
        """Fonction pure : calcul des dividendes SASU - Testable directement"""
        if not params.distribute_dividends or net_company_result <= 0:
            return DividendResult.zero()
        
        # Logique spécifique SASU : pas de charges sociales sur dividendes
        gross_dividends = net_company_result
        
        if params.use_progressive_tax:
            # Barème progressif avec abattement 40%
            taxable_dividends = gross_dividends * Decimal('0.6')
            tax_amount = gross_dividends * tax_rates.social_charges_rate  # Prélèvements sociaux uniquement
        else:
            # Flat tax 30%
            tax_amount = gross_dividends * tax_rates.flat_tax_rate
        
        return DividendResult(
            gross_amount=gross_dividends,
            social_charges=Decimal('0'),  # Pas de charges sociales en SASU
            tax_amount=tax_amount,
            net_amount=gross_dividends - tax_amount
        )
    
    def calculate_income_tax(self, net_salary: Decimal, dividend_result: DividendResult, params: SimulationParameters, tax_rates: TaxRates) -> Decimal:
        """Fonction pure : calcul de l'IR final - Testable directement"""
        # Abattement 10% sur salaire (plafonné)
        salary_allowance = min(net_salary * Decimal('0.10'), Decimal('14171'))
        taxable_salary = net_salary - salary_allowance
        
        # Ajout des dividendes si option barème progressif
        if params.use_progressive_tax and params.distribute_dividends:
            taxable_dividends = dividend_result.gross_amount * Decimal('0.6')  # Abattement 40%
            total_taxable_income = taxable_salary + taxable_dividends
        else:
            total_taxable_income = taxable_salary
        
        return self._income_tax_calc.calculate(total_taxable_income, params.tax_parts, tax_rates)
    
    def calculate_global_rate(self, annual_revenue: Decimal, salary_cost: SalaryCost, corporate_tax: Decimal, dividend_tax: Decimal, income_tax: Decimal) -> Decimal:
        """Fonction pure : calcul du taux de prélèvement global - Testable directement"""
        if annual_revenue <= 0:
            return Decimal('0')
        
        total_taxes = salary_cost.social_charges + corporate_tax + dividend_tax + income_tax
        return total_taxes / annual_revenue

class EURLSimulator:
    """Simulateur spécialisé pour le statut EURL"""
    
    def __init__(
        self,
        income_tax_calc: IncomeTaxCalculator,
        corporate_tax_calc: CorporateTaxCalculator,
        social_charges_calc: EURLChargesCalculator
    ):
        self._income_tax_calc = income_tax_calc
        self._corporate_tax_calc = corporate_tax_calc
        self._social_charges_calc = social_charges_calc
    
    def simulate(self, params: SimulationParameters, tax_rates: TaxRates) -> EURLResult:
        """Simulation EURL - fonction pure sans effets de bord"""
        # Logique similaire mais avec calculs spécifiques EURL
        ...

@dataclass(frozen=True)
class SalaryCost:
    """Résultat immutable du calcul de coût salarial"""
    net_salary: Decimal
    social_charges: Decimal
    total_cost: Decimal

@dataclass(frozen=True)
class DividendResult:
    """Résultat immutable du calcul de dividendes"""
    gross_amount: Decimal
    social_charges: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    
    @classmethod
    def zero(cls) -> 'DividendResult':
        """Factory pour un résultat vide"""
        return cls(Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0'))
```

#### Orchestrateur Principal

```python
class SimulationOrchestrator:
    """Orchestrateur qui compose les simulateurs - Responsabilité unique"""
    
    def __init__(
        self,
        sasu_simulator: SASUSimulator,
        eurl_simulator: EURLSimulator,
        validator: InputValidator
    ):
        self._sasu_simulator = sasu_simulator
        self._eurl_simulator = eurl_simulator
        self._validator = validator
    
    def compare_statuses(
        self, 
        params: SimulationParameters, 
        tax_rates: TaxRates
    ) -> ComparisonResult:
        """Compare les deux statuts - fonction pure"""
        self._validator.validate(params)
        
        sasu_result = self._sasu_simulator.simulate(params, tax_rates)
        eurl_result = self._eurl_simulator.simulate(params, tax_rates)
        
        return ComparisonResult(
            sasu=sasu_result,
            eurl=eurl_result,
            difference=eurl_result.net_available - sasu_result.net_available,
            better_status="EURL" if eurl_result.net_available > sasu_result.net_available else "SASU"
        )
```

## Data Models

### Hiérarchie des Résultats

```python
@dataclass(frozen=True)
class BaseSimulationResult:
    """Résultat de base commun aux deux statuts"""
    status: str
    annual_revenue: Decimal
    operating_expenses: Decimal
    profit_before_salary: Decimal
    net_salary: Decimal
    social_charges_salary: Decimal
    profit_after_salary: Decimal
    corporate_tax: Decimal
    net_company_result: Decimal
    income_tax: Decimal
    net_available: Decimal
    global_tax_rate: Decimal

@dataclass(frozen=True)
class SASUResult(BaseSimulationResult):
    """Résultat spécifique SASU"""
    gross_dividends: Decimal
    dividend_tax: Decimal
    net_dividends: Decimal
    
    @property
    def monthly_net(self) -> Decimal:
        """Net mensuel disponible"""
        return self.net_available / 12

@dataclass(frozen=True)
class EURLResult(BaseSimulationResult):
    """Résultat spécifique EURL"""
    gross_dividends: Decimal
    social_charges_dividends: Decimal
    dividend_tax: Decimal
    net_dividends: Decimal
    share_capital: Decimal
```

### Configuration Fiscale

```python
@dataclass(frozen=True)
class FiscalConfiguration:
    """Configuration fiscale pour une année donnée"""
    year: int = 2024
    tax_rates: TaxRates = field(default_factory=lambda: get_2024_tax_rates())
    
    @classmethod
    def for_year(cls, year: int) -> 'FiscalConfiguration':
        """Factory method pour une année donnée"""
        if year == 2024:
            return cls(year=year, tax_rates=get_2024_tax_rates())
        else:
            raise ValueError(f"Tax rates for year {year} not available")

def get_2024_tax_rates() -> TaxRates:
    """Taux fiscaux 2024 avec sources officielles"""
    return TaxRates(
        year=2024,
        income_tax_brackets=[
            TaxBracket(Decimal('11294'), Decimal('0.00')),
            TaxBracket(Decimal('28797'), Decimal('0.11')),
            TaxBracket(Decimal('82341'), Decimal('0.30')),
            TaxBracket(Decimal('177106'), Decimal('0.41')),
            TaxBracket(Decimal('inf'), Decimal('0.45')),
        ],
        corporate_tax_reduced_rate=Decimal('0.15'),
        corporate_tax_normal_rate=Decimal('0.25'),
        corporate_tax_threshold=Decimal('42500'),
        # ... autres taux avec références officielles
    )
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, several properties can be consolidated to eliminate redundancy:

- Properties 1.1, 4.1, and 6.2 all relate to modular architecture and can be combined into a comprehensive modularity property
- Properties 3.3, 7.1, and 6.5 all relate to monetary value validation and can be unified
- Properties 3.4, 3.5, and 7.2 all relate to rate bounds validation and can be combined
- Properties 4.2, 4.4, and 4.5 all relate to code quality standards and can be combined
- Properties 7.3, 7.4, and 7.5 all relate to input validation and error handling and can be unified
- Properties 5.1-5.5 are all tooling configuration examples that don't need separate properties
- Properties 8.1-8.5 are all documentation examples that can be verified through inspection

### Core Properties

**Property 1: Behavioral Equivalence**
*For any* valid simulation parameters, the refactored modular code should produce identical results to the original monolithic implementation
**Validates: Requirements 1.3**

**Property 2: Tax Calculation Monotonicity**
*For any* two income values where income_a < income_b, the total tax calculated should satisfy tax(income_a) <= tax(income_b)
**Validates: Requirements 3.1**

**Property 3: Monetary Value Consistency**
*For any* calculation result, all monetary values should be non-negative and use consistent decimal precision
**Validates: Requirements 3.3, 6.5, 7.1**

**Property 4: Rate Bounds Validation**
*For any* tax rate or percentage calculation, the result should be within valid bounds (0 <= rate <= 1.0 for rates, 0 <= percentage <= 100 for percentages)
**Validates: Requirements 3.4, 3.5, 7.2**

**Property 5: Module Independence and Composability**
*For any* business logic module, it should be instantiable and testable without dependencies on UI or external systems, and simulators should be composable from pure calculation functions
**Validates: Requirements 1.1, 4.1, 6.2**

**Property 6: Type Annotation Completeness**
*For any* public function in the refactored code, it should have complete type annotations for parameters and return values
**Validates: Requirements 1.5, 4.4**

**Property 7: Input Validation Robustness**
*For any* invalid input (negative monetary values, out-of-bounds rates, invalid business parameters), the system should reject it with a meaningful error message
**Validates: Requirements 7.3, 7.4, 7.5**

**Property 8: Simulation Parameter Consistency**
*For any* simulation run, SASU and EURL calculations should use identical base tax rates and fiscal parameters
**Validates: Requirements 3.2**

**Property 9: Code Quality Standards Compliance**
*For any* function or module in the refactored code, it should follow naming conventions, avoid duplication, and maintain descriptive names
**Validates: Requirements 1.4, 4.2, 4.5**

**Property 10: Data Model Structure Consistency**
*For any* structured data in the system, it should use dataclasses with proper type annotations rather than dictionaries or tuples
**Validates: Requirements 6.1, 6.4**

## Error Handling

### Input Validation Strategy

```python
class InputValidator:
    """Validateur centralisé pour tous les paramètres d'entrée"""
    
    def validate_simulation_parameters(self, params: SimulationParameters) -> None:
        """Validation complète des paramètres de simulation"""
        self._validate_monetary_values(params)
        self._validate_tax_parameters(params)
        self._validate_business_rules(params)
    
    def _validate_monetary_values(self, params: SimulationParameters) -> None:
        """Validation des valeurs monétaires"""
        if params.annual_revenue < 0:
            raise ValueError("Le chiffre d'affaires ne peut pas être négatif")
        if params.operating_expenses < 0:
            raise ValueError("Les charges d'exploitation ne peuvent pas être négatives")
        if params.target_net_salary < 0:
            raise ValueError("La rémunération cible ne peut pas être négative")
    
    def _validate_tax_parameters(self, params: SimulationParameters) -> None:
        """Validation des paramètres fiscaux"""
        if params.tax_parts <= 0 or params.tax_parts > 6:
            raise ValueError("Le nombre de parts fiscales doit être entre 0.5 et 6")
    
    def _validate_business_rules(self, params: SimulationParameters) -> None:
        """Validation des règles métier"""
        if params.share_capital <= 0:
            raise ValueError("Le capital social doit être positif")
        if params.target_net_salary * 12 > params.annual_revenue:
            raise ValueError("La rémunération cible ne peut pas dépasser le CA")
```

### Exception Hierarchy

```python
class SimulatorError(Exception):
    """Exception de base pour le simulateur"""
    pass

class ValidationError(SimulatorError):
    """Erreur de validation des paramètres"""
    pass

class CalculationError(SimulatorError):
    """Erreur lors des calculs"""
    pass

class ConfigurationError(SimulatorError):
    """Erreur de configuration fiscale"""
    pass
```

## Testing Strategy

### Dual Testing Approach

Le projet utilisera une approche de test duale combinant tests unitaires et tests basés sur les propriétés :

- **Tests unitaires** : Vérification d'exemples spécifiques, cas limites, et intégration entre composants
- **Tests basés sur les propriétés** : Vérification des propriétés universelles sur de larges ensembles de données générées

### Property-Based Testing

**Framework choisi** : Hypothesis (Python)
**Configuration** : Minimum 100 itérations par test de propriété

Chaque test de propriété sera tagué avec un commentaire référençant explicitement la propriété du document de design :

```python
@given(
    revenue=st.decimals(min_value=0, max_value=1000000, places=2),
    expenses=st.decimals(min_value=0, max_value=500000, places=2)
)
def test_behavioral_equivalence_property(revenue, expenses):
    """**Feature: code-quality-integration, Property 1: Behavioral Equivalence**"""
    # Test implementation
    ...
```

### Unit Testing Strategy

**Framework** : pytest avec pytest-cov pour la couverture
**Couverture cible** : 80% minimum sur la logique métier

Les tests unitaires couvriront :

- Exemples spécifiques avec valeurs connues
- Cas limites (valeurs nulles, seuils fiscaux)
- Intégration entre calculateurs
- Validation des erreurs

### Test Organization

```
tests/
├── unit/
│   ├── test_tax_calculator.py
│   ├── test_social_charges.py
│   ├── test_simulation_engine.py
│   ├── test_validators.py
│   └── test_data_models.py
├── property/
│   ├── test_calculation_properties.py
│   ├── test_validation_properties.py
│   ├── test_architecture_properties.py
│   └── test_code_quality_properties.py
├── integration/
│   ├── test_complete_simulation.py
│   └── test_ui_integration.py
└── fixtures/
    ├── conftest.py
    └── sample_data.py
```

### Quality Tools Integration

Le projet intégrera les outils de qualité de code suivants selon les standards définis :

**Formatage automatique** : Black avec configuration ligne 100 caractères
**Linting** : Ruff pour vérifications de qualité et tri des imports
**Vérification de types** : mypy pour validation des annotations
**Couverture de tests** : pytest-cov avec objectif 80% minimum
**Pre-commit hooks** : Automatisation des vérifications avant commit

Configuration dans `pyproject.toml` :

```toml
[tool.black]
line-length = 100
target-version = ['py39']

[tool.ruff]
line-length = 100
target-version = "py39"
select = ["E", "W", "F", "I", "N", "UP", "B", "C4"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
disallow_untyped_defs = false
check_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=simulateur_remuneration --cov-report=html --cov-report=term"
```

### Test Data Strategy

Utilisation de fixtures pytest pour les données de test réutilisables :

```python
@pytest.fixture
def sample_tax_rates():
    """Taux fiscaux 2024 pour les tests"""
    return get_2024_tax_rates()

@pytest.fixture
def valid_simulation_params():
    """Paramètres de simulation valides"""
    return SimulationParameters(
        annual_revenue=Decimal('100000'),
        operating_expenses=Decimal('10000'),
        target_net_salary=Decimal('48000'),
        distribute_dividends=True,
        tax_parts=Decimal('1.0'),
        use_progressive_tax=False
    )
```

### Validation Against Official Sources

Les tests incluront des cas de validation contre des sources officielles :

- Simulateurs URSSAF
- Exemples du service-public.fr
- Barèmes officiels des impôts

```python
def test_official_tax_calculation_examples():
    """Test contre des exemples officiels du service public"""
    # Exemple officiel : 50000€ de revenus, 1 part
    official_result = Decimal('6914')  # Source: impots.gouv.fr
    calculated_result = income_tax_calc.calculate(
        Decimal('50000'), Decimal('1.0'), get_2024_tax_rates()
    )
    assert abs(calculated_result - official_result) < Decimal('1')  # Tolérance 1€
```

### Documentation Strategy

La documentation technique sera organisée selon les exigences du Requirement 8 :

**Architecture et organisation** : Documentation claire des modules et dépendances
**Sources officielles** : Références aux sources gouvernementales pour tous les taux et formules
**Exemples d'utilisation** : Documentation API avec exemples pour toutes les fonctions publiques
**Stratégie de tests** : Explication de l'approche duale (unitaires + propriétés)
**Guide de maintenance** : Processus de mise à jour annuelle des taux fiscaux

Structure de documentation :

```
docs/
├── architecture.md      # Organisation des modules
├── api_reference.md     # Documentation des APIs publiques
├── testing_strategy.md  # Approche de test et rationale
├── maintenance.md       # Guide de mise à jour des taux
└── examples/
    ├── basic_usage.py
    ├── advanced_scenarios.py
    └── tax_rate_updates.py
```

### Design Rationale: Public vs Private Methods

#### Testability vs Encapsulation Trade-offs

Pour les fonctions critiques comme `calculate_progressive_tax`, nous privilégions la **testabilité** et la **transparence** sur l'encapsulation stricte :

##### Avantages de l'approche publique

- **Tests directs** : Permet de tester la logique complexe du barème progressif de manière isolée
- **Réutilisabilité** : La fonction peut être utilisée par d'autres calculateurs (CSG, prélèvements sociaux)
- **Transparence fiscale** : Les calculs fiscaux bénéficient de la transparence pour la vérification et l'audit
- **Debugging facilité** : Permet d'inspecter les calculs intermédiaires lors du débogage

##### Mitigation des inconvénients

- **Documentation claire** : Distinction explicite entre interface principale (`calculate`) et fonctions utilitaires (`calculate_progressive_tax`)
- **Tests complets** : Les deux niveaux d'abstraction sont testés
- **Versioning** : Les changements d'interface sont gérés par la sémantique de version

Cette approche suit le principe de **transparence** particulièrement important pour les calculs fiscaux où la vérifiabilité est cruciale.

#### Avantages de l'Architecture Refactorisée

##### Respect des Principes CUPID

1. **Composable** :
   - Simulateurs spécialisés composent des calculateurs purs
   - Chaque calculateur peut être utilisé indépendamment
   - Orchestrateur compose les simulateurs sans couplage fort

2. **Unix Philosophy** :
   - Chaque simulateur fait une chose (SASU ou EURL) et la fait bien
   - Fonctions pures sans effets de bord
   - Interface claire et prévisible

3. **Predictable** :
   - Pas d'état interne muté
   - Fonctions pures : mêmes entrées → mêmes sorties
   - Résultats immutables (dataclasses frozen)

4. **Idiomatic** :
   - Utilisation de dataclasses frozen pour l'immutabilité
   - Factory methods pour les cas spéciaux
   - Type hints complets

5. **Domain-based** :
   - Vocabulaire métier clair (SalaryCost, DividendResult)
   - Séparation claire entre SASU et EURL
   - Noms explicites révélant l'intention

##### Testabilité Améliorée

- Chaque fonction peut être testée isolément
- Pas de mocks nécessaires pour les calculs purs
- Tests de propriétés plus faciles sur les fonctions pures
- Composition testable étape par étape

#### Principe de Testabilité Appliqué Systématiquement

**Toutes les méthodes de calcul sont publiques** pour permettre :

1. **Tests unitaires granulaires** : Chaque étape de calcul peut être testée isolément
2. **Debugging facilité** : Possibilité d'inspecter les résultats intermédiaires
3. **Réutilisabilité** : Les méthodes peuvent être utilisées par d'autres composants
4. **Transparence** : Calculs fiscaux vérifiables étape par étape

##### Convention de nommage

- `simulate()` : Interface principale pour la simulation complète
- `calculate_*()` : Fonctions de calcul réutilisables et testables
- Pas de méthodes privées pour les calculs métier critiques

Cette approche privilégie la **testabilité** et la **transparence** sur l'encapsulation stricte, particulièrement appropriée pour les calculs fiscaux où la vérifiabilité est essentielle.

## Development Methodology: Test-Driven Development (TDD)

### TDD Approach for Fiscal Calculations

Ce projet utilisera une approche **Test-First/TDD** particulièrement adaptée aux calculs fiscaux :

#### Cycle TDD Adapté

L'adaptation intégre une quatrième étape du cycle, *Reflect*, qui permet à l'assistant IA de réviser son plan en fonction du design émergent.

1. **Red** : Écrire un test qui échoue
   - Commencer par les cas officiels (exemples service-public.fr)
   - Tester d'abord les fonctions de calcul pures
   - Utiliser les résultats du code existant comme référence

2. **Green** : Implémenter le minimum pour faire passer le test
   - Extraire la logique du code monolithique existant
   - Adapter aux nouvelles interfaces typées
   - Valider contre les résultats existants

3. **Refactor** : Améliorer le code tout en gardant les tests verts
   - Appliquer les principes CUPID
   - Optimiser la lisibilité et la performance
   - Éliminer la duplication
   - Corriger tous les tests "failed"

4. **Reflect** : Révise le plan an ajoutant/modifiant/supprimant les tâches nécessaires
    - Utilise les difficultés rencontrés dans la phase Green
    - Réfléchis à la généralisation du refactor
    - Documente les décisions importantes à prendre dans le futur

#### Stratégie de Migration TDD

#### Phase 1 : Tests de Caractérisation

```python
def test_existing_behavior_characterization():
    """Tests de caractérisation du comportement existant"""
    # Capturer le comportement actuel comme référence
    original_result = simuler_sasu(
        ca_ht=100000,
        charges_exploitation=10000,
        remuneration_nette_cible=48000,
        distribuer_dividendes=True,
        parts_fiscales=1.0
    )
    
    # Ces valeurs deviennent nos tests de régression
    assert original_result.net_disponible == expected_value
    assert original_result.taux_prelevement_global == expected_rate
```

#### Phase 2 : Tests Unitaires des Calculateurs

```python
def test_income_tax_calculator_official_examples():
    """Tests basés sur exemples officiels avant implémentation"""
    # Exemple officiel : 50000€, 1 part = 6914€ d'IR
    # Source: impots.gouv.fr/particulier/simulateur
    
    # RED: Test écrit avant l'implémentation
    calc = IncomeTaxCalculator()
    result = calc.calculate(
        Decimal('50000'), 
        Decimal('1.0'), 
        get_2024_tax_rates()
    )
    
    # GREEN: Implémentation pour faire passer le test
    assert result == Decimal('6914')

def test_progressive_tax_calculation_step_by_step():
    """Test de la logique progressive avant implémentation"""
    calc = IncomeTaxCalculator()
    
    # Test des tranches individuellement
    # Tranche 1: 0-11294€ à 0%
    assert calc.calculate_progressive_tax(
        Decimal('10000'), 
        get_2024_tax_rates().income_tax_brackets
    ) == Decimal('0')
    
    # Tranche 2: 11294-28797€ à 11%
    assert calc.calculate_progressive_tax(
        Decimal('20000'), 
        get_2024_tax_rates().income_tax_brackets
    ) == Decimal('957.66')  # (20000-11294) * 0.11
```

#### Phase 3 : Tests d'Intégration avec Comparaison

```python
def test_sasu_simulator_matches_original():
    """Validation que le nouveau simulateur produit les mêmes résultats"""
    # Paramètres de test
    params = SimulationParameters(...)
    
    # Résultat original (code existant)
    original = simuler_sasu(...)
    
    # Nouveau simulateur
    new_simulator = SASUSimulator(...)
    new_result = new_simulator.simulate(params, get_2024_tax_rates())
    
    # Validation de l'équivalence
    assert new_result.net_available == original.net_disponible
    assert abs(new_result.global_tax_rate - original.taux_prelevement_global) < 0.001
```

#### Avantages de l'Approche TDD pour ce Projet

1. **Sécurité de Refactoring** : Les tests garantissent que le comportement reste identique
2. **Documentation Vivante** : Les tests servent de spécification exécutable
3. **Design Émergent** : Les interfaces émergent naturellement des besoins des tests
4. **Confiance** : Chaque modification est validée immédiatement
5. **Régression Zero** : Impossible de casser le comportement existant sans s'en apercevoir

#### Ordre de Développement TDD

1. **Tests de caractérisation** du code existant
2. **Tests unitaires** des calculateurs fiscaux (avec exemples officiels)
3. **Tests des simulateurs** (SASU puis EURL)
4. **Tests d'intégration** (orchestrateur)
5. **Tests de propriétés** (validation sur large échelle)
6. **Tests de l'interface** Streamlit (si nécessaire)

Cette approche garantit une migration sûre et une amélioration continue de la qualité.
