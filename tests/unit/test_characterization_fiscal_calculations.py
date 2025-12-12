"""
Tests de caractérisation des calculs fiscaux existants.

Ces tests capturent le comportement actuel du code monolithique pour servir de référence
lors de la refactorisation. Ils implémentent la Property 1: Behavioral Equivalence.

**Feature: code-quality-integration, Property 1: Behavioral Equivalence**
**Validates: Requirements 1.3**
"""


import pytest

# Import des fonctions existantes à tester
from app import calcul_ir, calcul_is, simuler_eurl, simuler_sasu


class TestCharacterizationCalculIS:
    """Tests de caractérisation pour calcul_is - Impôt sur les Sociétés."""

    def test_calcul_is_zero_benefit(self):
        """Test avec bénéfice nul."""
        result = calcul_is(0)
        assert result == 0, "IS doit être 0 pour un bénéfice nul"

    def test_calcul_is_negative_benefit(self):
        """Test avec bénéfice négatif."""
        result = calcul_is(-10000)
        assert result == 0, "IS doit être 0 pour un bénéfice négatif"

    def test_calcul_is_below_threshold(self):
        """Test avec bénéfice sous le seuil de 42 500€ (taux réduit 15%)."""
        test_cases = [
            (10000, 1500),    # 10k€ * 15% = 1500€
            (25000, 3750),    # 25k€ * 15% = 3750€
            (42500, 6375),    # 42.5k€ * 15% = 6375€ (exactement au seuil)
        ]

        for benefice, expected_is in test_cases:
            result = calcul_is(benefice)
            assert result == expected_is, f"IS pour {benefice}€ devrait être {expected_is}€, obtenu {result}€"

    def test_calcul_is_above_threshold(self):
        """Test avec bénéfice au-dessus du seuil (taux normal 25%)."""
        test_cases = [
            # Calcul: 42500 * 0.15 + (benefice - 42500) * 0.25
            (50000, 8250.0),    # 6375 + 1875 = 8250€
            (100000, 20750.0),  # 6375 + 14375 = 20750€
            (200000, 45750.0),  # Valeur réelle capturée: 6375 + 39375 = 45750€
        ]

        for benefice, expected_is in test_cases:
            result = calcul_is(benefice)
            assert result == expected_is, f"IS pour {benefice}€ devrait être {expected_is}€, obtenu {result}€"

    def test_calcul_is_exact_threshold_boundary(self):
        """Test précis à la frontière du seuil IS."""
        # Exactement au seuil
        result_at_threshold = calcul_is(42500)
        assert result_at_threshold == 6375, "IS à 42500€ devrait être 6375€"

        # Juste au-dessus du seuil
        result_above_threshold = calcul_is(42501)
        expected = 42500 * 0.15 + 1 * 0.25  # 6375 + 0.25 = 6375.25
        assert result_above_threshold == expected, f"IS à 42501€ devrait être {expected}€"


class TestCharacterizationCalculIR:
    """Tests de caractérisation pour calcul_ir - Impôt sur le Revenu."""

    def test_calcul_ir_zero_income(self):
        """Test avec revenu nul."""
        result = calcul_ir(0, 1.0)
        assert result == 0, "IR doit être 0 pour un revenu nul"

    def test_calcul_ir_negative_income(self):
        """Test avec revenu négatif."""
        result = calcul_ir(-5000, 1.0)
        assert result == 0, "IR doit être 0 pour un revenu négatif"

    def test_calcul_ir_first_bracket(self):
        """Test dans la première tranche (0% jusqu'à 11 294€)."""
        test_cases = [
            (5000, 1.0, 0),      # Sous le seuil
            (11294, 1.0, 0),     # Exactement au seuil
        ]

        for revenu, parts, expected_ir in test_cases:
            result = calcul_ir(revenu, parts)
            assert result == expected_ir, f"IR pour {revenu}€ avec {parts} parts devrait être {expected_ir}€"

    def test_calcul_ir_second_bracket(self):
        """Test dans la deuxième tranche (11% de 11 294€ à 28 797€)."""
        test_cases = [
            (20000, 1.0, 957.66),    # (20000 - 11294) * 0.11 = 957.66€
            (28797, 1.0, 1925.33),   # (28797 - 11294) * 0.11 = 1925.33€
        ]

        for revenu, parts, expected_ir in test_cases:
            result = calcul_ir(revenu, parts)
            assert abs(result - expected_ir) < 0.01, f"IR pour {revenu}€ devrait être ~{expected_ir}€, obtenu {result}€"

    def test_calcul_ir_third_bracket(self):
        """Test dans la troisième tranche (30% de 28 797€ à 82 341€)."""
        # Calcul: 1925.33 (tranche 2) + (revenu - 28797) * 0.30
        test_cases = [
            (50000, 1.0, 8286.23),   # Valeur réelle capturée
            (82341, 1.0, 17988.53),  # Valeur réelle capturée
        ]

        for revenu, parts, expected_ir in test_cases:
            result = calcul_ir(revenu, parts)
            assert abs(result - expected_ir) < 0.01, f"IR pour {revenu}€ devrait être ~{expected_ir}€, obtenu {result}€"

    def test_calcul_ir_with_quotient_familial(self):
        """Test du quotient familial avec différents nombres de parts."""
        # Revenu de 50000€ avec différents nombres de parts
        base_income = 50000

        test_cases = [
            (1.0, 8286.23),    # 1 part - valeur réelle capturée
            (2.0, 3015.32),    # 2 parts - valeur réelle capturée
            (2.5, 2394.15),    # 2.5 parts - valeur réelle capturée
        ]

        for parts, expected_ir in test_cases:
            result = calcul_ir(base_income, parts)
            assert abs(result - expected_ir) < 0.01, f"IR pour {base_income}€ avec {parts} parts devrait être ~{expected_ir}€"

    def test_calcul_ir_high_income_brackets(self):
        """Test avec revenus élevés (tranches 41% et 45%)."""
        test_cases = [
            # Tranche 41%: de 82 341€ à 177 106€
            (150000, 1.0, 45728.72),  # Valeur réelle capturée
            # Tranche 45%: au-delà de 177 106€
            (200000, 1.0, 67144.48),  # Valeur réelle capturée
        ]

        for revenu, parts, expected_ir in test_cases:
            result = calcul_ir(revenu, parts)
            assert abs(result - expected_ir) < 0.01, f"IR pour {revenu}€ devrait être ~{expected_ir}€, obtenu {result}€"


class TestCharacterizationSimulationsSASU:
    """Tests de caractérisation pour simuler_sasu."""

    def test_simuler_sasu_basic_scenario(self):
        """Test de base SASU avec paramètres standards."""
        result = simuler_sasu(
            ca_ht=100000,
            charges_exploitation=10000,
            remuneration_nette_cible=48000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            option_bareme_ir=False
        )

        # Vérifications de cohérence
        assert result.statut == "SASU"
        assert result.ca_ht == 100000
        assert result.charges_exploitation == 10000
        assert result.benefice_avant_remuneration == 90000

        # Vérifications des calculs (valeurs de référence à capturer)
        assert abs(result.remuneration_nette - 48000) < 1, "Rémunération nette devrait être proche de 48000€"
        assert result.charges_sociales > 0, "Charges sociales SASU doivent être positives"
        assert result.is_societe >= 0, "IS doit être positif ou nul"
        assert result.net_disponible > 0, "Net disponible doit être positif"

    def test_simuler_sasu_no_dividends(self):
        """Test SASU sans distribution de dividendes."""
        result = simuler_sasu(
            ca_ht=80000,
            charges_exploitation=15000,
            remuneration_nette_cible=36000,
            distribuer_dividendes=False,
            parts_fiscales=1.0,
            option_bareme_ir=False
        )

        assert result.dividendes_bruts == 0
        assert result.dividendes_nets == 0
        assert result.impot_dividendes == 0
        assert result.charges_dividendes == 0

    def test_simuler_sasu_progressive_tax_option(self):
        """Test SASU avec option barème progressif."""
        result = simuler_sasu(
            ca_ht=120000,
            charges_exploitation=20000,
            remuneration_nette_cible=50000,
            distribuer_dividendes=True,
            parts_fiscales=2.0,
            option_bareme_ir=True
        )

        assert result.statut == "SASU"
        # Avec barème progressif, l'IR peut être différent
        assert result.ir_total >= 0, "IR doit être positif ou nul"

    def test_simuler_sasu_high_salary_scenario(self):
        """Test SASU avec rémunération élevée consommant tout le bénéfice."""
        result = simuler_sasu(
            ca_ht=60000,
            charges_exploitation=5000,
            remuneration_nette_cible=50000,  # Très élevée par rapport au CA
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            option_bareme_ir=False
        )

        # La rémunération devrait être limitée par le bénéfice disponible
        assert result.remuneration_nette < 50000, "Rémunération limitée par le bénéfice"
        assert result.dividendes_bruts == 0, "Pas de dividendes si tout consommé en salaire"


class TestCharacterizationSimulationsEURL:
    """Tests de caractérisation pour simuler_eurl."""

    def test_simuler_eurl_basic_scenario(self):
        """Test de base EURL avec paramètres standards."""
        result = simuler_eurl(
            ca_ht=100000,
            charges_exploitation=10000,
            remuneration_nette_cible=48000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            capital_social=1000,
            option_bareme_ir=False
        )

        # Vérifications de cohérence
        assert result.statut == "EURL"
        assert result.ca_ht == 100000
        assert result.charges_exploitation == 10000
        assert result.benefice_avant_remuneration == 90000

        # Vérifications spécifiques EURL
        assert abs(result.remuneration_nette - 48000) < 1, "Rémunération nette devrait être proche de 48000€"
        assert result.charges_sociales > 0, "Charges TNS doivent être positives"
        assert result.charges_dividendes >= 0, "Charges dividendes EURL peuvent être nulles ou positives"

    def test_simuler_eurl_dividend_charges_threshold(self):
        """Test EURL avec seuil 10% capital pour charges dividendes."""
        # Capital de 10000€, seuil à 1000€
        result = simuler_eurl(
            ca_ht=80000,
            charges_exploitation=10000,
            remuneration_nette_cible=30000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            capital_social=10000,  # Seuil à 1000€
            option_bareme_ir=False
        )

        assert result.statut == "EURL"
        # Si dividendes > 1000€, il devrait y avoir des charges sociales
        if result.dividendes_bruts > 1000:
            assert result.charges_dividendes > 0, "Charges dividendes attendues au-dessus du seuil"

    def test_simuler_eurl_low_capital(self):
        """Test EURL avec capital faible (charges dividendes importantes)."""
        result = simuler_eurl(
            ca_ht=100000,
            charges_exploitation=15000,
            remuneration_nette_cible=40000,
            distribuer_dividendes=True,
            parts_fiscales=1.0,
            capital_social=100,  # Capital très faible, seuil à 10€
            option_bareme_ir=False
        )

        # Avec capital faible, presque tous les dividendes sont soumis aux charges
        if result.dividendes_bruts > 10:
            assert result.charges_dividendes > 0, "Charges dividendes importantes avec capital faible"

    def test_simuler_eurl_vs_sasu_same_params(self):
        """Test comparatif EURL vs SASU avec mêmes paramètres."""
        params = {
            "ca_ht": 90000,
            "charges_exploitation": 12000,
            "remuneration_nette_cible": 42000,
            "distribuer_dividendes": True,
            "parts_fiscales": 1.5,
            "option_bareme_ir": False
        }

        result_sasu = simuler_sasu(**params)
        result_eurl = simuler_eurl(**params, capital_social=5000)

        # Vérifications de cohérence entre les deux
        assert result_sasu.ca_ht == result_eurl.ca_ht
        assert result_sasu.charges_exploitation == result_eurl.charges_exploitation
        assert result_sasu.benefice_avant_remuneration == result_eurl.benefice_avant_remuneration

        # Les résultats peuvent différer mais doivent être cohérents
        assert result_sasu.net_disponible > 0
        assert result_eurl.net_disponible > 0


class TestCharacterizationEdgeCases:
    """Tests de caractérisation pour cas limites."""

    def test_zero_revenue_scenario(self):
        """Test avec CA nul."""
        result_sasu = simuler_sasu(0, 0, 0, False, 1.0, False)
        result_eurl = simuler_eurl(0, 0, 0, False, 1.0, 1000, False)

        assert result_sasu.net_disponible == 0
        assert result_eurl.net_disponible == 0
        assert result_sasu.taux_prelevement_global == 0
        assert result_eurl.taux_prelevement_global == 0

    def test_expenses_equal_revenue(self):
        """Test avec charges égales au CA."""
        result_sasu = simuler_sasu(50000, 50000, 0, False, 1.0, False)
        result_eurl = simuler_eurl(50000, 50000, 0, False, 1.0, 1000, False)

        assert result_sasu.benefice_avant_remuneration == 0
        assert result_eurl.benefice_avant_remuneration == 0
        assert result_sasu.net_disponible == 0
        assert result_eurl.net_disponible == 0

    def test_very_high_tax_parts(self):
        """Test avec nombre de parts fiscales élevé."""
        result = simuler_sasu(
            ca_ht=150000,
            charges_exploitation=20000,
            remuneration_nette_cible=60000,
            distribuer_dividendes=True,
            parts_fiscales=4.0,  # Famille nombreuse
            option_bareme_ir=False
        )

        # Avec 4 parts, l'IR devrait être réduit
        assert result.ir_total >= 0
        assert result.net_disponible > 0


# Données de référence pour validation future
REFERENCE_CALCULATIONS = {
    "calcul_is": [
        (0, 0),
        (10000, 1500),
        (42500, 6375),
        (50000, 8250.0),
        (100000, 20750.0),
    ],
    "calcul_ir": [
        (0, 1.0, 0),
        (11294, 1.0, 0),
        (20000, 1.0, 957.66),
        (50000, 1.0, 8286.23),  # Valeur réelle capturée
        (50000, 2.0, 3015.32),  # Valeur réelle capturée
    ],
}


def test_reference_calculations_stability():
    """
    Test de stabilité des calculs de référence.

    **Feature: code-quality-integration, Property 1: Behavioral Equivalence**
    **Validates: Requirements 1.3**

    Ce test vérifie que les calculs de base restent stables et peuvent servir
    de référence pour la validation après refactorisation.
    """
    # Test calcul_is
    for benefice, expected_is in REFERENCE_CALCULATIONS["calcul_is"]:
        result = calcul_is(benefice)
        assert result == expected_is, f"calcul_is({benefice}) = {result}, attendu {expected_is}"

    # Test calcul_ir
    for revenu, parts, expected_ir in REFERENCE_CALCULATIONS["calcul_ir"]:
        result = calcul_ir(revenu, parts)
        if expected_ir == 0:
            assert result == expected_ir
        else:
            assert abs(result - expected_ir) < 0.01, f"calcul_ir({revenu}, {parts}) = {result}, attendu {expected_ir}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
