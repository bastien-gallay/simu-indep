# Standards de Code - Pro*C Analyzer

## Table des matières

1. [Introduction](#introduction)
2. [Principes CUPID](#principes-cupid)
3. [Clean Code](#clean-code)
4. [Quatre règles de conception simple](#quatre-règles-de-conception-simple)
5. [Typage et TypeGuard](#typage-et-typeguard)
6. [Architecture et organisation](#architecture-et-organisation)
7. [Tests](#tests)
8. [Documentation](#documentation)
9. [Outils et configuration](#outils-et-configuration)

---

## Introduction

Ce document définit les standards de code et les bonnes pratiques pour le projet **Pro*C Static Analyzer**, un analyseur statique pour code Pro*C (Oracle Embedded SQL).

### Objectifs

- Assurer la cohérence du code entre tous les contributeurs
- Faciliter la maintenance et l'évolution du projet
- Améliorer la qualité et la lisibilité du code
- Encourager les bonnes pratiques de développement Python

### Public cible

Ce document s'adresse à tous les développeurs contribuant au projet, qu'ils soient nouveaux ou expérimentés.

---

## Principes CUPID

Les principes **CUPID** (Composable, Unix philosophy, Predictable, Idiomatic, Domain-based) guident l'architecture et le design du code.

### Composable (Composable)

Les composants doivent être réutilisables et composables. Préférer la composition à l'héritage.

**✅ Bon exemple :**

```python
# Les calculateurs sont indépendants et composables
class CyclomaticCalculator:
    def __init__(self, parser: ProCParser):
        self.parser = parser
    
    def calculate(self, function: FunctionInfo) -> int:
        # Calcul indépendant, réutilisable
        ...

class CognitiveCalculator:
    def __init__(self, parser: ProCParser):
        self.parser = parser
    
    def calculate(self, function: FunctionInfo) -> int:
        # Calcul indépendant, réutilisable
        ...

# Dans analyzer.py, on compose les calculateurs
cyclo_calc = CyclomaticCalculator(self.parser)
cognitive_calc = CognitiveCalculator(self.parser)
```

**❌ À éviter :**

```python
# Héritage inutile qui crée des dépendances rigides
class BaseCalculator:
    ...

class CyclomaticCalculator(BaseCalculator):
    ...
```

### Unix Philosophy

Chaque module doit faire **une chose et la faire bien**. Interfaces simples et claires.

**✅ Bon exemple :**

```python
# parser.py : fait uniquement le parsing
class ProCParser:
    def parse(self, source: str) -> None:
        ...
    
    def get_functions(self) -> List[FunctionInfo]:
        ...

# cyclomatic.py : calcule uniquement la complexité cyclomatique
class CyclomaticCalculator:
    def calculate(self, function: FunctionInfo) -> int:
        ...
```

**❌ À éviter :**

```python
# Classe qui fait trop de choses
class ParserAndAnalyzer:
    def parse(self, source: str): ...
    def calculate_cyclomatic(self): ...
    def calculate_cognitive(self): ...
    def analyze_memory(self): ...
```

### Predictable (Prévisible)

Le comportement doit être prévisible. Pas de side effects cachés, pas de mutations inattendues.

**✅ Bon exemple :**

```python
# Fonction pure, résultat prévisible
def calculate(self, function: FunctionInfo) -> int:
    """Retourne toujours un entier >= 0"""
    complexity = 0
    # Calcul déterministe
    ...
    return complexity

# Méthode qui modifie l'état de manière explicite
def analyze(self, source: str) -> MemoryAnalysisResult:
    """Crée un nouveau résultat, ne modifie pas l'état global"""
    self.result = MemoryAnalysisResult()  # Reset explicite
    ...
    return self.result
```

**❌ À éviter :**

```python
# Side effect caché
def calculate(self, function: FunctionInfo) -> int:
    self._global_state += 1  # Modification inattendue
    ...

# Comportement non déterministe
def get_result(self) -> int:
    return random.randint(0, 10)  # Non prévisible
```

### Idiomatic (Idiomatique)

Utiliser les idiomes Python et respecter les conventions PEP 8.

**✅ Bon exemple :**

```python
# Utilisation de dataclasses
@dataclass
class FunctionMetrics:
    name: str
    start_line: int
    cyclomatic_complexity: int

# Utilisation de properties
@property
def avg_cyclomatic(self) -> float:
    if not self.functions:
        return 0.0
    return sum(f.cyclomatic_complexity for f in self.functions) / len(self.functions)

# Utilisation de context managers (si applicable)
with open(filepath) as f:
    source = f.read()
```

**❌ À éviter :**

```python
# Code non idiomatique
class FunctionMetrics:
    def __init__(self):
        self._name = None
    
    def get_name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name

# Utiliser des getters/setters au lieu de properties
```

### Domain-based (Basé sur le domaine)

Utiliser un vocabulaire métier clair et expressif.

**✅ Bon exemple :**

```python
# Vocabulaire métier clair
@dataclass
class FunctionMetrics:
    """Métriques pour une fonction"""
    name: str
    cyclomatic_complexity: int
    cognitive_complexity: int
    sql_blocks_count: int

@dataclass
class AnalysisReport:
    """Rapport d'analyse complet"""
    files: List[FileMetrics]
    module_inventory: Optional[Dict]

# Méthodes avec noms métier
def get_high_complexity_functions(
    self, 
    cyclo_threshold: int = 10, 
    cognitive_threshold: int = 15
) -> List[tuple]:
    """Retourne les fonctions dépassant les seuils"""
    ...
```

**❌ À éviter :**

```python
# Vocabulaire générique ou technique
@dataclass
class Data:
    """Trop générique"""
    ...

@dataclass
class Thing:
    """Pas expressif"""
    ...

# Noms techniques au lieu de métier
def get_nodes_by_type(self, node_type: str) -> List:
    """Devrait être get_functions() ou get_statements()"""
    ...
```

---

## Clean Code

### Noms significatifs

Les noms doivent révéler l'intention. Préférer la clarté à la brièveté.

**✅ Bon exemple :**

```python
def get_high_complexity_functions(
    self, 
    cyclo_threshold: int = 10, 
    cognitive_threshold: int = 15
) -> List[tuple]:
    """Nom explicite, paramètres clairs"""
    ...

def _find_function_body(self, func_node: Node) -> Optional[Node]:
    """Nom privé avec underscore, intention claire"""
    ...
```

**❌ À éviter :**

```python
def get_hc(self, ct: int, cgt: int) -> List:
    """Abbréviations cryptiques"""
    ...

def find(self, n: Node) -> Node:
    """Nom trop générique"""
    ...
```

### Fonctions courtes et focalisées

Une fonction doit faire **une seule chose** et la faire bien. Préférer plusieurs petites fonctions à une grande.

**✅ Bon exemple :**

```python
def analyze(self, source: str) -> MemoryAnalysisResult:
    """Orchestre l'analyse, délègue aux méthodes spécialisées"""
    self.result = MemoryAnalysisResult()
    self._lines = source.split('\n')
    self._allocations = {}
    
    self._find_allocations(source)
    self._find_frees(source)
    self._check_null_verifications(source)
    self._find_dangerous_functions(source)
    self._check_sizeof_pointer(source)
    self._report_unfreed_allocations()
    
    return self.result

def _find_allocations(self, source: str) -> None:
    """Responsabilité unique : trouver les allocations"""
    ...
```

**❌ À éviter :**

```python
def analyze(self, source: str) -> MemoryAnalysisResult:
    """Fait tout dans une seule méthode, difficile à tester et maintenir"""
    # 200 lignes de code mélangeant parsing, détection, reporting
    ...
```

### Commentaires utiles

Les commentaires doivent expliquer le **pourquoi**, pas le **quoi**. Le code doit être auto-documenté.

**✅ Bon exemple :**

```python
# Structures qui incrémentent la complexité ET augmentent l'imbrication
NESTING_STRUCTURES = {
    'if_statement',
    'while_statement', 
    'for_statement',
    ...
}

# else: +1 mais garde le même niveau pour son contenu
complexity += 1
for subchild in child.children:
    if subchild.type == 'compound_statement':
        complexity += self._calculate_recursive(subchild, nesting_level + 1)
```

**❌ À éviter :**

```python
# Incrémente la complexité
complexity += 1  # Le code le montre déjà, commentaire inutile

# Trouve les fonctions
def get_functions(self):  # Nom déjà explicite
    ...
```

### Éviter les commentaires d'algorithme

**Règle importante :** Les commentaires qui décrivent **comment** le code fonctionne (commentaires d'algorithme) doivent être évités. Privilégier les **bons nommages** et l'**extraction de fonctions ou variables** pour rendre le code auto-documenté.

Si vous ressentez le besoin d'ajouter un commentaire pour expliquer un algorithme complexe, c'est souvent un signe que le code doit être refactoré avec des noms plus expressifs ou des fonctions extraites.

**✅ Bon exemple :**

```python
# Utilisation de noms expressifs et extraction de fonctions
def calculate_cyclomatic_complexity(self, function: FunctionInfo) -> int:
    """Calcule la complexité cyclomatique d'une fonction"""
    complexity = self._base_complexity()
    
    for node in self._walk_function_body(function):
        if self._is_decision_point(node):
            complexity += self._get_decision_complexity(node)
    
    return complexity

def _is_decision_point(self, node: Node) -> bool:
    """Vérifie si un nœud représente un point de décision"""
    return node.type in DECISION_NODE_TYPES

def _get_decision_complexity(self, node: Node) -> int:
    """Retourne la complexité ajoutée par ce point de décision"""
    if node.type == 'if_statement':
        return self._calculate_if_complexity(node)
    elif node.type == 'while_statement':
        return self._calculate_loop_complexity(node)
    return 1
```

**❌ À éviter :**

```python
# Commentaires d'algorithme qui décrivent le "comment"
def calculate_cyclomatic_complexity(self, function: FunctionInfo) -> int:
    """Calcule la complexité cyclomatique d'une fonction"""
    # On commence avec une complexité de base de 1
    complexity = 1
    
    # On parcourt tous les nœuds du corps de la fonction
    for node in self._walk_function_body(function):
        # Si c'est un if, while, for, case, ||, &&, ou ?:, on incrémente
        if node.type in ['if_statement', 'while_statement', 'for_statement', 
                         'case_statement', 'logical_or', 'logical_and', 'conditional_expression']:
            # On ajoute 1 à la complexité pour chaque point de décision
            complexity += 1
    
    return complexity
```

**✅ Refactorisation avec extraction de variables :**

```python
# Au lieu de commenter, extraire des variables expressives
def process_high_complexity_functions(self, threshold: int) -> List[FunctionMetrics]:
    """Traite les fonctions dépassant le seuil de complexité"""
    high_complexity_functions = [
        func for func in self.functions 
        if func.cyclomatic_complexity > threshold
    ]
    
    return self._generate_report_for(high_complexity_functions)
```

**❌ À éviter :**

```python
# Commentaire d'algorithme inutile
def process_high_complexity_functions(self, threshold: int) -> List[FunctionMetrics]:
    """Traite les fonctions dépassant le seuil de complexité"""
    # On filtre les fonctions dont la complexité cyclomatique dépasse le seuil
    result = []
    for func in self.functions:
        if func.cyclomatic_complexity > threshold:
            result.append(func)
    
    # On génère un rapport pour ces fonctions
    return self._generate_report_for(result)
```

**Principe clé :** Si un commentaire décrit **ce que fait** le code ou **comment** il le fait, le code doit être refactoré pour être auto-documenté. Les commentaires doivent uniquement expliquer le **pourquoi** (raisons métier, contraintes, décisions de design).

### Formatage cohérent

Utiliser des outils automatiques pour le formatage (Black) et le linting (Ruff).

**Configuration recommandée :**

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py39']

[tool.ruff]
line-length = 100
target-version = "py39"
```

### Gestion d'erreurs explicite

Gérer les erreurs de manière explicite, avec des messages clairs.

**✅ Bon exemple :**

```python
def analyze_file(self, filepath: str) -> FileMetrics:
    path = Path(filepath)
    
    if not path.exists():
        return FileMetrics(
            filepath=str(path),
            total_lines=0,
            non_empty_lines=0,
            parse_errors=True,
            error_message=f"File not found: {filepath}"
        )
    
    try:
        source = path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return FileMetrics(
            filepath=str(path),
            total_lines=0,
            non_empty_lines=0,
            parse_errors=True,
            error_message=f"Cannot read file: {e}"
        )
    
    return self.analyze_source(source, str(path))
```

**❌ À éviter :**

```python
def analyze_file(self, filepath: str) -> FileMetrics:
    source = Path(filepath).read_text()  # Peut lever une exception non gérée
    return self.analyze_source(source, filepath)
```

---

## Quatre règles de conception simple

Les **quatre règles de conception simple** de Kent Beck et Martin Fowler doivent guider toutes les décisions de design.

### Règle 1 : Runs all the tests

Le code doit être **testable** et **testé**. Les tests doivent passer.

**✅ Bon exemple :**

```python
# Code testable : pas de dépendances cachées
class CyclomaticCalculator:
    def __init__(self, parser: ProCParser):
        self.parser = parser  # Injection de dépendance
    
    def calculate(self, function: FunctionInfo) -> int:
        # Méthode pure, facile à tester
        ...

# Tests complets
def test_calculate_simple_function():
    parser = ProCParser()
    parser.parse("int add(int a, int b) { return a + b; }")
    calc = CyclomaticCalculator(parser)
    func = parser.get_functions()[0]
    assert calc.calculate(func) == 1
```

**❌ À éviter :**

```python
# Code difficile à tester : dépendances globales
class CyclomaticCalculator:
    def calculate(self, function: FunctionInfo) -> int:
        parser = ProCParser()  # Création interne, non testable
        global_state.modify()  # Side effect, tests fragiles
        ...
```

### Règle 2 : Contains no duplication

**DRY** (Don't Repeat Yourself). Éliminer toute duplication de code.

**✅ Bon exemple :**

```python
# Pattern réutilisable
def _calculate_recursive(self, node: Node, nesting_level: int) -> int:
    """Méthode récursive générique pour différents types de nœuds"""
    complexity = 0
    
    if node.type in self.NESTING_STRUCTURES:
        complexity += 1 + nesting_level
        # Traitement récursif
        ...
    
    return complexity
```

**❌ À éviter :**

```python
# Duplication de code
def calculate_if(self, node: Node, level: int) -> int:
    complexity = 1 + level
    for child in node.children:
        if child.type == 'compound_statement':
            complexity += self.calculate_if(child, level + 1)
    return complexity

def calculate_while(self, node: Node, level: int) -> int:
    complexity = 1 + level  # Code dupliqué
    for child in node.children:
        if child.type == 'compound_statement':
            complexity += self.calculate_while(child, level + 1)  # Code dupliqué
    return complexity
```

### Règle 3 : Expresses intent

Le code doit être **lisible** et **expressif**. Il doit révéler l'intention.

**✅ Bon exemple :**

```python
# Code expressif
@property
def avg_cyclomatic(self) -> float:
    """Calcule la complexité cyclomatique moyenne"""
    if not self.functions:
        return 0.0
    return sum(f.cyclomatic_complexity for f in self.functions) / len(self.functions)

# Comparaison claire
if (func.cyclomatic_complexity > cyclo_threshold or 
    func.cognitive_complexity > cognitive_threshold):
    results.append((file.filepath, func))
```

**❌ À éviter :**

```python
# Code cryptique
def ac(self) -> float:
    if not self.f:
        return 0.0
    return sum(x.c for x in self.f) / len(self.f)

# Logique complexe non expliquée
if f.c > ct or f.cc > cct:
    r.append((fp, f))
```

### Règle 4 : Minimizes classes and methods

**YAGNI** (You Aren't Gonna Need It). Ne pas créer de classes ou méthodes "au cas où".

**✅ Bon exemple :**

```python
# Classe simple, fait ce qui est nécessaire
@dataclass
class FunctionMetrics:
    name: str
    start_line: int
    cyclomatic_complexity: int
    # Pas de champs "futurs" inutiles
```

**❌ À éviter :**

```python
# Classe avec trop de champs "au cas où"
@dataclass
class FunctionMetrics:
    name: str
    start_line: int
    cyclomatic_complexity: int
    future_field_1: Optional[str] = None  # Pas utilisé
    future_field_2: Optional[Dict] = None  # Pas utilisé
    metadata: Optional[Dict] = None  # Pas utilisé
```

---

## Typage et TypeGuard

### Utilisation systématique des annotations de type

Toutes les fonctions publiques doivent avoir des annotations de type complètes.

**✅ Bon exemple :**

```python
from typing import List, Dict, Optional, Iterator
from tree_sitter import Node

def get_functions(self) -> List[FunctionInfo]:
    """Type de retour explicite"""
    ...

def analyze_file(self, filepath: str) -> FileMetrics:
    """Paramètres et retour typés"""
    ...

def get_high_complexity_functions(
    self, 
    cyclo_threshold: int = 10, 
    cognitive_threshold: int = 15
) -> List[tuple]:
    """Tous les paramètres typés"""
    ...
```

**❌ À éviter :**

```python
# Pas d'annotations de type
def get_functions(self):
    ...

def analyze_file(self, filepath):
    ...
```

### TypeGuard pour le narrowing de types

Utiliser `TypeGuard` pour affiner les types dans les fonctions de vérification.

**✅ Bon exemple :**

```python
from typing import TypeGuard

def is_valid_function_info(obj: Any) -> TypeGuard[FunctionInfo]:
    """Vérifie et affinit le type"""
    return (
        isinstance(obj, FunctionInfo) and
        hasattr(obj, 'name') and
        hasattr(obj, 'start_line')
    )

# Utilisation
def process_function(func: Any) -> None:
    if is_valid_function_info(func):
        # Ici, func est de type FunctionInfo (narrowing)
        print(func.name)  # Type checker sait que func a .name
```

### Utilisation de Protocol pour les interfaces

Utiliser `typing.Protocol` pour définir des interfaces sans héritage.

**✅ Bon exemple :**

```python
from typing import Protocol

class Calculator(Protocol):
    """Interface pour les calculateurs de complexité"""
    def calculate(self, function: FunctionInfo) -> int:
        """Calcule la complexité d'une fonction"""
        ...

# Implémentation
class CyclomaticCalculator:
    def calculate(self, function: FunctionInfo) -> int:
        """Implémente Calculator"""
        ...

# Utilisation polymorphe
def analyze_complexity(
    calculator: Calculator, 
    function: FunctionInfo
) -> int:
    """Fonctionne avec tout Calculator"""
    return calculator.calculate(function)
```

### Types union et optionnels

Utiliser `Optional[T]` pour les valeurs qui peuvent être `None`, et `Union[T, U]` pour les types multiples.

**✅ Bon exemple :**

```python
from typing import Optional, Union

@dataclass
class FileMetrics:
    filepath: str
    module_info: Optional[Dict] = None  # Peut être None
    cursor_analysis: Optional[Dict] = None

def find_node(
    self, 
    node_type: str, 
    root: Optional[Node] = None
) -> Optional[Node]:
    """Retourne None si non trouvé"""
    ...

# Union pour plusieurs types possibles
def process_value(value: Union[str, int, float]) -> str:
    """Accepte plusieurs types"""
    return str(value)
```

### Exemples avec le code existant

Le projet utilise déjà de bonnes pratiques de typage :

```python
# analyzer.py
@dataclass
class FunctionMetrics:
    name: str
    start_line: int
    end_line: int
    halstead: Optional[Dict] = None  # Type optionnel

def analyze_directory(
    self, 
    directory: str, 
    pattern: str = "*.pc",
    recursive: bool = True
) -> AnalysisReport:  # Type de retour explicite
    ...

# parser.py
def get_functions(self) -> List[FunctionInfo]:  # Liste typée
    ...

def walk(self, node: Optional[Node] = None) -> Iterator[Node]:  # Iterator typé
    ...
```

---

## Architecture et organisation

### Structure modulaire

Un module = une responsabilité. Chaque module doit avoir un objectif clair.

**Structure actuelle :**

```
proc_analyzer/
├── preprocessor.py   # Neutralise EXEC SQL → C parsable
├── parser.py         # AST via tree-sitter
├── cyclomatic.py     # Calcul complexité cyclomatique
├── cognitive.py      # Calcul complexité cognitive
├── halstead.py       # Métriques Halstead
├── comments.py       # Analyse TODO/FIXME + modules
├── cursors.py        # Détection curseurs SQL
├── memory.py         # Analyse sécurité mémoire
├── analyzer.py        # Orchestration
└── cli.py            # Interface utilisateur
```

**✅ Bon exemple :**

```python
# cyclomatic.py : fait uniquement le calcul cyclomatique
class CyclomaticCalculator:
    """Responsabilité unique : calculer la complexité cyclomatique"""
    ...

# cognitive.py : fait uniquement le calcul cognitif
class CognitiveCalculator:
    """Responsabilité unique : calculer la complexité cognitive"""
    ...
```

### Séparation des préoccupations

Séparer clairement :

- **Parsing** : extraction de l'AST (`parser.py`)
- **Calcul** : métriques (`cyclomatic.py`, `cognitive.py`, `halstead.py`)
- **Analyse** : détection de problèmes (`memory.py`, `cursors.py`)
- **Orchestration** : coordination (`analyzer.py`)
- **Présentation** : affichage (`cli.py`)

### Utilisation de dataclasses

Utiliser `@dataclass` pour les structures de données immutables ou mutables simples.

**✅ Bon exemple :**

```python
from dataclasses import dataclass, field

@dataclass
class FunctionMetrics:
    """Métriques pour une fonction"""
    name: str
    start_line: int
    end_line: int
    line_count: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    sql_blocks_count: int = 0
    halstead: Optional[Dict] = None
    
    @property
    def avg_complexity(self) -> float:
        """Properties pour les calculs dérivés"""
        return (self.cyclomatic_complexity + self.cognitive_complexity) / 2
```

### Patterns utilisés

**Pattern Strategy** pour les calculateurs :

```python
# Interface commune (implicite via Protocol)
class CyclomaticCalculator:
    def calculate(self, function: FunctionInfo) -> int:
        ...

class CognitiveCalculator:
    def calculate(self, function: FunctionInfo) -> int:
        ...

# Utilisation dans analyzer.py
cyclo_calc = CyclomaticCalculator(self.parser)
cognitive_calc = CognitiveCalculator(self.parser)

for func in self.parser.get_functions():
    func_metrics.cyclomatic_complexity = cyclo_calc.calculate(func)
    func_metrics.cognitive_complexity = cognitive_calc.calculate(func)
```

---

## Tests

### ⚠️ RÈGLE OBLIGATOIRE : Tests requis

**IMPORTANT : Toute nouvelle fonctionnalité, classe ou module DOIT être accompagné de tests unitaires.**

- ❌ **Interdit** : Ajouter du code sans tests correspondants
- ✅ **Obligatoire** : Pour chaque nouvelle fonctionnalité, créer ou mettre à jour les tests correspondants
- ✅ **Validation** : Les tests doivent passer avant de considérer une fonctionnalité comme terminée

**Workflow obligatoire :**

1. Écrire le code de la fonctionnalité
2. **Immédiatement après**, écrire les tests unitaires
3. Vérifier que tous les tests passent (`pytest`)
4. Vérifier la couverture (`pytest --cov`)

### Couverture de tests

Viser une couverture de **80% minimum** pour le code de production. Les tests critiques (parsing, calculs) doivent être à **100%**.

### Tests unitaires

Chaque module doit avoir ses tests unitaires correspondants. **Les tests doivent être créés en même temps que le code, pas après.**

**Structure :**

```
tests/
├── test_analyzer.py
├── test_parser.py
├── test_cyclomatic.py
├── test_cognitive.py
├── test_halstead.py
├── test_memory.py
├── test_cursors.py
└── test_comments.py
```

**✅ Bon exemple :**

```python
# tests/test_cyclomatic.py
def test_calculate_simple_function():
    """Test d'une fonction simple (complexité = 1)"""
    parser = ProCParser()
    parser.parse("int add(int a, int b) { return a + b; }")
    calc = CyclomaticCalculator(parser)
    func = parser.get_functions()[0]
    assert calc.calculate(func) == 1

def test_calculate_with_if():
    """Test avec une condition (complexité = 2)"""
    source = """
    int max(int a, int b) {
        if (a > b) {
            return a;
        }
        return b;
    }
    """
    parser = ProCParser()
    parser.parse(source)
    calc = CyclomaticCalculator(parser)
    func = parser.get_functions()[0]
    assert calc.calculate(func) == 2
```

### Tests d'intégration

Tester les workflows complets, de l'analyse d'un fichier au rapport final.

**✅ Bon exemple :**

```python
# tests/test_analyzer.py
def test_analyze_file_complete_workflow(tmp_proc_file):
    """Test du workflow complet d'analyse"""
    analyzer = ProCAnalyzer()
    metrics = analyzer.analyze_file(str(tmp_proc_file))
    
    assert metrics is not None
    assert metrics.filepath == str(tmp_proc_file)
    assert len(metrics.functions) > 0
    assert metrics.avg_cyclomatic >= 0
```

### Utilisation de fixtures pytest

Utiliser des fixtures pour éviter la duplication dans les tests.

**✅ Bon exemple :**

```python
# tests/conftest.py
@pytest.fixture
def simple_proc_source():
    """Source Pro*C simple pour les tests"""
    return """
    EXEC SQL BEGIN DECLARE SECTION;
    int emp_id;
    EXEC SQL END DECLARE SECTION;
    
    int get_employee(int id) {
        EXEC SQL SELECT name INTO :emp_id FROM employees WHERE id = :id;
        return emp_id;
    }
    """

@pytest.fixture
def tmp_proc_file(tmp_path, simple_proc_source):
    """Fichier Pro*C temporaire pour les tests"""
    file = tmp_path / "test.pc"
    file.write_text(simple_proc_source)
    return file
```

### Checklist avant commit

Avant de considérer une fonctionnalité comme terminée, vérifier :

- [ ] Tests unitaires créés pour toutes les nouvelles fonctions/classes
- [ ] Tests d'intégration pour les nouveaux workflows
- [ ] Tous les tests passent (`pytest`)
- [ ] Couverture de code >= 80% (`pytest --cov`)
- [ ] Aucun test existant n'a été cassé

---

## Documentation

### Docstrings

Utiliser le style **Google** pour les docstrings (cohérent avec le code existant).

**✅ Bon exemple :**

```python
def calculate(self, function: FunctionInfo) -> int:
    """
    Calcule la complexité cognitive d'une fonction.
    
    Args:
        function: Information sur la fonction à analyser
        
    Returns:
        Complexité cognitive
        
    Raises:
        ValueError: Si la fonction n'a pas de corps
    """
    ...
```

**Format pour les classes :**

```python
class CognitiveCalculator:
    """
    Calcule la complexité cognitive selon les principes SonarSource.
    
    Cette métrique évalue l'effort mental nécessaire pour comprendre le code,
    en pénalisant particulièrement les structures imbriquées.
    
    Attributes:
        parser: Parser avec le code source analysé
        _cache: Cache des résultats pour éviter les recalculs
    """
    ...
```

### Documentation des APIs publiques

Toutes les fonctions et classes publiques doivent être documentées.

**Modules à documenter :**

- `__init__.py` : exports publics
- Classes publiques : `ProCAnalyzer`, `ProCParser`, etc.
- Méthodes publiques : toutes les méthodes non préfixées par `_`

### Exemples d'utilisation

Inclure des exemples dans la documentation ou le README.

**✅ Bon exemple (déjà présent dans README.md) :**

```python
from proc_analyzer import ProCAnalyzer

analyzer = ProCAnalyzer(
    enable_halstead=True,
    enable_todos=True,
    enable_cursors=True,
    enable_memory=True,
)

# Analyser un fichier
metrics = analyzer.analyze_file('program.pc')
print(f"Fonctions: {metrics.function_count}")
print(f"TODOs: {metrics.todo_count}")
```

---

## Outils et configuration

### Linters

**Ruff** : linter rapide et moderne (remplace flake8, isort, etc.)

**Configuration recommandée (`pyproject.toml`) :**

```toml
[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = [
    "E501",  # line too long (géré par black)
]

[tool.ruff.lint.isort]
known-first-party = ["proc_analyzer"]
```

### Type checking

**mypy** : vérification statique des types

**Configuration recommandée (`pyproject.toml`) :**

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Progressif
disallow_incomplete_defs = false
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
```

### Formatters

**Black** : formateur de code automatique

**Configuration recommandée (`pyproject.toml`) :**

```toml
[tool.black]
line-length = 100
target-version = ['py39']
include = '\.pyi?$'
```

### Pre-commit hooks (recommandé)

Créer un fichier `.pre-commit-config.yaml` :

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### Commandes utiles

```bash
# Formater le code
black proc_analyzer/ tests/

# Linter
ruff check proc_analyzer/ tests/

# Type checking
mypy proc_analyzer/

# Tests
pytest tests/ -v --cov=proc_analyzer

# Tout en une fois (recommandé avant commit)
black . && ruff check . && mypy proc_analyzer/ && pytest
```

---

## Conclusion

Ces standards de code visent à maintenir la qualité, la maintenabilité et la cohérence du projet. Ils doivent être appliqués progressivement et peuvent évoluer avec le projet.

**Rappel des principes clés :**

1. **CUPID** : Composable, Unix philosophy, Predictable, Idiomatic, Domain-based
2. **Clean Code** : Noms clairs, fonctions courtes, commentaires utiles
3. **4 règles simples** : Tests, pas de duplication, expressif, minimal
4. **Typage** : Annotations complètes, TypeGuard, Protocol
5. **Architecture** : Modules focalisés, séparation des préoccupations
6. **Tests** : Couverture élevée, tests unitaires et d'intégration
7. **Documentation** : Docstrings complètes, exemples d'utilisation
8. **Outils** : Ruff, mypy, Black pour automatiser la qualité

---

Dernière mise à jour : 2024
