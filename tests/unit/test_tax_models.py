"""
Tests unitaires pour les modèles fiscaux.

Tests de validation des structures de données fiscales et des paramètres
de simulation avec leurs règles de validation métier.
"""

from decimal import Decimal

import pytest

from simulateur_remuneration.models.simulation import SimulationParameters
from simulateur_remuneration.models.tax_models import (
    FiscalConfiguration,
    TaxBracket,
    TaxRates,
    get_2024_tax_rates,
)


class TestTaxBracket:
    """Tests pour la classe TaxBracket."""

    def test_valid_tax_bracket_creation(self):
        """Test création d'une tranche fiscale valide."""
        bracket = TaxBracket(Decimal("11294"), Decimal("0.11"))
        assert bracket.threshold == Decimal("11294")
        assert bracket.rate == Decimal("0.11")

    def test_invalid_rate_too_high(self):
        """Test validation taux trop élevé."""
        with pytest.raises(ValueError, match="Le taux d'imposition doit être entre 0 et 1"):
            TaxBracket(Decimal("1000"), Decimal("1.5"))

    def test_invalid_rate_negative(self):
        """Test validation taux négatif."""
        with pytest.raises(ValueError, match="Le taux d'imposition doit être entre 0 et 1"):
            TaxBracket(Decimal("1000"), Decimal("-0.1"))

    def test_invalid_threshold_negative(self):
        """Test validation seuil négatif."""
        with pytest.raises(ValueError, match="Le seuil de la tranche doit être positif"):
            TaxBracket(Decimal("-1000"), Decimal("0.1"))


class TestTaxRates:
    """Tests pour la classe TaxRates."""

    def test_get_2024_tax_rates(self):
        """Test récupération des taux 2024."""
        rates = get_2024_tax_rates()
        assert rates.year == 2024
        assert len(rates.income_tax_brackets) == 5
        assert rates.corporate_tax_reduced_rate == Decimal("0.15")
        assert rates.corporate_tax_normal_rate == Decimal("0.25")
        assert rates.corporate_tax_threshold == Decimal("42500")

    def test_tax_rates_validation_invalid_year(self):
        """Test validation année invalide."""
        with pytest.raises(ValueError, match="Année fiscale invalide"):
            TaxRates(
                year=1990,
                income_tax_brackets=[TaxBracket(Decimal("1000"), Decimal("0.1"))],
                corporate_tax_reduced_rate=Decimal("0.15"),
                corporate_tax_normal_rate=Decimal("0.25"),
                corporate_tax_threshold=Decimal("42500"),
                flat_tax_rate=Decimal("0.30"),
                social_charges_rate=Decimal("0.172"),
                sasu_social_charges_rate=Decimal("0.82"),
                eurl_tns_social_charges_rate=Decimal("0.45"),
                eurl_dividend_social_charges_rate=Decimal("0.45"),
            )


class TestFiscalConfiguration:
    """Tests pour la classe FiscalConfiguration."""

    def test_fiscal_configuration_2024(self):
        """Test configuration fiscale 2024."""
        config = FiscalConfiguration.for_year(2024)
        assert config.year == 2024
        assert config.tax_rates.year == 2024

    def test_unsupported_year(self):
        """Test année non supportée."""
        with pytest.raises(
            ValueError, match="Les taux fiscaux pour l'année 2025 ne sont pas disponibles"
        ):
            FiscalConfiguration.for_year(2025)


class TestSimulationParameters:
    """Tests pour la classe SimulationParameters."""

    def test_valid_simulation_parameters(self):
        """Test création de paramètres valides."""
        params = SimulationParameters(
            annual_revenue=Decimal("100000"),
            operating_expenses=Decimal("10000"),
            target_net_salary=Decimal("4000"),
            distribute_dividends=True,
            tax_parts=Decimal("1.0"),
            use_progressive_tax=False,
        )
        assert params.gross_profit == Decimal("90000")
        assert params.annual_target_salary == Decimal("48000")

    def test_negative_revenue_validation(self):
        """Test validation CA négatif."""
        with pytest.raises(ValueError, match="Le chiffre d'affaires ne peut pas être négatif"):
            SimulationParameters(
                annual_revenue=Decimal("-1000"),
                operating_expenses=Decimal("10000"),
                target_net_salary=Decimal("4000"),
                distribute_dividends=True,
                tax_parts=Decimal("1.0"),
                use_progressive_tax=False,
            )

    def test_invalid_tax_parts(self):
        """Test validation parts fiscales invalides."""
        with pytest.raises(
            ValueError, match="Le nombre de parts fiscales doit être entre 0.5 et 6.0"
        ):
            SimulationParameters(
                annual_revenue=Decimal("100000"),
                operating_expenses=Decimal("10000"),
                target_net_salary=Decimal("4000"),
                distribute_dividends=True,
                tax_parts=Decimal("0.3"),  # Trop faible
                use_progressive_tax=False,
            )

    def test_salary_exceeds_revenue(self):
        """Test validation rémunération > CA."""
        with pytest.raises(ValueError, match="ne peut pas dépasser le chiffre d'affaires"):
            SimulationParameters(
                annual_revenue=Decimal("50000"),
                operating_expenses=Decimal("10000"),
                target_net_salary=Decimal("5000"),  # 60k annuel > 50k CA
                distribute_dividends=True,
                tax_parts=Decimal("1.0"),
                use_progressive_tax=False,
            )

    def test_validate_for_eurl_status(self):
        """Test validation spécifique EURL."""
        params = SimulationParameters(
            annual_revenue=Decimal("100000"),
            operating_expenses=Decimal("10000"),
            target_net_salary=Decimal("4000"),
            distribute_dividends=True,
            tax_parts=Decimal("1.0"),
            use_progressive_tax=False,
            share_capital=Decimal("50"),  # Capital trop faible
        )

        with pytest.raises(ValueError, match="Capital social trop faible pour EURL"):
            params.validate_for_status("EURL")

    def test_validate_for_sasu_status(self):
        """Test validation spécifique SASU."""
        params = SimulationParameters(
            annual_revenue=Decimal("100000"),
            operating_expenses=Decimal("10000"),
            target_net_salary=Decimal("4000"),
            distribute_dividends=True,
            tax_parts=Decimal("1.0"),
            use_progressive_tax=False,
        )

        # Ne doit pas lever d'exception
        params.validate_for_status("SASU")
