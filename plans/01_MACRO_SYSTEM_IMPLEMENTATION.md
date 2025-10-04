# MACRO SYSTEM IMPLEMENTATION PLAN

**Goal**: Port Perl macro system to Python, achieving 1:1 feature parity
**Estimated Effort**: 8-12 weeks (1 developer) | 4-6 weeks (2 developers)
**Priority**: CRITICAL - Blocks 90% of problem rendering

---

## EXECUTIVE SUMMARY

The macro system is the **largest gap** in the Python port. We need to port ~13,500 LOC from 211 Perl files to establish the foundational macro infrastructure that all PG problems depend on.

**Current State**: 21 Python files (~1,500 LOC) = 10% coverage
**Target State**: Core macros functional, 80%+ problem compatibility

---

## PHASE 1: MACRO LOADING INFRASTRUCTURE (Week 1-2)

### 1.1 Macro Loader System

**Location**: `packages/pg_translator/pg_translator/macro_loader.py`

**Implementation**:
```python
class MacroLoader:
    """
    Load and execute PG macro files in isolated namespace.

    Equivalent to Translator.pm:unrestricted_load() and PG_macro_file_eval()
    """

    def __init__(self, sandbox: PGSandbox):
        self.sandbox = sandbox
        self.loaded_macros: dict[str, Any] = {}
        self.macro_cache: dict[str, ModuleType] = {}

    def load_macro(self, macro_name: str, unrestricted: bool = False) -> None:
        """
        Load a macro file (.pl or .py).

        Args:
            macro_name: Name of macro (e.g., "PGstandard.pl")
            unrestricted: If True, load with full permissions (like PG.pl)
        """
        # 1. Find macro file (search paths: macros/, custom paths)
        # 2. Check cache - return if already loaded
        # 3. For .pl files: convert to Python or execute via bridge
        # 4. For .py files: import and register
        # 5. Execute _init function if present
        # 6. Register exports to sandbox namespace
        pass

    def unrestricted_load(self, filepath: str) -> None:
        """
        Load macro with full sandbox permissions.

        Equivalent to Translator.pm:346-392
        """
        # Save current opcode mask
        # Set mask to empty (allow all)
        # Execute macro file
        # Call _<name>_init() if exists
        # Restore mask
        pass

    def load_macros(self, *macro_names: str) -> None:
        """
        Load multiple macros (equivalent to loadMacros()).
        """
        for name in macro_names:
            self.load_macro(name)
```

**Files to create**:
- `macro_loader.py` (400 lines)
- `macro_cache.py` (200 lines)
- `macro_bridge.py` (300 lines) - Bridge Perl to Python
- Tests: `test_macro_loader.py` (200 lines)

**Deliverable**: Macro loading system that can load .py macros and basic .pl macros

---

## PHASE 2: CORE MACRO PORTS (Week 3-6)

### 2.1 PG.pl Port (Week 3)

**Current**: 2,441 lines Perl → **Target**: ~1,800 lines Python

**Key Components**:

```python
# packages/pg_macros/core/pg_core.py

# 1. Core initialization (lines 1-200)
def _PG_init():
    """Initialize PG environment in sandbox."""
    pass

# 2. loadMacros() - THE critical function (lines 250-350)
def loadMacros(*macro_files: str) -> None:
    """
    Load macro files into problem namespace.

    Reference: PG.pl:load_macro_file (lines 250-350)
    """
    loader = get_macro_loader()
    for macro in macro_files:
        loader.load_macro(macro)

# 3. TEXT() and friends (lines 400-600)
def TEXT(*args: str) -> None:
    """Append text to problem output."""
    env = get_environment()
    env.append_text("".join(str(arg) for arg in args))

def BEGIN_TEXT() -> str:
    """Start text block (syntactic sugar)."""
    return ""

def END_TEXT() -> str:
    """End text block."""
    return ""

# 4. ANS() - Answer registration (lines 700-850)
def ANS(*evaluators: AnswerEvaluator) -> None:
    """
    Register answer evaluators.

    Matches evaluators to answer blanks in order.
    Reference: PG.pl:700-850
    """
    env = get_environment()
    for evaluator in evaluators:
        answer_name = env.next_answer_name()
        env.register_answer(answer_name, evaluator)

# 5. NAMED_ANS() (lines 900-950)
def NAMED_ANS(name: str, evaluator: AnswerEvaluator) -> None:
    """Register named answer evaluator."""
    env = get_environment()
    env.register_answer(name, evaluator)

# 6. DOCUMENT() / ENDDOCUMENT() (lines 1000-1100)
def DOCUMENT() -> None:
    """Start problem document."""
    env = get_environment()
    env.start_document()

def ENDDOCUMENT() -> None:
    """End problem document and finalize."""
    env = get_environment()
    env.end_document()

# 7. SOLUTION() / HINT() (lines 1200-1400)
def SOLUTION(*args: str) -> None:
    """Add solution text."""
    env = get_environment()
    env.append_solution("".join(str(arg) for arg in args))

def HINT(*args: str) -> None:
    """Add hint text."""
    env = get_environment()
    env.append_hint("".join(str(arg) for arg in args))

# 8. Environment access (lines 1500-1700)
def get_problem_seed() -> int:
    """Get current problem seed."""
    return get_environment().seed

def get_random_generator() -> random.Random:
    """Get problem RNG."""
    return get_environment().rng
```

**Files to create**:
- `packages/pg_macros/core/pg_core.py` (1,800 lines)
- `packages/pg_macros/core/__init__.py` (100 lines)
- Tests: `test_pg_core.py` (400 lines)

**Deliverable**: Core PG.pl functionality ported and tested

---

### 2.2 PGbasicmacros.pl Port (Week 4)

**Current**: 3,200 lines Perl → **Target**: ~2,200 lines Python

**Key Components**:

```python
# packages/pg_macros/core/pg_basic_macros.py

# 1. Display mode constants (lines 40-170)
class DisplayConstants:
    """Display mode-specific constants."""

    @staticmethod
    def PAR(mode: str = "HTML") -> str:
        """Paragraph break."""
        return {"HTML": "<p>", "TeX": "\n\n", "PTX": "<p>"}[mode]

    @staticmethod
    def BR(mode: str = "HTML") -> str:
        """Line break."""
        return {"HTML": "<br/>", "TeX": "\\\\", "PTX": "<br/>"}[mode]

    # ... 50+ more constants

def _PGbasicmacros_init():
    """
    Initialize basic macros in sandbox.

    Reference: PGbasicmacros.pl:39-170
    """
    mode = get_display_mode()

    # Export all constants to sandbox
    constants = DisplayConstants()
    for const_name in dir(constants):
        if const_name.isupper():
            value = getattr(constants, const_name)(mode)
            set_sandbox_var(const_name, value)

# 2. Answer blank macros (lines 200-600)
def ans_rule(width: int = 20) -> str:
    """
    Create answer blank.

    Args:
        width: Width of input field

    Returns:
        HTML for answer input
    """
    env = get_environment()
    name = env.next_answer_name()
    return f'<input type="text" name="{name}" size="{width}" />'

def ans_radio_buttons(*options: tuple[str, str]) -> str:
    """
    Create radio button answer group.

    Args:
        *options: (value, label) pairs

    Returns:
        HTML for radio buttons
    """
    env = get_environment()
    name = env.next_answer_name()

    html_parts = []
    for value, label in options:
        checked = "checked" if value.startswith("%") else ""
        value = value.lstrip("%")
        html_parts.append(
            f'<label><input type="radio" name="{name}" '
            f'value="{value}" {checked}/>{label}</label>'
        )
    return " ".join(html_parts)

def pop_up_list(options: list | dict) -> str:
    """
    Create dropdown select.

    Args:
        options: List of values or dict of value=>label
    """
    env = get_environment()
    name = env.next_answer_name()

    if isinstance(options, list):
        options = {opt: opt for opt in options}

    html = f'<select name="{name}">'
    for value, label in options.items():
        html += f'<option value="{value}">{label}</option>'
    html += '</select>'
    return html

# 3. Named answer blanks (lines 700-900)
def NAMED_ANS_RULE(name: str, width: int = 20) -> str:
    """Named answer rule."""
    return f'<input type="text" name="{name}" size="{width}" />'

# 4. Text formatting (lines 1000-1500)
def EV3(*args: str) -> str:
    """
    Evaluate with variable substitution.

    Reference: PGbasicmacros.pl:1000-1200
    """
    # Complex evaluation logic
    pass

def EV3P(text: str) -> str:
    """
    Evaluate and protect LaTeX.

    Reference: PGbasicmacros.pl:1300-1400
    """
    pass

def MODES(*, HTML: str = "", TeX: str = "", PTX: str = "") -> str:
    """
    Mode-specific text.

    Returns appropriate text for current display mode.
    """
    mode = get_display_mode()
    return {"HTML": HTML, "TeX": TeX, "PTX": PTX}.get(mode, HTML)

# 5. Mathematical constants (lines 1700-1900)
def PI() -> float:
    """Return π."""
    return 3.14159265358979323846

def E() -> float:
    """Return e."""
    return 2.71828182845904523536

# 6. Image/LaTeX helpers (lines 2000-2500)
def image(filename: str, width: int = None, height: int = None,
          tex_size: int = None, alt_text: str = "") -> str:
    """
    Insert image.

    Reference: PGbasicmacros.pl:2100-2300
    """
    if get_display_mode() == "TeX":
        # TeX mode: use includegraphics
        return f"\\includegraphics[width={tex_size}pt]{{{filename}}}"
    else:
        # HTML/PTX: img tag
        attrs = f'width="{width}"' if width else ""
        if height:
            attrs += f' height="{height}"'
        return f'<img src="{filename}" alt="{alt_text}" {attrs}/>'
```

**Files to create**:
- `packages/pg_macros/core/pg_basic_macros.py` (2,200 lines)
- `packages/pg_macros/core/display_constants.py` (500 lines)
- Tests: `test_pg_basic_macros.py` (500 lines)

**Deliverable**: Basic macros ported (answer blanks, formatting, constants)

---

### 2.3 PGML.pl Port (Week 5-6)

**Current**: 2,100 lines Perl → **Target**: ~1,500 lines Python

**Architecture**:

```python
# packages/pg_pgml/pg_pgml/parser.py

class PGMLParser:
    """
    Parse PGML markup to HTML/TeX.

    PGML is a markdown-like language for PG problems.
    Reference: PGML.pl
    """

    def __init__(self, mode: str = "HTML"):
        self.mode = mode
        self.tokenizer = PGMLTokenizer()

    def parse(self, pgml_text: str) -> str:
        """
        Parse PGML to output format.

        Handles:
        - [@ ... @] - LaTeX math
        - [` ... `] - Code
        - [* ... *] - Lists
        - [| ... |] - Tables
        - [@ ... @]* - Answer blanks
        """
        tokens = self.tokenizer.tokenize(pgml_text)
        return self.render(tokens)

    def render(self, tokens: list[PGMLToken]) -> str:
        """Render tokens to output."""
        if self.mode == "HTML":
            return self.render_html(tokens)
        elif self.mode == "TeX":
            return self.render_tex(tokens)
        else:
            return self.render_ptx(tokens)

# PGML Format2 - main entry point
def Format2(text: str) -> str:
    """
    Format PGML text (PGML version 2).

    Reference: PGML.pl:Format2
    """
    mode = get_display_mode()
    parser = PGMLParser(mode)
    return parser.parse(text)

# BEGIN_PGML / END_PGML
def BEGIN_PGML() -> str:
    """Start PGML block."""
    return ""

def END_PGML() -> str:
    """End PGML block."""
    return ""
```

**PGML Syntax Support**:
- `[@ math @]` - Inline LaTeX math
- `[`` code ``]` - Code blocks
- `[* item *]` - Lists
- `[| row | cell |]` - Tables
- `[_____]{ans1}` - Answer blanks with evaluators
- Bold: `*text*`
- Italic: `_text_`
- Links: `[text](url)`

**Files to create**:
- `packages/pg_pgml/pg_pgml/parser.py` (800 lines)
- `packages/pg_pgml/pg_pgml/tokenizer.py` (400 lines)
- `packages/pg_pgml/pg_pgml/renderer.py` (300 lines)
- Tests: `test_pgml_parser.py` (400 lines)

**Deliverable**: PGML parser with 80%+ syntax coverage

---

## PHASE 3: AUXILIARY MACROS (Week 7-8)

### 3.1 PGauxiliaryFunctions.pl Port

**Current**: 1,800 lines → **Target**: ~1,200 lines Python

**Key Functions**:
```python
# packages/pg_macros/core/pg_auxiliary_functions.py

# Trigonometric (with degree mode support)
def asin(x: float) -> float: ...
def acos(x: float) -> float: ...
def atan(x: float) -> float: ...
def sec(x: float) -> float: ...
def csc(x: float) -> float: ...
def cot(x: float) -> float: ...

# Hyperbolic
def sinh(x: float) -> float: ...
def cosh(x: float) -> float: ...
def tanh(x: float) -> float: ...
def sech(x: float) -> float: ...
def csch(x: float) -> float: ...
def coth(x: float) -> float: ...

# Inverse hyperbolic
def asinh(x: float) -> float: ...
def acosh(x: float) -> float: ...
def atanh(x: float) -> float: ...

# Rounding/truncation
def floor(x: float) -> int: ...
def ceil(x: float) -> int: ...
def round(x: float, decimals: int = 0) -> float: ...
def sgn(x: float) -> int: ...

# Statistics
def max(*args: float) -> float: ...
def min(*args: float) -> float: ...
def mean(*args: float) -> float: ...
def median(*args: float) -> float: ...
def std_dev(*args: float) -> float: ...

# Special functions
def factorial(n: int) -> int: ...
def C(n: int, k: int) -> int:  # Combinations
    """n choose k"""
    pass

def P(n: int, k: int) -> int:  # Permutations
    """n permute k"""
    pass

def gcd(*args: int) -> int: ...
def lcm(*args: int) -> int: ...
```

**Files**: `pg_auxiliary_functions.py` (1,200 lines)

---

### 3.2 Choice Macros (Complete)

**Extend existing** `packages/pg_macros/choice/`:

```python
# pg_choice_macros.py additions

# Multiple choice
class MultipleChoice:
    """Full multiple choice with randomization."""

    def qa(self, question: str, answer: str) -> None: ...
    def extra(*distractors: str) -> None: ...
    def makeLast(*options: str) -> None: ...
    def print_q() -> str: ...
    def print_a() -> str: ...

# True/False
class TrueFalse(MultipleChoice): ...

# Matching
class Match:
    """Matching questions."""

    def qa(self, question: str, answer: str) -> None: ...
    def choose(n: int, order: str = "random") -> None: ...
    def print_q() -> str: ...
    def print_a() -> str: ...

# Popup lists with math
def PopUp(options: list[str]) -> PopUpList:
    """Create popup list object."""
    pass
```

**Files**: Extend `pg_choice_macros.py` (+500 lines)

---

## PHASE 4: SPECIALIZED MACROS (Week 9-10)

### 4.1 Answer Macros (Complete)

**Extend** `packages/pg_macros/answers/pg_answer_macros.py`:

```python
# Units support
def num_cmp(
    correct: float,
    units: str = None,
    **options
) -> NumericEvaluator:
    """Numeric with unit checking."""
    if units:
        return NumericWithUnitsEvaluator(
            correct_answer=correct,
            units=units,
            **options
        )
    return NumericEvaluator(correct_answer=correct, **options)

# List/Vector/Matrix
def list_cmp(correct: list, **options) -> ListEvaluator: ...
def vec_cmp(correct: Vector, **options) -> VectorEvaluator: ...
def mat_cmp(correct: Matrix, **options) -> MatrixEvaluator: ...

# Fraction
def frac_cmp(correct: str, **options) -> FractionEvaluator: ...

# PC (legacy compatibility)
def pc_evaluator(correct: str, **options) -> PCEvaluator:
    """Parser/Compute evaluator (legacy)."""
    pass
```

**Files**: Extend `pg_answer_macros.py` (+400 lines)

---

### 4.2 Parser Macros

```python
# packages/pg_macros/parsers/parser_macros.py

def parserPopUp(options: list[str]) -> PopUp:
    """Parser-compatible popup."""
    pass

def parserRadioButtons(*options) -> RadioButtons:
    """Parser-compatible radio buttons."""
    pass

def parserCheckboxes(*options) -> Checkboxes:
    """Parser checkbox group."""
    pass

def parserMultiAnswer(*answers) -> MultiAnswer:
    """Create multi-answer object."""
    pass
```

**Files**: `parser_macros.py` (600 lines)

---

## PHASE 5: GRAPH/UI MACROS (Week 11-12)

### 5.1 Graph Macros (Basic)

**Note**: Full graph support is complex. Start with essential functions.

```python
# packages/pg_macros/graph/pg_graph_macros.py

from PIL import Image, ImageDraw

class WWPlot:
    """Basic graphing for PG."""

    def __init__(self, xmin: float, xmax: float, ymin: float, ymax: float,
                 size: tuple[int, int] = (400, 400)):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.size = size
        self.image = Image.new('RGB', size, 'white')
        self.draw = ImageDraw.Draw(self.image)

    def fn(self, func: Callable, color: str = "blue",
           weight: int = 2) -> None:
        """Plot function."""
        pass

    def stamps(self, points: list[tuple[float, float]],
               color: str = "red") -> None:
        """Plot points."""
        pass

    def lb(self, x: float, y: float, label: str,
           color: str = "black") -> None:
        """Add label."""
        pass

    def save(self, filename: str) -> str:
        """Save and return image tag."""
        self.image.save(filename)
        return f'<img src="{filename}" />'
```

**Deliverable**: Basic graphing (plots functions, points, labels)

---

### 5.2 UI Macros

```python
# packages/pg_macros/ui/pg_ui_macros.py

def ColumnTable(*columns: list[str], **options) -> str:
    """Create column table."""
    pass

def BeginTable(options: str = "") -> str:
    """Start HTML table."""
    return f'<table {options}>'

def EndTable() -> str:
    """End table."""
    return '</table>'

def Row(*cells: str, **options) -> str:
    """Table row."""
    pass

def DataTable(data: list[list[str]], **options) -> str:
    """Full data table."""
    pass
```

**Files**: `pg_ui_macros.py` (400 lines)

---

## INTEGRATION & TESTING

### Integration Points

1. **Translator Integration**:
```python
# In pg_translator/translator.py

from pg_macros.core import pg_core
from pg_macros.loader import MacroLoader

class PGTranslator:
    def __init__(self):
        self.macro_loader = MacroLoader(self.executor.sandbox)

        # Pre-load core macros
        self.macro_loader.unrestricted_load("PG.pl")

    def translate(self, pg_file: Path, seed: int, ...):
        # Macros are now available in sandbox
        ...
```

2. **Sandbox Integration**:
```python
# In executor.py

class PGSandbox:
    def __init__(self):
        # Register macro functions
        self.register_function("loadMacros", loadMacros)
        self.register_function("TEXT", TEXT)
        self.register_function("ANS", ANS)
        # ... all core functions
```

### Testing Strategy

**Unit Tests** (Per macro file):
```python
# test_pg_core.py
def test_loadMacros():
    loader = MacroLoader(sandbox)
    loader.load_macros("PGstandard.pl")
    assert "TEXT" in sandbox.namespace
    assert "ANS" in sandbox.namespace

def test_TEXT():
    env = PGEnvironment(seed=1)
    TEXT("Hello ", "world")
    assert env.get_text() == "Hello world"

def test_ANS():
    env = PGEnvironment(seed=1)
    ANS(num_cmp(42))
    assert len(env.answers) == 1
```

**Integration Tests** (Real problems):
```python
def test_simple_problem():
    """Test problem with macros."""
    problem = '''
    loadMacros("PGstandard.pl", "PGML.pl");

    $a = random(1, 10);
    $ans = Compute("$a^2");

    BEGIN_PGML
    What is [$a]^2?

    Answer: [_____]{$ans}
    END_PGML
    '''

    result = translator.translate_source(problem, seed=123)
    assert result.statement_html
    assert len(result.answer_blanks) == 1
```

---

## DELIVERABLES & MILESTONES

### Week 2: ✅ Macro Loading Infrastructure
- MacroLoader class functional
- Can load .py macros
- Basic .pl bridge working

### Week 3: ✅ PG.pl Core
- loadMacros(), TEXT(), ANS() working
- DOCUMENT/ENDDOCUMENT functional
- 10+ basic problems render

### Week 4: ✅ PGbasicmacros.pl
- Answer blanks (ans_rule, radio, popup)
- Display constants
- 50+ problems render

### Week 6: ✅ PGML Parser
- PGML syntax parsing
- HTML/TeX rendering
- 100+ PGML problems render

### Week 8: ✅ Auxiliary Functions
- Math functions available
- Choice macros complete
- 200+ problems render

### Week 10: ✅ Specialized Macros
- Answer evaluator macros complete
- Parser macros functional
- 400+ problems render

### Week 12: ✅ Graph/UI
- Basic graphing works
- UI macros available
- 500+ problems render (80% coverage)

---

## RISKS & MITIGATION

### Risk 1: Perl→Python Translation Complexity
**Mitigation**:
- Start with .py versions of critical macros
- Use AST analysis to semi-automate Perl→Python
- Create Perl bridge for complex macros initially

### Risk 2: Safe Compartment Differences
**Mitigation**:
- Document opcode restrictions
- Test permission boundaries extensively
- Provide fallback execution modes

### Risk 3: Macro Interdependencies
**Mitigation**:
- Map dependency graph
- Load in topological order
- Detect circular dependencies

---

## SUCCESS CRITERIA

1. **Functional**:
   - Core macros (PG, PGbasic, PGML) 100% functional
   - 500+ problems render correctly

2. **Performance**:
   - Macro loading <100ms per file
   - Total initialization <500ms

3. **Compatibility**:
   - 80% of OPL problems render
   - All tutorial problems work

4. **Quality**:
   - 90% test coverage
   - Zero regression in existing tests

---

## APPENDIX: MACRO FILE PRIORITY

### Tier 1 (Critical - Week 1-6):
1. PG.pl
2. PGbasicmacros.pl
3. PGML.pl
4. PGauxiliaryFunctions.pl
5. PGanswermacros.pl

### Tier 2 (Important - Week 7-10):
6. PGchoicemacros.pl
7. PGgraphmacros.pl (basic)
8. parserPopUp.pl
9. parserRadioButtons.pl
10. contextFraction.pl

### Tier 3 (Optional - Week 11-12):
11. Remaining UI macros
12. Advanced graph macros
13. Specialized contexts
14. Legacy compatibility macros

---

**End of Macro System Implementation Plan**
