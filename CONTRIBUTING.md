# Guide de Contribution

Merci de votre intérêt pour contribuer au Simulateur de Rémunération SASU/EURL !

## 🚀 Comment contribuer

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](../../issues)
2. Créez une nouvelle issue avec :
   - Une description claire du problème
   - Les étapes pour reproduire le bug
   - Le comportement attendu vs observé
   - Votre environnement (OS, version Python, etc.)

### Proposer une amélioration

1. Ouvrez une issue pour discuter de votre idée
2. Décrivez clairement l'amélioration proposée
3. Expliquez pourquoi cette amélioration serait utile

### Contribuer au code

1. **Fork** le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout de ma fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une **Pull Request**

## 📋 Standards de code

### Style Python

- Suivez [PEP 8](https://pep8.org/)
- Utilisez des noms de variables explicites
- Commentez le code complexe
- Documentez les fonctions avec des docstrings

### Structure du code

```python
def ma_fonction(param1: float, param2: str) -> float:
    """
    Description de la fonction.
    
    Args:
        param1: Description du paramètre 1
        param2: Description du paramètre 2
    
    Returns:
        Description de la valeur retournée
    """
    # Implémentation
    return resultat
```

### Tests

- Ajoutez des tests pour les nouvelles fonctionnalités
- Vérifiez que tous les tests passent avant de soumettre
- Testez avec différents paramètres d'entrée

## 🧪 Environnement de développement

### Installation

```bash
# Cloner votre fork
git clone https://github.com/votre-username/simulateur-remuneration.git
cd simulateur-remuneration

# Créer un environnement virtuel avec uv
uv venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows

# Installer les dépendances
uv pip install -r requirements.txt

# Installer les dépendances de développement
uv pip install -r requirements-dev.txt

# Ou installation directe avec uv sync
uv sync --dev
```

### Lancer l'application

```bash
# Avec environnement activé
streamlit run app.py

# Ou directement avec uv
uv run streamlit run app.py
```

### Commandes de test et qualité

```bash
# Lancer les tests (si disponibles)
uv run pytest tests/

# Vérifier le style de code Python
uv run flake8 app.py
uv run mypy app.py

# Formatage automatique Python
uv run black app.py
uv run isort app.py

# Vérifier le Markdown (si markdownlint-cli est installé)
markdownlint *.md
```

## 📊 Données fiscales

### Mise à jour des taux

Les taux fiscaux et sociaux sont définis dans les constantes en début de `app.py`.
Lors de la mise à jour annuelle :

1. Vérifiez les nouveaux taux officiels
2. Mettez à jour les constantes
3. Ajoutez un commentaire avec l'année de référence
4. Testez avec des cas d'usage variés

### Sources officielles

- [Service-public.fr](https://www.service-public.fr/)
- [URSSAF](https://www.urssaf.fr/)
- [Impots.gouv.fr](https://www.impots.gouv.fr/)

## 🔍 Validation des calculs

Avant de soumettre des modifications aux calculs :

1. Vérifiez avec des cas réels
2. Comparez avec d'autres simulateurs
3. Documentez vos sources
4. Ajoutez des tests unitaires

## 📝 Documentation

- Mettez à jour le README si nécessaire
- Documentez les nouvelles fonctionnalités
- Expliquez les choix techniques complexes

## ❓ Questions

Si vous avez des questions, n'hésitez pas à :

- Ouvrir une issue
- Consulter la documentation existante
- Regarder les issues fermées pour des questions similaires

Merci pour votre contribution ! 🙏
