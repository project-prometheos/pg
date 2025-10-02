# Comprehensive Answer Checking Plan

## Current State
- ✅ Basic numeric comparison with tolerance
- ❌ No symbolic/algebraic expression handling
- ❌ No support for equivalence up to constant multiple
- ❌ No support for different answer formats (intervals, vectors, etc.)
- ❌ Limited error messages

## Goals
Build a robust answer checking system that can:
1. Parse and evaluate mathematical expressions
2. Check algebraic equivalence (not just numeric equality)
3. Support various answer types (formulas, intervals, sets, etc.)
4. Provide detailed feedback to students
5. Support WeBWorK's advanced features (partial credit, custom checkers, etc.)

---

## Architecture

### 1. Answer Checker Framework
```
Answer Checker (Base Class)
├── NumericChecker (numbers with tolerance)
├── FormulaChecker (algebraic expressions)
├── IntervalChecker ([a, b], (a, b), etc.)
├── PointChecker ((x, y, z))
├── VectorChecker (<a, b, c>)
├── SetChecker ({1, 2, 3})
├── StringChecker (exact text match)
└── CustomChecker (user-defined logic)
```

### 2. Expression System
```
Input String → Parser → AST → Simplifier → Checker
     ↓           ↓       ↓        ↓          ↓
"(x-1)(x+2)" → Tokens → Tree → x²+x-2 → Compare
```

---

## Implementation Phases

### Phase 1: Expression Parser & Evaluator (Week 1)
**Goal**: Parse and evaluate algebraic expressions

#### Components:
1. **Tokenizer** (`packages/pg_renderer/pg_renderer/expression/tokenizer.py`)
   - Convert string to tokens (numbers, operators, variables, functions)
   - Handle: `+`, `-`, `*`, `/`, `^`, `()`, functions like `sin`, `cos`, `sqrt`

2. **Parser** (`packages/pg_renderer/pg_renderer/expression/parser.py`)
   - Convert tokens to AST using recursive descent or Pratt parsing
   - Support operator precedence
   - Handle implicit multiplication (e.g., `2x`, `(x+1)(x-1)`)

3. **AST Nodes** (`packages/pg_renderer/pg_renderer/expression/ast_nodes.py`)
   ```python
   class Expr:
       pass
   
   class Number(Expr):
       value: float
   
   class Variable(Expr):
       name: str
   
   class BinaryOp(Expr):
       op: str  # '+', '-', '*', '/', '^'
       left: Expr
       right: Expr
   
   class UnaryOp(Expr):
       op: str  # '-', '+'
       operand: Expr
   
   class FunctionCall(Expr):
       name: str  # 'sin', 'cos', 'sqrt', etc.
       args: List[Expr]
   ```

4. **Evaluator** (`packages/pg_renderer/pg_renderer/expression/evaluator.py`)
   - Evaluate AST at specific variable values
   - Support for symbolic evaluation (keep variables)

#### Example Usage:
```python
from pg_renderer.expression import parse_expression, evaluate

expr = parse_expression("(x-1)(x+2)")
# Returns: BinaryOp('*', BinaryOp('-', Var('x'), Num(1)), BinaryOp('+', Var('x'), Num(2)))

result = evaluate(expr, {'x': 3})
# Returns: 10  # (3-1)(3+2) = 2*5 = 10
```

---

### Phase 2: Expression Simplification (Week 2)
**Goal**: Normalize expressions for comparison

#### Components:
1. **Expander** (`packages/pg_renderer/pg_renderer/expression/expander.py`)
   - Expand products: `(x-1)(x+2)` → `x² + x - 2`
   - Distribute: `2(x+3)` → `2x + 6`

2. **Collector** (`packages/pg_renderer/pg_renderer/expression/collector.py`)
   - Collect like terms: `x + 2x + 3` → `3x + 3`
   - Polynomial form: `ax² + bx + c`

3. **Simplifier** (`packages/pg_renderer/pg_renderer/expression/simplifier.py`)
   - Apply algebraic rules
   - Combine multiple simplification strategies

#### Example:
```python
from pg_renderer.expression import parse_expression, simplify

student = parse_expression("(x-1)(x+2)")
correct = parse_expression("x^2 + x - 2")

student_simplified = simplify(student)
correct_simplified = simplify(correct)

# Both become: x² + x - 2 (canonical form)
```

---

### Phase 3: Formula Checker (Week 3)
**Goal**: Check if two expressions are algebraically equivalent

#### Implementation:
```python
class FormulaChecker:
    def __init__(self, tolerance: float = 0.01):
        self.tolerance = tolerance
    
    def check(self, student_answer: str, correct_answer: str, 
              context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if student formula is equivalent to correct formula.
        
        Returns:
            (is_correct, message)
        """
        try:
            student_expr = parse_expression(student_answer)
            correct_expr = parse_expression(correct_answer)
            
            # Method 1: Symbolic comparison (expand and compare)
            if self._symbolic_equal(student_expr, correct_expr):
                return True, "Correct!"
            
            # Method 2: Numeric sampling (evaluate at random points)
            if self._numerically_equal(student_expr, correct_expr, context):
                return True, "Correct!"
            
            return False, "Your answer is not equivalent to the correct answer."
            
        except ParseError as e:
            return False, f"Syntax error: {str(e)}"
    
    def _symbolic_equal(self, expr1: Expr, expr2: Expr) -> bool:
        """Compare expressions symbolically."""
        simp1 = simplify(expr1)
        simp2 = simplify(expr2)
        return ast_equal(simp1, simp2)
    
    def _numerically_equal(self, expr1: Expr, expr2: Expr, 
                           context: Dict[str, Any]) -> bool:
        """
        Test equivalence by evaluating at multiple random points.
        This is more robust for complex expressions.
        """
        variables = set(find_variables(expr1)) | set(find_variables(expr2))
        
        # Test at 10 random points
        for _ in range(10):
            test_values = {var: random.uniform(-10, 10) for var in variables}
            
            val1 = evaluate(expr1, test_values)
            val2 = evaluate(expr2, test_values)
            
            if not self._close_enough(val1, val2):
                return False
        
        return True
```

---

### Phase 4: Special Comparison Modes
**Goal**: Support WeBWorK's comparison flags

#### Modes:
1. **Up to Constant Multiple** (`checker="up_to_constant"`)
   ```python
   # Student: 2x + 4
   # Correct: x + 2
   # Should be marked correct (differ by factor of 2)
   
   def check_up_to_constant(student, correct):
       # Check if student = k * correct for some k != 0
       # Method: Divide at multiple points, check if ratio is constant
       pass
   ```

2. **Ordered vs Unordered** (for lists/sets)
   ```python
   # [1, 2, 3] vs [3, 1, 2] - depends on ordered flag
   ```

3. **Ignore Case** (for string answers)

4. **Tolerance Control** (for numeric answers)
   - Absolute tolerance: `|student - correct| < tol`
   - Relative tolerance: `|student - correct| / |correct| < tol`

---

### Phase 5: Additional Answer Types

#### 1. Interval Checker
```python
class IntervalChecker:
    """
    Parse and check intervals:
    - [a, b] - closed
    - (a, b) - open
    - [a, b) - half-open
    - (-inf, 5] - unbounded
    """
    
    def parse(self, text: str) -> Interval:
        # Parse "[1, 5)" → Interval(1, 5, left_closed=True, right_closed=False)
        pass
    
    def check(self, student: str, correct: str) -> Tuple[bool, str]:
        # Compare endpoints and open/closed status
        pass
```

#### 2. Point/Vector Checker
```python
class PointChecker:
    """
    Parse and check points: (1, 2, 3)
    """
    def parse(self, text: str) -> Tuple[float, ...]:
        pass
```

#### 3. Set Checker
```python
class SetChecker:
    """
    Parse and check sets: {1, 2, 3}
    Support for unordered comparison
    """
    pass
```

---

### Phase 6: Answer Context System
**Goal**: Track answer type and checking mode

#### Answer Context:
```python
class AnswerContext:
    """Context for how an answer should be checked."""
    
    type: str  # 'number', 'formula', 'interval', 'point', 'vector', 'string'
    variables: List[str]  # Variables in the formula
    checker: str  # 'standard', 'up_to_constant', 'up_to_sign', etc.
    tolerance: float
    num_samples: int  # For numeric checking
    allow_implicit_mult: bool  # Allow 2x instead of 2*x
    
    # Formula-specific
    domain: Optional[Interval]  # Valid domain for testing
    
    # String-specific
    case_sensitive: bool
    trim_whitespace: bool
```

#### Store in Problem Metadata:
```python
{
    'answers': {
        'AnSwEr0001': {
            'correct_value': 'x^2 + x - 2',
            'type': 'formula',
            'variables': ['x'],
            'checker': 'up_to_constant',
            'tolerance': 0.01
        }
    }
}
```

---

### Phase 7: Frontend Improvements

#### Enhanced Answer Input:
```tsx
// Auto-detect answer type and provide appropriate input
<AnswerInput
  answerId="AnSwEr0001"
  type="formula"  // or 'number', 'interval', etc.
  variables={['x']}
  value={studentAnswer}
  onChange={handleChange}
  onSubmit={handleSubmit}
  feedback={feedback}
/>
```

#### Real-time Syntax Checking:
```tsx
// Show syntax errors as user types
if (syntaxError) {
  return <span className="text-red-600">⚠ {syntaxError}</span>
}
```

#### Preview Rendering:
```tsx
// Show LaTeX preview of entered formula
<div className="mt-2">
  <span className="text-sm text-gray-600">Preview:</span>
  <Markdown>${formatForLatex(studentAnswer)}$</Markdown>
</div>
```

---

## Testing Strategy

### Unit Tests:
```python
# test_expression_parser.py
def test_parse_simple():
    assert parse("x + 2") == BinaryOp('+', Var('x'), Num(2))

def test_parse_nested():
    assert parse("(x+1)(x-1)") == BinaryOp('*', ...)

def test_implicit_mult():
    assert parse("2x") == BinaryOp('*', Num(2), Var('x'))

# test_simplifier.py
def test_expand():
    assert simplify("(x-1)(x+2)") == "x^2 + x - 2"

# test_checker.py
def test_equivalent_formulas():
    checker = FormulaChecker()
    assert checker.check("(x-1)(x+2)", "x^2+x-2")[0] == True

def test_up_to_constant():
    checker = FormulaChecker(mode='up_to_constant')
    assert checker.check("2x+4", "x+2")[0] == True
```

---

## Libraries to Consider

### Option 1: SymPy (Recommended)
**Pros:**
- ✅ Mature symbolic math library
- ✅ Excellent simplification, expansion
- ✅ Large community, well-documented
- ✅ Can handle complex expressions

**Cons:**
- ❌ Heavy dependency (~10 MB)
- ❌ Slower for simple comparisons

**Usage:**
```python
from sympy import sympify, simplify, Eq
from sympy.parsing.sympy_parser import parse_expr

student = parse_expr("(x-1)(x+2)")
correct = parse_expr("x**2 + x - 2")

# Expand and simplify
student_expanded = student.expand()
# Compare
assert student_expanded.equals(correct)
```

### Option 2: Custom Parser (Lightweight)
**Pros:**
- ✅ Minimal dependencies
- ✅ Fast for simple expressions
- ✅ Full control over behavior

**Cons:**
- ❌ Need to implement everything
- ❌ More bugs to fix
- ❌ Limited to what we implement

**Recommendation**: Start with **SymPy** for MVP, optimize later if needed.

---

## Implementation Timeline

### Week 1: Core Expression System
- [ ] Add SymPy dependency
- [ ] Create expression parser wrapper
- [ ] Implement basic formula checker
- [ ] Update answer checker to use formula checker

### Week 2: Answer Types & Modes
- [ ] Implement up-to-constant checker
- [ ] Add interval checker
- [ ] Add point/vector checker
- [ ] Update problem metadata to specify checker type

### Week 3: Frontend & Polish
- [ ] Add syntax validation in frontend
- [ ] Implement preview rendering
- [ ] Improve error messages
- [ ] Add unit tests

### Week 4: Advanced Features
- [ ] Custom checker functions
- [ ] Partial credit support
- [ ] Performance optimization
- [ ] Documentation

---

## Example Usage (End Goal)

### Backend:
```python
# In problem setup
answer = Formula("x^2 + x - 2")
answer.checker = "up_to_constant"
answer.variables = ["x"]

# When checking
checker = FormulaChecker(mode="up_to_constant")
is_correct, message = checker.check(
    student_answer="(x-1)(x+2)",
    correct_answer="x^2 + x - 2",
    context={'variables': ['x']}
)
```

### Frontend:
```tsx
<AnswerInput
  type="formula"
  placeholder="Enter an expression in x"
  hint="Expand or factor your answer"
  showPreview={true}
  variables={['x']}
/>
```

---

## Next Steps

1. **Start with SymPy** - Add to `packages/pg_renderer/requirements.txt`
2. **Create FormulaChecker** - Wrap SymPy for our use case
3. **Update answer checker** - Route to appropriate checker based on type
4. **Test with current problems** - Verify it works on existing sample problems
5. **Iterate** - Add more features as needed


