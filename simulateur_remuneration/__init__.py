"""
Simulateur de rémunération SASU vs EURL.

Ce package fournit les outils nécessaires pour simuler et comparer
les différents statuts juridiques d'entreprise en France.
"""

__version__ = "1.0.0"
__author__ = "Simulateur Team"

# Imports principaux pour faciliter l'utilisation du package
from .models.simulation import SimulationParameters
from .models.tax_models import FiscalConfiguration, TaxBracket, TaxRates

__all__ = [
    "SimulationParameters",
    "TaxBracket",
    "TaxRates",
    "FiscalConfiguration",
]
