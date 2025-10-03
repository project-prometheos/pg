# WeBWorK PG Port: Perl to Python Migration Plan

**Version**: 1.0
**Date**: October 2, 2025
**Status**: Planning Phase
**Goal**: Achieve 100% parity between legacy Perl PG system and modern Python implementation

---

## Executive Summary

The WeBWorK Problem Generator (PG) is undergoing a migration from a mature **~133,000 line Perl codebase** to a modern Python implementation. Currently, the Python implementation consists of **~3,800 lines** representing approximately **2.8% completion** by line count.

**Current State**:
- ✅ **problemkit**: Framework-agnostic Python authoring API (complete for its scope)
- 🟡 **pg_renderer**: Basic MVP (~10-15% of full PG capability)
- ✅ **backend**: FastAPI service layer (complete for current features)

**Estimated Timeline**: 24-33 months for full parity (2-2.75 years)
**Recommended Strategy**: Hybrid approach (Python-first for new problems, Perl bridge for legacy)

---

## Table of Contents

1. [Current System Inventory](#1-current-system-inventory)
2. [Gap Analysis](#2-gap-analysis)
3. [Architecture Design (SOLID Principles)](#3-architecture-design-solid-principles)
4. [Implementation Phases](#4-implementation-phases)
5. [Technical Challenges & Solutions](#5-technical-challenges--solutions)
6. [Testing Strategy](#6-testing-strategy)
7. [Risk Management](#7-risk-management)
8. [Success Metrics](#8-success-metrics)
9. [File Mapping Reference](#9-file-mapping-reference)

---

## 1. Current System Inventory

### 1.1 Legacy Perl System (~133,000 lines)

#### Core Components

| Component | Lines | Purpose | Complexity |
|-----------|-------|---------|------------|
| **Parser.pm** | 908 | Expression tokenization & AST construction | High |
| **Value.pm** + subtypes | ~6,230 | MathObjects system (intelligent math values) | Very High |
| **Translator.pm** | 1,385 | .pg file execution engine | Very High |
| **PGcore.pm** | 785 | Problem environment, answer registration | Medium |
| **PGML.pl** | 2,068 | Problem markup language parser/renderer | High |
| **Context System** | ~3,000 | Mathematical parsing environments | High |
| **Answer Evaluators** | ~10,000 | Type-specific answer checking | Medium |
| **Macro System** | 85,737 | Reusable problem authoring components | Very High |
| **Image Generation** | ~1,500 | LaTeX→PNG, TikZ graphics | Medium |
| **Graph Generation** | ~8,000 | 2D/3D plotting utilities | Medium |
| **Core Utilities** | ~5,000 | Supporting functions | Low-Medium |

**Total**: ~133,164 lines of production Perl code (20+ years of development)

#### Key Subsystems Detail

**Parser/Tokenizer** (`lib/Parser.pm`):
- Regex-based tokenization with context-aware patterns
- Recursive descent parsing with operator precedence
- Implicit multiplication handling (`2x` → `2*x`)
- Multiple parenthesis types: `()`, `[]`, `{}`, `||`
- Error reporting with position tracking
- Multiple output formats: eval, string, TeX, Perl

**MathObjects** (`lib/Value.pm` + `lib/Value/*.pm`):
- Type hierarchy with precedence: Number → Real → Complex → Point → Vector → Matrix → List → Interval → Set → Union → String → Formula
- Operator overloading (all Perl operators)
- Fuzzy comparison with configurable tolerances
- Automatic type promotion
- Context-aware behavior
- Built-in answer checking

**Context System** (`lib/Parser/Context.pm`):
- Defines allowed variables, constants, functions
- Operator precedence and associativity
- Reduction rules (simplification)
- Tolerance modes (relative, absolute, significant digits)
- Extensible via custom contexts

**PGML** (`macros/core/PGML.pl`):
- Markdown-like syntax for problem authoring
- Variable interpolation: `[$var]`
- Answer blanks: `[_____]`, `[@ ans_rule() @]`
- Auto-formatting (bold, italic, lists, tables)
- Math rendering (inline/display)
- Nested structures

**Macro System** (`macros/`):
- 85,737 lines across hundreds of `.pl` files
- Organized by category: core, contexts, parsers, math, graph, ui, answers
- Loaded dynamically via `loadMacros()`
- Provides problem authoring DSL

### 1.2 Modern Python System (~3,800 lines)

#### Implemented Components

**problemkit** (`packages/problemkit/` - 168 lines):
- ✅ Pydantic models: `ProblemInstance`, `InputSpec`
- ✅ `@problem` decorator for authoring
- ✅ Problem registry with variant IDs
- ✅ Deterministic RNG wrapper
- ✅ Sample problems using SymPy

**Purpose**: Pure Python authoring API (NOT a Perl port, new paradigm)

**pg_renderer** (`packages/pg_renderer/` - ~1,335 lines):
- 🟡 `parser.py` (65 lines): Basic PG file section extraction
- 🟡 `evaluator.py` (119 lines): Simplified variable evaluation
  - Basic assignments: `$var = expr`
  - Simple function calls: `random()`, `Formula()`, `Compute()`
  - Context detection (incomplete)
- 🟡 `pgml.py`: Partial PGML renderer
- 🟡 `context.py` (35 lines): Stub only
- ✅ `random.py`: Seeded RNG
- 🟡 `answer_checker.py`: Basic numeric/formula/interval checking

**Missing Critical Components**:
- ❌ Full Perl execution engine
- ❌ Mathematical expression parser/tokenizer
- ❌ MathObjects system (no Value.pm equivalent)
- ❌ Full Context system
- ❌ Macro loading/execution
- ❌ Most PGML features
- ❌ Image generation
- ❌ Comprehensive answer evaluator framework

**backend** (`apps/backend/` - ~2,298 lines):
- ✅ FastAPI application structure
- ✅ REST API routers (problems, solutions, checks, health)
- ✅ Database search integration (SQLite/Chroma)
- ✅ `PGRenderService` wrapper
- ✅ Pydantic schemas for API contracts

---

## 2. Gap Analysis

### 2.1 Coverage Matrix

| Component | Perl (LOC) | Python (LOC) | Coverage | Status |
|-----------|-----------|--------------|----------|--------|
| Parser/Tokenizer | 908 | 0 | 0% | ❌ Not started |
| MathObjects | 6,230 | 0 | 0% | ❌ Not started |
| PG Translator | 1,385 | ~200 | ~14% | 🟡 Stub only |
| PGML Parser | 2,068 | ~400 | ~19% | 🟡 Partial |
| Context System | 3,000 | 35 | ~1% | 🟡 Stub only |
| Answer Evaluators | 10,000 | ~200 | ~2% | 🟡 Basic types only |
| Macro System | 85,737 | 0 | 0% | ❌ Not started |
| Image Generation | 1,500 | 0 | 0% | ❌ Not started |
| Graph Generation | 8,000 | 0 | 0% | ❌ Not started |
| Core Utilities | 5,000 | ~200 | ~4% | 🟡 Minimal |
| **TOTAL** | **133,164** | **~1,800** | **~1.4%** | **Planning** |

### 2.2 Critical Missing Functionality

**Blocking Items** (cannot render most problems without these):
1. **Expression Parser**: Cannot parse mathematical expressions (`2*x + sin(pi)`)
2. **MathObjects**: No intelligent value types (Real, Complex, Vector, etc.)
3. **Full Context System**: Cannot configure parsing environments
4. **PGML**: Only partial implementation
5. **Perl Code Execution**: Cannot execute .pg file Perl code

**High Priority** (needed for common problems):
6. **Answer Evaluators**: Limited to basic numeric/formula checking
7. **Core Macros**: Most macros not implemented
8. **Full Translator**: Cannot process complex .pg files

**Medium Priority** (needed for specialized problems):
9. **Image Generation**: No LaTeX rendering
10. **Graph Generation**: No plotting capabilities

---

## 3. Architecture Design (SOLID Principles)

### 3.1 Recommended Layered Architecture

```
┌────────────────────────────────────────────────────────┐
│              Presentation Layer (FastAPI)              │
│  • REST API endpoints                                  │
│  • Request/response serialization (Pydantic)           │
│  • Authentication/authorization                        │
└────────────────────────────────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│            Application Layer (Use Cases)               │
│  • ProblemGenerationUseCase                            │
│  • AnswerCheckingUseCase                               │
│  • SolutionRenderingUseCase                            │
│  • Workflow orchestration                              │
└────────────────────────────────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│                   Domain Layer                         │
│  ┌──────────────┬──────────────┬──────────────────┐   │
│  │ Parser       │ MathObjects  │ Answer Checking  │   │
│  │              │              │                  │   │
│  │ • Tokenizer  │ • Value      │ • Evaluators     │   │
│  │ • AST        │ • Real       │ • Comparators    │   │
│  │ • Context    │ • Complex    │ • Graders        │   │
│  │ • Evaluator  │ • Vector     │ • Partial Credit │   │
│  │              │ • Formula    │                  │   │
│  └──────────────┴──────────────┴──────────────────┘   │
│  ┌──────────────┬──────────────┬──────────────────┐   │
│  │ PGML         │ PG           │ Macro System     │   │
│  │              │ Translator   │                  │   │
│  │ • Parser     │ • Preproc    │ • Registry       │   │
│  │ • Renderer   │ • Executor   │ • Loader         │   │
│  │ • Formatter  │ • Sandbox    │ • Core Macros    │   │
│  └──────────────┴──────────────┴──────────────────┘   │
└────────────────────────────────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│             Infrastructure Layer                       │
│  • Rendering (HTML, TeX, PTX)                          │
│  • Image generation (LaTeX → SVG)                      │
│  • Graph generation (matplotlib, plotly)               │
│  • Caching (Redis, diskcache)                          │
│  • Persistence (SQLite, PostgreSQL)                    │
│  • External services (KaTeX, MathJax)                  │
└────────────────────────────────────────────────────────┘
```

### 3.2 SOLID Principles Application

#### **S - Single Responsibility Principle**

**Problem**: Perl `Translator.pm` does everything (parsing, execution, evaluation, rendering)

**Solution**: Separate concerns into focused classes

```python
# Each class has ONE responsibility

class PGTokenizer:
    """ONLY tokenizes PG file content"""
    def tokenize(self, source: str) -> list[Token]:
        ...

class PGParser:
    """ONLY builds AST from tokens"""
    def parse(self, tokens: list[Token]) -> PGProblemAST:
        ...

class PGEvaluator:
    """ONLY evaluates expressions"""
    def eval(self, ast: ASTNode, context: Context) -> MathValue:
        ...

class PGRenderer:
    """ONLY generates output (HTML/TeX)"""
    def render(self, problem: Problem, format: str) -> str:
        ...

class PGProblemExecutor:
    """Orchestrates the pipeline (composition)"""
    def __init__(self, tokenizer, parser, evaluator, renderer):
        self.tokenizer = tokenizer
        self.parser = parser
        self.evaluator = evaluator
        self.renderer = renderer
```

#### **O - Open/Closed Principle**

**Principle**: Open for extension, closed for modification

**Solution**: Use Strategy Pattern for pluggable behaviors

```python
# Base strategy (abstract)
class AnswerEvaluator(ABC):
    @abstractmethod
    def check(
        self,
        student_answer: str,
        correct_answer: str,
        context: Context
    ) -> AnswerResult:
        pass

# Concrete strategies (extensible without modifying base)
class NumericEvaluator(AnswerEvaluator):
    def check(self, student, correct, context) -> AnswerResult:
        # Numeric-specific logic with tolerances
        ...

class FormulaEvaluator(AnswerEvaluator):
    def check(self, student, correct, context) -> AnswerResult:
        # Symbolic + test point evaluation
        ...

class IntervalEvaluator(AnswerEvaluator):
    def check(self, student, correct, context) -> AnswerResult:
        # Set-based comparison
        ...

# Registry for dynamic dispatch
class EvaluatorRegistry:
    def register(self, type_name: str, evaluator: AnswerEvaluator):
        ...

    def get(self, type_name: str) -> AnswerEvaluator:
        ...
```

**Context Configuration**: Data-driven (YAML/JSON, not code)

```yaml
# contexts/numeric.yaml
name: Numeric
variables: [x, y, z, t]
constants:
  pi: 3.14159265358979
  e: 2.71828182845905
functions:
  - sin, cos, tan
  - sqrt, exp, ln, log
operators:
  - symbol: "+"
    precedence: 1
    associativity: left
  - symbol: "*"
    precedence: 3
    associativity: left
tolerances:
  relative: 0.001
  absolute: 0.0001
```

#### **L - Liskov Substitution Principle**

**Principle**: Subtypes must be substitutable for their base types

**Solution**: Proper inheritance hierarchy with consistent behavior

```python
class MathValue(ABC):
    """Base for all mathematical values"""

    @abstractmethod
    def promote(self, other: 'MathValue') -> 'MathValue':
        """Type promotion (e.g., Real + Complex → Complex)"""
        pass

    @abstractmethod
    def compare(self, other: 'MathValue', tolerance: float) -> bool:
        """Fuzzy comparison"""
        pass

    @abstractmethod
    def to_tex(self) -> str:
        """LaTeX representation"""
        pass

    # All subclasses implement these consistently

class Real(MathValue):
    def __init__(self, value: float):
        self.value = value

    def promote(self, other: MathValue) -> MathValue:
        if isinstance(other, Complex):
            return Complex(self.value, 0)
        elif isinstance(other, Vector):
            raise TypeError("Cannot promote Real to Vector")
        return self

    def compare(self, other: MathValue, tolerance: float) -> bool:
        # Type promotion ensures same types compared
        promoted = self.promote(other)
        if isinstance(promoted, Real):
            return abs(self.value - promoted.value) < tolerance
        return promoted.compare(other, tolerance)

class Complex(MathValue):
    def __init__(self, real: float, imag: float):
        self.real = real
        self.imag = imag

    def promote(self, other: MathValue) -> MathValue:
        # Complex is higher in hierarchy, no promotion needed
        return self

    def compare(self, other: MathValue, tolerance: float) -> bool:
        # Consistent with Real's interface
        ...

# Substitution works everywhere
def check_answer(student: MathValue, correct: MathValue) -> bool:
    # Works for ANY MathValue subtype
    return student.compare(correct, tolerance=0.01)
```

#### **I - Interface Segregation Principle**

**Principle**: Clients shouldn't depend on interfaces they don't use

**Solution**: Separate interfaces for different capabilities

```python
# Separate protocols for different capabilities

class Evaluable(Protocol):
    """Can be evaluated with variable bindings"""
    def eval(self, bindings: dict[str, MathValue]) -> MathValue:
        ...

class Reducible(Protocol):
    """Can be simplified/reduced"""
    def reduce(self) -> 'ASTNode':
        ...

class Renderable(Protocol):
    """Can be rendered to string formats"""
    def to_string(self) -> str:
        ...

    def to_tex(self) -> str:
        ...

class Differentiable(Protocol):
    """Can be differentiated"""
    def diff(self, var: str) -> 'ASTNode':
        ...

# A Formula might implement ALL of these
class Formula(Evaluable, Reducible, Renderable, Differentiable):
    ...

# But a Number only needs some
class Number(Evaluable, Renderable):
    ...

# Functions can depend on only what they need
def render_problem(obj: Renderable) -> str:
    return obj.to_tex()  # Works with Formula OR Number

def evaluate_at_point(obj: Evaluable, x: float) -> MathValue:
    return obj.eval({'x': Real(x)})  # Only needs Evaluable
```

#### **D - Dependency Inversion Principle**

**Principle**: Depend on abstractions, not concretions

**Solution**: Inject dependencies via constructor

```python
# Define abstract interfaces
class ParserInterface(Protocol):
    def parse(self, source: str) -> ProblemAST:
        ...

class EvaluatorInterface(Protocol):
    def eval(self, ast: ASTNode) -> MathValue:
        ...

class RendererInterface(Protocol):
    def render(self, problem: Problem) -> str:
        ...

# High-level module depends on abstractions
class PGProblemExecutor:
    def __init__(
        self,
        parser: ParserInterface,
        evaluator: EvaluatorInterface,
        renderer: RendererInterface
    ):
        # Depends on INTERFACES, not concrete classes
        self.parser = parser
        self.evaluator = evaluator
        self.renderer = renderer

    def execute(self, pg_file: str) -> str:
        ast = self.parser.parse(pg_file)
        problem = self.evaluator.eval(ast)
        return self.renderer.render(problem)

# Concrete implementations (can swap easily)
class SymPyEvaluator(EvaluatorInterface):
    def eval(self, ast: ASTNode) -> MathValue:
        # SymPy-based implementation
        ...

class NumPyEvaluator(EvaluatorInterface):
    def eval(self, ast: ASTNode) -> MathValue:
        # NumPy-based implementation (faster for numerics)
        ...

# Dependency injection (can swap implementations)
executor = PGProblemExecutor(
    parser=PGParser(),
    evaluator=SymPyEvaluator(),  # or NumPyEvaluator()
    renderer=HTMLRenderer()
)
```

### 3.3 Recommended Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Expression Parsing** | **SymPy** + **pyparsing** | SymPy for symbolic math, pyparsing for custom grammar |
| **Type System** | **Pydantic V2** | Data validation, type coercion, serialization |
| **Pattern Matching** | **Python 3.10+ match/case** | Clean visitor pattern for AST traversal |
| **Numerical Computing** | **NumPy** | Fast vector/matrix operations |
| **Symbolic Math** | **SymPy** | Differentiation, integration, simplification |
| **Dependency Injection** | **Manual + Protocol** | SOLID compliance without framework complexity |
| **Testing** | **pytest** + **hypothesis** | Unit + property-based testing for math |
| **Math Rendering** | **KaTeX.js** (server-side) | Already used in frontend, fast |
| **Graphing** | **matplotlib** + **plotly** | 2D static + interactive |
| **Caching** | **diskcache** or **Redis** | Equation/image caching |
| **Sandboxing** | **RestrictedPython** | Safe Perl-like code execution |

### 3.4 Project Structure (Recommended)

```
packages/
├── pg_parser/               # Phase 1: Parser & AST
│   ├── tokenizer.py         # Regex-based tokenization
│   ├── parser.py            # Recursive descent parser
│   ├── ast.py               # AST node definitions
│   └── context.py           # Context system
│
├── pg_math/                 # Phase 2: MathObjects
│   ├── value.py             # Base MathValue class
│   ├── numeric.py           # Real, Complex, Infinity
│   ├── geometric.py         # Point, Vector, Matrix
│   ├── sets.py              # Interval, Set, Union
│   ├── formula.py           # Formula (wraps AST)
│   └── operators.py         # Operator overloading
│
├── pg_answer/               # Phase 3: Answer Evaluation
│   ├── evaluator.py         # Base AnswerEvaluator
│   ├── answer_hash.py       # AnswerResult data class
│   ├── graders.py           # Problem graders
│   └── evaluators/
│       ├── numeric.py       # NumericEvaluator
│       ├── formula.py       # FormulaEvaluator
│       ├── string.py        # StringEvaluator
│       └── ...
│
├── pg_pgml/                 # Phase 4: PGML
│   ├── tokenizer.py         # PGML tokenizer
│   ├── parser.py            # PGML parser
│   └── renderer.py          # HTML/TeX renderer
│
├── pg_translator/           # Phase 5: Problem Translator
│   ├── preprocessor.py      # BEGIN_TEXT expansion
│   ├── executor.py          # Safe code execution
│   └── translator.py        # Pipeline orchestrator
│
├── pg_macros/               # Phase 6: Macro System
│   ├── registry.py          # Macro loader
│   └── core/
│       ├── pg_standard.py   # Core macros
│       ├── math_objects.py  # MathObjects macros
│       └── ...
│
├── pg_render/               # Phase 7: Image/Graph Gen
│   ├── latex.py             # LaTeX → SVG
│   ├── images.py            # Image caching
│   └── graphs.py            # matplotlib/plotly wrapper
│
└── pg_core/                 # Shared utilities
    ├── rng.py               # Random number generation
    ├── errors.py            # Exception hierarchy
    └── utils.py             # Helpers
```

---

## 4. Implementation Phases

### Phase 1: Core Parser & AST (Foundation)

**Duration**: 3-4 months
**Goal**: Parse mathematical expressions to AST
**Dependencies**: None
**Risk**: Medium

#### Components to Build

1. **Tokenizer** (`pg_parser/tokenizer.py`)
   - Regex-based pattern matching
   - Token types: Number, Variable, Operator, Function, Parenthesis, String
   - Context-aware tokenization (different patterns per context)
   - Position tracking for error reporting
   - **Perl Reference**: `Parser.pm::tokenize()` (lines 100-135)

2. **AST Node Definitions** (`pg_parser/ast.py`)
   ```python
   # Base node
   class ASTNode(ABC):
       @abstractmethod
       def accept(self, visitor: 'ASTVisitor'):
           pass

   # Leaf nodes
   class Number(ASTNode): ...
   class Variable(ASTNode): ...
   class Constant(ASTNode): ...  # pi, e, i
   class String(ASTNode): ...

   # Composite nodes
   class BinaryOp(ASTNode):      # 2 + 3, x * y
       left: ASTNode
       op: str
       right: ASTNode

   class UnaryOp(ASTNode):       # -x, !n
       op: str
       operand: ASTNode

   class FunctionCall(ASTNode):  # sin(x), sqrt(2)
       name: str
       args: list[ASTNode]

   class List(ASTNode):          # [1, 2, 3]
       elements: list[ASTNode]

   # Higher-order nodes
   class Point(ASTNode):         # (x, y)
   class Vector(ASTNode):        # <1, 2, 3>
   class Matrix(ASTNode):        # [[1,2],[3,4]]
   class Interval(ASTNode):      # [0, 1), (-inf, inf)
   ```

3. **Parser** (`pg_parser/parser.py`)
   - Recursive descent with operator precedence (Pratt parsing)
   - Context-driven parsing rules
   - Implicit multiplication: `2x`, `sin x`, `(x+1)(x-1)`
   - Multiple parenthesis types: `()`, `[]`, `{}`, `|x|`
   - Error recovery and reporting
   - **Perl Reference**: `Parser.pm::parse()` (lines 147-171)

4. **Context System** (`pg_parser/context.py`)
   ```python
   @dataclass
   class Context:
       name: str
       variables: dict[str, VariableConfig]
       constants: dict[str, float | complex]
       functions: dict[str, FunctionConfig]
       operators: dict[str, OperatorConfig]
       reduction_rules: list[ReductionRule]
       tolerances: ToleranceConfig

       @classmethod
       def from_yaml(cls, path: str) -> 'Context':
           """Load context from YAML file"""
           ...
   ```
   - Data-driven configuration (YAML files)
   - Built-in contexts: Numeric, Complex, Vector, Matrix, Interval, etc.
   - Extensible for custom contexts
   - **Perl Reference**: `Parser/Context.pm`, `Parser/Context/Default.pm`

5. **AST Visitor Pattern** (for eval, string, TeX)
   ```python
   class ASTVisitor(ABC):
       @abstractmethod
       def visit_number(self, node: Number): ...
       @abstractmethod
       def visit_binary_op(self, node: BinaryOp): ...
       # ... other visit methods

   class StringVisitor(ASTVisitor):
       """Converts AST to string: 2*x + 1"""
       ...

   class TeXVisitor(ASTVisitor):
       """Converts AST to LaTeX: 2x + 1"""
       ...

   class EvalVisitor(ASTVisitor):
       """Evaluates AST to MathValue"""
       ...
   ```

#### Deliverables

- ✅ Parse expressions to AST: `"2*x + sin(pi*x)"` → AST tree
- ✅ Support all standard contexts (Numeric, Complex, Vector, etc.)
- ✅ AST → string, AST → TeX conversion
- ✅ Unit tests with >90% coverage
- ✅ Performance: <10ms for typical expressions

#### Testing Strategy

- **Unit tests**: Port from `t/parser/` directory
- **Property-based**: `parse(str(ast)) == ast` (round-trip)
- **Fuzz testing**: Random expression generation
- **Golden tests**: Compare output to Perl for 100+ expressions

---

### Phase 2: MathObjects & Type System

**Duration**: 4-5 months
**Goal**: Intelligent mathematical value objects
**Dependencies**: Phase 1 (Parser)
**Risk**: High

#### Components to Build

1. **Base Value Class** (`pg_math/value.py`)
   ```python
   class MathValue(ABC):
       """Base for all mathematical values"""

       # Type promotion precedence
       type_precedence: ClassVar[int]

       @abstractmethod
       def promote(self, other: 'MathValue') -> 'MathValue':
           """Type promotion (e.g., Real + Complex → Complex)"""
           pass

       @abstractmethod
       def compare(
           self,
           other: 'MathValue',
           tolerance: float,
           mode: str = 'relative'
       ) -> bool:
           """Fuzzy comparison"""
           pass

       # Operator overloading (Python magic methods)
       @abstractmethod
       def __add__(self, other): ...
       @abstractmethod
       def __mul__(self, other): ...
       # ... all operators

       # Rendering
       @abstractmethod
       def to_string(self) -> str: ...
       @abstractmethod
       def to_tex(self) -> str: ...
   ```

2. **Numeric Types** (`pg_math/numeric.py`)
   - `Real(value: float)`: type_precedence = 1
   - `Complex(real: float, imag: float)`: type_precedence = 3
   - `Infinity(sign: int)`: type_precedence = 2
   - Arithmetic operations with type promotion
   - Fuzzy comparison (relative, absolute, significant digits)
   - **Perl Reference**: `Value/Real.pm`, `Value/Complex.pm`, `Value/Infinity.pm`

3. **Geometric Types** (`pg_math/geometric.py`)
   - `Point(coords: list[Real])`: type_precedence = 4
   - `Vector(components: list[Real])`: type_precedence = 5
   - `Matrix(rows: list[list[Real]])`: type_precedence = 6
   - Dot product, cross product, matrix operations
   - Norm, distance, angle calculations
   - **Perl Reference**: `Value/Point.pm`, `Value/Vector.pm`, `Value/Matrix.pm`

4. **Set Types** (`pg_math/sets.py`)
   - `Interval(left: Real, right: Real, open_left: bool, open_right: bool)`: type_precedence = 8
   - `Set(elements: list[Real])`: type_precedence = 9
   - `Union(sets: list[Interval | Set])`: type_precedence = 10
   - Set operations: intersection, union, complement, contains
   - **Perl Reference**: `Value/Interval.pm`, `Value/Set.pm`, `Value/Union.pm`

5. **List & String Types** (`pg_math/collections.py`)
   - `List(elements: list[MathValue])`: type_precedence = 7
   - `String(value: str)`: type_precedence = 11
   - **Perl Reference**: `Value/List.pm`, `Value/String.pm`

6. **Formula Type** (`pg_math/formula.py`)
   ```python
   class Formula(MathValue):
       """Wraps AST for deferred evaluation"""
       type_precedence = 12

       def __init__(self, ast: ASTNode, context: Context):
           self.ast = ast
           self.context = context

       def eval(self, **bindings) -> MathValue:
           """Evaluate with variable bindings"""
           visitor = EvalVisitor(bindings, self.context)
           return self.ast.accept(visitor)

       def reduce(self) -> 'Formula':
           """Simplify expression"""
           ...

       def substitute(self, var: str, value: MathValue) -> 'Formula':
           """Variable substitution"""
           ...

       def diff(self, var: str) -> 'Formula':
           """Differentiation (using SymPy)"""
           ...
   ```
   - **Perl Reference**: `Value/Formula.pm`

7. **Type Promotion System**
   ```python
   def promote_types(a: MathValue, b: MathValue) -> tuple[MathValue, MathValue]:
       """Promote both to common type"""
       if a.type_precedence < b.type_precedence:
           return a.promote(b), b
       elif b.type_precedence < a.type_precedence:
           return a, b.promote(a)
       return a, b
   ```

#### Deliverables

- ✅ All MathObject types implemented
- ✅ Full operator overloading (+ - * / ** == != < >)
- ✅ Type promotion working correctly
- ✅ Fuzzy comparison with all tolerance modes
- ✅ Formula evaluation, reduction, substitution
- ✅ Unit tests with >90% coverage
- ✅ Performance: <1ms for typical operations

#### Testing Strategy

- **Unit tests**: Port from `t/value/` directory
- **Property-based**: Commutative, associative, distributive laws
- **Tolerance edge cases**: 0.0001 vs 0.00011 with various modes
- **Type promotion**: Ensure hierarchy respected

---

### Phase 3: Answer Evaluation Framework

**Duration**: 2-3 months
**Goal**: Pluggable answer checking system
**Dependencies**: Phase 2 (MathObjects)
**Risk**: Medium

#### Components to Build

1. **Answer Result** (`pg_answer/answer_hash.py`)
   ```python
   @dataclass
   class AnswerResult:
       score: float  # 0.0 to 1.0
       correct: bool
       student_answer: str
       correct_answer: str
       message: str = ""
       preview_latex: str = ""
       student_value: MathValue | None = None
       correct_value: MathValue | None = None
       error: str | None = None
   ```

2. **Base Evaluator** (`pg_answer/evaluator.py`)
   ```python
   class AnswerEvaluator(ABC):
       @abstractmethod
       def check(
           self,
           student_answer: str,
           correct_answer: str | MathValue,
           context: Context,
           **options
       ) -> AnswerResult:
           pass

   class EvaluatorRegistry:
       _evaluators: dict[str, AnswerEvaluator] = {}

       @classmethod
       def register(cls, type_name: str, evaluator: AnswerEvaluator):
           cls._evaluators[type_name] = evaluator

       @classmethod
       def get(cls, type_name: str) -> AnswerEvaluator:
           return cls._evaluators[type_name]
   ```

3. **Type-Specific Evaluators** (`pg_answer/evaluators/`)

   **NumericEvaluator** (`numeric.py`):
   - Parse student answer to number
   - Compare with tolerance (relative/absolute/sig figs)
   - Unit handling (optional)
   - **Perl Reference**: `macros/answers/PGanswermacros.pl::num_cmp()`

   **FormulaEvaluator** (`formula.py`):
   - Parse both student and correct to Formula
   - Symbolic comparison (if possible via SymPy)
   - Test point evaluation (5-10 random points)
   - Derivative checking (for uniqueness)
   - **Perl Reference**: `macros/answers/PGanswermacros.pl::fun_cmp()`

   **StringEvaluator** (`string.py`):
   - Exact match, case-insensitive, regex
   - Whitespace handling
   - **Perl Reference**: `macros/answers/PGanswermacros.pl::str_cmp()`

   **IntervalEvaluator** (`interval.py`):
   - Parse interval notation: `[0, 1)`, `(-inf, 2]`
   - Compare intervals (endpoints + openness)
   - **Perl Reference**: `Value/Interval.pm` answer checker

   **VectorEvaluator** (`vector.py`):
   - Parse vector: `<1, 2, 3>` or `[1, 2, 3]`
   - Component-wise comparison with tolerance
   - Parallel/orthogonal checking (optional)

   **MatrixEvaluator** (`matrix.py`):
   - Parse matrix notation
   - Element-wise comparison
   - Row-reduced echelon form equivalence

4. **Graders** (`pg_answer/graders.py`)
   ```python
   class ProblemGrader(ABC):
       @abstractmethod
       def grade(
           self,
           answer_results: list[AnswerResult],
           weights: list[float] | None = None
       ) -> float:
           """Returns overall problem score (0.0 to 1.0)"""
           pass

   class StandardGrader(ProblemGrader):
       """All-or-nothing: All answers correct = 1.0, else 0.0"""
       def grade(self, answer_results, weights=None):
           return 1.0 if all(r.correct for r in answer_results) else 0.0

   class AverageGrader(ProblemGrader):
       """Weighted average of individual scores"""
       def grade(self, answer_results, weights=None):
           if weights is None:
               weights = [1.0] * len(answer_results)
           total_weight = sum(weights)
           weighted_score = sum(
               r.score * w
               for r, w in zip(answer_results, weights)
           )
           return weighted_score / total_weight
   ```

#### Deliverables

- ✅ Pluggable evaluator framework
- ✅ All major answer types supported (numeric, formula, string, interval, vector, matrix)
- ✅ Partial credit support
- ✅ Standard and average graders
- ✅ Unit tests for all evaluators

#### Testing Strategy

- **Unit tests**: Each evaluator with edge cases
- **Tolerance testing**: Boundary conditions
- **Formula equivalence**: Multiple representations (x^2 vs x*x)

---

### Phase 4: PGML Parser & Renderer

**Duration**: 3-4 months
**Goal**: Full PGML support for problem authoring
**Dependencies**: Phases 1-2 (Parser, MathObjects)
**Risk**: Medium

#### Components to Build

1. **PGML Tokenizer** (`pg_pgml/tokenizer.py`)
   - Split PGML text into tokens
   - Patterns: `[$var]`, `[_____]`, `[@ code @]`, `[```math```]`
   - Block detection: `>>text<<`, `[:marker:]...[::marker]`
   - Nesting tracking
   - **Perl Reference**: `PGML.pl::Split()` (lines 79-84)

2. **PGML Parser** (`pg_pgml/parser.py`)
   ```python
   class PGMLParser:
       def parse(self, pgml_text: str, context: dict) -> PGMLDocument:
           """
           Parse PGML text to structured document

           Args:
               pgml_text: PGML source
               context: Variable bindings for interpolation

           Returns:
               PGMLDocument with blocks, inlines, answer blanks
           """
           ...

   @dataclass
   class PGMLDocument:
       blocks: list[Block]
       answer_blanks: list[AnswerBlank]

   class Block(ABC):
       pass

   class Paragraph(Block):
       inlines: list[Inline]

   class List(Block):
       items: list[list[Inline]]
       ordered: bool

   class Table(Block):
       rows: list[list[list[Inline]]]

   class Inline(ABC):
       pass

   class Text(Inline):
       content: str

   class Math(Inline):
       latex: str
       display: bool  # True for display math, False for inline

   class Variable(Inline):
       name: str
       value: MathValue

   class AnswerBlank(Inline):
       name: str
       width: int
       type: str  # 'text', 'math', 'radio', 'checkbox'
   ```
   - **Perl Reference**: `PGML.pl::Parse()` (lines 147-177)

3. **PGML Renderer** (`pg_pgml/renderer.py`)
   ```python
   class HTMLRenderer:
       def render(self, doc: PGMLDocument) -> str:
           """Render PGML document to HTML"""
           ...

   class TeXRenderer:
       def render(self, doc: PGMLDocument) -> str:
           """Render PGML document to LaTeX"""
           ...
   ```
   - Variable interpolation: `[$a]` → `3.14`
   - Math rendering: `[``x^2``]` → `<span class="katex">...</span>`
   - Answer blanks: `[_____]` → `<input type="text" name="ans1" />`
   - Formatting: `*bold*`, `_italic_`, `[link](url)`
   - Lists, tables, alignment
   - **Perl Reference**: `PGML.pl` render methods

4. **PGML Features**
   - ✅ Variable interpolation: `The answer is [$a].`
   - ✅ Math: `Solve [``x^2 + [$a]x + [$b] = 0``]`
   - ✅ Answer blanks: `x = [_____]{$ans1}`
   - ✅ Code evaluation: `[@ $f = Formula("x^2") @]* The derivative is [@ $f->D @]`
   - ✅ Formatting: `*bold*`, `_italic_`, `[link](url)`
   - ✅ Lists: `- item 1`, `1. item 1`
   - ✅ Tables: `| col1 | col2 |`
   - ✅ Alignment: `>>center<<`, `[:indent:]...text...[::indent]`
   - ✅ Solutions: `BEGIN_PGML_SOLUTION ... END_PGML_SOLUTION`
   - ✅ Hints: `BEGIN_PGML_HINT ... END_PGML_HINT`

#### Deliverables

- ✅ Parse all PGML syntax
- ✅ Render to HTML with KaTeX math
- ✅ Render to LaTeX/TeX
- ✅ Variable interpolation working
- ✅ Answer blank numbering and association
- ✅ Unit tests with >90% coverage

#### Testing Strategy

- **Golden tests**: Compare HTML output to Perl PGML for 50+ examples
- **Nesting tests**: Deeply nested structures
- **Edge cases**: Empty blocks, malformed syntax

---

### Phase 5: Problem Translator & Execution

**Duration**: 2-3 months
**Goal**: Execute .pg problem files
**Dependencies**: Phases 1-4
**Risk**: High

#### Components to Build

1. **Preprocessor** (`pg_translator/preprocessor.py`)
   ```python
   class PGPreprocessor:
       def preprocess(self, pg_source: str) -> str:
           """
           Transform PG syntactic sugar:
           - BEGIN_TEXT...END_TEXT → TEXT(EV3(<<'END_TEXT'...END_TEXT))
           - BEGIN_PGML...END_PGML → PGML(<<'END_PGML'...END_PGML)
           - Backslash handling
           - Comment removal
           """
           ...
   ```
   - **Perl Reference**: `Translator.pm::default_preprocess_code()` (lines 1348-1378)

2. **Safe Execution Environment** (`pg_translator/executor.py`)
   ```python
   class PGExecutor:
       def __init__(self):
           # RestrictedPython or custom sandbox
           self.safe_globals = {
               # Safe built-ins only
               'abs': abs,
               'min': min,
               'max': max,
               # PG functions
               'random': self._random,
               'Formula': self._formula,
               'Compute': self._compute,
               'Real': self._real,
               # Context
               'Context': self._context,
               # Text accumulation
               'TEXT': self._text,
               'PGML': self._pgml,
               # Answer registration
               'ANS': self._ans,
           }

       def execute(self, code: str, seed: int) -> PGProblemResult:
           """Execute PG code in sandbox"""
           # Set seed
           # Execute code with restricted globals
           # Collect text, answers, metadata
           # Return structured result
           ...
   ```
   - **Perl Reference**: `Translator.pm::set_mask()`, Safe compartment

3. **Problem Coordinator** (`pg_translator/translator.py`)
   ```python
   class PGTranslator:
       def __init__(
           self,
           preprocessor: PGPreprocessor,
           executor: PGExecutor,
           pgml_renderer: PGMLRenderer
       ):
           ...

       def translate(
           self,
           pg_file_path: str,
           seed: int,
           inputs: dict[str, str] | None = None
       ) -> ProblemResult:
           """
           Full pipeline:
           1. Load .pg file
           2. Preprocess
           3. Execute in sandbox
           4. Render text (PGML → HTML)
           5. Collect answers
           6. Check answers (if inputs provided)
           7. Return result
           """
           ...

   @dataclass
   class ProblemResult:
       statement_html: str
       statement_tex: str
       answer_blanks: list[AnswerBlank]
       solution_html: str | None
       hint_html: str | None
       metadata: dict
       answer_results: list[AnswerResult] | None = None
       score: float | None = None
   ```
   - **Perl Reference**: `Translator.pm::translate()` (lines 679-794)

4. **Macro Loading** (`pg_translator/macro_loader.py`)
   ```python
   class MacroLoader:
       def load(self, macro_name: str) -> dict[str, Callable]:
           """
           Load macro file and return exported functions

           For now, map Perl macro names to Python implementations:
           - "PGstandard.pl" → pg_macros.core.pg_standard
           - "MathObjects.pl" → pg_macros.core.math_objects
           - "PGML.pl" → pg_macros.core.pgml
           """
           ...
   ```

#### Deliverables

- ✅ Execute .pg files safely
- ✅ Collect problem text, answers, solutions, hints
- ✅ Error reporting with line numbers
- ✅ loadMacros() support for core macros
- ✅ Answer checking integration
- ✅ Unit tests with real .pg files

#### Testing Strategy

- **Integration tests**: Run 20+ simple .pg files end-to-end
- **Error handling**: Malformed .pg files, runtime errors
- **Security**: Attempt to break sandbox (file access, network, etc.)

---

### Phase 6: Macro System (Incremental)

**Duration**: 6-8 months (ongoing)
**Goal**: Port essential macros to Python
**Dependencies**: Phases 1-5
**Risk**: Very High

#### Strategy: Prioritized by Usage

**Priority 1 - Core Macros** (2 months):
- `PGstandard.pl`: TEXT, ANS, NAMED_ANS, image, etc.
- `MathObjects.pl`: Load MathObjects (mostly done if Phase 2 complete)
- `PGML.pl`: PGML renderer (done if Phase 4 complete)
- `PGanswermacros.pl`: num_cmp, fun_cmp, str_cmp, etc.

**Priority 2 - Common Macros** (2 months):
- `PGgraphmacros.pl`: Basic graphing (delegate to matplotlib)
- `PGchoicemacros.pl`: Multiple choice, true/false, matching
- `niceTables.pl`: Table formatting
- `scaffold.pl`: Multi-part problems (progressive disclosure)

**Priority 3 - Specialized Macros** (2-4 months, as needed):
- Context-specific: `contextFraction.pl`, `contextLimitedNumeric.pl`
- Graphing: `WWPlot.pm`, `Circle.pm`, `TikZ.pm`
- Statistics: `Statistics.pl`, `RserveClient.pl`
- Chemistry: `chemparse.pl`, `periodic_table.pl`
- Custom parsers: `parserPopUp.pl`, `parserRadioButtons.pl`

#### Approach

**Option A: Direct Port** (for simple macros)
```perl
# Perl: PGanswermacros.pl
sub num_cmp {
    my $correct = shift;
    my %options = @_;
    # ... implementation
}
```

```python
# Python: pg_macros/answers/num_cmp.py
def num_cmp(
    correct: float | str,
    *,
    tolType: str = 'relative',
    tolerance: float = 0.001,
    **options
) -> AnswerEvaluator:
    """Numeric comparison answer evaluator"""
    return NumericEvaluator(
        correct=correct,
        tol_type=tolType,
        tolerance=tolerance,
        **options
    )
```

**Option B: Python Equivalent** (for complex macros)
- Use existing Python libraries (matplotlib, SymPy, etc.)
- Provide similar API, different implementation

**Option C: Perl Bridge** (for rarely-used macros)
- Keep Perl implementation, call via subprocess
- Avoid porting 85,000 lines of rarely-used code

#### Macro Registry

```python
class MacroRegistry:
    _macros: dict[str, dict[str, Callable]] = {}

    @classmethod
    def register_file(cls, filename: str, exports: dict[str, Callable]):
        """Register all exports from a macro file"""
        cls._macros[filename] = exports

    @classmethod
    def load(cls, filename: str) -> dict[str, Callable]:
        """Load macro file (like loadMacros in Perl)"""
        if filename not in cls._macros:
            # Try to import Python module
            module = importlib.import_module(f"pg_macros.{filename.replace('.pl', '')}")
            cls._macros[filename] = module.__dict__
        return cls._macros[filename]

# Usage in problem execution
def loadMacros(*filenames):
    """Load macros into global namespace"""
    for filename in filenames:
        exports = MacroRegistry.load(filename)
        globals().update(exports)
```

#### Deliverables (Incremental)

- ✅ Macro loading framework
- ✅ Top 20 most-used macros ported
- ✅ Top 50 most-used macros ported
- ✅ Documentation for macro authors
- ✅ Porting guide (Perl → Python)

#### Testing Strategy

- **Unit tests**: Each macro function
- **Integration tests**: .pg files using each macro
- **Golden tests**: Compare output to Perl for 100+ problems

---

### Phase 7: Image & Graph Generation

**Duration**: 2-3 months
**Goal**: Generate mathematical images and graphs
**Dependencies**: Phase 5
**Risk**: Low

#### Components to Build

1. **LaTeX Rendering** (`pg_render/latex.py`)
   ```python
   class LaTeXRenderer:
       def __init__(self, cache_dir: Path):
           self.cache = diskcache.Cache(cache_dir)

       def render(self, latex: str, format: str = 'svg') -> bytes:
           """
           Render LaTeX to image

           Options:
           - Server-side KaTeX (fast, limited)
           - MathJax-node (slower, full LaTeX)
           - Full LaTeX → SVG (dvisvgm)
           """
           # Check cache first
           cache_key = hashlib.sha256(latex.encode()).hexdigest()
           if cache_key in self.cache:
               return self.cache[cache_key]

           # Render (using one of the options)
           image_bytes = self._render_katex(latex)  # or _render_mathjax

           # Cache result
           self.cache[cache_key] = image_bytes
           return image_bytes
   ```
   - **Perl Reference**: `ImageGenerator.pm`

2. **Graph Generation** (`pg_render/graphs.py`)
   ```python
   class GraphGenerator:
       def plot_2d(
           self,
           functions: list[str],
           x_range: tuple[float, float],
           y_range: tuple[float, float] | None = None,
           **options
       ) -> bytes:
           """
           Generate 2D plot using matplotlib

           Returns: PNG or SVG bytes
           """
           fig, ax = plt.subplots()
           # ... plotting logic
           buffer = io.BytesIO()
           fig.savefig(buffer, format='svg')
           return buffer.getvalue()

       def plot_interactive(
           self,
           functions: list[str],
           x_range: tuple[float, float],
           **options
       ) -> str:
           """
           Generate interactive plot using plotly

           Returns: HTML string with embedded plotly
           """
           ...
   ```
   - **Perl Reference**: `macros/graph/`, `Plots/` directory

3. **TikZ Export** (for static TeX documents)
   ```python
   class TikZGenerator:
       def generate(self, plot_spec: PlotSpec) -> str:
           """Generate TikZ code for LaTeX"""
           return f"""
           \\begin{{tikzpicture}}
           \\begin{{axis}}[
               xmin={plot_spec.x_min}, xmax={plot_spec.x_max},
               ymin={plot_spec.y_min}, ymax={plot_spec.y_max}
           ]
           \\addplot[color=blue] {{{plot_spec.function}}};
           \\end{{axis}}
           \\end{{tikzpicture}}
           """
   ```

#### Deliverables

- ✅ Render LaTeX equations to SVG
- ✅ Generate 2D graphs (matplotlib)
- ✅ Interactive graphs (plotly)
- ✅ TikZ export for TeX
- ✅ Caching system for performance
- ✅ Unit tests

#### Testing Strategy

- **Visual regression**: Compare generated images to reference
- **Cache hit rate**: Monitor for performance

---

### Phase 8: Integration & Testing

**Duration**: 2-3 months
**Goal**: End-to-end system validation
**Dependencies**: All previous phases
**Risk**: Medium

#### Activities

1. **Problem Library Testing**
   - Select 100-200 representative .pg files from OPL (Open Problem Library)
   - Run through Python renderer
   - Compare output to Perl renderer (golden tests)
   - Identify regressions, fix bugs

2. **Performance Testing**
   - Benchmark: 1000 problems/second target
   - Profiling: Identify bottlenecks (cProfile, py-spy)
   - Optimization: Hot path optimization, caching tuning
   - Load testing: Concurrent requests

3. **Compatibility Testing**
   - Test all contexts (Numeric, Complex, Vector, etc.)
   - Test all answer types
   - Test edge cases (0, infinity, empty intervals)
   - Test error handling

4. **Migration Tools**
   - .pg file analyzer (detect required macros)
   - Compatibility report generator
   - Automated porting tools (where possible)

5. **Documentation**
   - API documentation (Sphinx)
   - Migration guide for problem authors
   - Macro porting guide
   - Architecture documentation

#### Deliverables

- ✅ 95%+ compatibility with common problem patterns
- ✅ Performance parity or better than Perl
- ✅ Migration guide
- ✅ API documentation
- ✅ Compatibility report tool

---

## 5. Technical Challenges & Solutions

### Challenge 1: Perl's Dynamic Nature

**Problem**: Perl allows:
- Runtime code generation (`eval STRING`)
- Dynamic method calls (`$obj->$method()`)
- Symbol table manipulation (`*name = \&function`)
- Typeglobs and references

**Solution**:
- **Accept limitations**: No runtime `eval` of arbitrary Perl code
- **RestrictedPython**: Safe execution for Python-like code
- **Python DSL**: Provide Python equivalents for common patterns
- **Hybrid approach**: Keep Perl engine for truly dynamic problems, subprocess call

**Example**:
```perl
# Perl (dynamic)
my $method = "diff";
my $result = $f->$method('x');  # Dynamic method call
```

```python
# Python (static alternative)
result = f.diff('x')  # Direct call

# Or use getattr for dynamic calls
method_name = "diff"
result = getattr(f, method_name)('x')
```

### Challenge 2: Context System Complexity

**Problem**: Contexts affect:
- Parsing rules (what's a valid expression)
- Evaluation behavior
- Comparison tolerances
- Reduction rules
- String/TeX rendering

**Solution**:
- **Data-driven**: YAML/JSON configuration files
- **Strategy Pattern**: Pluggable behaviors
- **Sensible defaults**: 90% of problems use standard contexts
- **Override mechanism**: Custom contexts for special cases

**Example**:
```yaml
# contexts/fraction.yaml
name: Fraction
base: Numeric
number_type: fraction  # Parse "1/2" as Fraction, not 0.5
reduction: enforce  # Require reduced form
flags:
  showMixedNumbers: false
  allowProperFractions: true
  requireProperFractions: false
```

### Challenge 3: Macro System Compatibility

**Problem**: 85,000 lines of macros, many interdependent

**Solution**:
- **Pareto Principle**: Port 20% of macros used in 80% of problems
- **Usage analytics**: Analyze OPL to find most-used macros
- **Compatibility layer**: Shim for common patterns
- **Perl bridge**: Subprocess calls for rare macros
- **Documentation**: Porting guide for custom macros

**Hybrid Execution**:
```python
class HybridMacroLoader:
    def load(self, filename: str):
        # Try Python first
        try:
            return self._load_python_macro(filename)
        except ModuleNotFoundError:
            # Fall back to Perl bridge
            return self._load_perl_macro_bridge(filename)

    def _load_perl_macro_bridge(self, filename: str):
        """Execute Perl macro via subprocess"""
        # Expensive but works for rare macros
        ...
```

### Challenge 4: Fuzzy Math Comparison

**Problem**: Floating-point comparison modes:
- Relative tolerance: `|a - b| / |b| < tol`
- Absolute tolerance: `|a - b| < tol`
- Significant digits: `floor(log10(|a - b|)) < -digits`
- Zero is special case

**Solution**:
- **Port exact Perl logic**: Don't reinvent, reimplement
- **SymPy symbolic**: Use symbolic comparison when possible
- **Extensive testing**: Edge cases (0.0001 vs 0.00011, near zero, etc.)

```python
def fuzzy_compare(a: float, b: float, tolerance: float, mode: str = 'relative') -> bool:
    # Handle exact zero
    if a == 0 and b == 0:
        return True

    if mode == 'absolute':
        return abs(a - b) < tolerance

    elif mode == 'relative':
        # Avoid division by zero
        if b == 0:
            return abs(a) < tolerance
        return abs((a - b) / b) < tolerance

    elif mode == 'sigfigs':
        # Significant figures mode
        if a == b:
            return True
        diff = abs(a - b)
        if diff == 0:
            return True
        avg = (abs(a) + abs(b)) / 2
        if avg == 0:
            return diff < 10 ** (-tolerance)
        return math.floor(math.log10(diff / avg)) < -tolerance

    else:
        raise ValueError(f"Unknown tolerance mode: {mode}")
```

### Challenge 5: Performance

**Problem**:
- Perl is fast for regex/text processing
- Python is fast for numerical computation (NumPy)
- Need competitive performance

**Solution**:
- **Compiled regex**: Use `re.compile()` for repeated patterns
- **NumPy**: Vectorized operations for vector/matrix math
- **Caching**: Memoize expensive operations (parsing, evaluation)
- **Profiling**: Continuous profiling to identify bottlenecks
- **JIT compilation**: Consider PyPy or Numba for hot paths

**Example - Caching**:
```python
from functools import lru_cache

class Parser:
    @lru_cache(maxsize=1000)
    def parse(self, expression: str, context_name: str) -> ASTNode:
        """Cache parsed expressions"""
        # Parsing is expensive, cache results
        ...
```

### Challenge 6: Testing & Validation

**Problem**: How to ensure Python behaves identically to Perl?

**Solution**:
- **Golden tests**: Run same .pg file in Perl and Python, compare output
- **Property-based testing**: Use hypothesis to generate test cases
- **Regression suite**: Every bug becomes a test
- **Gradual rollout**: Run both engines in parallel, compare results
- **Fuzz testing**: Random input generation

**Example - Golden Test**:
```python
def test_golden_product_rule():
    """Compare Python output to Perl reference output"""
    pg_file = "Calculus/product_rule.pg"
    seed = 12345

    # Python renderer
    python_result = pg_renderer.render(pg_file, seed)

    # Perl renderer (via subprocess)
    perl_result = perl_renderer.render(pg_file, seed)

    # Compare HTML (ignoring whitespace differences)
    assert normalize_html(python_result.html) == normalize_html(perl_result.html)

    # Compare TeX
    assert normalize_tex(python_result.tex) == normalize_tex(perl_result.tex)
```

---

## 6. Testing Strategy

### 6.1 Testing Levels

**Unit Tests** (pytest):
- Individual functions, classes
- Mock dependencies
- Fast (<1s per test)
- Target: >90% coverage for core modules

**Integration Tests**:
- Component interactions (parser + evaluator + renderer)
- Real .pg files (simple cases)
- Moderate speed (<10s per test)

**End-to-End Tests**:
- Full .pg file rendering
- Answer checking workflow
- Golden tests (Perl vs Python)
- Slower (can be minutes for large suites)

**Property-Based Tests** (hypothesis):
- Automatically generate test cases
- Test mathematical properties (commutative, associative, etc.)
- Find edge cases

**Performance Tests**:
- Benchmarking (pytest-benchmark)
- Profiling (cProfile, py-spy)
- Load testing (locust)

### 6.2 Testing Tools

- **pytest**: Test runner, fixtures, parameterization
- **hypothesis**: Property-based testing
- **pytest-cov**: Coverage reporting
- **pytest-benchmark**: Performance benchmarking
- **pytest-xdist**: Parallel test execution
- **mypy**: Static type checking
- **ruff**: Linting

### 6.3 Test Organization

```
tests/
├── unit/
│   ├── test_parser.py
│   ├── test_tokenizer.py
│   ├── test_mathobjects.py
│   ├── test_answer_evaluators.py
│   └── ...
├── integration/
│   ├── test_parser_evaluator.py
│   ├── test_pgml_rendering.py
│   └── ...
├── e2e/
│   ├── test_simple_problems.py
│   ├── test_calculus_problems.py
│   └── ...
├── golden/
│   ├── test_golden_suite.py
│   └── reference_outputs/  # Perl outputs for comparison
│       ├── problem1.json
│       ├── problem2.json
│       └── ...
├── properties/
│   ├── test_math_properties.py  # Hypothesis tests
│   └── ...
└── performance/
    ├── test_benchmarks.py
    └── ...
```

### 6.4 Continuous Integration

- **Pre-commit hooks**: ruff, mypy, pytest (fast tests only)
- **GitHub Actions**: Full test suite on push
- **Coverage gates**: Fail if coverage drops below 85%
- **Performance regression**: Fail if benchmarks regress >10%

---

## 7. Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Incomplete macro porting** | High | High | Hybrid approach (Python + Perl bridge), prioritize by usage |
| **Performance regressions** | Medium | Medium | Profiling, caching, benchmarking gates |
| **Behavioral differences** | High | High | Extensive testing (golden, property-based), gradual rollout |
| **Developer burnout** | High | High | Incremental delivery, celebrate milestones, realistic timeline |
| **Scope creep** | High | Medium | Strict prioritization (must-have vs nice-to-have), MVP mindset |
| **Loss of Perl knowledge** | Medium | High | Document Perl behavior extensively, pair with Perl experts |
| **Breaking API changes** | Low | High | Semantic versioning, deprecation warnings, migration guides |
| **Security vulnerabilities** | Low | Very High | RestrictedPython, security audits, sandboxing tests |

### Risk Mitigation Strategies

**Technical Risks**:
- **Continuous validation**: Run golden tests weekly against Perl
- **Feature flags**: Enable new features gradually
- **Rollback capability**: Keep Perl engine as fallback

**People Risks**:
- **Knowledge transfer**: Document Perl system before porting
- **Realistic timelines**: 2-3 years is acceptable for 133k lines
- **Celebrate wins**: MVP at 12 months, critical mass at 24 months

**Process Risks**:
- **Agile methodology**: Sprint planning, retrospectives
- **Stakeholder communication**: Monthly progress reports
- **Scope management**: Ruthless prioritization

---

## 8. Success Metrics

### 8.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Functionality Coverage** | 95% of actively-used .pg problems render correctly | Golden test suite (200+ problems) |
| **Performance - Render Time** | <100ms per problem (target: 50ms) | Benchmark suite |
| **Performance - Throughput** | >1000 problems/second | Load testing |
| **Test Coverage** | >85% for core modules | pytest-cov |
| **Bug Rate** | <5 bugs per 1000 problems | Production monitoring |
| **Answer Checking Accuracy** | >99.9% agreement with Perl | Golden tests with student submissions |

### 8.2 Adoption Metrics

| Metric | Month 6 | Month 12 | Month 24 | Month 36 |
|--------|---------|----------|----------|----------|
| **New problems using Python** | 10% | 50% | 80% | 95% |
| **Migrated problems** | 5% | 20% | 50% | 75% |
| **Python-only installations** | 0% | 10% | 40% | 70% |

### 8.3 Quality Metrics

- **Code maintainability**: Pylint score >8.0
- **Documentation coverage**: 100% of public APIs
- **Type safety**: mypy strict mode, 0 errors
- **Security**: 0 critical vulnerabilities (Snyk scans)

---

## 9. File Mapping Reference

### Core Components

| Perl File | Lines | Python Equivalent | Priority | Complexity |
|-----------|-------|-------------------|----------|------------|
| `lib/Parser.pm` | 908 | `pg_parser/parser.py`, `tokenizer.py`, `ast.py` | **Critical** | High |
| `lib/Value.pm` | 1,230 | `pg_math/value.py` | **Critical** | High |
| `lib/Value/Real.pm` | 243 | `pg_math/numeric.py::Real` | **Critical** | Medium |
| `lib/Value/Complex.pm` | 318 | `pg_math/numeric.py::Complex` | **Critical** | Medium |
| `lib/Value/Infinity.pm` | 135 | `pg_math/numeric.py::Infinity` | High | Low |
| `lib/Value/Point.pm` | 294 | `pg_math/geometric.py::Point` | High | Medium |
| `lib/Value/Vector.pm` | 446 | `pg_math/geometric.py::Vector` | High | Medium |
| `lib/Value/Matrix.pm` | 752 | `pg_math/geometric.py::Matrix` | High | High |
| `lib/Value/Formula.pm` | 1,156 | `pg_math/formula.py` | **Critical** | High |
| `lib/Value/Interval.pm` | 489 | `pg_math/sets.py::Interval` | High | Medium |
| `lib/Value/Set.pm` | 331 | `pg_math/sets.py::Set` | High | Medium |
| `lib/Value/Union.pm` | 284 | `pg_math/sets.py::Union` | High | Medium |
| `lib/Value/List.pm` | 371 | `pg_math/collections.py::List` | Medium | Low |
| `lib/Value/String.pm` | 211 | `pg_math/collections.py::String` | Medium | Low |
| `lib/Parser/Context.pm` | 1,043 | `pg_parser/context.py` | **Critical** | Medium |
| `lib/WeBWorK/PG/Translator.pm` | 1,385 | `pg_translator/translator.py`, `executor.py`, `preprocessor.py` | **Critical** | Very High |
| `lib/PGcore.pm` | 785 | `pg_core/core.py` | High | Medium |
| `lib/AnswerHash.pm` | 267 | `pg_answer/answer_hash.py` | High | Low |
| `lib/WeBWorK/PG/ImageGenerator.pm` | 724 | `pg_render/latex.py`, `images.py` | Medium | Medium |

### Macro Files (Priority 1 - Core)

| Perl File | Lines | Python Equivalent | Priority |
|-----------|-------|-------------------|----------|
| `macros/core/PGstandard.pl` | 1,234 | `pg_macros/core/pg_standard.py` | **Critical** |
| `macros/core/PGML.pl` | 2,068 | `pg_pgml/parser.py`, `renderer.py` | **Critical** |
| `macros/core/MathObjects.pl` | 89 | `pg_macros/core/math_objects.py` | **Critical** |
| `macros/core/PGanswermacros.pl` | 2,145 | `pg_answer/evaluators/` (multiple files) | **Critical** |

### Macro Files (Priority 2 - Common)

| Perl File | Lines | Python Equivalent | Priority |
|-----------|-------|-------------------|----------|
| `macros/graph/PGgraphmacros.pl` | 1,521 | `pg_render/graphs.py` | High |
| `macros/ui/PGchoicemacros.pl` | 1,089 | `pg_macros/ui/choice.py` | High |
| `macros/ui/niceTables.pl` | 487 | `pg_pgml/tables.py` | High |
| `macros/ui/scaffold.pl` | 654 | `pg_macros/ui/scaffold.py` | High |

---

## Conclusion

Achieving 100% parity between the legacy Perl PG system and a modern Python implementation is a **substantial but feasible undertaking**. The estimated timeline of **24-33 months** reflects the complexity and scale (~133,000 lines) of the Perl codebase.

### Key Recommendations

1. **Adopt a hybrid strategy**: Python-first for new problems, Perl bridge for legacy macros
2. **Follow SOLID principles**: Build modular, testable, extensible architecture
3. **Prioritize ruthlessly**: Port the 20% of macros used in 80% of problems
4. **Test extensively**: Golden tests, property-based tests, continuous validation
5. **Deliver incrementally**: MVP in 12 months, critical mass in 24 months, full parity in 33 months
6. **Document thoroughly**: Architecture, APIs, migration guides for future maintainers
7. **Celebrate milestones**: Recognize progress to sustain team motivation

### Success Factors

- **Strong Perl domain knowledge**: Understand legacy system deeply before porting
- **Python expertise**: Modern Python idioms, type hints, async patterns
- **Realistic expectations**: 2-3 years for full port is acceptable
- **Stakeholder buy-in**: Clear communication of progress and value
- **Quality over speed**: Correctness is paramount for educational software

With proper planning, execution, and continuous validation, the Python port will provide a **modern, maintainable, extensible** problem generation system positioned for the next 20+ years of WeBWorK development.
