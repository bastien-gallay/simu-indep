"""
Modèles de paramètres de simulation pour le simulateur de rémunération.

Ce module contient les structures de données typées pour représenter
les paramètres d'entrée des simulations SASU/EURL avec validation
composable des règles métier.
"""

from dataclasses import dataclass
from decimal import Decimal

from .validators import (
    BusinessLogicValidator,
    MonetaryValueValidator,
    StatusValidatorFactory,
    TaxPartsValidator,
)


@dataclass(frozen=True)
class SimulationParameters:
    """
    Paramètres d'entrée pour une simulation de rémunération.

    Encapsule tous les paramètres nécessaires pour effectuer une simulation
    comparative entre les statuts SASU et EURL, avec validation composable
    des règles métier françaises.

    Args:
        annual_revenue: Chiffre d'affaires annuel HT en euros
        operating_expenses: Charges d'exploitation annuelles en euros
        target_net_salary: Rémunération nette mensuelle cible en euros
        distribute_dividends: Si True, distribue le résultat net en dividendes
        tax_parts: Nombre de parts fiscales pour le calcul IR (quotient familial)
        use_progressive_tax: Si True, utilise le barème progressif pour les dividendes
                           Si False, utilise la flat tax (30%)
        share_capital: Capital social de la société en euros (défaut: 1000€)

    Raises:
        ValueError: Si les paramètres ne respectent pas les règles métier

    Example:
        >>> params = SimulationParameters(
        ...     annual_revenue=Decimal('100000'),
        ...     operating_expenses=Decimal('10000'),
        ...     target_net_salary=Decimal('4000'),
        ...     distribute_dividends=True,
        ...     tax_parts=Decimal('1.0'),
        ...     use_progressive_tax=False
        ... )
        >>> params.annual_revenue
        Decimal('100000')
    """

    annual_revenue: Decimal
    operating_expenses: Decimal
    target_net_salary: Decimal
    distribute_dividends: bool
    tax_parts: Decimal
    use_progressive_tax: bool
    share_capital: Decimal = Decimal("1000")

    def __post_init__(self) -> None:
        """Validation composable des paramètres selon les règles métier."""
        self._validate_monetary_values()
        self._validate_tax_parts()
        self._validate_business_logic()

    def _validate_monetary_values(self) -> None:
        """Valide toutes les valeurs monétaires."""
        MonetaryValueValidator("Le chiffre d'affaires").validate(self.annual_revenue)
        MonetaryValueValidator("Les charges d'exploitation").validate(self.operating_expenses)
        MonetaryValueValidator("La rémunération cible").validate(self.target_net_salary)
        MonetaryValueValidator("Le capital social", allow_zero=False).validate(self.share_capital)

    def _validate_tax_parts(self) -> None:
        """Valide les parts fiscales."""
        TaxPartsValidator().validate(self.tax_parts)

    def _validate_business_logic(self) -> None:
        """Valide les règles métier complexes."""
        BusinessLogicValidator.validate_revenue_expenses_coherence(
            self.annual_revenue, self.operating_expenses
        )
        BusinessLogicValidator.validate_salary_revenue_coherence(
            self.annual_target_salary, self.annual_revenue
        )
        BusinessLogicValidator.validate_dividend_feasibility(
            self.annual_revenue,
            self.operating_expenses,
            self.annual_target_salary,
            self.distribute_dividends,
        )

    @property
    def gross_profit(self) -> Decimal:
        """Bénéfice brut avant rémunération."""
        return self.annual_revenue - self.operating_expenses

    @property
    def annual_target_salary(self) -> Decimal:
        """Rémunération nette annuelle cible."""
        return self.target_net_salary * 12

    def validate_for_status(self, status: str) -> None:
        """Validation spécifique à un statut juridique via composition."""
        validator = StatusValidatorFactory.get_validator(status)
        validator.validate(self)
