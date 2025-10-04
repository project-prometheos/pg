# ANSWER SYSTEM IMPLEMENTATION PLAN

**Goal**: Complete answer checking system with filter architecture and MultiAnswer
**Estimated Effort**: 2-3 weeks (1 developer)
**Priority**: HIGH - Blocks sophisticated answer checking

---

## EXECUTIVE SUMMARY

The Python answer system has basic evaluators but is missing critical infrastructure from the Perl implementation:
- Answer filter chains (pre/post processing)
- Value::cmp() answer checkers for all types
- MultiAnswer coordination system
- Answer modifiers and customization

**Current State**: Basic evaluate() methods (400 lines)
**Target State**: Full AnswerEvaluator.pm + Value::AnswerChecker.pm parity (1,250 lines)

---

## PHASE 1: ANSWER FILTER ARCHITECTURE (Week 1, Days 1-3)

### 1.1 Filter Chain System

**Reference**: AnswerEvaluator.pm:200-350

```python
from typing import Callable, Any
from dataclasses import dataclass

@dataclass
class AnswerFilter:
    """
    Answer processing filter.

    Filters transform answer data before or after evaluation.
    """
    name: str
    function: Callable[[AnswerHash], AnswerHash]
    priority: int = 0


class FilterChain:
    """Manages chain of answer filters."""

    def __init__(self):
        self.pre_filters: list[AnswerFilter] = []
        self.post_filters: list[AnswerFilter] = []

    def add_pre_filter(
        self,
        name: str,
        function: Callable[[AnswerHash], AnswerHash],
        priority: int = 0
    ) -> None:
        """
        Add pre-processing filter.

        Pre-filters run before answer evaluation.
        Common uses:
        - Trim whitespace
        - Normalize input
        - Convert units
        - Parse special formats
        """
        filter = AnswerFilter(name, function, priority)
        self.pre_filters.append(filter)
        # Sort by priority (higher first)
        self.pre_filters.sort(key=lambda f: -f.priority)

    def add_post_filter(
        self,
        name: str,
        function: Callable[[AnswerHash], AnswerHash],
        priority: int = 0
    ) -> None:
        """
        Add post-processing filter.

        Post-filters run after answer evaluation.
        Common uses:
        - Modify feedback messages
        - Add hints
        - Adjust scores
        - Format preview
        """
        filter = AnswerFilter(name, function, priority)
        self.post_filters.append(filter)
        self.post_filters.sort(key=lambda f: -f.priority)

    def apply_pre_filters(self, answer_hash: AnswerHash) -> AnswerHash:
        """Apply all pre-filters in order."""
        for filter in self.pre_filters:
            try:
                answer_hash = filter.function(answer_hash)
            except Exception as e:
                answer_hash.error_message = f"Pre-filter '{filter.name}' error: {e}"
                answer_hash.error_flag = True
        return answer_hash

    def apply_post_filters(self, answer_hash: AnswerHash) -> AnswerHash:
        """Apply all post-filters in order."""
        for filter in self.post_filters:
            try:
                answer_hash = filter.function(answer_hash)
            except Exception as e:
                answer_hash.error_message = f"Post-filter '{filter.name}' error: {e}"
                answer_hash.error_flag = True
        return answer_hash


class AnswerEvaluator:
    """
    Enhanced evaluator with filter support.

    Reference: AnswerEvaluator.pm
    """

    def __init__(self, correct_answer: Any, **options):
        self.correct_answer = correct_answer
        self.options = options
        self.filter_chain = FilterChain()

        # Add default filters
        self._add_default_filters()

    def _add_default_filters(self) -> None:
        """Add standard pre/post filters."""
        # Pre-filter: trim whitespace
        self.filter_chain.add_pre_filter(
            "trim_whitespace",
            lambda ah: self._trim_whitespace(ah),
            priority=100
        )

        # Pre-filter: remove blank answers
        self.filter_chain.add_pre_filter(
            "remove_blank",
            lambda ah: self._check_blank(ah),
            priority=90
        )

        # Post-filter: format preview
        self.filter_chain.add_post_filter(
            "format_preview",
            lambda ah: self._format_preview(ah),
            priority=100
        )

    def _trim_whitespace(self, ah: AnswerHash) -> AnswerHash:
        """Trim whitespace from student answer."""
        if isinstance(ah.student_answer, str):
            ah.student_answer = ah.student_answer.strip()
        return ah

    def _check_blank(self, ah: AnswerHash) -> AnswerHash:
        """Check for blank answer."""
        if not ah.student_answer or str(ah.student_answer).strip() == "":
            ah.score = 0
            ah.ans_message = "Answer is blank"
            ah.error_flag = True
        return ah

    def _format_preview(self, ah: AnswerHash) -> AnswerHash:
        """Format preview strings."""
        # Default: use student answer as preview
        if not ah.preview_text_string:
            ah.preview_text_string = str(ah.student_answer)
        return ah

    def evaluate(self, student_answer: str) -> AnswerResult:
        """
        Evaluate with filter chain.

        Process:
        1. Create AnswerHash
        2. Apply pre-filters
        3. Check if pre-filters set error
        4. Call _do_evaluate() if no error
        5. Apply post-filters
        6. Convert to AnswerResult
        """
        # Create answer hash
        answer_hash = AnswerHash(
            student_answer=student_answer,
            correct_answer=self.correct_answer
        )

        # Apply pre-filters
        answer_hash = self.filter_chain.apply_pre_filters(answer_hash)

        # Check for pre-filter errors
        if not answer_hash.error_flag:
            # Do actual evaluation
            answer_hash = self._do_evaluate(answer_hash)

        # Apply post-filters
        answer_hash = self.filter_chain.apply_post_filters(answer_hash)

        # Convert to result
        return answer_hash.to_result()

    def _do_evaluate(self, answer_hash: AnswerHash) -> AnswerHash:
        """
        Actual evaluation logic (override in subclasses).

        Args:
            answer_hash: Pre-filtered answer hash

        Returns:
            Evaluated answer hash
        """
        raise NotImplementedError("Subclasses must implement _do_evaluate")

    # Filter management methods

    def with_pre_filter(
        self,
        name: str,
        function: Callable[[AnswerHash], AnswerHash],
        priority: int = 0
    ) -> "AnswerEvaluator":
        """
        Add pre-filter (fluent interface).

        Returns:
            self for chaining
        """
        self.filter_chain.add_pre_filter(name, function, priority)
        return self

    def with_post_filter(
        self,
        name: str,
        function: Callable[[AnswerHash], AnswerHash],
        priority: int = 0
    ) -> "AnswerEvaluator":
        """Add post-filter (fluent interface)."""
        self.filter_chain.add_post_filter(name, function, priority)
        return self
```

**Usage Example**:
```python
# Create evaluator with custom filters
evaluator = num_cmp(42)

# Add custom pre-filter
def round_to_int(ah):
    """Round student answer to integer."""
    try:
        ah.student_answer = str(int(float(ah.student_answer)))
    except:
        pass
    return ah

evaluator.with_pre_filter("round", round_to_int)

# Add custom post-filter for feedback
def add_hint(ah):
    """Add hint if wrong."""
    if ah.score < 1:
        ah.ans_message += " Hint: The answer is a perfect square."
    return ah

evaluator.with_post_filter("hint", add_hint)
```

**Deliverable**: Filter chain architecture with pre/post filters

---

### 1.2 Common Answer Filters

**Reference**: Various PG macro files

```python
# packages/pg_answer/pg_answer/filters.py

class StandardFilters:
    """Collection of standard answer filters."""

    @staticmethod
    def ignore_case(answer_hash: AnswerHash) -> AnswerHash:
        """Convert student answer to lowercase."""
        if isinstance(answer_hash.student_answer, str):
            answer_hash.student_answer = answer_hash.student_answer.lower()
        return answer_hash

    @staticmethod
    def ignore_whitespace(answer_hash: AnswerHash) -> AnswerHash:
        """Remove all whitespace."""
        if isinstance(answer_hash.student_answer, str):
            answer_hash.student_answer = "".join(answer_hash.student_answer.split())
        return answer_hash

    @staticmethod
    def units_filter(expected_units: str):
        """Filter for unit checking."""
        def filter_func(answer_hash: AnswerHash) -> AnswerHash:
            # Parse student answer for units
            # Format: "42 kg" or "42kg"
            import re
            match = re.match(r"([0-9.+-eE]+)\s*([a-zA-Z]+)?", str(answer_hash.student_answer))

            if match:
                number, units = match.groups()
                answer_hash.student_answer = number

                if units and units != expected_units:
                    answer_hash.ans_message = f"Wrong units. Expected {expected_units}, got {units}"
                    answer_hash.score = 0
                elif not units:
                    answer_hash.ans_message = f"Missing units. Please include {expected_units}"
                    answer_hash.score = 0

            return answer_hash

        return filter_func

    @staticmethod
    def fraction_filter(answer_hash: AnswerHash) -> AnswerHash:
        """Parse fraction input (e.g., "3/4")."""
        if isinstance(answer_hash.student_answer, str):
            import re
            match = re.match(r"(-?\d+)/(-?\d+)", answer_hash.student_answer)
            if match:
                num, denom = match.groups()
                if int(denom) != 0:
                    answer_hash.student_answer = str(int(num) / int(denom))
        return answer_hash

    @staticmethod
    def latex_preview_filter(answer_hash: AnswerHash) -> AnswerHash:
        """Generate LaTeX preview."""
        # Use pg_parser to parse and convert to LaTeX
        try:
            from pg_parser import Parser
            from pg_parser.visitors import TeXVisitor

            parser = Parser()
            ast = parser.parse(str(answer_hash.student_answer))
            visitor = TeXVisitor()
            latex = ast.accept(visitor)

            answer_hash.preview_latex_string = latex
        except:
            pass  # Silently fail if can't parse

        return answer_hash
```

**Deliverable**: Standard filter library

---

## PHASE 2: VALUE::CMP() FOR ALL TYPES (Week 1, Days 4-5 + Week 2, Days 1-2)

### 2.1 Base cmp() Method

**Reference**: Value::AnswerChecker.pm:1-100

```python
class MathValue(ABC):
    """Enhanced with answer checking."""

    def cmp(self, **options) -> AnswerEvaluator:
        """
        Create answer checker for this value.

        Reference: Value::AnswerChecker.pm

        Returns an AnswerEvaluator that checks student answers
        against this value.

        Args:
            **options: Evaluator options
                - tolerance: Comparison tolerance
                - tolType: "relative" or "absolute"
                - showTypeWarnings: Show type mismatch warnings
                - studentsMustReduceUnions: Require reduced unions
                - ... (type-specific options)

        Returns:
            AnswerEvaluator for this value type
        """
        # Get appropriate evaluator for value type
        from pg_answer.evaluators import get_evaluator_for_type

        evaluator_class = get_evaluator_for_type(type(self))
        evaluator = evaluator_class(
            correct_answer=self,
            **options
        )

        # Transfer flags from value to evaluator
        self._transfer_flags_to_evaluator(evaluator)

        return evaluator

    def _transfer_flags_to_evaluator(self, evaluator: AnswerEvaluator) -> None:
        """Transfer relevant flags to evaluator."""
        # Transfer tolerance settings
        if hasattr(self, "tolerance"):
            evaluator.tolerance = self.tolerance
        if hasattr(self, "tolType"):
            evaluator.tolerance_mode = self.tolType
        if hasattr(self, "zeroLevel"):
            evaluator.zero_level = self.zeroLevel
        if hasattr(self, "zeroLevelTol"):
            evaluator.zero_level_tolerance = self.zeroLevelTol
```

**Deliverable**: Base cmp() method on MathValue

---

### 2.2 Type-Specific cmp() Implementations

```python
# Real numbers
class Real(MathValue):
    """Real with cmp()."""

    def cmp(self, **options) -> NumericEvaluator:
        """Numeric answer checker."""
        return NumericEvaluator(
            correct_answer=self.value,
            tolerance=options.get("tolerance", 0.001),
            tolerance_mode=options.get("tolType", "relative"),
            **options
        )


# Complex numbers
class Complex(MathValue):
    """Complex with cmp()."""

    def cmp(self, **options) -> ComplexEvaluator:
        """Complex answer checker."""
        return ComplexEvaluator(
            correct_answer=self,
            tolerance=options.get("tolerance", 0.001),
            **options
        )


# Vectors
class Vector(MathValue):
    """Vector with cmp()."""

    def cmp(self, **options) -> VectorEvaluator:
        """Vector answer checker."""
        return VectorEvaluator(
            correct_answer=self,
            tolerance=options.get("tolerance", 0.001),
            parallel_allowed=options.get("parallel", False),
            **options
        )


# Matrices
class Matrix(MathValue):
    """Matrix with cmp()."""

    def cmp(self, **options) -> MatrixEvaluator:
        """Matrix answer checker."""
        return MatrixEvaluator(
            correct_answer=self,
            tolerance=options.get("tolerance", 0.001),
            **options
        )


# Intervals
class Interval(MathValue):
    """Interval with cmp()."""

    def cmp(self, **options) -> IntervalEvaluator:
        """Interval answer checker."""
        return IntervalEvaluator(
            correct_answer=self,
            **options
        )


# Sets
class Set(MathValue):
    """Set with cmp()."""

    def cmp(self, **options) -> SetEvaluator:
        """Set answer checker."""
        return SetEvaluator(
            correct_answer=self,
            **options
        )


# Formulas (already has cmp)
class Formula(MathValue):
    """Formula with enhanced cmp()."""

    def cmp(self, **options) -> FormulaEvaluator:
        """
        Formula answer checker.

        Options:
            - limits: Variable limits for test points
            - num_points: Number of test points
            - vars: Variables to use
            - test_at: Specific test points
        """
        return FormulaEvaluator(
            correct_answer=self,
            test_points=options.get("num_points", 5),
            limits=options.get("limits"),
            variables=options.get("vars", self.variables),
            test_at=options.get("test_at"),
            **options
        )


# Points
class Point(MathValue):
    """Point with cmp()."""

    def cmp(self, **options) -> PointEvaluator:
        """Point answer checker."""
        return PointEvaluator(
            correct_answer=self,
            tolerance=options.get("tolerance", 0.001),
            **options
        )


# Lists
class List(MathValue):
    """List with cmp()."""

    def cmp(self, **options) -> ListEvaluator:
        """
        List answer checker.

        Options:
            - ordered: Require same order (default True)
            - entry_type: Expected element type
        """
        return ListEvaluator(
            correct_answer=self,
            ordered=options.get("ordered", True),
            **options
        )


# Strings
class String(MathValue):
    """String with cmp()."""

    def cmp(self, **options) -> StringEvaluator:
        """
        String answer checker.

        Options:
            - case_sensitive: Case matters (default True)
            - trim_whitespace: Remove surrounding whitespace
        """
        return StringEvaluator(
            correct_answer=self.value,
            case_sensitive=options.get("case_sensitive", True),
            **options
        )
```

**Deliverable**: cmp() method for all MathValue types

---

## PHASE 3: MULTIANSWER SYSTEM (Week 2, Days 3-5)

### 3.1 MultiAnswer Implementation

**Reference**: MultiAnswer.pm (600 lines)

```python
class MultiAnswer:
    """
    Coordinate multiple related answer blanks.

    Reference: MultiAnswer.pm

    MultiAnswer allows checking answers that depend on each other.
    For example:
    - Point and its equation
    - Function and its derivative
    - Matrix and its determinant

    Usage:
        ma = MultiAnswer(answer1, answer2)
        ma.with_checker(lambda correct, student, self: ...)

        TEXT("Point: ", ma.ans_rule(0))
        TEXT("Slope: ", ma.ans_rule(1))

        ANS(ma.cmp())
    """

    def __init__(self, *correct_answers: MathValue, **options):
        """
        Create multi-answer object.

        Args:
            *correct_answers: Correct answers for each blank
            **options:
                - checker: Custom checker function
                - separator: Separator for combined preview
                - ordered: Require same order
                - tex_separator: LaTeX separator
        """
        self.correct_answers = list(correct_answers)
        self.num_answers = len(correct_answers)
        self.options = options

        # Custom checker function
        self.checker: Callable | None = options.get("checker")

        # Answer blank tracking
        self.answer_names: list[str] = []
        self.student_answers: list[Any] = []

        # Results
        self.results: list[AnswerResult] = []

    def with_checker(
        self,
        checker: Callable[[list[Any], list[Any], "MultiAnswer"], list[int]]
    ) -> "MultiAnswer":
        """
        Set custom checker function.

        The checker receives:
            - correct: List of correct answers
            - student: List of student answers
            - self: The MultiAnswer object

        Returns:
            List of scores (0 or 1) for each answer

        Example:
            def check_point_and_line(correct, student, ma):
                # correct = [Point, Line]
                # student = [student_point, student_line]

                # Check if point is on line
                point = student[0]
                line = student[1]

                if line.contains(point):
                    return [1, 1]  # Both correct
                else:
                    return [0, 0]  # Both wrong

            ma.with_checker(check_point_and_line)
        """
        self.checker = checker
        return self

    def ans_rule(self, index: int = 0, width: int = 20) -> str:
        """
        Create answer rule for specific answer.

        Args:
            index: Which answer (0-indexed)
            width: Width of input field

        Returns:
            HTML for answer blank
        """
        env = get_environment()
        name = env.next_answer_name()

        # Track this answer blank
        self.answer_names.append(name)

        return f'<input type="text" name="{name}" size="{width}" />'

    def cmp(self) -> "MultiAnswerEvaluator":
        """
        Create evaluator for this multi-answer.

        Returns:
            MultiAnswerEvaluator that coordinates all blanks
        """
        return MultiAnswerEvaluator(self)


class MultiAnswerEvaluator(AnswerEvaluator):
    """
    Evaluator for MultiAnswer.

    Coordinates evaluation of multiple related answers.
    """

    def __init__(self, multi_answer: MultiAnswer):
        self.multi_answer = multi_answer
        super().__init__(
            correct_answer=multi_answer.correct_answers,
            **multi_answer.options
        )

        # Create individual evaluators
        self.evaluators: list[AnswerEvaluator] = []
        for correct in multi_answer.correct_answers:
            if hasattr(correct, "cmp"):
                evaluator = correct.cmp()
            else:
                # Fallback: numeric evaluator
                from pg_answer.evaluators import NumericEvaluator
                evaluator = NumericEvaluator(correct_answer=correct)

            self.evaluators.append(evaluator)

    def _do_evaluate(self, answer_hash: AnswerHash) -> AnswerHash:
        """
        Evaluate all answers together.

        Process:
        1. Get student answers for all blanks
        2. Evaluate individually if no custom checker
        3. If custom checker, call it with all answers
        4. Store individual results
        5. Return combined result
        """
        env = get_environment()

        # Collect student answers
        student_answers = []
        for name in self.multi_answer.answer_names:
            student_ans = env.inputs.get(name, "")
            student_answers.append(student_ans)

        # Evaluate
        if self.multi_answer.checker:
            # Custom checker
            scores = self.multi_answer.checker(
                self.multi_answer.correct_answers,
                student_answers,
                self.multi_answer
            )

            # Create results for each answer
            for i, score in enumerate(scores):
                result = AnswerResult(
                    score=score,
                    correct=(score == 1),
                    student_answer=str(student_answers[i]),
                    correct_answer=str(self.multi_answer.correct_answers[i])
                )
                self.multi_answer.results.append(result)

            # Overall score: average or all-or-nothing
            if self.options.get("allow_partial_credit", False):
                overall_score = sum(scores) / len(scores)
            else:
                overall_score = 1 if all(s == 1 for s in scores) else 0

            answer_hash.score = overall_score
            answer_hash.correct = (overall_score == 1)

        else:
            # Evaluate individually
            scores = []
            for i, evaluator in enumerate(self.evaluators):
                result = evaluator.evaluate(student_answers[i])
                self.multi_answer.results.append(result)
                scores.append(result.score)

            # Overall score
            if self.options.get("allow_partial_credit", False):
                answer_hash.score = sum(scores) / len(scores)
            else:
                answer_hash.score = 1 if all(s == 1 for s in scores) else 0

            answer_hash.correct = (answer_hash.score == 1)

        # Set preview (combined)
        separator = self.options.get("separator", ", ")
        answer_hash.preview_text_string = separator.join(
            str(ans) for ans in student_answers
        )

        return answer_hash
```

**Usage Example**:
```python
# Problem: Enter a point and a line through it

point = Point([2, 3])
line = Formula("y = 2*x - 1", variables=["x", "y"])

ma = MultiAnswer(point, line)

def check(correct, student, ma):
    """Check if student's point is on student's line."""
    try:
        student_point = student[0]  # Parse point
        student_line = student[1]   # Parse line

        # Evaluate line at point's x-coordinate
        x_val = student_point.x
        y_expected = student_line.eval(x=x_val)

        if abs(y_expected - student_point.y) < 0.001:
            return [1, 1]  # Both correct
        else:
            return [0, 0]  # Wrong
    except:
        return [0, 0]

ma.with_checker(check)

TEXT("Point: ", ma.ans_rule(0))
TEXT("Line: ", ma.ans_rule(1))

ANS(ma.cmp())
```

**Deliverable**: MultiAnswer system for related answer blanks

---

## PHASE 4: ENHANCED EVALUATORS (Week 3, Days 1-3)

### 4.1 Units Support

```python
class NumericWithUnitsEvaluator(NumericEvaluator):
    """
    Numeric evaluator with unit checking.

    Reference: parserNumberWithUnits.pl
    """

    def __init__(
        self,
        correct_answer: float,
        units: str,
        **options
    ):
        super().__init__(correct_answer, **options)
        self.expected_units = units

        # Add units filter
        self.with_pre_filter(
            "units",
            StandardFilters.units_filter(units),
            priority=50
        )


def num_cmp(correct: float, units: str = None, **options):
    """
    Enhanced num_cmp with units.

    Usage:
        ANS(num_cmp(9.8, units="m/s^2"))
    """
    if units:
        return NumericWithUnitsEvaluator(correct, units, **options)
    else:
        return NumericEvaluator(correct, **options)
```

**Deliverable**: Units support in numeric evaluator

---

### 4.2 Fraction Evaluator

```python
class FractionEvaluator(AnswerEvaluator):
    """
    Evaluator for fractions.

    Checks that answer is in reduced form.
    """

    def __init__(
        self,
        correct_answer: str | tuple[int, int],
        require_reduced: bool = True,
        **options
    ):
        if isinstance(correct_answer, str):
            # Parse "3/4"
            num, denom = map(int, correct_answer.split("/"))
            correct_answer = (num, denom)

        super().__init__(correct_answer, **options)
        self.require_reduced = require_reduced

        # Add fraction parsing filter
        self.with_pre_filter("parse_fraction", self._parse_fraction)

    def _parse_fraction(self, ah: AnswerHash) -> AnswerHash:
        """Parse fraction from student answer."""
        import re
        from math import gcd

        match = re.match(r"(-?\d+)/(-?\d+)", str(ah.student_answer))
        if not match:
            ah.ans_message = "Please enter answer as a fraction (e.g., 3/4)"
            ah.error_flag = True
            return ah

        num, denom = map(int, match.groups())

        if denom == 0:
            ah.ans_message = "Denominator cannot be zero"
            ah.error_flag = True
            return ah

        # Store as tuple
        ah.student_answer = (num, denom)

        # Check if reduced
        if self.require_reduced:
            g = gcd(abs(num), abs(denom))
            if g > 1:
                ah.ans_message = "Fraction must be in reduced form"
                ah.score = 0

        return ah

    def _do_evaluate(self, ah: AnswerHash) -> AnswerHash:
        """Compare fractions."""
        correct_num, correct_denom = self.correct_answer
        student_num, student_denom = ah.student_answer

        # Compare as floats
        correct_val = correct_num / correct_denom
        student_val = student_num / student_denom

        if abs(correct_val - student_val) < 1e-10:
            ah.score = 1
            ah.correct = True
        else:
            ah.score = 0
            ah.correct = False

        return ah
```

**Deliverable**: Fraction evaluator with reduction checking

---

## INTEGRATION & TESTING

### Testing Strategy

```python
def test_filter_chain():
    """Test pre/post filter execution."""
    evaluator = NumericEvaluator(42)

    # Add custom pre-filter
    calls = []
    def track_filter(ah):
        calls.append("pre")
        return ah

    evaluator.with_pre_filter("track", track_filter)

    # Evaluate
    result = evaluator.evaluate("42")

    assert "pre" in calls
    assert result.correct

def test_value_cmp():
    """Test cmp() on all value types."""
    # Real
    real = Real(42)
    evaluator = real.cmp()
    assert evaluator.evaluate("42").correct

    # Vector
    vec = Vector([1, 2, 3])
    evaluator = vec.cmp()
    assert evaluator.evaluate("<1, 2, 3>").correct

    # Formula
    formula = Formula("x^2", variables=["x"])
    evaluator = formula.cmp()
    assert evaluator.evaluate("x**2").correct

def test_multi_answer():
    """Test MultiAnswer coordination."""
    point = Point([1, 2])
    slope = Real(3)

    ma = MultiAnswer(point, slope)

    def check(correct, student, ma):
        # Check if point and slope are consistent
        # (This is a simplified example)
        return [1, 1] if student[0] and student[1] else [0, 0]

    ma.with_checker(check)

    # This would be tested with full problem context
    evaluator = ma.cmp()
    assert evaluator is not None

def test_units():
    """Test numeric with units."""
    evaluator = num_cmp(9.8, units="m/s^2")

    # Correct units
    result = evaluator.evaluate("9.8 m/s^2")
    assert result.correct

    # Wrong units
    result = evaluator.evaluate("9.8 kg")
    assert not result.correct
    assert "Wrong units" in result.ans_message
```

---

## DELIVERABLES & MILESTONES

### Week 1:
- ✅ Day 3: Filter chain system
- ✅ Day 5: cmp() for numeric, vector, formula

### Week 2:
- ✅ Day 2: cmp() for all remaining types
- ✅ Day 5: MultiAnswer implementation

### Week 3:
- ✅ Day 3: Enhanced evaluators (units, fractions)
- ✅ Day 5: Full integration and testing

---

## SUCCESS CRITERIA

1. **Functional**:
   - Filter chains work for all evaluators
   - cmp() available on all MathValue types
   - MultiAnswer coordinates related answers
   - Units and fractions supported

2. **Compatibility**:
   - Matches Perl filter behavior
   - All answer types checkable
   - MultiAnswer patterns work

3. **Quality**:
   - 95% test coverage
   - All edge cases handled
   - Zero regression

---

**End of Answer System Implementation Plan**
