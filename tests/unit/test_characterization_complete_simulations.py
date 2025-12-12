"""
Tests de caractérisation des simulations complètes.

Ces tests capturent le comportement actuel des fonctions simuler_sasu et simuler_eurl
avec des paramètres variés pour servir de référence lors de la refactorisation.

**Feature: code-quality-integration, Property 1: Behavioral Equivalence**
**Validates: Requirements 1.3**
"""

import pytest

# Import des fonctions existantes à tester
from app import ResultatSimulation, simuler_eurl, simuler_sasu


class TestCharacterizationSASUCompleteSimulations:
    """Tests de caractérisation complets pour simuler_sasu avec paramètres variés."""

    def test_sasu_low_revenue_scenario(self):
        """Test SASU avec revenus faibles."""
        result = simuler_sasu(
            ca_ht=30000,
            charges_exploitation=5000,
            remuneration_nette_cible=20000,
            distribuer_dividendes=False,
            parts_fiscales=1.0,
            option_bareme_ir=True,
        )

        # Validation de tous les champs ResultatSimulation
        assert isinstance(result, ResultatSimulation)
        assert result.statut == "SASU"
        assert result.ca_ht == 30000
        assert result.charges_exploitation == 5000
        assert result.benefice_avant_remuneration == 25000

        # Rémunération limitée par le bénéfice disponible
        assert result.remuneration_nette <= 20000
        assert result.charges_sociales > 0
        assert result.remuneration_brute > result.remuneration_nette

        # Pas de dividendes demandés
        assert result.dividendes_bruts == 0
        assert result.dividendes_nets == 0
        assert result.impot_dividendes == 0
        assert result.charges_dividendes == 0

        # Cohérence des calculs
        assert result.benefice_apres_remuneration >= 0
        assert result.is_societe >= 0
        assert result.resultat_net_societe >= 0
        assert result.revenu_imposable_ir >= 0
        assert result.ir_total >= 0
        assert result.net_disponible >= 0
        assert 0 <= result.taux_prelevement_global <= 1

    def test_sasu_medium_revenue_with_dividends(self):
        """Test SASU avec revenus moyens - rémunération consomme tout le bénéfice."""
        result = simuler_sasu(
            ca_ht=80000,
            charges_exploitation=15000,
            remuneration_nette_cible=36000,
            distribuer_dividendes=True,
            parts_fiscales=1.5,
            option_bareme_ir=False,
        )

        # Validation complète des champs
        assert result.statut == "SASU"
        assert result.ca_ht == 80000
        assert result.charges_exploitation == 15000
        assert result.benefice_avant_remuneration == 65000

        # Rémunération limitée par le bénéfice disponible
        # Coût total = 65000, donc net = 65000 / (1 + 0.82) ≈ 35714
        expected_net = 65000 / (1 + 0.82)
        assert abs(result.remuneration_nette - expected_net) < 1
        assert result.charges_sociales == pytest.approx(result.remuneration_nette * 0.82, rel=0.01)

        # Pas de dividendes car tout le bénéfice est consommé par la rémunération
        assert result.dividendes_bruts == 0
        assert result.dividendes_nets == 0
        assert result.impot_dividendes == 0
        assert result.charges_dividendes == 0  # Pas de charges sociales sur dividendes SASU
        assert result.benefice_apres_remuneration == 0  # Tout consommé

        # Cohérence globale
        assert result.net_disponible > 0
        assert result.taux_prelevement_global > 0

    def test_sasu_with_actual_dividends(self):
        """Test SASU avec dividendes réels (salaire plus faible)."""
        result = simuler_sasu(
            ca_ht=100000,
            charges_exploitation=15000,
            remuneration_nette_cible=30000,  # Salaire plus faible pour laisser place aux dividendes
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            option_bareme_ir=False,
        )

        # Validation des champs
        assert result.statut == "SASU"
        assert result.ca_ht == 100000
        assert result.benefice_avant_remuneration == 85000

        # Rémunération proche de la cible
        assert abs(result.remuneration_nette - 30000) < 100
        assert result.charges_sociales == pytest.approx(30000 * 0.82, rel=0.01)

        # Dividendes distribués
        assert result.dividendes_bruts > 0
        assert result.dividendes_nets > 0
        assert result.impot_dividendes > 0
        assert result.charges_dividendes == 0  # Pas de charges sociales sur dividendes SASU

        # Flat tax appliquée (30%)
        assert result.impot_dividendes == pytest.approx(result.dividendes_bruts * 0.30, rel=0.01)

        # Cohérence
        assert result.net_disponible > 0
        assert result.taux_prelevement_global > 0

    def test_sasu_high_revenue_progressive_tax(self):
        """Test SASU avec revenus élevés et option barème progressif."""
        result = simuler_sasu(
            ca_ht=150000,
            charges_exploitation=25000,
            remuneration_nette_cible=60000,
            distribuer_dividendes=True,
            parts_fiscales=2.0,
            option_bareme_ir=True,
        )

        # Validation des champs
        assert result.statut == "SASU"
        assert result.ca_ht == 150000
        assert result.charges_exploitation == 25000
        assert result.benefice_avant_remuneration == 125000

        # Rémunération élevée
        assert abs(result.remuneration_nette - 60000) < 100
        assert result.charges_sociales > 40000  # ~82% de 60k

        # Dividendes avec barème progressif
        assert result.dividendes_bruts > 0
        assert result.dividendes_nets > 0
        # Avec barème progressif: prélèvements sociaux uniquement sur dividendes
        assert result.impot_dividendes == pytest.approx(result.dividendes_bruts * 0.172, rel=0.01)

        # IR élevé avec 2 parts fiscales
        assert result.ir_total > 0
        assert (
            result.revenu_imposable_ir > result.remuneration_nette
        )  # Inclut dividendes imposables

        # Cohérence
        assert result.net_disponible > 0
        assert result.taux_prelevement_global > 0

    def test_sasu_salary_exceeds_profit(self):
        """Test SASU où la rémunération cible dépasse le bénéfice disponible."""
        result = simuler_sasu(
            ca_ht=50000,
            charges_exploitation=10000,
            remuneration_nette_cible=35000,  # Très élevée
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            option_bareme_ir=False,
        )

        # Rémunération limitée par le bénéfice
        benefice_disponible = 40000
        cout_max = benefice_disponible / (1 + 0.82)  # Coût total limité
        assert result.remuneration_nette < 35000
        assert result.remuneration_nette <= cout_max

        # Pas de dividendes car tout consommé en salaire
        assert result.dividendes_bruts == 0
        assert result.dividendes_nets == 0
        assert result.benefice_apres_remuneration <= 1  # Proche de 0

        # Cohérence
        assert result.net_disponible >= 0
        assert result.is_societe >= 0

    def test_sasu_zero_salary_only_dividends(self):
        """Test SASU avec salaire nul, uniquement dividendes."""
        result = simuler_sasu(
            ca_ht=70000,
            charges_exploitation=20000,
            remuneration_nette_cible=0,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            option_bareme_ir=False,
        )

        # Pas de rémunération
        assert result.remuneration_nette == 0
        assert result.charges_sociales == 0
        assert result.remuneration_brute == 0

        # Tout en dividendes
        assert result.benefice_apres_remuneration == 50000
        assert result.dividendes_bruts > 0
        assert result.impot_dividendes > 0

        # IR uniquement sur dividendes (si barème progressif)
        assert result.revenu_imposable_ir >= 0
        assert result.net_disponible > 0


class TestCharacterizationEURLCompleteSimulations:
    """Tests de caractérisation complets pour simuler_eurl avec différents capitaux sociaux."""

    def test_eurl_low_capital_high_dividend_charges(self):
        """Test EURL avec capital faible (charges dividendes importantes)."""
        result = simuler_eurl(
            ca_ht=90000,
            charges_exploitation=15000,
            remuneration_nette_cible=40000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            capital_social=500,  # Capital faible, seuil à 50€
            option_bareme_ir=False,
        )

        # Validation des champs
        assert result.statut == "EURL"
        assert result.ca_ht == 90000
        assert result.charges_exploitation == 15000
        assert result.benefice_avant_remuneration == 75000

        # Rémunération TNS (45% de charges)
        assert abs(result.remuneration_nette - 40000) < 100
        assert result.charges_sociales == pytest.approx(result.remuneration_nette * 0.45, rel=0.01)

        # Dividendes avec charges sociales importantes (capital faible)
        seuil_10_pourcent = 500 * 0.10  # 50€
        if result.dividendes_bruts > seuil_10_pourcent:
            dividendes_soumis = result.dividendes_bruts - seuil_10_pourcent
            charges_attendues = dividendes_soumis * 0.45
            assert result.charges_dividendes == pytest.approx(charges_attendues, rel=0.01)

        # Flat tax sur dividendes après charges
        dividendes_apres_charges = result.dividendes_bruts - result.charges_dividendes
        assert result.impot_dividendes == pytest.approx(dividendes_apres_charges * 0.30, rel=0.01)

        # Cohérence
        assert result.net_disponible > 0
        assert result.taux_prelevement_global > 0

    def test_eurl_high_capital_low_dividend_charges(self):
        """Test EURL avec capital élevé (charges dividendes réduites)."""
        result = simuler_eurl(
            ca_ht=120000,
            charges_exploitation=20000,
            remuneration_nette_cible=50000,
            distribuer_dividendes=True,
            parts_fiscales=2.0,
            capital_social=50000,  # Capital élevé, seuil à 5000€
            option_bareme_ir=True,
        )

        # Validation des champs
        assert result.statut == "EURL"
        assert result.ca_ht == 120000
        assert result.charges_exploitation == 20000

        # Rémunération TNS
        assert abs(result.remuneration_nette - 50000) < 100
        assert result.charges_sociales == pytest.approx(50000 * 0.45, rel=0.01)

        # Dividendes avec seuil élevé (moins de charges sociales)
        seuil_10_pourcent = 50000 * 0.10  # 5000€
        if result.dividendes_bruts <= seuil_10_pourcent:
            assert result.charges_dividendes == 0
        else:
            dividendes_soumis = result.dividendes_bruts - seuil_10_pourcent
            charges_attendues = dividendes_soumis * 0.45
            assert result.charges_dividendes == pytest.approx(charges_attendues, rel=0.01)

        # Barème progressif avec abattement 40%
        dividendes_apres_charges = result.dividendes_bruts - result.charges_dividendes
        assert result.impot_dividendes == pytest.approx(dividendes_apres_charges * 0.172, rel=0.01)

        # IR avec quotient familial (2 parts)
        assert result.ir_total >= 0
        assert result.net_disponible > 0

    def test_eurl_medium_capital_mixed_scenario(self):
        """Test EURL avec capital moyen, scénario mixte."""
        result = simuler_eurl(
            ca_ht=100000,
            charges_exploitation=18000,
            remuneration_nette_cible=42000,
            distribuer_dividendes=True,
            parts_fiscales=1.5,
            capital_social=10000,  # Capital moyen, seuil à 1000€
            option_bareme_ir=False,
        )

        # Validation complète
        assert result.statut == "EURL"
        assert result.ca_ht == 100000
        assert result.charges_exploitation == 18000
        assert result.benefice_avant_remuneration == 82000

        # Calculs de rémunération
        assert abs(result.remuneration_nette - 42000) < 100
        assert result.charges_sociales > 0

        # Dividendes avec seuil moyen
        seuil_10_pourcent = 1000  # 10% de 10000€
        assert result.dividendes_bruts > 0

        if result.dividendes_bruts > seuil_10_pourcent:
            assert result.charges_dividendes > 0

        # Flat tax
        dividendes_apres_charges = result.dividendes_bruts - result.charges_dividendes
        assert result.impot_dividendes == pytest.approx(dividendes_apres_charges * 0.30, rel=0.01)

        # Cohérence globale
        assert result.net_disponible > 0
        assert 0 < result.taux_prelevement_global < 1

    def test_eurl_no_dividends_scenario(self):
        """Test EURL sans distribution de dividendes."""
        result = simuler_eurl(
            ca_ht=75000,
            charges_exploitation=12000,
            remuneration_nette_cible=45000,
            distribuer_dividendes=False,
            parts_fiscales=1.0,
            capital_social=5000,
            option_bareme_ir=True,
        )

        # Pas de dividendes
        assert result.dividendes_bruts == 0
        assert result.dividendes_nets == 0
        assert result.impot_dividendes == 0
        assert result.charges_dividendes == 0

        # Rémunération limitée par le bénéfice disponible
        # Coût total = 63000, donc net = 63000 / (1 + 0.45) ≈ 43448
        expected_net = 63000 / (1 + 0.45)
        assert abs(result.remuneration_nette - expected_net) < 1
        assert result.charges_sociales > 0

        # Pas de résultat société car tout consommé en rémunération
        assert result.resultat_net_societe == 0  # Tout consommé en rémunération
        assert result.is_societe == 0  # Pas d'IS car pas de bénéfice restant
        assert result.benefice_apres_remuneration == 0  # Tout consommé

        # Net disponible = rémunération nette - IR
        assert result.net_disponible == pytest.approx(
            result.remuneration_nette - result.ir_total, rel=0.01
        )

    def test_eurl_extreme_capital_values(self):
        """Test EURL avec valeurs extrêmes de capital."""
        # Capital minimal (1€)
        result_min = simuler_eurl(
            ca_ht=60000,
            charges_exploitation=10000,
            remuneration_nette_cible=30000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            capital_social=1,  # Capital minimal
            option_bareme_ir=False,
        )

        # Presque tous les dividendes soumis aux charges (seuil = 0.1€)
        if result_min.dividendes_bruts > 0.1:
            charges_attendues = (result_min.dividendes_bruts - 0.1) * 0.45
            assert result_min.charges_dividendes == pytest.approx(charges_attendues, rel=0.01)

        # Capital très élevé (100000€)
        result_max = simuler_eurl(
            ca_ht=60000,
            charges_exploitation=10000,
            remuneration_nette_cible=30000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            capital_social=100000,  # Capital très élevé
            option_bareme_ir=False,
        )

        # Seuil très élevé (10000€), probablement pas de charges sur dividendes
        seuil_max = 100000 * 0.10  # 10000€
        if result_max.dividendes_bruts <= seuil_max:
            assert result_max.charges_dividendes == 0

        # Comparaison: capital minimal devrait avoir plus de charges
        assert result_min.charges_dividendes >= result_max.charges_dividendes


class TestCharacterizationSASUvsEURLComparison:
    """Tests de caractérisation comparatifs SASU vs EURL."""

    def test_identical_parameters_comparison(self):
        """Test comparatif avec paramètres identiques."""
        params = {
            "ca_ht": 85000,
            "charges_exploitation": 15000,
            "remuneration_nette_cible": 40000,
            "distribuer_dividendes": True,
            "parts_fiscales": 1.0,
            "option_bareme_ir": False,
        }

        result_sasu = simuler_sasu(**params)
        result_eurl = simuler_eurl(**params, capital_social=5000)

        # Vérifications de cohérence
        assert result_sasu.ca_ht == result_eurl.ca_ht
        assert result_sasu.charges_exploitation == result_eurl.charges_exploitation
        assert result_sasu.benefice_avant_remuneration == result_eurl.benefice_avant_remuneration

        # Différences attendues
        # SASU: charges sociales plus élevées (82% vs 45%)
        assert result_sasu.charges_sociales > result_eurl.charges_sociales

        # EURL: peut avoir charges sociales sur dividendes
        assert result_sasu.charges_dividendes == 0  # Toujours 0 en SASU
        assert result_eurl.charges_dividendes >= 0  # Peut être > 0 en EURL

        # Les deux doivent avoir des résultats cohérents
        assert result_sasu.net_disponible > 0
        assert result_eurl.net_disponible > 0
        assert result_sasu.taux_prelevement_global > 0
        assert result_eurl.taux_prelevement_global > 0

    def test_high_revenue_comparison(self):
        """Test comparatif avec revenus élevés."""
        params = {
            "ca_ht": 200000,
            "charges_exploitation": 30000,
            "remuneration_nette_cible": 70000,
            "distribuer_dividendes": True,
            "parts_fiscales": 2.5,
            "option_bareme_ir": True,
        }

        result_sasu = simuler_sasu(**params)
        result_eurl = simuler_eurl(**params, capital_social=20000)

        # Validation des calculs complexes
        assert result_sasu.benefice_avant_remuneration == 170000
        assert result_eurl.benefice_avant_remuneration == 170000

        # Rémunérations proches
        assert abs(result_sasu.remuneration_nette - result_eurl.remuneration_nette) < 1000

        # Charges sociales différentes
        charges_sasu_attendues = result_sasu.remuneration_nette * 0.82
        charges_eurl_attendues = result_eurl.remuneration_nette * 0.45
        assert result_sasu.charges_sociales == pytest.approx(charges_sasu_attendues, rel=0.01)
        assert result_eurl.charges_sociales == pytest.approx(charges_eurl_attendues, rel=0.01)

        # Dividendes et charges
        assert result_sasu.dividendes_bruts > 0
        assert result_eurl.dividendes_bruts > 0
        assert result_sasu.charges_dividendes == 0
        # EURL peut avoir charges dividendes selon le capital

        # IR avec barème progressif et 2.5 parts
        assert result_sasu.ir_total >= 0
        assert result_eurl.ir_total >= 0

        # Net disponible positif pour les deux
        assert result_sasu.net_disponible > 0
        assert result_eurl.net_disponible > 0


class TestCharacterizationEdgeCasesComplete:
    """Tests de caractérisation pour cas limites complets."""

    def test_zero_profit_scenario(self):
        """Test avec bénéfice nul (charges = CA)."""
        result_sasu = simuler_sasu(
            ca_ht=40000,
            charges_exploitation=40000,
            remuneration_nette_cible=10000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            option_bareme_ir=False,
        )

        result_eurl = simuler_eurl(
            ca_ht=40000,
            charges_exploitation=40000,
            remuneration_nette_cible=10000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            capital_social=1000,
            option_bareme_ir=False,
        )

        # Bénéfice nul
        assert result_sasu.benefice_avant_remuneration == 0
        assert result_eurl.benefice_avant_remuneration == 0

        # Pas de rémunération possible
        assert result_sasu.remuneration_nette == 0
        assert result_eurl.remuneration_nette == 0
        assert result_sasu.charges_sociales == 0
        assert result_eurl.charges_sociales == 0

        # Pas de dividendes
        assert result_sasu.dividendes_bruts == 0
        assert result_eurl.dividendes_bruts == 0

        # Net disponible nul
        assert result_sasu.net_disponible == 0
        assert result_eurl.net_disponible == 0

        # Taux de prélèvement nul (division par CA > 0)
        assert result_sasu.taux_prelevement_global == 0
        assert result_eurl.taux_prelevement_global == 0

    def test_maximum_tax_parts_scenario(self):
        """Test avec nombre maximum de parts fiscales."""
        result_sasu = simuler_sasu(
            ca_ht=180000,
            charges_exploitation=30000,
            remuneration_nette_cible=80000,
            distribuer_dividendes=True,
            parts_fiscales=4.0,  # Famille nombreuse
            option_bareme_ir=True,
        )

        result_eurl = simuler_eurl(
            ca_ht=180000,
            charges_exploitation=30000,
            remuneration_nette_cible=80000,
            distribuer_dividendes=True,
            parts_fiscales=4.0,
            capital_social=15000,
            option_bareme_ir=True,
        )

        # Avec 4 parts, l'IR devrait être significativement réduit
        assert result_sasu.ir_total >= 0
        assert result_eurl.ir_total >= 0

        # Validation de la cohérence avec quotient familial
        assert result_sasu.revenu_imposable_ir > 0
        assert result_eurl.revenu_imposable_ir > 0

        # Net disponible élevé grâce aux parts fiscales
        assert result_sasu.net_disponible > 0
        assert result_eurl.net_disponible > 0


# Données de référence pour validation future des simulations complètes
REFERENCE_COMPLETE_SIMULATIONS = {
    "sasu_standard": {
        "params": {
            "ca_ht": 100000,
            "charges_exploitation": 15000,
            "remuneration_nette_cible": 45000,
            "distribuer_dividendes": True,
            "parts_fiscales": 1.0,
            "option_bareme_ir": False,
        },
        "expected_fields": [
            "statut",
            "ca_ht",
            "charges_exploitation",
            "benefice_avant_remuneration",
            "remuneration_brute",
            "charges_sociales",
            "remuneration_nette",
            "benefice_apres_remuneration",
            "is_societe",
            "resultat_net_societe",
            "dividendes_bruts",
            "charges_dividendes",
            "impot_dividendes",
            "dividendes_nets",
            "revenu_imposable_ir",
            "ir_total",
            "net_disponible",
            "taux_prelevement_global",
        ],
    },
    "eurl_standard": {
        "params": {
            "ca_ht": 100000,
            "charges_exploitation": 15000,
            "remuneration_nette_cible": 45000,
            "distribuer_dividendes": True,
            "parts_fiscales": 1.0,
            "capital_social": 5000,
            "option_bareme_ir": False,
        },
        "expected_fields": [
            "statut",
            "ca_ht",
            "charges_exploitation",
            "benefice_avant_remuneration",
            "remuneration_brute",
            "charges_sociales",
            "remuneration_nette",
            "benefice_apres_remuneration",
            "is_societe",
            "resultat_net_societe",
            "dividendes_bruts",
            "charges_dividendes",
            "impot_dividendes",
            "dividendes_nets",
            "revenu_imposable_ir",
            "ir_total",
            "net_disponible",
            "taux_prelevement_global",
        ],
    },
}


def test_complete_simulation_structure_validation():
    """
    Test de validation de la structure complète des résultats de simulation.

    **Feature: code-quality-integration, Property 1: Behavioral Equivalence**
    **Validates: Requirements 1.3**

    Vérifie que tous les champs de ResultatSimulation sont présents et cohérents.
    """
    # Test SASU
    sasu_params = REFERENCE_COMPLETE_SIMULATIONS["sasu_standard"]["params"]
    sasu_result = simuler_sasu(**sasu_params)

    expected_fields = REFERENCE_COMPLETE_SIMULATIONS["sasu_standard"]["expected_fields"]
    for field in expected_fields:
        assert hasattr(sasu_result, field), f"Champ manquant dans ResultatSimulation SASU: {field}"
        value = getattr(sasu_result, field)
        assert value is not None, f"Champ {field} ne doit pas être None"
        if isinstance(value, (int, float)):
            assert value >= 0 or field in [
                "benefice_apres_remuneration"
            ], f"Champ {field} doit être positif ou nul"

    # Test EURL
    eurl_params = REFERENCE_COMPLETE_SIMULATIONS["eurl_standard"]["params"]
    eurl_result = simuler_eurl(**eurl_params)

    expected_fields = REFERENCE_COMPLETE_SIMULATIONS["eurl_standard"]["expected_fields"]
    for field in expected_fields:
        assert hasattr(eurl_result, field), f"Champ manquant dans ResultatSimulation EURL: {field}"
        value = getattr(eurl_result, field)
        assert value is not None, f"Champ {field} ne doit pas être None"
        if isinstance(value, (int, float)):
            assert value >= 0 or field in [
                "benefice_apres_remuneration"
            ], f"Champ {field} doit être positif ou nul"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
