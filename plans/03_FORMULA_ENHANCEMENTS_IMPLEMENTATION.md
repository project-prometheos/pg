# FORMULA ENHANCEMENTS IMPLEMENTATION PLAN

**Goal**: Achieve 1:1 parity with Value::Formula.pm (1,156 lines)
**Estimated Effort**: 2 weeks (1 developer)
**Priority**: HIGH - Blocks accurate answer checking

---

## EXECUTIVE SUMMARY

The Python Formula class (700 lines) is missing critical features from Value::Formula.pm (1,156 lines). The gap of 456 lines represents sophisticated functionality essential for:
- Adaptive parameter handling
- Test point caching and optimization
- Domain checking with undefined points
- Advanced differentiation
- Formula comparison accuracy

**Current State**: Basic formula with eval(), diff(), reduce()
**Target State**: Full Formula.pm parity with adaptive parameters, caching, domain checking

---

## PHASE 1: TEST POINT SYSTEM ENHANCEMENTS (Week 1, Days 1-2)

### 1.1 createRandomPoints() - Advanced Implementation

**Reference**: Value::Formula.pm:300-380

```python
class Formula(MathValue):
    """Enhanced Formula with test point generation."""

    def create_random_points(
        self,
        n: int | None = None,
        test_at: dict[str, list[float]] | None = None
    ) -> list[list[float]]:
        """
        Generate random test points for formula evaluation.

        Reference: Value::Formula.pm:300-380

        Process:
        1. Determine number of points (from flags or default 5)
        2. Get variable limits from context or use defaults
        3. Handle special test_at points (must-include values)
        4. Generate random points within limits
        5. Ensure good distribution across domain

        Args:
            n: Number of test points (overrides context setting)
            test_at: Specific points to include {var: [values]}

        Returns:
            List of test points (each point is list of values)
        """
        # Get number of points
        if n is None:
            n = self.getFlag("num_points", 5)

        # Get variables
        vars_list = sorted(self.variables)
        if not vars_list:
            return [[]]  # No variables, return empty point

        # Get limits for each variable
        context = self.context
        limits = {}
        default_limits = self.getFlag("limits", [-2, 2])

        for var in vars_list:
            var_obj = context.variables.get(var)
            if var_obj and hasattr(var_obj, "limits"):
                limits[var] = var_obj.limits
            else:
                limits[var] = default_limits

        # Handle test_at (must-include points)
        must_include = []
        if test_at:
            for var, values in test_at.items():
                if var in vars_list:
                    for val in values:
                        # Create point with this value for var, random for others
                        point = []
                        for v in vars_list:
                            if v == var:
                                point.append(val)
                            else:
                                lo, hi = limits[v]
                                point.append(random.uniform(lo, hi))
                        must_include.append(point)

        # Generate random points
        points = []
        rng = self._get_rng()

        # Add must-include points
        points.extend(must_include)

        # Generate remaining random points
        remaining = n - len(must_include)
        for _ in range(remaining):
            point = []
            for var in vars_list:
                lo, hi = limits[var]
                point.append(rng.uniform(lo, hi))
            points.append(point)

        # Ensure good distribution using granularity
        granularity = self.getFlag("granularity", 1000)
        if granularity > 0:
            points = self._apply_granularity(points, limits, granularity)

        return points

    def _apply_granularity(
        self,
        points: list[list[float]],
        limits: dict[str, tuple[float, float]],
        granularity: int
    ) -> list[list[float]]:
        """
        Apply granularity to ensure evenly-spaced test points.

        Reference: Value::Formula.pm:340-360
        """
        vars_list = sorted(self.variables)
        adjusted = []

        for point in points:
            adjusted_point = []
            for i, var in enumerate(vars_list):
                lo, hi = limits[var]
                val = point[i]

                # Round to granularity
                range_size = hi - lo
                step = range_size / granularity
                rounded = round((val - lo) / step) * step + lo

                # Clamp to limits
                rounded = max(lo, min(hi, rounded))
                adjusted_point.append(rounded)

            adjusted.append(adjusted_point)

        return adjusted

    def _get_rng(self) -> random.Random:
        """Get RNG from context or create new one."""
        if hasattr(self, "_rng"):
            return self._rng

        # Get seed from context or use default
        seed = self.context.get("problem_seed", 12345)
        self._rng = random.Random(seed)
        return self._rng
```

**Deliverable**: Advanced random point generation with granularity

---

### 1.2 createPointValues() with Caching

**Reference**: Value::Formula.pm:264-299

```python
def create_point_values(
    self,
    points: list[list[float]] | None = None,
    show_error: bool = True,
    cache_results: bool = False,
    check_undefined: bool = False
) -> list[MathValue | None]:
    """
    Evaluate formula at test points with caching.

    Reference: Value::Formula.pm:264-299

    Process:
    1. Get or generate test points
    2. Create Python function if not cached
    3. Evaluate at each point
    4. Handle undefined points (domain errors)
    5. Cache results if requested
    6. Transfer tolerance flags to values

    Args:
        points: Test points to use
        show_error: Raise error on undefined point
        cache_results: Cache points and values
        check_undefined: Track undefined points

    Returns:
        List of evaluated values (None for undefined points)
    """
    # Get test points
    if points is None:
        if hasattr(self, "_test_points"):
            points = self._test_points
        else:
            points = self.create_random_points()

    # Get variables
    vars_list = sorted(self.variables)
    params_list = sorted(self.context.variables.parameters)
    param_zeros = [0] * len(params_list)

    # Get or create Python function
    if not hasattr(self, "_python_func"):
        self._python_func = self.python_function(
            vars=vars_list + params_list
        )

    func = self._python_func

    # Track undefined points
    undefined_count = 0
    max_undefined = self.getFlag("max_undefined", len(points))

    # Evaluate at each point
    values = []
    for point in points:
        try:
            # Call function with point values and parameter zeros
            result = func(*point, *param_zeros)

            if result is None:
                if not check_undefined:
                    if show_error:
                        raise ValueError(
                            f"Can't evaluate formula on test point ({', '.join(map(str, point))})"
                        )
                    return None

                # Track undefined
                undefined_count += 1
                if undefined_count > max_undefined:
                    if show_error:
                        raise ValueError(
                            f"Too many undefined points (>{max_undefined})"
                        )
                    return None

                values.append(None)
            else:
                # Convert to MathValue
                value = MathValue.from_python(result)
                value = value.with_context(self.context)

                # Transfer tolerance flags from formula
                value.transfer_flags_from(self, [
                    "tolerance", "tolType", "zeroLevel", "zeroLevelTol"
                ])

                values.append(value)

        except Exception as e:
            if not check_undefined:
                if show_error:
                    raise ValueError(
                        f"Error evaluating formula: {e}"
                    )
                return None

            values.append(None)

    # Cache if requested
    if cache_results:
        self._test_points = points
        self._test_values = values

    return values
```

**Deliverable**: Point value evaluation with caching and error handling

---

## PHASE 2: ADAPTIVE PARAMETERS (Week 1, Days 3-5)

### 2.1 AdaptParameters() Implementation

**Reference**: Value::Formula.pm:382-435

```python
def adapt_parameters(
    self,
    student_formula: "Formula",
    parameters: list[str]
) -> bool:
    """
    Adapt parameters to match student formula.

    Reference: Value::Formula.pm:382-435

    This is the key feature for handling formulas with undetermined constants.
    For example, if correct answer is "C*e^x" and student enters "5*e^x",
    we adapt C=5 and re-evaluate.

    Process:
    1. Check if we have parameters to adapt
    2. Evaluate both formulas at test points
    3. For each point, solve for parameter values
    4. Store adapted parameter values
    5. Re-evaluate with adapted parameters
    6. Return True if adaptation successful

    Args:
        student_formula: Student's formula
        parameters: List of parameter names to adapt

    Returns:
        True if parameters adapted successfully
    """
    if not parameters:
        return False

    # Get test points
    points = self._test_points or self.create_random_points()

    # Get correct values (already computed)
    correct_values = self._test_values or self.create_point_values(points, cache_results=True)

    # Variables (not parameters)
    vars_list = sorted(self.variables)
    all_vars = vars_list + list(parameters)

    # Create function with parameters
    if not hasattr(self, "_param_func"):
        self._param_func = self.python_function(vars=all_vars)

    # Student function
    student_func = student_formula.python_function(vars=vars_list)

    # Adapted values will be stored here
    adapted_values = []

    # For each test point, solve for parameters
    for i, point in enumerate(points):
        correct_val = correct_values[i]
        if correct_val is None:
            continue

        # Get student value at this point
        try:
            student_val = student_func(*point)
            student_val = MathValue.from_python(student_val)
        except:
            # Can't evaluate student formula
            return False

        # Solve for parameters
        # For simple case: one parameter
        if len(parameters) == 1:
            # Try to solve: correct(x, param) = student(x)
            # This requires numerical solving
            param_value = self._solve_for_parameter(
                point, correct_val, student_val
            )
            if param_value is None:
                return False

            # Evaluate with adapted parameter
            try:
                adapted_val = self._param_func(*point, param_value)
                adapted_val = MathValue.from_python(adapted_val)
                adapted_values.append(adapted_val)
            except:
                return False
        else:
            # Multiple parameters: more complex solving
            # This requires optimization/least-squares
            param_values = self._solve_for_parameters(
                point, correct_val, student_val, parameters
            )
            if param_values is None:
                return False

            try:
                adapted_val = self._param_func(*point, *param_values)
                adapted_val = MathValue.from_python(adapted_val)
                adapted_values.append(adapted_val)
            except:
                return False

    # Store adapted values for comparison
    self._test_adapt = adapted_values
    return True

def _solve_for_parameter(
    self,
    point: list[float],
    correct_val: MathValue,
    student_val: MathValue
) -> float | None:
    """
    Solve for single parameter value.

    For linear case: if correct = C*f(x) and student = g(x)
    Then: C = g(x) / f(x)
    """
    # Simple case: linear parameter
    # Evaluate correct formula with param=1
    vars_list = sorted(self.variables)
    try:
        base_val = self._param_func(*point, 1.0)
        base_val = MathValue.from_python(base_val)

        # If base is zero, can't solve
        if abs(base_val.to_python()) < 1e-14:
            return None

        # Parameter value
        param = student_val.to_python() / base_val.to_python()
        return param

    except:
        return None

def _solve_for_parameters(
    self,
    point: list[float],
    correct_val: MathValue,
    student_val: MathValue,
    parameters: list[str]
) -> list[float] | None:
    """Solve for multiple parameters using optimization."""
    from scipy.optimize import least_squares

    def residual(param_vals):
        """Residual function for least squares."""
        try:
            val = self._param_func(*point, *param_vals)
            val = MathValue.from_python(val)
            return val.to_python() - student_val.to_python()
        except:
            return 1e10  # Large residual for errors

    # Initial guess: all parameters = 1
    x0 = [1.0] * len(parameters)

    try:
        result = least_squares(residual, x0)
        if result.success:
            return list(result.x)
    except:
        pass

    return None
```

**Deliverable**: Adaptive parameter system for formula comparison

---

### 2.2 Enhanced compare() with Adaptive Parameters

**Reference**: Value::Formula.pm:169-235

```python
def compare(
    self,
    other: MathValue,
    tolerance: float = 0.001,
    mode: str = ToleranceMode.RELATIVE
) -> bool:
    """
    Compare formulas with adaptive parameter support.

    Reference: Value::Formula.pm:169-235

    Process:
    1. Convert other to Formula if needed
    2. Get test points
    3. Evaluate both formulas
    4. Check for adaptive parameters
    5. If adaptive, solve and re-compare
    6. Compare values with tolerance

    Args:
        other: Other formula/value
        tolerance: Comparison tolerance
        mode: Tolerance mode

    Returns:
        True if formulas are equal within tolerance
    """
    # Convert to formula
    if not isinstance(other, Formula):
        other = Formula(str(other), context=self.context)

    # Must be same context
    if self.context != other.context:
        raise ValueError("Formulas from different contexts can't be compared")

    # Get test points and values
    points = self._test_points or self.create_random_points()
    correct_values = self._test_values or self.create_point_values(points, cache_results=True)

    # Evaluate student formula
    check_undefined = self.getFlag("checkUndefinedPoints", False)
    student_values = other.create_point_values(points, show_error=True, check_undefined=check_undefined)

    # Check for domain mismatch
    if student_values is None:
        self.domain_mismatch = True
        return False

    # Try adaptive parameters
    parameters = list(self.context.variables.parameters)
    if self.adapt_parameters(other, parameters):
        # Use adapted values for comparison
        correct_values = self._test_adapt

        # Compare with adapted values
        tolerance_val = self.getFlag("tolerance", tolerance)
        is_relative = (mode == ToleranceMode.RELATIVE)
        zero_level = self.getFlag("zeroLevel", 1e-14)
        zero_level_tol = self.getFlag("zeroLevelTol", 1e-12)

        for i in range(len(points)):
            correct = correct_values[i]
            student = student_values[i]

            # Handle undefined points
            if correct is None or student is None:
                if correct is None and student is None:
                    continue  # Both undefined, OK
                else:
                    self.domain_mismatch = True
                    return False

            # Calculate tolerance for this point
            tol = tolerance_val
            c_val = correct.to_python()
            s_val = student.to_python()
            a_val = self._test_adapt[i].to_python() if hasattr(self, "_test_adapt") else c_val

            if is_relative:
                if abs(c_val) <= zero_level:
                    tol = zero_level_tol
                else:
                    tol *= abs(a_val)

            # Compare
            if abs(s_val - a_val) >= tol:
                return False

        return True

    # No adaptive parameters, standard comparison
    domain_error = False
    for i in range(len(points)):
        correct = correct_values[i]
        student = student_values[i]

        # Check undefined mismatch
        if (correct is None) != (student is None):
            domain_error = True
            continue

        if correct is None:
            continue

        # Compare values
        if not correct.compare(student, tolerance, mode):
            return False

    self.domain_mismatch = domain_error
    return True
```

**Deliverable**: Formula comparison with adaptive parameters

---

## PHASE 3: DOMAIN CHECKING (Week 2, Days 1-2)

### 3.1 Undefined Point Tracking

**Reference**: Value::Formula.pm:700-800

```python
# Use special UNDEF sentinel
class UNDEF:
    """Sentinel for undefined points."""
    pass

UNDEF_VALUE = UNDEF()

class Formula(MathValue):
    """Enhanced with domain checking."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Domain checking flags
        self.domain_mismatch = False
        self.check_undefined_points = kwargs.get("check_undefined_points", False)
        self.max_undefined = kwargs.get("max_undefined", None)

    def create_point_values_with_undefined(
        self,
        points: list[list[float]]
    ) -> list[MathValue | UNDEF]:
        """
        Evaluate with undefined point tracking.

        Returns UNDEF_VALUE for points where formula can't be evaluated.
        """
        func = self.python_function()
        values = []
        undefined_count = 0
        max_undef = self.max_undefined or len(points)

        for point in points:
            try:
                result = func(*point)
                if result is None or (isinstance(result, float) and math.isnan(result)):
                    # Undefined
                    undefined_count += 1
                    if undefined_count > max_undef:
                        raise ValueError(f"Too many undefined points: {undefined_count} > {max_undef}")
                    values.append(UNDEF_VALUE)
                else:
                    values.append(MathValue.from_python(result))
            except (ZeroDivisionError, ValueError, OverflowError):
                # Domain error
                undefined_count += 1
                if undefined_count > max_undef:
                    raise ValueError(f"Too many undefined points: {undefined_count} > {max_undef}")
                values.append(UNDEF_VALUE)

        return values

    def check_domain_compatibility(
        self,
        other: "Formula",
        points: list[list[float]]
    ) -> bool:
        """
        Check if two formulas have compatible domains.

        Returns True if they're undefined at the same points.
        """
        self_values = self.create_point_values_with_undefined(points)
        other_values = other.create_point_values_with_undefined(points)

        domain_compatible = True
        for i in range(len(points)):
            self_undef = isinstance(self_values[i], UNDEF)
            other_undef = isinstance(other_values[i], UNDEF)

            if self_undef != other_undef:
                # Mismatch in defined/undefined
                domain_compatible = False
                break

        return domain_compatible
```

**Deliverable**: Undefined point tracking and domain checking

---

## PHASE 4: DIFFERENTIATION ENHANCEMENTS (Week 2, Days 3-4)

### 4.1 Advanced Derivative with Chain Rule

**Reference**: Value::Formula.pm:580-650

```python
def D(self, var: str | None = None) -> "Formula":
    """
    Differentiate with respect to variable.

    Reference: Value::Formula.pm:580-650

    Enhanced to handle:
    - Chain rule
    - Multiple variables
    - Derivative context preservation

    Args:
        var: Variable to differentiate (uses default if None)

    Returns:
        Derivative formula
    """
    if var is None:
        # Get default variable from context
        vars_list = sorted(self.variables)
        if not vars_list:
            raise ValueError("Formula has no variables to differentiate")
        var = vars_list[0]

    if var not in self.variables:
        # Derivative of constant is zero
        return Formula("0", context=self.context)

    # Use SymPy for differentiation
    if not SYMPY_AVAILABLE:
        raise RuntimeError("SymPy required for differentiation")

    if not hasattr(self, "_sympy_expr"):
        self._build_sympy_expr()

    # Differentiate
    derivative = sp.diff(self._sympy_expr, sp.Symbol(var))

    # Create new Formula
    deriv_formula = Formula(
        derivative,
        variables=self.variables,
        context=self.context
    )

    # Transfer flags
    deriv_formula.transfer_flags_from(self, [
        "tolerance", "tolType", "zeroLevel", "zeroLevelTol",
        "limits", "num_points", "granularity"
    ])

    # Mark as derivative
    deriv_formula.is_derivative = True
    deriv_formula.derivative_of = self
    deriv_formula.derivative_var = var

    return deriv_formula

def transfer_flags_from(self, other: MathValue, flags: list[str]) -> None:
    """
    Transfer specified flags from another object.

    Reference: Value.pm:992-1009
    """
    for flag in flags:
        if hasattr(other, flag):
            setattr(self, flag, getattr(other, flag))
```

**Deliverable**: Enhanced differentiation with proper flag transfer

---

## PHASE 5: PYTHON FUNCTION GENERATION (Week 2, Day 5)

### 5.1 python_function() Implementation

**Reference**: Parser.pm:794-834 (perlFunction equivalent)

```python
def python_function(
    self,
    name: str | None = None,
    vars: list[str] | None = None
) -> Callable:
    """
    Generate Python function from formula.

    Reference: Parser.pm:794-834 (perlFunction)

    Process:
    1. Get variables (use formula vars if not specified)
    2. Generate Python code for evaluation
    3. Compile to function
    4. Cache for reuse

    Args:
        name: Function name (None for lambda)
        vars: Variable names (uses formula vars if None)

    Returns:
        Compiled Python function
    """
    # Use formula variables if not specified
    if vars is None:
        vars = sorted(self.variables)

    # Check cache
    cache_key = (name or "", tuple(vars))
    if hasattr(self, "_func_cache") and cache_key in self._func_cache:
        return self._func_cache[cache_key]

    # Build function code
    if SYMPY_AVAILABLE and hasattr(self, "_sympy_expr"):
        # Use SymPy lambdify (fast!)
        func = sp.lambdify(
            [sp.Symbol(v) for v in vars],
            self._sympy_expr,
            modules=["numpy", "math"]
        )
    else:
        # Fallback: use eval
        func = self._build_eval_function(vars)

    # Cache function
    if not hasattr(self, "_func_cache"):
        self._func_cache = {}
    self._func_cache[cache_key] = func

    return func

def _build_eval_function(self, vars: list[str]) -> Callable:
    """Build function using eval."""
    # Convert formula to Python expression
    expr_str = str(self.expression)

    # Build function
    var_params = ", ".join(vars)
    func_code = f"""
def formula_func({var_params}):
    import math
    return {expr_str}
"""

    # Compile
    namespace = {}
    exec(func_code, namespace)
    return namespace["formula_func"]
```

**Deliverable**: Python function generation with caching

---

## INTEGRATION & TESTING

### Integration with Existing Formula

```python
class Formula(MathValue):
    """Fully-featured Formula class."""

    def __init__(
        self,
        expression: str | Any,
        variables: list[str] | None = None,
        context: Any | None = None,
        # Test point configuration
        test_points: list[list[float]] | None = None,
        num_test_points: int = 5,
        limits: dict[str, tuple[float, float]] | None = None,
        # Domain checking
        check_undefined_points: bool = False,
        max_undefined: int | None = None,
        # Adaptive parameters
        parameters: list[str] | None = None
    ):
        """Initialize with all features."""
        self.expression = expression
        self.variables = variables or []
        self.context = context

        # Test points
        self._test_points = test_points
        self._test_values = None
        self._test_adapt = None
        self._num_test_points = num_test_points
        self._limits = limits or {}

        # Domain checking
        self.domain_mismatch = False
        self.check_undefined_points = check_undefined_points
        self.max_undefined = max_undefined or num_test_points

        # Adaptive parameters
        self._parameters = parameters or []

        # Caching
        self._python_func = None
        self._param_func = None
        self._func_cache = {}

        # Build SymPy expression
        if SYMPY_AVAILABLE:
            self._build_sympy_expr()
```

### Testing Strategy

```python
def test_adaptive_parameters():
    """Test adaptive parameter system."""
    correct = Formula("C*e^x", variables=["x"], parameters=["C"])
    student = Formula("5*e^x", variables=["x"])

    # Should adapt C=5
    assert correct.compare(student)
    assert correct._test_adapt is not None

def test_undefined_points():
    """Test domain checking."""
    f1 = Formula("1/x", variables=["x"], check_undefined_points=True)
    f2 = Formula("1/x", variables=["x"])

    points = [[0], [1], [2]]  # 0 is undefined

    values = f1.create_point_values_with_undefined(points)
    assert isinstance(values[0], UNDEF)
    assert not isinstance(values[1], UNDEF)

def test_differentiation():
    """Test derivative calculation."""
    f = Formula("x^2 + 2*x + 1", variables=["x"])
    df = f.D("x")

    assert df.eval(x=0) == 2
    assert df.eval(x=1) == 4
    assert df.eval(x=2) == 6

def test_python_function():
    """Test function generation."""
    f = Formula("x^2 + y", variables=["x", "y"])
    func = f.python_function()

    assert func(2, 3) == 7
    assert func(0, 5) == 5
```

---

## DELIVERABLES & MILESTONES

### Week 1:
- ✅ Day 2: Advanced test point generation
- ✅ Day 5: Adaptive parameter system

### Week 2:
- ✅ Day 2: Domain checking with undefined points
- ✅ Day 4: Enhanced differentiation
- ✅ Day 5: Python function generation

---

## SUCCESS CRITERIA

1. **Functional**:
   - Adaptive parameters work for common cases (C*f(x))
   - Domain checking identifies undefined points
   - Differentiation works with chain rule
   - Python functions generate and cache correctly

2. **Accuracy**:
   - Formula comparison matches Perl behavior
   - Test points well-distributed (granularity works)
   - Tolerance handling correct

3. **Performance**:
   - Function caching speeds up repeated evaluation
   - Test point generation <10ms
   - Adaptive parameter solving <50ms

4. **Quality**:
   - 95% test coverage
   - All edge cases handled
   - Zero regression

---

**End of Formula Enhancements Implementation Plan**
