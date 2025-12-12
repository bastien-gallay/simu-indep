"""
Simulateur de Rémunération - Entrepreneur Indépendant Français
SASU vs EURL - Comparaison des statuts juridiques

Auteur: Assistant Claude pour Bastien
"""

from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Simulateur SASU/EURL", page_icon="💼", layout="wide")

# --- CONSTANTES FISCALES 2024 ---

# Impôt sur les Sociétés
IS_TAUX_REDUIT = 0.15  # Jusqu'à 42 500€
IS_TAUX_NORMAL = 0.25  # Au-delà
IS_SEUIL_REDUIT = 42500

# Flat Tax (PFU) sur dividendes
FLAT_TAX = 0.30  # 12.8% IR + 17.2% prélèvements sociaux
PRELEVEMENT_SOCIAUX = 0.172

# Charges sociales SASU (assimilé salarié)
# Environ 82% de charges patronales+salariales sur le net
# Soit environ 45% du brut
CHARGES_SASU_TAUX = 0.82  # Sur le net pour obtenir le coût total

# Charges sociales EURL (TNS)
# Environ 45% de charges sur la rémunération nette
CHARGES_EURL_TNS_TAUX = 0.45

# Charges sur dividendes EURL (au-delà de 10% du capital)
CHARGES_DIVIDENDES_EURL = 0.45

# Barème IR 2024 (revenus 2023)
TRANCHES_IR = [(11294, 0.00), (28797, 0.11), (82341, 0.30), (177106, 0.41), (float("inf"), 0.45)]

# --- FONCTIONS DE CALCUL ---


def calcul_is(benefice: float) -> float:
    """Calcule l'Impôt sur les Sociétés"""
    if benefice <= 0:
        return 0
    if benefice <= IS_SEUIL_REDUIT:
        return benefice * IS_TAUX_REDUIT
    return IS_SEUIL_REDUIT * IS_TAUX_REDUIT + (benefice - IS_SEUIL_REDUIT) * IS_TAUX_NORMAL


def calcul_ir(revenu_imposable: float, parts: float = 1) -> float:
    """Calcule l'Impôt sur le Revenu avec le quotient familial"""
    if revenu_imposable <= 0:
        return 0

    revenu_par_part = revenu_imposable / parts
    impot_par_part = 0
    tranche_precedente = 0

    for seuil, taux in TRANCHES_IR:
        if revenu_par_part <= seuil:
            impot_par_part += (revenu_par_part - tranche_precedente) * taux
            break
        else:
            impot_par_part += (seuil - tranche_precedente) * taux
            tranche_precedente = seuil

    return impot_par_part * parts


def calcul_taux_marginal_ir(revenu_imposable: float, parts: float = 1) -> float:
    """Retourne le taux marginal d'imposition"""
    revenu_par_part = revenu_imposable / parts
    for seuil, taux in TRANCHES_IR:
        if revenu_par_part <= seuil:
            return taux
    return 0.45


@dataclass
class ResultatSimulation:
    """Résultat d'une simulation de rémunération"""

    statut: str
    ca_ht: float
    charges_exploitation: float
    benefice_avant_remuneration: float
    remuneration_brute: float
    charges_sociales: float
    remuneration_nette: float
    benefice_apres_remuneration: float
    is_societe: float
    resultat_net_societe: float
    dividendes_bruts: float
    charges_dividendes: float
    impot_dividendes: float
    dividendes_nets: float
    revenu_imposable_ir: float
    ir_total: float
    net_disponible: float
    taux_prelevement_global: float


def simuler_sasu(
    ca_ht: float,
    charges_exploitation: float,
    remuneration_nette_cible: float,
    distribuer_dividendes: bool,
    parts_fiscales: float,
    option_bareme_ir: bool = False,
) -> ResultatSimulation:
    """Simulation complète pour une SASU"""

    benefice_avant_remuneration = ca_ht - charges_exploitation

    # Calcul de la rémunération (assimilé salarié)
    # Coût total = net + charges (82% du net)
    cout_total_remuneration = remuneration_nette_cible * (1 + CHARGES_SASU_TAUX)
    charges_sociales = remuneration_nette_cible * CHARGES_SASU_TAUX

    # On limite la rémunération au bénéfice disponible
    if cout_total_remuneration > benefice_avant_remuneration:
        cout_total_remuneration = benefice_avant_remuneration
        remuneration_nette = cout_total_remuneration / (1 + CHARGES_SASU_TAUX)
        charges_sociales = cout_total_remuneration - remuneration_nette
    else:
        remuneration_nette = remuneration_nette_cible

    benefice_apres_remuneration = benefice_avant_remuneration - cout_total_remuneration

    # IS sur le bénéfice restant
    is_societe = calcul_is(benefice_apres_remuneration)
    resultat_net_societe = benefice_apres_remuneration - is_societe

    # Dividendes
    if distribuer_dividendes and resultat_net_societe > 0:
        dividendes_bruts = resultat_net_societe
        charges_dividendes = 0  # Pas de charges sociales sur dividendes en SASU

        if option_bareme_ir:
            # Option barème progressif avec abattement de 40%
            dividendes_imposables = dividendes_bruts * 0.6
            impot_dividendes = dividendes_bruts * PRELEVEMENT_SOCIAUX  # PS uniquement ici
        else:
            # Flat tax (PFU)
            dividendes_imposables = 0  # Pas dans l'IR
            impot_dividendes = dividendes_bruts * FLAT_TAX

        dividendes_nets = dividendes_bruts - impot_dividendes
    else:
        dividendes_bruts = 0
        charges_dividendes = 0
        dividendes_imposables = 0
        impot_dividendes = 0
        dividendes_nets = 0

    # Calcul IR sur la rémunération
    # Abattement de 10% pour frais professionnels (plafonné à 14 171€)
    abattement_10 = min(remuneration_nette * 0.10, 14171)
    revenu_imposable_salaire = remuneration_nette - abattement_10

    if option_bareme_ir and distribuer_dividendes:
        revenu_imposable_ir = revenu_imposable_salaire + dividendes_imposables
    else:
        revenu_imposable_ir = revenu_imposable_salaire

    ir_total = calcul_ir(revenu_imposable_ir, parts_fiscales)

    # Net disponible final
    net_disponible = remuneration_nette + dividendes_nets - ir_total

    # Taux de prélèvement global
    total_preleve = charges_sociales + is_societe + impot_dividendes + ir_total
    taux_prelevement = total_preleve / ca_ht if ca_ht > 0 else 0

    return ResultatSimulation(
        statut="SASU",
        ca_ht=ca_ht,
        charges_exploitation=charges_exploitation,
        benefice_avant_remuneration=benefice_avant_remuneration,
        remuneration_brute=remuneration_nette + charges_sociales * 0.55,  # Approximation brut
        charges_sociales=charges_sociales,
        remuneration_nette=remuneration_nette,
        benefice_apres_remuneration=benefice_apres_remuneration,
        is_societe=is_societe,
        resultat_net_societe=resultat_net_societe,
        dividendes_bruts=dividendes_bruts,
        charges_dividendes=charges_dividendes,
        impot_dividendes=impot_dividendes,
        dividendes_nets=dividendes_nets,
        revenu_imposable_ir=revenu_imposable_ir,
        ir_total=ir_total,
        net_disponible=net_disponible,
        taux_prelevement_global=taux_prelevement,
    )


def simuler_eurl(
    ca_ht: float,
    charges_exploitation: float,
    remuneration_nette_cible: float,
    distribuer_dividendes: bool,
    parts_fiscales: float,
    capital_social: float = 1000,
    option_bareme_ir: bool = False,
) -> ResultatSimulation:
    """Simulation complète pour une EURL à l'IS"""

    benefice_avant_remuneration = ca_ht - charges_exploitation

    # Calcul de la rémunération (TNS)
    # Coût total = net + charges (45% du net)
    cout_total_remuneration = remuneration_nette_cible * (1 + CHARGES_EURL_TNS_TAUX)
    charges_sociales = remuneration_nette_cible * CHARGES_EURL_TNS_TAUX

    # On limite la rémunération au bénéfice disponible
    if cout_total_remuneration > benefice_avant_remuneration:
        cout_total_remuneration = benefice_avant_remuneration
        remuneration_nette = cout_total_remuneration / (1 + CHARGES_EURL_TNS_TAUX)
        charges_sociales = cout_total_remuneration - remuneration_nette
    else:
        remuneration_nette = remuneration_nette_cible

    benefice_apres_remuneration = benefice_avant_remuneration - cout_total_remuneration

    # IS sur le bénéfice restant
    is_societe = calcul_is(benefice_apres_remuneration)
    resultat_net_societe = benefice_apres_remuneration - is_societe

    # Dividendes avec charges sociales sur la partie > 10% du capital
    if distribuer_dividendes and resultat_net_societe > 0:
        dividendes_bruts = resultat_net_societe
        seuil_10_pourcent = capital_social * 0.10

        # Partie soumise à charges sociales
        dividendes_soumis_charges = max(0, dividendes_bruts - seuil_10_pourcent)
        charges_dividendes = dividendes_soumis_charges * CHARGES_DIVIDENDES_EURL

        dividendes_apres_charges = dividendes_bruts - charges_dividendes

        if option_bareme_ir:
            dividendes_imposables = dividendes_apres_charges * 0.6
            impot_dividendes = dividendes_apres_charges * PRELEVEMENT_SOCIAUX
        else:
            dividendes_imposables = 0
            impot_dividendes = dividendes_apres_charges * FLAT_TAX

        dividendes_nets = dividendes_apres_charges - impot_dividendes
    else:
        dividendes_bruts = 0
        charges_dividendes = 0
        dividendes_imposables = 0
        impot_dividendes = 0
        dividendes_nets = 0

    # Calcul IR
    abattement_10 = min(remuneration_nette * 0.10, 14171)
    revenu_imposable_salaire = remuneration_nette - abattement_10

    if option_bareme_ir and distribuer_dividendes:
        revenu_imposable_ir = revenu_imposable_salaire + dividendes_imposables
    else:
        revenu_imposable_ir = revenu_imposable_salaire

    ir_total = calcul_ir(revenu_imposable_ir, parts_fiscales)

    # Net disponible final
    net_disponible = remuneration_nette + dividendes_nets - ir_total

    # Taux de prélèvement global
    total_preleve = charges_sociales + charges_dividendes + is_societe + impot_dividendes + ir_total
    taux_prelevement = total_preleve / ca_ht if ca_ht > 0 else 0

    return ResultatSimulation(
        statut="EURL",
        ca_ht=ca_ht,
        charges_exploitation=charges_exploitation,
        benefice_avant_remuneration=benefice_avant_remuneration,
        remuneration_brute=remuneration_nette * 1.31,  # Approximation
        charges_sociales=charges_sociales,
        remuneration_nette=remuneration_nette,
        benefice_apres_remuneration=benefice_apres_remuneration,
        is_societe=is_societe,
        resultat_net_societe=resultat_net_societe,
        dividendes_bruts=dividendes_bruts,
        charges_dividendes=charges_dividendes,
        impot_dividendes=impot_dividendes,
        dividendes_nets=dividendes_nets,
        revenu_imposable_ir=revenu_imposable_ir,
        ir_total=ir_total,
        net_disponible=net_disponible,
        taux_prelevement_global=taux_prelevement,
    )


# --- INTERFACE STREAMLIT ---

st.title("💼 Simulateur de Rémunération")
st.subheader("Entrepreneur Indépendant - SASU vs EURL")

st.markdown(
    """
Comparez votre rémunération nette selon le statut juridique choisi.
Les calculs sont basés sur les taux 2024 et sont fournis à titre indicatif.
"""
)

# Sidebar pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres")

    st.subheader("Activité")
    ca_ht = st.number_input(
        "Chiffre d'affaires HT annuel (€)",
        min_value=0,
        max_value=1000000,
        value=100000,
        step=5000,
        help="Votre CA annuel hors taxes",
    )

    charges_exploitation = st.number_input(
        "Charges d'exploitation (€)",
        min_value=0,
        max_value=500000,
        value=10000,
        step=1000,
        help="Loyer, matériel, sous-traitance, etc.",
    )

    st.subheader("Rémunération souhaitée")
    remuneration_nette = st.slider(
        "Rémunération nette mensuelle (€)",
        min_value=0,
        max_value=15000,
        value=4000,
        step=100,
        help="Objectif de rémunération nette mensuelle",
    )
    remuneration_annuelle = remuneration_nette * 12

    st.subheader("Dividendes")
    distribuer_dividendes = st.checkbox(
        "Distribuer les dividendes",
        value=True,
        help="Distribuer le résultat net restant en dividendes",
    )

    option_bareme_ir = st.checkbox(
        "Option barème IR (vs Flat Tax)",
        value=False,
        help="Choisir le barème progressif de l'IR au lieu de la flat tax à 30%",
    )

    st.subheader("Situation fiscale")
    parts_fiscales = st.selectbox(
        "Parts fiscales",
        options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
        index=0,
        help="Nombre de parts pour le quotient familial",
    )

    st.subheader("Capital (EURL)")
    capital_social = st.number_input(
        "Capital social EURL (€)",
        min_value=1,
        max_value=100000,
        value=1000,
        step=100,
        help="Impact sur les charges sociales des dividendes",
    )

# Calculs
resultat_sasu = simuler_sasu(
    ca_ht=ca_ht,
    charges_exploitation=charges_exploitation,
    remuneration_nette_cible=remuneration_annuelle,
    distribuer_dividendes=distribuer_dividendes,
    parts_fiscales=parts_fiscales,
    option_bareme_ir=option_bareme_ir,
)

resultat_eurl = simuler_eurl(
    ca_ht=ca_ht,
    charges_exploitation=charges_exploitation,
    remuneration_nette_cible=remuneration_annuelle,
    distribuer_dividendes=distribuer_dividendes,
    parts_fiscales=parts_fiscales,
    capital_social=capital_social,
    option_bareme_ir=option_bareme_ir,
)

# Affichage des résultats
st.header("📊 Comparaison des résultats")

col1, col2 = st.columns(2)


def afficher_resultat(col, resultat: ResultatSimulation, couleur: str):
    with col:
        st.markdown(f"### {resultat.statut}")

        # Métriques clés
        st.metric(
            "💰 Net disponible annuel",
            f"{resultat.net_disponible:,.0f} €".replace(",", " "),
            delta=f"{resultat.net_disponible/12:,.0f} €/mois".replace(",", " "),
        )

        st.metric("📉 Taux de prélèvement global", f"{resultat.taux_prelevement_global*100:.1f}%")

        # Détails
        with st.expander("Voir le détail du calcul"):
            st.markdown("**Société**")
            st.write(f"- CA HT : {resultat.ca_ht:,.0f} €".replace(",", " "))
            st.write(
                f"- Charges exploitation : {resultat.charges_exploitation:,.0f} €".replace(",", " ")
            )
            st.write(
                f"- Bénéfice avant rémunération : {resultat.benefice_avant_remuneration:,.0f} €".replace(
                    ",", " "
                )
            )

            st.markdown("**Rémunération**")
            st.write(
                f"- Rémunération nette : {resultat.remuneration_nette:,.0f} €".replace(",", " ")
            )
            st.write(f"- Charges sociales : {resultat.charges_sociales:,.0f} €".replace(",", " "))

            st.markdown("**Résultat société**")
            st.write(
                f"- Bénéfice après rémunération : {resultat.benefice_apres_remuneration:,.0f} €".replace(
                    ",", " "
                )
            )
            st.write(f"- IS : {resultat.is_societe:,.0f} €".replace(",", " "))
            st.write(f"- Résultat net : {resultat.resultat_net_societe:,.0f} €".replace(",", " "))

            if resultat.dividendes_bruts > 0:
                st.markdown("**Dividendes**")
                st.write(
                    f"- Dividendes bruts : {resultat.dividendes_bruts:,.0f} €".replace(",", " ")
                )
                if resultat.charges_dividendes > 0:
                    st.write(
                        f"- Charges sociales dividendes : {resultat.charges_dividendes:,.0f} €".replace(
                            ",", " "
                        )
                    )
                st.write(
                    f"- Impôt dividendes : {resultat.impot_dividendes:,.0f} €".replace(",", " ")
                )
                st.write(f"- Dividendes nets : {resultat.dividendes_nets:,.0f} €".replace(",", " "))

            st.markdown("**Impôt sur le revenu**")
            st.write(
                f"- Revenu imposable : {resultat.revenu_imposable_ir:,.0f} €".replace(",", " ")
            )
            st.write(f"- IR : {resultat.ir_total:,.0f} €".replace(",", " "))


afficher_resultat(col1, resultat_sasu, "#1f77b4")
afficher_resultat(col2, resultat_eurl, "#ff7f0e")

# Comparaison visuelle
st.header("📈 Visualisation")

# Graphique de répartition
fig = go.Figure()

categories = ["SASU", "EURL"]

fig.add_trace(
    go.Bar(
        name="Charges sociales",
        x=categories,
        y=[
            resultat_sasu.charges_sociales + resultat_sasu.charges_dividendes,
            resultat_eurl.charges_sociales + resultat_eurl.charges_dividendes,
        ],
        marker_color="#e74c3c",
    )
)

fig.add_trace(
    go.Bar(
        name="IS",
        x=categories,
        y=[resultat_sasu.is_societe, resultat_eurl.is_societe],
        marker_color="#f39c12",
    )
)

fig.add_trace(
    go.Bar(
        name="IR + Impôt dividendes",
        x=categories,
        y=[
            resultat_sasu.ir_total + resultat_sasu.impot_dividendes,
            resultat_eurl.ir_total + resultat_eurl.impot_dividendes,
        ],
        marker_color="#9b59b6",
    )
)

fig.add_trace(
    go.Bar(
        name="Net disponible",
        x=categories,
        y=[resultat_sasu.net_disponible, resultat_eurl.net_disponible],
        marker_color="#2ecc71",
    )
)

fig.update_layout(
    barmode="stack",
    title="Répartition du CA entre charges et net disponible",
    yaxis_title="Montant (€)",
    legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
)

st.plotly_chart(fig, use_container_width=True)

# Tableau récapitulatif
st.header("📋 Tableau récapitulatif")

df_comparaison = pd.DataFrame(
    {
        "Élément": [
            "CA HT",
            "Charges exploitation",
            "Rémunération nette",
            "Charges sociales (rémunération)",
            "Charges sociales (dividendes)",
            "IS",
            "Dividendes bruts",
            "Impôt dividendes",
            "Dividendes nets",
            "IR",
            "**Net disponible**",
            "Net mensuel",
            "Taux prélèvement",
        ],
        "SASU": [
            f"{resultat_sasu.ca_ht:,.0f} €",
            f"{resultat_sasu.charges_exploitation:,.0f} €",
            f"{resultat_sasu.remuneration_nette:,.0f} €",
            f"{resultat_sasu.charges_sociales:,.0f} €",
            f"{resultat_sasu.charges_dividendes:,.0f} €",
            f"{resultat_sasu.is_societe:,.0f} €",
            f"{resultat_sasu.dividendes_bruts:,.0f} €",
            f"{resultat_sasu.impot_dividendes:,.0f} €",
            f"{resultat_sasu.dividendes_nets:,.0f} €",
            f"{resultat_sasu.ir_total:,.0f} €",
            f"**{resultat_sasu.net_disponible:,.0f} €**",
            f"{resultat_sasu.net_disponible/12:,.0f} €",
            f"{resultat_sasu.taux_prelevement_global*100:.1f}%",
        ],
        "EURL": [
            f"{resultat_eurl.ca_ht:,.0f} €",
            f"{resultat_eurl.charges_exploitation:,.0f} €",
            f"{resultat_eurl.remuneration_nette:,.0f} €",
            f"{resultat_eurl.charges_sociales:,.0f} €",
            f"{resultat_eurl.charges_dividendes:,.0f} €",
            f"{resultat_eurl.is_societe:,.0f} €",
            f"{resultat_eurl.dividendes_bruts:,.0f} €",
            f"{resultat_eurl.impot_dividendes:,.0f} €",
            f"{resultat_eurl.dividendes_nets:,.0f} €",
            f"{resultat_eurl.ir_total:,.0f} €",
            f"**{resultat_eurl.net_disponible:,.0f} €**",
            f"{resultat_eurl.net_disponible/12:,.0f} €",
            f"{resultat_eurl.taux_prelevement_global*100:.1f}%",
        ],
    }
)

st.dataframe(df_comparaison, use_container_width=True, hide_index=True)

# Différence
diff = resultat_eurl.net_disponible - resultat_sasu.net_disponible
meilleur = "EURL" if diff > 0 else "SASU"
st.info(
    f"💡 Avec ces paramètres, **{meilleur}** vous permet de gagner **{abs(diff):,.0f} €** de plus par an ({abs(diff)/12:,.0f} €/mois)".replace(
        ",", " "
    )
)

# Notes et avertissements
st.header("ℹ️ Notes importantes")

st.markdown(
    """
**Limites de ce simulateur :**
- Les taux de charges sont des approximations moyennes (ils varient selon votre situation exacte)
- Ne prend pas en compte : ACRE, exonérations, crédits d'impôt, prévoyance complémentaire
- Les cotisations TNS sont en réalité calculées sur N-2 avec régularisation
- La CSG déductible n'est pas prise en compte dans le détail

**Protection sociale :**
- **SASU** : Meilleure protection (régime général), mais plus chère
- **EURL** : Protection moindre, mais charges réduites. Pensez à la prévoyance !

**Conseil :** Consultez un expert-comptable pour une simulation personnalisée.
"""
)

# Footer
st.markdown("---")
st.markdown("*Simulateur créé à titre indicatif - Données 2024*")
