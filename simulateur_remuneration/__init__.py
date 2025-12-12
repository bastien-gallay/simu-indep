"""
Simulateur de rémunération SASU vs EURL.

Ce package fournit les outils nécessaires pour simuler et comparer
les différents statuts juridiques d'entreprise en France.
"""

__version__ = "1.0.0"
__author__ = "Simulateur Team"

# Imports principaux pour faciliter l'utilisation du package
from .models.results import ComparisonResult, EURLResult, SASUResult
from .models.simulation import SimulationParameters

__all__ = [
    "SimulationParameters",
    "SASUResult",
    "EURLResult",
    "ComparisonResult",
]
