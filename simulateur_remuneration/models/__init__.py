"""
Modèles de données pour le simulateur de rémunération.

Ce module contient les structures de données typées utilisées
pour représenter les paramètres de simulation et les résultats.
"""

from .simulation import SimulationParameters
from .tax_models import FiscalConfiguration, TaxBracket, TaxRates

__all__ = [
    # Tax models
    "TaxBracket",
    "TaxRates",
    "FiscalConfiguration",
    # Simulation parameters
    "SimulationParameters",
]
