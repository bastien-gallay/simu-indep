"""
Modèles de données fiscales pour le simulateur de rémunération.

Ce module contient les structures de données typées pour représenter
les taux fiscaux, tranches d'imposition et configurations fiscales
utilisées dans les calculs de simulation.

Sources officielles:
- Code général des impôts (CGI)
- Service-public.fr
- URSSAF.fr
- Impots.gouv.fr
"""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class TaxBracket:
    """
    Tranche d'imposition avec seuil et taux.

    Représente une tranche du barème progressif de l'impôt sur le revenu
    ou d'autres impôts progressifs.

    Args:
        threshold: Seuil supérieur de la tranche en euros
        rate: Taux d'imposition de la tranche (entre 0 et 1)

    Raises:
        ValueError: Si le taux n'est pas entre 0 et 1, ou si le seuil est négatif

    Example:
        >>> bracket = TaxBracket(Decimal('11294'), Decimal('0.00'))
        >>> bracket.threshold
        Decimal('11294')
        >>> bracket.rate
        Decimal('0.00')
    """

    threshold: Decimal
    rate: Decimal

    def __post_init__(self) -> None:
        """Validation composable des paramètres de la tranche fiscale."""
        from .validators import MonetaryValueValidator, RateValidator

        RateValidator("Le taux d'imposition", max_rate=Decimal("1")).validate(self.rate)
        MonetaryValueValidator("Le seuil de la tranche").validate(self.threshold)


@dataclass(frozen=True)
class TaxRates:
    """
    Taux fiscaux officiels pour une année donnée.

    Contient tous les taux et seuils fiscaux nécessaires aux calculs
    de simulation SASU/EURL selon la législation française.

    Sources:
    - Barème IR 2024: https://www.impots.gouv.fr/particulier/bareme-de-limpot-sur-le-revenu
    - IS 2024: Article 219 du CGI
    - Charges sociales: URSSAF.fr
    - Flat tax: Article 200 A du CGI

    Args:
        year: Année fiscale de référence
        income_tax_brackets: Tranches du barème progressif IR
        corporate_tax_reduced_rate: Taux réduit IS (15% jusqu'à 42 500€)
        corporate_tax_normal_rate: Taux normal IS (25% au-delà)
        corporate_tax_threshold: Seuil d'application du taux réduit IS
        flat_tax_rate: Taux de la flat tax sur dividendes (30%)
        social_charges_rate: Taux des prélèvements sociaux (17.2%)
        sasu_social_charges_rate: Taux charges sociales SASU sur net (82%)
        eurl_tns_social_charges_rate: Taux charges TNS EURL (45%)
        eurl_dividend_social_charges_rate: Taux charges dividendes EURL (45%)

    Raises:
        ValueError: Si les taux ne sont pas dans les bornes valides
    """

    year: int
    income_tax_brackets: list[TaxBracket]
    corporate_tax_reduced_rate: Decimal
    corporate_tax_normal_rate: Decimal
    corporate_tax_threshold: Decimal
    flat_tax_rate: Decimal
    social_charges_rate: Decimal
    sasu_social_charges_rate: Decimal
    eurl_tns_social_charges_rate: Decimal
    eurl_dividend_social_charges_rate: Decimal

    def __post_init__(self) -> None:
        """Validation composable des taux fiscaux."""
        self._validate_year()
        self._validate_rates()
        self._validate_corporate_tax_threshold()
        self._validate_income_tax_brackets()

    def _validate_year(self) -> None:
        """Valide l'année fiscale."""
        if self.year < 2020 or self.year > 2030:
            raise ValueError(f"Année fiscale invalide: {self.year}")

    def _validate_rates(self) -> None:
        """Valide tous les taux fiscaux."""
        from .validators import RateValidator

        rate_validator = RateValidator("Taux fiscal")
        rates_to_validate = [
            ("corporate_tax_reduced_rate", self.corporate_tax_reduced_rate),
            ("corporate_tax_normal_rate", self.corporate_tax_normal_rate),
            ("flat_tax_rate", self.flat_tax_rate),
            ("social_charges_rate", self.social_charges_rate),
            ("sasu_social_charges_rate", self.sasu_social_charges_rate),
            ("eurl_tns_social_charges_rate", self.eurl_tns_social_charges_rate),
            ("eurl_dividend_social_charges_rate", self.eurl_dividend_social_charges_rate),
        ]

        for rate_name, rate_value in rates_to_validate:
            try:
                rate_validator.validate(rate_value)
            except ValueError as e:
                raise ValueError(f"{rate_name} doit être entre 0 et 2, reçu: {rate_value}") from e

    def _validate_corporate_tax_threshold(self) -> None:
        """Valide le seuil IS."""
        from .validators import MonetaryValueValidator

        MonetaryValueValidator("Le seuil IS", allow_zero=False).validate(
            self.corporate_tax_threshold
        )

    def _validate_income_tax_brackets(self) -> None:
        """Valide les tranches IR."""
        if not self.income_tax_brackets:
            raise ValueError("Au moins une tranche IR doit être définie")

        for i in range(1, len(self.income_tax_brackets)):
            if self.income_tax_brackets[i].threshold <= self.income_tax_brackets[i - 1].threshold:
                raise ValueError("Les tranches IR doivent être ordonnées par seuil croissant")


@dataclass(frozen=True)
class FiscalConfiguration:
    """
    Configuration fiscale complète pour une année donnée.

    Encapsule les taux fiscaux et fournit des méthodes de factory
    pour obtenir la configuration d'une année spécifique.

    Args:
        year: Année fiscale
        tax_rates: Taux fiscaux pour cette année

    Example:
        >>> config = FiscalConfiguration.for_year(2024)
        >>> config.year
        2024
        >>> len(config.tax_rates.income_tax_brackets)
        5
    """

    year: int = 2024
    tax_rates: TaxRates = field(default_factory=lambda: get_2024_tax_rates())

    @classmethod
    def for_year(cls, year: int) -> "FiscalConfiguration":
        """
        Factory method pour obtenir la configuration fiscale d'une année.

        Args:
            year: Année fiscale souhaitée

        Returns:
            Configuration fiscale pour l'année demandée

        Raises:
            ValueError: Si l'année n'est pas supportée
        """
        if year == 2024:
            return cls(year=year, tax_rates=get_2024_tax_rates())
        else:
            raise ValueError(
                f"Les taux fiscaux pour l'année {year} ne sont pas disponibles. "
                f"Années supportées: 2024"
            )


def get_2024_tax_rates() -> TaxRates:
    """
    Retourne les taux fiscaux officiels pour l'année 2024.

    Sources officielles:
    - Barème IR 2024 (revenus 2023):
      https://www.impots.gouv.fr/particulier/bareme-de-limpot-sur-le-revenu
    - IS 2024: Article 219 du Code général des impôts
    - Charges sociales SASU: Environ 82% selon URSSAF
    - Charges TNS EURL: Environ 45% selon URSSAF
    - Flat tax: Article 200 A du CGI (12.8% IR + 17.2% PS = 30%)
    - Prélèvements sociaux: 17.2% (CSG 9.2% + CRDS 0.5% + autres 7.5%)

    Returns:
        TaxRates: Configuration complète des taux 2024

    Note:
        Les taux de charges sociales sont des moyennes indicatives.
        Les taux réels peuvent varier selon la situation spécifique
        de l'entreprise et du dirigeant.
    """
    return TaxRates(
        year=2024,
        # Barème IR 2024 (revenus 2023)
        # Source: https://www.impots.gouv.fr/particulier/bareme-de-limpot-sur-le-revenu
        income_tax_brackets=[
            TaxBracket(Decimal("11294"), Decimal("0.00")),  # 0% jusqu'à 11 294€
            TaxBracket(Decimal("28797"), Decimal("0.11")),  # 11% de 11 294€ à 28 797€
            TaxBracket(Decimal("82341"), Decimal("0.30")),  # 30% de 28 797€ à 82 341€
            TaxBracket(Decimal("177106"), Decimal("0.41")),  # 41% de 82 341€ à 177 106€
            TaxBracket(Decimal("inf"), Decimal("0.45")),  # 45% au-delà de 177 106€
        ],
        # Impôt sur les Sociétés 2024
        # Source: Article 219 du CGI
        corporate_tax_reduced_rate=Decimal("0.15"),  # 15% jusqu'à 42 500€
        corporate_tax_normal_rate=Decimal("0.25"),  # 25% au-delà
        corporate_tax_threshold=Decimal("42500"),  # Seuil d'application taux réduit
        # Flat tax sur dividendes (PFU)
        # Source: Article 200 A du CGI
        flat_tax_rate=Decimal("0.30"),  # 12.8% IR + 17.2% PS = 30%
        # Prélèvements sociaux sur dividendes
        # Source: Articles L136-1 et suivants du CSS
        social_charges_rate=Decimal("0.172"),  # CSG + CRDS + autres = 17.2%
        # Charges sociales SASU (assimilé salarié)
        # Source: Taux moyens URSSAF pour cadre
        # Charges patronales + salariales ≈ 82% du net
        sasu_social_charges_rate=Decimal("0.82"),
        # Charges sociales EURL TNS
        # Source: Taux moyens cotisations TNS
        eurl_tns_social_charges_rate=Decimal("0.45"),
        # Charges sociales sur dividendes EURL (au-delà de 10% du capital)
        # Source: Article L131-6 du CSS
        eurl_dividend_social_charges_rate=Decimal("0.45"),
    )
