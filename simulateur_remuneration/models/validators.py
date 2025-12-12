"""
Validateurs composables pour les modèles de données.

Ce module contient des validateurs réutilisables qui suivent les principes
CUPID et permettent une validation composable et explicite.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .simulation import SimulationParameters


class Validator(Protocol):
    """Interface pour les validateurs."""

    def validate(self, value: object) -> None:
        """
        Valide une valeur.

        Args:
            value: Valeur à valider

        Raises:
            ValueError: Si la validation échoue
        """
        ...


class MonetaryValueValidator:
    """Validateur pour les valeurs monétaires."""

    def __init__(self, field_name: str, allow_zero: bool = True) -> None:
        self.field_name = field_name
        self.allow_zero = allow_zero

    def validate(self, value: Decimal) -> None:
        """Valide qu'une valeur monétaire est positive ou nulle."""
        if value < 0:
            raise ValueError(f"{self.field_name} ne peut pas être négatif: {value}€")
        if not self.allow_zero and value == 0:
            raise ValueError(f"{self.field_name} doit être strictement positif: {value}€")


class RateValidator:
    """Validateur pour les taux (pourcentages)."""

    def __init__(
        self, field_name: str, min_rate: Decimal = Decimal("0"), max_rate: Decimal = Decimal("2")
    ) -> None:
        self.field_name = field_name
        self.min_rate = min_rate
        self.max_rate = max_rate

    def validate(self, value: Decimal) -> None:
        """Valide qu'un taux est dans les bornes acceptables."""
        if value < self.min_rate or value > self.max_rate:
            raise ValueError(
                f"{self.field_name} doit être entre {self.min_rate} et {self.max_rate}, reçu: {value}"
            )


class TaxPartsValidator:
    """Validateur pour les parts fiscales françaises."""

    def validate(self, value: Decimal) -> None:
        """Valide le nombre de parts fiscales selon la législation française."""
        if value < Decimal("0.5") or value > Decimal("6.0"):
            raise ValueError(f"Le nombre de parts fiscales doit être entre 0.5 et 6.0: {value}")


class BusinessLogicValidator:
    """Validateur pour les règles métier complexes."""

    @staticmethod
    def validate_revenue_expenses_coherence(revenue: Decimal, expenses: Decimal) -> None:
        """Valide la cohérence entre CA et charges."""
        if expenses > revenue:
            raise ValueError(
                f"Les charges d'exploitation ({expenses}€) "
                f"ne peuvent pas dépasser le chiffre d'affaires ({revenue}€)"
            )

    @staticmethod
    def validate_salary_revenue_coherence(annual_salary: Decimal, revenue: Decimal) -> None:
        """Valide la cohérence entre rémunération et CA."""
        if annual_salary > revenue:
            raise ValueError(
                f"La rémunération annuelle cible ({annual_salary}€) "
                f"ne peut pas dépasser le chiffre d'affaires ({revenue}€)"
            )

    @staticmethod
    def validate_dividend_feasibility(
        revenue: Decimal, expenses: Decimal, annual_salary: Decimal, distribute_dividends: bool
    ) -> None:
        """Valide la faisabilité de distribution de dividendes."""
        if not distribute_dividends:
            return

        estimated_salary_cost = annual_salary * Decimal("1.5")
        remaining_profit = revenue - expenses - estimated_salary_cost

        if remaining_profit < 0:
            raise ValueError(
                "Impossible de distribuer des dividendes: "
                f"bénéfice estimé négatif après rémunération ({remaining_profit:.0f}€). "
                "Réduisez la rémunération cible ou désactivez la distribution de dividendes."
            )


class StatusSpecificValidator(ABC):
    """Validateur abstrait pour les validations spécifiques à un statut."""

    @abstractmethod
    def validate(self, params: SimulationParameters) -> None:
        """Valide les paramètres pour un statut spécifique."""
        ...


class SASUValidator(StatusSpecificValidator):
    """Validateur spécifique au statut SASU."""

    def validate(self, params: SimulationParameters) -> None:
        """Valide les paramètres pour SASU (pas de contraintes spécifiques)."""
        pass


class EURLValidator(StatusSpecificValidator):
    """Validateur spécifique au statut EURL."""

    def __init__(self, min_capital: Decimal = Decimal("100")) -> None:
        self.min_capital = min_capital

    def validate(self, params: SimulationParameters) -> None:
        """Valide les paramètres pour EURL."""
        if params.share_capital < self.min_capital:
            raise ValueError(
                f"Capital social trop faible pour EURL: {params.share_capital}€. "
                f"Minimum recommandé: {self.min_capital}€"
            )


class StatusValidatorFactory:
    """Factory pour créer les validateurs spécifiques aux statuts."""

    _validators = {"SASU": SASUValidator(), "EURL": EURLValidator()}

    @classmethod
    def get_validator(cls, status: str) -> StatusSpecificValidator:
        """Retourne le validateur approprié pour un statut."""
        if status not in cls._validators:
            raise ValueError(f"Statut invalide: {status}. Attendu: SASU ou EURL")
        return cls._validators[status]
