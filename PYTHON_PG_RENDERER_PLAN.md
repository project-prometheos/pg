# Pure Python PG Renderer Implementation Plan

## Philosophy: Start Small, Grow Incrementally

Instead of trying to support all PG features at once, we'll:
1. **Week 1**: Support 20% of PG features → Render 50% of problems
2. **Week 2**: Support 50% of PG features → Render 80% of problems  
3. **Week 3**: Support 80% of PG features → Render 95% of problems

This follows the Pareto Principle: most problems use a small subset of PG features.

---

## PG Language Analysis

After analyzing the 157 tutorial problems, here's what they actually use:

### Tier 1: Core Features (Used in 90%+ of problems)
```perl
# Variables & Math
$a = 5;
$b = random(1, 10, 1);
$answer = $a + $b;

# Context
Context("Numeric");
Context("Fraction");

# PGML markup
BEGIN_PGML
Text with [$variable] interpolation.
Answer blank: [_____]{$answer}
Bold: [*text*], Italic: [|text|]
END_PGML

# Formulas
$f = Formula("x^2 + 3*x + 1");
$f = Compute("2*pi");
```

### Tier 2: Common Features (Used in 50%+ of problems)
```perl
# MathObjects
Context()->variables->add(y => 'Real');
$point = Point(1, 2);
$vector = Vector(1, 2, 3);
$interval = Interval("[0, 1]");
$list = List(1, 2, 3);

# Random functions
random(min, max, step);
non_zero_random(min, max, step);
list_random(@items);

# Answer evaluators
ANS($answer->cmp);
ANS(num_cmp($answer));
```

### Tier 3: Advanced Features (Used in 20%+ of problems)
```perl
# Graphs
$graph = init_graph(-5, -5, 5, 5);
add_functions($graph, "$f for x in <-5,5>");

# Matrices
$M = Matrix([[1, 2], [3, 4]]);

# Custom checkers
$answer->cmp(checker => sub { ... });
```

### Tier 4: Rare Features (Used in <10%)
- MultiAnswer
- Custom JavaScript
- Draggable proofs
- Chemical equations

---

## Architecture: Modular Python Implementation

```
packages/pg_renderer/
├── pg_renderer/
│   ├── __init__.py
│   ├── parser.py          # Parse PG → AST
│   ├── context.py         # MathObjects Context system
│   ├── evaluator.py       # Execute Perl-like code in Python
│   ├── pgml.py            # PGML → HTML renderer
│   ├── math_objects.py    # Formula, Point, Vector, etc.
│   ├── random.py          # Deterministic random with seed
│   ├── answer_checker.py  # Numerical/formula answer checking
│   └── graph.py           # Basic graph support (optional)
├── tests/
│   ├── test_parser.py
│   ├── test_evaluator.py
│   └── test_integration.py
└── pyproject.toml
```

---

## Week 1: MVP - Numeric Problems (50% coverage)

### Goal: Render simple numeric problems with one answer blank

**Example Problem:**
```perl
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");

Context("Numeric");
$a = random(1, 5, 1);
$b = random(2, 6, 1);
$answer = $a + $b;

BEGIN_PGML
What is [$a] + [$b]?

Answer: [_____]{$answer}
END_PGML
ENDDOCUMENT();
```

### Implementation: Step by Step

#### Step 1: Parser (Day 1-2)

```python
# packages/pg_renderer/pg_renderer/parser.py

import re
from typing import Tuple, Dict, Any, List
from dataclasses import dataclass

@dataclass
class PGProblem:
    """Parsed PG problem structure."""
    setup: str          # Code before BEGIN_PGML
    pgml: str           # Content between BEGIN_PGML...END_PGML
    solution: str       # Content in solution section (if any)
    macros: List[str]   # Loaded macro files

class PGParser:
    """Parse PG files into structured format."""
    
    def parse(self, pg_source: str) -> PGProblem:
        """Parse PG file into sections."""
        
        # Extract loadMacros
        macros = self._extract_macros(pg_source)
        
        # Extract PGML section
        pgml_match = re.search(
            r'BEGIN_PGML\s*\n(.*?)\nEND_PGML',
            pg_source,
            re.DOTALL
        )
        pgml = pgml_match.group(1) if pgml_match else ""
        
        # Extract setup (everything before BEGIN_PGML)
        if pgml_match:
            setup = pg_source[:pgml_match.start()]
        else:
            setup = pg_source
        
        # Extract solution (optional)
        solution_match = re.search(
            r'BEGIN_PGML_SOLUTION\s*\n(.*?)\nEND_PGML_SOLUTION',
            pg_source,
            re.DOTALL
        )
        solution = solution_match.group(1) if solution_match else ""
        
        return PGProblem(
            setup=setup,
            pgml=pgml,
            solution=solution,
            macros=macros
        )
    
    def _extract_macros(self, pg_source: str) -> List[str]:
        """Extract macro files from loadMacros()."""
        match = re.search(r'loadMacros\((.*?)\);', pg_source, re.DOTALL)
        if not match:
            return []
        
        macro_list = match.group(1)
        # Extract quoted strings
        return re.findall(r'["\']([^"\']+)["\']', macro_list)
```

#### Step 2: Evaluator (Day 2-3)

```python
# packages/pg_renderer/pg_renderer/evaluator.py

import re
import math
from typing import Dict, Any
from .context import Context
from .random import PGRandom

class PGEvaluator:
    """Execute Perl-like PG setup code in Python."""
    
    def __init__(self, seed: int = 0):
        self.seed = seed
        self.random = PGRandom(seed)
        self.context = Context("Numeric")
        self.variables: Dict[str, Any] = {}
        
        # Built-in functions
        self.builtins = {
            'random': self.random.random,
            'non_zero_random': self.random.non_zero_random,
            'list_random': self.random.list_random,
            'pi': math.pi,
            'e': math.e,
        }
    
    def evaluate(self, setup_code: str) -> Dict[str, Any]:
        """
        Execute setup code and return variable bindings.
        
        This is a simplified Perl→Python translator.
        Only supports basic variable assignments and function calls.
        """
        
        # Clean up code
        setup_code = self._strip_comments(setup_code)
        
        # Process line by line
        for line in setup_code.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle Context() calls
            if 'Context(' in line:
                self._handle_context(line)
                continue
            
            # Handle variable assignments: $var = expr;
            if match := re.match(r'\$(\w+)\s*=\s*(.+?);', line):
                var_name = match.group(1)
                expr = match.group(2)
                self.variables[var_name] = self._eval_expression(expr)
                continue
        
        return self.variables
    
    def _eval_expression(self, expr: str) -> Any:
        """Evaluate a Perl-like expression in Python."""
        
        # Replace Perl variables with Python dict lookups
        # $a → self.variables['a']
        expr_py = re.sub(r'\$(\w+)', r"self.variables['\1']", expr)
        
        # Replace Perl operators
        expr_py = expr_py.replace('^', '**')  # Power operator
        
        # Handle function calls
        # random(1, 5, 1) → self.random.random(1, 5, 1)
        for func in ['random', 'non_zero_random', 'list_random']:
            expr_py = expr_py.replace(f'{func}(', f'self.random.{func}(')
        
        # Handle Formula() and Compute()
        if 'Formula(' in expr or 'Compute(' in expr:
            return self._handle_formula(expr)
        
        # Evaluate safely
        try:
            # Create safe namespace
            namespace = {
                'self': self,
                'math': math,
                'pi': math.pi,
                'e': math.e,
            }
            return eval(expr_py, namespace)
        except Exception as e:
            raise ValueError(f"Failed to evaluate: {expr} → {expr_py}: {e}")
    
    def _handle_context(self, line: str):
        """Handle Context() declarations."""
        match = re.search(r'Context\(["\'](\w+)["\']\)', line)
        if match:
            context_name = match.group(1)
            self.context = Context(context_name)
    
    def _handle_formula(self, expr: str) -> str:
        """Handle Formula() and Compute() objects."""
        # Extract the formula string
        match = re.search(r'(?:Formula|Compute)\(["\'](.+?)["\']\)', expr)
        if match:
            return match.group(1)
        return expr
    
    def _strip_comments(self, code: str) -> str:
        """Remove Perl comments."""
        return re.sub(r'#.*$', '', code, flags=re.MULTILINE)
```

#### Step 3: Random Number Generator (Day 1)

```python
# packages/pg_renderer/pg_renderer/random.py

import random
from typing import List, Any, Union

class PGRandom:
    """
    Deterministic random number generator for PG problems.
    Mimics Perl's PG_random_generator behavior.
    """
    
    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)
    
    def random(self, min_val: float, max_val: float, step: float = 1) -> float:
        """
        Return random value in [min, max] with given step.
        
        Mimics: random(1, 5, 1) → one of [1, 2, 3, 4, 5]
        """
        if step == 0:
            return self.rng.uniform(min_val, max_val)
        
        num_steps = int((max_val - min_val) / step) + 1
        return min_val + self.rng.randrange(num_steps) * step
    
    def non_zero_random(self, min_val: float, max_val: float, step: float = 1) -> float:
        """Random value excluding zero."""
        val = self.random(min_val, max_val, step)
        while val == 0:
            val = self.random(min_val, max_val, step)
        return val
    
    def list_random(self, items: List[Any]) -> Any:
        """Pick random element from list."""
        return self.rng.choice(items)
```

#### Step 4: PGML Renderer (Day 3-4)

```python
# packages/pg_renderer/pg_renderer/pgml.py

import re
from typing import Dict, Any, List, Tuple

class PGMLRenderer:
    """Render PGML markup to HTML."""
    
    def __init__(self, variables: Dict[str, Any]):
        self.variables = variables
        self.answer_counter = 0
        self.answer_blanks: Dict[str, str] = {}  # answer_id → correct_value
    
    def render(self, pgml: str) -> Tuple[str, Dict[str, str]]:
        """
        Render PGML to HTML.
        
        Returns:
            (html_string, answer_blanks_dict)
        """
        html = pgml
        
        # 1. Variable interpolation: [$var]
        html = re.sub(r'\[\$(\w+)\]', self._interpolate_var, html)
        
        # 2. Answer blanks: [_____]{$answer}
        html = re.sub(r'\[_+\]\{([^}]+)\}', self._create_answer_blank, html)
        
        # 3. Math delimiters: [` ... `] → LaTeX
        html = re.sub(r'\[\`(.*?)\`\]', r'\\( \1 \\)', html)
        
        # 4. Display math: [``` ... ```] → LaTeX display
        html = re.sub(r'\[\`\`\`(.*?)\`\`\`\]', r'\\[ \1 \\]', html, flags=re.DOTALL)
        
        # 5. Formatting
        html = re.sub(r'\[\*(.*?)\*\]', r'<strong>\1</strong>', html)  # Bold
        html = re.sub(r'\[\|(.*?)\|\]', r'<em>\1</em>', html)         # Italic
        html = re.sub(r'\[_(.*?)_\]', r'<u>\1</u>', html)             # Underline
        
        # 6. Lists
        html = re.sub(r'^\*\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
        
        # 7. Paragraphs
        html = '<p>' + html.replace('\n\n', '</p><p>') + '</p>'
        
        return html, self.answer_blanks
    
    def _interpolate_var(self, match: re.Match) -> str:
        """Replace [$var] with variable value."""
        var_name = match.group(1)
        value = self.variables.get(var_name, f'${var_name}')
        
        # Format numbers nicely
        if isinstance(value, float):
            # Remove trailing zeros
            return f'{value:g}'
        return str(value)
    
    def _create_answer_blank(self, match: re.Match) -> str:
        """Create HTML input for answer blank."""
        answer_expr = match.group(1)
        
        # Generate unique answer ID
        self.answer_counter += 1
        answer_id = f'AnSwEr{self.answer_counter:04d}'
        
        # Evaluate answer expression to get correct value
        correct_value = self._eval_answer(answer_expr)
        self.answer_blanks[answer_id] = str(correct_value)
        
        # Return HTML input
        return f'<input type="text" name="{answer_id}" size="15" />'
    
    def _eval_answer(self, expr: str) -> Any:
        """Evaluate answer expression."""
        # Remove $
        expr = expr.strip().lstrip('$')
        
        # Look up variable
        return self.variables.get(expr, expr)
```

#### Step 5: Main Renderer (Day 4)

```python
# packages/pg_renderer/pg_renderer/__init__.py

from typing import Dict, Any
from .parser import PGParser, PGProblem
from .evaluator import PGEvaluator
from .pgml import PGMLRenderer

class PGRenderer:
    """Main PG problem renderer."""
    
    def render(self, pg_source: str, seed: int = 0) -> Dict[str, Any]:
        """
        Render a PG problem to HTML with answer evaluators.
        
        Args:
            pg_source: Full PG file content
            seed: Random seed for problem variation
            
        Returns:
            {
                'statement_html': str,
                'inputs': List[str],
                'answers': Dict[str, Dict],
                'solution_html': str,
                'warnings': List[str],
                'errors': List[str]
            }
        """
        try:
            # Step 1: Parse PG file
            parser = PGParser()
            problem = parser.parse(pg_source)
            
            # Step 2: Execute setup code
            evaluator = PGEvaluator(seed=seed)
            variables = evaluator.evaluate(problem.setup)
            
            # Step 3: Render PGML
            pgml_renderer = PGMLRenderer(variables)
            statement_html, answer_blanks = pgml_renderer.render(problem.pgml)
            
            # Step 4: Render solution (if any)
            solution_html = ""
            if problem.solution:
                solution_renderer = PGMLRenderer(variables)
                solution_html, _ = solution_renderer.render(problem.solution)
            
            # Step 5: Format answers
            answers = {}
            for answer_id, correct_value in answer_blanks.items():
                answers[answer_id] = {
                    'correct_value': correct_value,
                    'type': 'number'
                }
            
            return {
                'statement_html': statement_html,
                'inputs': list(answer_blanks.keys()),
                'answers': answers,
                'solution_html': solution_html,
                'warnings': [],
                'errors': []
            }
            
        except Exception as e:
            return {
                'statement_html': f'<p class="error">Error rendering problem</p>',
                'inputs': [],
                'answers': {},
                'solution_html': '',
                'warnings': [],
                'errors': [str(e)]
            }

# Public API
__all__ = ['PGRenderer']
```

#### Step 6: Answer Checking (Day 5)

```python
# packages/pg_renderer/pg_renderer/answer_checker.py

import re
from typing import Dict, Any, Tuple

class AnswerChecker:
    """Check student answers against correct values."""
    
    def __init__(self, tolerance: float = 0.01):
        self.tolerance = tolerance
    
    def check(self, student_answer: str, correct_answer: str, 
              answer_type: str = 'number') -> Tuple[bool, str]:
        """
        Check if student answer matches correct answer.
        
        Returns:
            (is_correct, feedback_message)
        """
        if answer_type == 'number':
            return self._check_numeric(student_answer, correct_answer)
        elif answer_type == 'formula':
            return self._check_formula(student_answer, correct_answer)
        else:
            return self._check_string(student_answer, correct_answer)
    
    def _check_numeric(self, student: str, correct: str) -> Tuple[bool, str]:
        """Check numeric answer with tolerance."""
        try:
            student_val = self._parse_number(student)
            correct_val = self._parse_number(correct)
            
            # Check with relative tolerance
            if abs(correct_val) < 1e-10:
                # Absolute tolerance for values near zero
                is_correct = abs(student_val - correct_val) < self.tolerance
            else:
                # Relative tolerance
                rel_error = abs((student_val - correct_val) / correct_val)
                is_correct = rel_error < self.tolerance
            
            if is_correct:
                return True, "Correct!"
            else:
                return False, f"Incorrect. (Expected {correct_val})"
                
        except ValueError:
            return False, "Please enter a valid number."
    
    def _parse_number(self, s: str) -> float:
        """Parse number from string, handling various formats."""
        s = s.strip().lower()
        
        # Handle fractions: 1/2
        if '/' in s:
            parts = s.split('/')
            return float(parts[0]) / float(parts[1])
        
        # Handle scientific notation
        s = s.replace('e', 'e')
        
        return float(s)
    
    def _check_formula(self, student: str, correct: str) -> Tuple[bool, str]:
        """Check formula answer (simplified for MVP)."""
        # For MVP, just do string comparison after normalization
        student_norm = self._normalize_formula(student)
        correct_norm = self._normalize_formula(correct)
        
        if student_norm == correct_norm:
            return True, "Correct!"
        else:
            return False, "Incorrect formula."
    
    def _normalize_formula(self, formula: str) -> str:
        """Normalize formula for comparison."""
        # Remove spaces
        formula = re.sub(r'\s+', '', formula)
        # Normalize multiplication: 2x → 2*x
        formula = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', formula)
        return formula.lower()
    
    def _check_string(self, student: str, correct: str) -> Tuple[bool, str]:
        """Check string answer (case-insensitive)."""
        if student.strip().lower() == correct.strip().lower():
            return True, "Correct!"
        else:
            return False, "Incorrect."
```

#### Step 7: Integration with Backend (Day 5-6)

```python
# apps/backend/app/services/pg_renderer_python.py

from typing import Dict, Any
import sys
from pathlib import Path

# Add pg_renderer package to path
pg_renderer_path = Path(__file__).parent.parent.parent.parent.parent / 'packages' / 'pg_renderer'
sys.path.insert(0, str(pg_renderer_path))

from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker

class PGRenderService:
    """Service for rendering PG problems using Python renderer."""
    
    def __init__(self):
        self.renderer = PGRenderer()
        self.checker = AnswerChecker(tolerance=0.01)
    
    def render_problem(self, pg_source: str, seed: int = 0) -> Dict[str, Any]:
        """Render a PG problem."""
        return self.renderer.render(pg_source, seed=seed)
    
    def check_answers(self, pg_source: str, seed: int, 
                     student_inputs: Dict[str, str]) -> Dict[str, Any]:
        """Check student answers for a problem."""
        # Render to get correct answers
        rendered = self.renderer.render(pg_source, seed=seed)
        
        results = {}
        for answer_id, student_answer in student_inputs.items():
            if answer_id in rendered['answers']:
                correct_answer = rendered['answers'][answer_id]['correct_value']
                answer_type = rendered['answers'][answer_id]['type']
                
                is_correct, message = self.checker.check(
                    student_answer,
                    correct_answer,
                    answer_type
                )
                
                results[answer_id] = {
                    'correct': is_correct,
                    'message': message,
                    'student_answer': student_answer,
                }
        
        all_correct = all(r['correct'] for r in results.values())
        
        return {
            'results': results,
            'all_correct': all_correct,
            'score': sum(1 for r in results.values() if r['correct']) / len(results) if results else 0
        }

# Singleton
_service = None

def get_pg_render_service() -> PGRenderService:
    global _service
    if _service is None:
        _service = PGRenderService()
    return _service
```

#### Step 8: pyproject.toml

```toml
# packages/pg_renderer/pyproject.toml

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "pg-renderer"
version = "0.1.0"
description = "Pure Python PG (Problem Generation) renderer for WeBWorK"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

---

## Week 1 Testing Strategy

```python
# packages/pg_renderer/tests/test_simple_numeric.py

from pg_renderer import PGRenderer

def test_simple_addition():
    pg_source = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
Context("Numeric");
$a = 2;
$b = 3;
$answer = $a + $b;
BEGIN_PGML
What is [$a] + [$b]?
Answer: [_____]{$answer}
END_PGML
ENDDOCUMENT();
"""
    renderer = PGRenderer()
    result = renderer.render(pg_source, seed=0)
    
    assert '2' in result['statement_html']
    assert '3' in result['statement_html']
    assert len(result['inputs']) == 1
    assert result['answers'][result['inputs'][0]]['correct_value'] == '5'
    assert len(result['errors']) == 0

def test_random_values():
    pg_source = """
loadMacros("PGML.pl");
Context("Numeric");
$a = random(1, 5, 1);
$b = random(2, 6, 1);
$answer = $a + $b;
BEGIN_PGML
Answer: [_____]{$answer}
END_PGML
"""
    renderer = PGRenderer()
    
    # Test determinism with same seed
    result1 = renderer.render(pg_source, seed=42)
    result2 = renderer.render(pg_source, seed=42)
    assert result1['statement_html'] == result2['statement_html']
    
    # Test variation with different seed
    result3 = renderer.render(pg_source, seed=123)
    assert result1['statement_html'] != result3['statement_html']

def test_answer_checking():
    from pg_renderer.answer_checker import AnswerChecker
    
    checker = AnswerChecker(tolerance=0.01)
    
    # Exact match
    is_correct, msg = checker.check("5", "5", "number")
    assert is_correct
    
    # Within tolerance
    is_correct, msg = checker.check("5.001", "5.0", "number")
    assert is_correct
    
    # Outside tolerance
    is_correct, msg = checker.check("6", "5", "number")
    assert not is_correct
```

---

## Week 1 Deliverables

At end of Week 1, you'll have:

✅ **Package**: `packages/pg_renderer/` with ~600 LOC
✅ **Renders**: Simple numeric problems (50+ from tutorial)
✅ **Features**: Variables, random(), basic PGML, answer checking
✅ **Tests**: 10+ unit tests
✅ **Integration**: Works with existing backend API
✅ **Zero Dependencies**: Pure Python stdlib

### Example Problems That Work:
- ✅ Algebra: Linear equations, polynomial evaluation
- ✅ Arithmetic: Basic operations, fractions
- ✅ Calculus: Numeric derivative values
- ✅ Any problem with numeric answers and basic PGML

---

## Week 2: Formula Support (80% coverage)

### New Features:
1. **Formula parsing**: `Formula("x^2 + 3*x + 1")`
2. **Context variables**: `Context()->variables->add(y => 'Real')`
3. **Formula evaluation**: Check if student formula is equivalent
4. **List answers**: `List(1, 2, 3)`
5. **Interval answers**: `Interval("[0,1]")`

### Key Addition: SymPy Integration

```python
# packages/pg_renderer/pg_renderer/formula.py

from sympy import sympify, simplify, Symbol, latex
from sympy.parsing.sympy_parser import parse_expr

class Formula:
    """Represent a mathematical formula."""
    
    def __init__(self, formula_str: str, variables: list = None):
        self.formula_str = formula_str
        self.variables = variables or ['x']
        
        # Parse to SymPy
        self.expr = parse_expr(formula_str, transformations='all')
    
    def evaluate(self, **values) -> float:
        """Evaluate formula at given values."""
        return float(self.expr.subs(values))
    
    def is_equivalent(self, other: 'Formula', test_points: int = 5) -> bool:
        """Check if two formulas are mathematically equivalent."""
        # Simplify difference
        diff = simplify(self.expr - other.expr)
        if diff == 0:
            return True
        
        # Test at random points
        import random
        for _ in range(test_points):
            test_vals = {v: random.uniform(-10, 10) for v in self.variables}
            if abs(self.evaluate(**test_vals) - other.evaluate(**test_vals)) > 0.001:
                return False
        return True
```

**New dependency**: Add `sympy` to requirements

---

## Week 3: Advanced Features (95% coverage)

### New Features:
1. **Graphs**: Basic plotting with matplotlib
2. **Matrices**: Using numpy
3. **MultiAnswer**: Multiple related inputs
4. **Custom checkers**: User-defined validation
5. **Tables**: DataTable rendering

---

## Timeline Summary

| Week | Features | Problems Supported | LOC |
|------|----------|-------------------|-----|
| 1 | Numeric, basic PGML, random | 50-80 (50%) | 600 |
| 2 | Formulas, Lists, Intervals | 120-140 (80%) | 1000 |
| 3 | Graphs, Matrices, Advanced | 150+ (95%) | 1500 |

---

## Advantages of This Approach

✅ **Portable**: No Perl dependency, runs anywhere Python runs
✅ **Maintainable**: Clean Python code, easy to debug
✅ **Extensible**: Easy to add new features incrementally
✅ **Testable**: Unit tests for each component
✅ **Fast**: No subprocess overhead
✅ **Modern**: Uses modern Python features (dataclasses, type hints)

## Trade-offs

⚠️ **Time**: 3 weeks vs 1 day for Perl approach
⚠️ **Coverage**: May not support 100% of PG features initially
⚠️ **Compatibility**: Behavior might differ slightly from Perl version

---

## Getting Started (Next Steps)

1. **Create package structure**:
```bash
mkdir -p packages/pg_renderer/pg_renderer
mkdir -p packages/pg_renderer/tests
touch packages/pg_renderer/pyproject.toml
touch packages/pg_renderer/README.md
```

2. **Implement core modules** (Day 1-2):
   - `parser.py`
   - `random.py`
   - `evaluator.py`

3. **Implement rendering** (Day 3-4):
   - `pgml.py`
   - `__init__.py`

4. **Add tests** (Day 5):
   - Test with 5-10 real problems from tutorial

5. **Integrate with backend** (Day 6-7):
   - Add service wrapper
   - Update API endpoints
   - Test end-to-end

---

**Ready to start?** Let me know and I'll begin implementing the Week 1 MVP!

