# 💼 Simulateur de Rémunération SASU/EURL

Simulateur interactif pour comparer la rémunération nette disponible selon le statut juridique choisi (SASU ou EURL à l'IS).

## 🚀 Lancement rapide

### Prérequis

- Python 3.8 ou supérieur
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets Python moderne)

### Installation d'uv

```bash
# Sur macOS/Linux avec curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou avec Homebrew sur macOS
brew install uv

# Ou avec pip
pip install uv
```

### Installation du projet

```bash
# Cloner le projet
git clone <url-du-repo>
cd simulateur-remuneration

# Créer un environnement virtuel et installer les dépendances
uv venv
source .venv/bin/activate  # Sur macOS/Linux
# ou .venv\Scripts\activate sur Windows

# Installation des dépendances
uv pip install -r requirements.txt
```

### Alternative avec uv sync (recommandé)

```bash
# Installation directe avec uv (plus rapide)
uv sync
```

### Lancement

```bash
# Avec environnement activé
streamlit run app.py

# Ou directement avec uv
uv run streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

## 📊 Fonctionnalités

- **Comparaison SASU vs EURL** : Calcul du net disponible pour les deux statuts
- **Paramètres ajustables** :
  - Chiffre d'affaires HT
  - Charges d'exploitation
  - Rémunération nette souhaitée
  - Distribution de dividendes (oui/non)
  - Option Flat Tax vs Barème IR
  - Parts fiscales (quotient familial)
  - Capital social (impact EURL)
- **Visualisations** : Graphiques de répartition des charges
- **Détail des calculs** : Transparence totale sur chaque étape

## 📐 Hypothèses de calcul

### SASU (Président assimilé salarié)

- Charges sociales : ~82% du net (régime général)
- Dividendes : Flat tax 30% (ou option barème)
- Pas de charges sociales sur dividendes

### EURL (Gérant TNS)

- Charges sociales : ~45% du net (régime TNS)
- Dividendes > 10% du capital : soumis à charges sociales (45%)
- Flat tax 30% sur la partie nette (ou option barème)

### Fiscalité commune

- IS : 15% jusqu'à 42 500€, puis 25%
- IR : Barème progressif 2024 avec quotient familial
- Abattement 10% sur salaires (plafonné à 14 171€)

## ⚠️ Avertissements

Ce simulateur est fourni **à titre indicatif uniquement**. Les résultats ne constituent pas un conseil fiscal ou juridique.

**Non pris en compte :**

- ACRE et autres exonérations
- CSG déductible détaillée
- Prévoyance complémentaire
- Crédits d'impôt
- Régularisation N-2 des cotisations TNS

**Recommandation** : Consultez un expert-comptable pour une simulation personnalisée adaptée à votre situation.

## 🛠️ Technologies

- [Streamlit](https://streamlit.io/) - Framework d'applications web Python
- [Plotly](https://plotly.com/) - Visualisations interactives
- [Pandas](https://pandas.pydata.org/) - Manipulation de données

## 📝 Licence

Usage libre - Créé avec l'aide de Claude (Anthropic)
