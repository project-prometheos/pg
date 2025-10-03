"""Check student answers against correct values."""

import re
from typing import Tuple, Dict, Any

# Import new checker system
from .checkers import NumericChecker, IntervalChecker, VectorChecker, PointChecker, InequalityChecker
from .checkers.base import AnswerChecker as BaseChecker
from pg_answer.evaluators.formula import FormulaEvaluator
from pg_math import ToleranceMode


class AnswerChecker:
    """
    Main answer checker that routes to appropriate checker type.
    
    This is a backward-compatible wrapper that maintains the old interface
    while using the new pluggable checker system.
    """
    
    def __init__(self, tolerance: float = 0.01):
        self.tolerance = tolerance
        
        # Initialize specific checkers
        self.numeric_checker = NumericChecker(tolerance=tolerance)
    
    def check(
        self,
        student_answer: str,
        correct_answer: str,
        answer_type: str = 'number',
        context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Check if student answer matches correct answer.
        
        Args:
            student_answer: The student's submitted answer
            correct_answer: The correct answer to compare against
            answer_type: Type of answer ('number', 'formula', 'string')
            context: Additional context (variables, checker mode, etc.)
        
        Returns:
            (is_correct, feedback_message)
        """
        context = context or {}
        
        if answer_type == 'number':
            return self.numeric_checker.check(student_answer, correct_answer, context)
        elif answer_type == 'formula':
            # Check if it's an inequality (contains comparison operators) — but ignore method arrows '->'
            sa = self._strip_method_calls(student_answer)
            ca = self._strip_method_calls(correct_answer)
            if self._looks_like_inequality(sa, context) or self._looks_like_inequality(ca, context):
                # Delegate to inequality checker (sampling-based), but keep answer_type 'formula'
                ineq = InequalityChecker(tolerance=self.tolerance)
                return ineq.check(sa, ca, context)
            
            # Regular formula checking
            checker_mode = context.get('checker', 'standard')
            options = context.get('options', {})

            # Fraction flags pre-checks
            if options.get('studentsMustReduceFractions', False):
                if self._is_fraction(student_answer) and not self._is_reduced_fraction(student_answer):
                    return False, "You must reduce your fraction to lowest terms."
            if options.get('allowMixedNumbers', True) is False:
                if self._is_mixed_number(student_answer):
                    return False, "Mixed numbers are not allowed. Use improper fractions instead."

            # Build evaluator with options from context
            eval_kwargs = {
                'tolerance': context.get('tolerance', self.tolerance),
                'tolerance_mode': context.get('tolerance_mode', ToleranceMode.RELATIVE),
                'variables': context.get('variables', None),
                'test_points': context.get('numPoints', options.get('numPoints', 5)),
                'test_at_zero': context.get('testAtZero', options.get('testAtZero', True)),
                'limits': options.get('limits', None),
                'check_undefined_points': options.get('checkUndefined', False),
            }
            # Additive constant parity
            if checker_mode == 'up_to_additive_constant':
                eval_kwargs['up_to_additive_constant'] = True

            evaluator = FormulaEvaluator(correct_answer=correct_answer, **eval_kwargs)
            result = evaluator.evaluate(student_answer)
            return (result.correct, result.answer_message or ("Correct!" if result.correct else "Incorrect."))
        elif answer_type == 'interval':
            return IntervalChecker(tolerance=self.tolerance).check(student_answer, correct_answer, context)
        elif answer_type == 'point':
            return PointChecker(tolerance=self.tolerance).check(student_answer, correct_answer, context)
        elif answer_type == 'vector':
            return VectorChecker(tolerance=self.tolerance).check(student_answer, correct_answer, context)
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
                return False, f"Incorrect."
                
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

    # Inequality detection helpers
    def _strip_method_calls(self, s: str) -> str:
        """Remove Perl-style method calls like ->cmp(...) or ->withPostFilter(...)."""
        # Quick remove for top-level method calls; conservative
        return re.sub(r"->\s*\w+\s*\([^)]*\)", "", s)

    def _looks_like_inequality(self, s: str, context: Dict[str, Any]) -> bool:
        # Exclude occurrences of '>' that are part of '->'
        if re.search(r"(?<!-)>(?!=)|>=|<=|<", s):
            # Only treat as inequality if variables are present in context
            vars_ = context.get('variables') or []
            return bool(vars_)
        return False
    
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
    
    # Removed string-based inequality/interval fallback in favor of dedicated checkers

    # Fraction helpers (parity with Perl fraction cmp flags)
    def _is_fraction(self, answer: str) -> bool:
        return '/' in answer and not any(op in answer for op in ['+', '-', '*', '^', '(', ')'])

    def _is_reduced_fraction(self, answer: str) -> bool:
        if not self._is_fraction(answer):
            return True
        try:
            num, den = answer.split('/', 1)
            num_val = int(num.strip())
            den_val = int(den.strip())
            from math import gcd
            return gcd(num_val, den_val) == 1
        except Exception:
            return True

    def _is_mixed_number(self, answer: str) -> bool:
        return bool(re.match(r'^\s*\d+\s+\d+/\d+\s*$', answer))

