"""Formula/expression answer checker using SymPy."""

import random
from typing import Tuple, Dict, Any, Set, Optional
from .base import AnswerChecker

try:
    from sympy import sympify, simplify, expand, Symbol, SympifyError, Rational
    from sympy.core.expr import Expr
    from sympy.parsing.sympy_parser import (
        parse_expr,
        standard_transformations,
        implicit_multiplication_application,
        convert_xor
    )
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    sympify = None
    Expr = None
    parse_expr = None
    Rational = None


class FormulaChecker(AnswerChecker):
    """
    Check algebraic formula/expression answers.
    
    Supports multiple checking modes:
    - standard: Exact algebraic equivalence
    - up_to_constant: Answers differ by constant multiple (e.g., 2x vs x)
    - up_to_sign: Answers differ by sign (e.g., x vs -x)
    """
    
    def __init__(
        self,
        tolerance: float = 0.01,
        mode: str = 'standard',
        num_test_points: int = 10
    ):
        """
        Initialize formula checker.
        
        Args:
            tolerance: Numeric tolerance for test point evaluation
            mode: Checking mode ('standard', 'up_to_constant', 'up_to_sign')
            num_test_points: Number of random points to test for equivalence
        """
        super().__init__(tolerance)
        self.mode = mode
        self.num_test_points = num_test_points
        
        if not SYMPY_AVAILABLE:
            raise ImportError(
                "SymPy is required for formula checking. "
                "Install it with: pip install sympy"
            )
    
    def check(
        self,
        student_answer: str,
        correct_answer: str,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Check if student formula is equivalent to correct formula.
        
        Args:
            student_answer: Student's expression string
            correct_answer: Correct expression string (may include ->cmp(...))
            context: Additional context with 'variables', 'domain', etc.
        
        Returns:
            (is_correct, feedback_message)
        """
        context = context or {}
        
        # Parse cmp() method parameters if present
        cmp_params = {}
        if '->cmp(' in correct_answer:
            cmp_params = self._parse_cmp_params(correct_answer)
            # Extract just the expression part
            correct_answer = correct_answer.split('->cmp(')[0]
        
        try:
            # Parse expressions
            student_expr = self._parse_expression(student_answer)
            correct_expr = self._parse_expression(correct_answer)
            
        except SympifyError as e:
            return False, f"Syntax error in your answer: {str(e)}"
        except Exception as e:
            return False, f"Could not parse your answer: {str(e)}"
        
        try:
            # Check cmp() parameters first
            if cmp_params:
                cmp_result = self._check_cmp_params(student_answer, student_expr, correct_expr, cmp_params)
                if cmp_result is not None:
                    return cmp_result
            
            # Get variables from context or auto-detect
            variables = context.get('variables', None)
            if variables is None:
                variables = self._get_variables(student_expr, correct_expr)
            
            # Check equivalence based on mode
            if self.mode == 'standard':
                is_correct = self._check_standard(student_expr, correct_expr, variables)
            elif self.mode == 'up_to_constant':
                is_correct = self._check_up_to_constant(student_expr, correct_expr, variables)
            elif self.mode == 'up_to_sign':
                is_correct = self._check_up_to_sign(student_expr, correct_expr, variables)
            else:
                return False, f"Unknown checking mode: {self.mode}"
            
            if is_correct:
                return True, "Correct!"
            else:
                return False, "Your answer is not equivalent to the correct answer."
                
        except Exception as e:
            return False, f"Error checking answer: {str(e)}"
    
    def _parse_expression(self, expr_str: str) -> Expr:
        """
        Parse string to SymPy expression.
        
        Handles common input formats:
        - Implicit multiplication: 2x → 2*x
        - Powers: x^2 → x**2
        """
        # Replace ^ with ** for powers
        expr_str = expr_str.replace('^', '**')
        
        # Use parse_expr with transformations for implicit multiplication
        transformations = (
            standard_transformations + 
            (implicit_multiplication_application, convert_xor)
        )
        
        return parse_expr(expr_str, transformations=transformations)
    
    def _parse_cmp_params(self, answer_str: str) -> Dict[str, Any]:
        """Parse cmp() method parameters from answer string."""
        if '->cmp(' not in answer_str:
            return {}
        
        # Extract the cmp(...) part
        cmp_start = answer_str.find('->cmp(') + 6  # Skip '->cmp('
        cmp_end = answer_str.rfind(')')
        if cmp_end == -1:
            return {}
        
        cmp_str = answer_str[cmp_start:cmp_end]
        
        # Parse parameters like "studentsMustReduceFractions => 1"
        params = {}
        for param in cmp_str.split(','):
            param = param.strip()
            if '=>' in param:
                key, value = param.split('=>', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert value to appropriate type
                if value == '1':
                    params[key] = True
                elif value == '0':
                    params[key] = False
                else:
                    try:
                        params[key] = int(value)
                    except ValueError:
                        params[key] = value
        
        return params
    
    def _check_cmp_params(
        self, 
        student_answer: str, 
        student_expr: Expr, 
        correct_expr: Expr, 
        cmp_params: Dict[str, Any]
    ) -> Optional[Tuple[bool, str]]:
        """
        Check answer against cmp() parameters.
        
        Returns:
            (is_correct, message) if cmp params should override normal checking
            None if normal checking should proceed
        """
        from sympy import Rational, simplify
        
        # Check if studentsMustReduceFractions is required
        if cmp_params.get('studentsMustReduceFractions', False):
            # Student must provide reduced form
            if self._is_fraction(student_answer):
                if not self._is_reduced_fraction(student_answer):
                    return False, "You must reduce your fraction to lowest terms."
        
        # Check if allowMixedNumbers is disabled
        if not cmp_params.get('allowMixedNumbers', True):
            if self._is_mixed_number(student_answer):
                return False, "Mixed numbers are not allowed. Use improper fractions instead."
        
        # If reduceFractions is enabled, reduce both for comparison
        if cmp_params.get('reduceFractions', False):
            # Reduce the correct answer for comparison
            correct_reduced = simplify(correct_expr)
            student_reduced = simplify(student_expr)
            
            # Check if they're equivalent after reduction
            if student_reduced == correct_reduced:
                # But if studentsMustReduceFractions is required, check if student provided reduced form
                if cmp_params.get('studentsMustReduceFractions', False):
                    if self._is_fraction(student_answer):
                        if not self._is_reduced_fraction(student_answer):
                            return False, "You must reduce your fraction to lowest terms."
                return True, "Correct!"
            else:
                return False, "Your answer is not equivalent to the correct answer."
        
        # No special handling needed, proceed with normal checking
        return None
    
    def _is_fraction(self, answer: str) -> bool:
        """Check if answer looks like a fraction."""
        return '/' in answer and not any(op in answer for op in ['+', '-', '*', '^', '(', ')'])
    
    def _parse_fraction(self, answer: str) -> Optional[Rational]:
        """Parse fraction string to Rational."""
        try:
            if '/' in answer:
                num, den = answer.split('/', 1)
                return Rational(int(num.strip()), int(den.strip()))
        except (ValueError, ZeroDivisionError):
            pass
        return None
    
    def _is_reduced_fraction(self, answer: str) -> bool:
        """Check if fraction string is in reduced form."""
        if not self._is_fraction(answer):
            return True  # Not a fraction, so consider it "reduced"
        
        try:
            if '/' in answer:
                num, den = answer.split('/', 1)
                num_val = int(num.strip())
                den_val = int(den.strip())
                from math import gcd
                return gcd(num_val, den_val) == 1
        except (ValueError, ZeroDivisionError):
            pass
        return True  # If we can't parse, assume it's fine
    
    def _is_mixed_number(self, answer: str) -> bool:
        """Check if answer looks like a mixed number (e.g., '1 1/2')."""
        import re
        return bool(re.match(r'^\d+\s+\d+/\d+$', answer.strip()))
    
    def _get_variables(self, *exprs: Expr) -> Set[Symbol]:
        """Extract all variables from expressions."""
        variables = set()
        for expr in exprs:
            variables.update(expr.free_symbols)
        return variables
    
    def _check_standard(
        self,
        student: Expr,
        correct: Expr,
        variables: Set[Symbol]
    ) -> bool:
        """
        Check exact algebraic equivalence.
        
        Uses two methods:
        1. Symbolic: Simplify both and check if difference is zero
        2. Numeric: Test at multiple random points
        """
        # Method 1: Symbolic comparison
        try:
            diff = simplify(expand(student) - expand(correct))
            if diff == 0:
                return True
        except Exception:
            pass  # Fall back to numeric if symbolic fails
        
        # Method 2: Numeric sampling
        return self._numerically_equal(student, correct, variables)
    
    def _check_up_to_constant(
        self,
        student: Expr,
        correct: Expr,
        variables: Set[Symbol]
    ) -> bool:
        """
        Check if student = k * correct for some constant k != 0.
        
        Method: Divide student/correct at multiple points, check if ratio is constant.
        """
        if not variables:
            # No variables - just check if they're proportional
            try:
                student_val = float(student)
                correct_val = float(correct)
                return abs(correct_val) > 1e-10  # Correct is non-zero
            except:
                return False
        
        # Test at multiple points
        ratios = []
        for _ in range(self.num_test_points):
            test_values = self._generate_test_point(variables)
            
            try:
                student_val = float(student.subs(test_values))
                correct_val = float(correct.subs(test_values))
                
                # Skip if correct is zero (undefined ratio)
                if abs(correct_val) < 1e-10:
                    continue
                
                ratio = student_val / correct_val
                ratios.append(ratio)
                
            except (ValueError, TypeError, ZeroDivisionError):
                continue
        
        if len(ratios) < 3:
            # Not enough valid test points
            return False
        
        # Check if all ratios are approximately equal
        first_ratio = ratios[0]
        return all(abs(r - first_ratio) < self.tolerance for r in ratios)
    
    def _check_up_to_sign(
        self,
        student: Expr,
        correct: Expr,
        variables: Set[Symbol]
    ) -> bool:
        """Check if student = ±correct."""
        return (
            self._check_standard(student, correct, variables) or
            self._check_standard(student, -correct, variables)
        )
    
    def _numerically_equal(
        self,
        expr1: Expr,
        expr2: Expr,
        variables: Set[Symbol]
    ) -> bool:
        """
        Test if expressions are numerically equal at multiple random points.
        
        Returns True if they evaluate to the same value (within tolerance)
        at all test points.
        """
        if not variables:
            # No variables - direct comparison
            try:
                val1 = float(expr1)
                val2 = float(expr2)
                return self._close_enough(val1, val2)
            except:
                return False
        
        # Test at multiple random points
        for _ in range(self.num_test_points):
            test_values = self._generate_test_point(variables)
            
            try:
                val1 = float(expr1.subs(test_values))
                val2 = float(expr2.subs(test_values))
                
                if not self._close_enough(val1, val2):
                    return False
                    
            except (ValueError, TypeError, ZeroDivisionError):
                # If evaluation fails at this point, try another
                continue
        
        return True
    
    def _generate_test_point(
        self,
        variables: Set[Symbol],
        min_val: float = -10,
        max_val: float = 10
    ) -> Dict[Symbol, float]:
        """Generate random values for all variables."""
        return {
            var: random.uniform(min_val, max_val)
            for var in variables
        }

