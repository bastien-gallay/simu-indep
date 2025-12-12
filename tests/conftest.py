"""Configuration et fixtures pytest pour les tests du simulateur de rémunération."""

import pytest
from decimal import Decimal
from typing import Dict, Any


@pytest.fixture
def sample_simulation_params() -> Dict[str, Any]:
    """Paramètres de simulation valides pour les tests."""
    return {
        "annual_revenue": Decimal("100000"),
        "operating_expenses": Decimal("10000"),
        "target_net_salary": Decimal("48000"),
        "distribute_dividends": True,
        "tax_parts": Decimal("1.0"),
        "use_progressive_tax": False,
        "share_capital": Decimal("1000"),
    }


@pytest.fixture
def sample_tax_rates_2024() -> Dict[str, Any]:
    """Taux fiscaux 2024 pour les tests."""
    return {
        "year": 2024,
        "income_tax_brackets": [
            {"threshold": Decimal("11294"), "rate": Decimal("0.00")},
            {"threshold": Decimal("28797"), "rate": Decimal("0.11")},
            {"threshold": Decimal("82341"), "rate": Decimal("0.30")},
            {"threshold": Decimal("177106"), "rate": Decimal("0.41")},
            {"threshold": Decimal("inf"), "rate": Decimal("0.45")},
        ],
        "corporate_tax_reduced_rate": Decimal("0.15"),
        "corporate_tax_normal_rate": Decimal("0.25"),
        "corporate_tax_threshold": Decimal("42500"),
        "flat_tax_rate": Decimal("0.30"),
        "social_charges_sasu": Decimal("0.82"),
        "social_charges_eurl_tns": Decimal("0.45"),
        "social_charges_eurl_dividends": Decimal("0.172"),
    }


@pytest.fixture
def low_revenue_params() -> Dict[str, Any]:
    """Paramètres pour revenus faibles."""
    return {
        "annual_revenue": Decimal("30000"),
        "operating_expenses": Decimal("5000"),
        "target_net_salary": Decimal("20000"),
        "distribute_dividends": False,
        "tax_parts": Decimal("1.0"),
        "use_progressive_tax": True,
        "share_capital": Decimal("1000"),
    }


@pytest.fixture
def high_revenue_params() -> Dict[str, Any]:
    """Paramètres pour revenus élevés."""
    return {
        "annual_revenue": Decimal("200000"),
        "operating_expenses": Decimal("20000"),
        "target_net_salary": Decimal("60000"),
        "distribute_dividends": True,
        "tax_parts": Decimal("2.0"),
        "use_progressive_tax": False,
        "share_capital": Decimal("10000"),
    }


@pytest.fixture
def edge_case_params() -> Dict[str, Any]:
    """Paramètres pour cas limites."""
    return {
        "annual_revenue": Decimal("0"),
        "operating_expenses": Decimal("0"),
        "target_net_salary": Decimal("0"),
        "distribute_dividends": False,
        "tax_parts": Decimal("1.0"),
        "use_progressive_tax": True,
        "share_capital": Decimal("1"),
    }