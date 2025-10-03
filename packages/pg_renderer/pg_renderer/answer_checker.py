"""Check student answers against correct values."""

import re
from typing import Tuple, Dict, Any, List

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
    
    def build_context(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Build a normalized context dictionary from rendered metadata."""
        options = meta.get('options', {})
        if isinstance(options, dict):
            options = dict(options)
        else:
            options = {}
        context = {
            'variables': meta.get('variables', []),
            'checker': meta.get('checker', 'standard'),
            'options': options,
            'tolerance': meta.get('tolerance', self.tolerance),
            'group': meta.get('group'),
            'group_index': meta.get('group_index'),
        }
        if 'tolerance' in meta:
            context['tolerance'] = meta['tolerance']
        return context

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
            # Custom checker unsupported for now
            if context.get('checker') == 'custom':
                return False, "Custom checker (->with(checker => sub {...})) is not supported yet."
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
        elif answer_type == 'multi':
            return False, "MultiAnswer groups are not supported yet in the Python port."
        else:
            return self._check_string(student_answer, correct_answer)





    def check_multi_group(
        self,
        group_id: str,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Check a MultiAnswer group and return per-item results."""
        if not items:
            return {
                'items': [],
                'group_score': 0.0,
                'group_correct': True,
                'partial_credit': True,
            }

        sorted_items = sorted(
            items,
            key=lambda item: item.get('meta', {}).get('group_index', 0),
        )

        first_meta = sorted_items[0]['meta']
        options = first_meta.get('options', {})
        if not isinstance(options, dict):
            options = {}
        partial_credit_setting = options.get('partialCredit')
        if partial_credit_setting is None:
            partial_credit = True
        elif isinstance(partial_credit_setting, bool):
            partial_credit = partial_credit_setting
        elif isinstance(partial_credit_setting, (int, float)):
            partial_credit = bool(partial_credit_setting)
        else:
            partial_credit = str(partial_credit_setting).strip().lower() not in ('0', 'false', 'no')

        group_checker = first_meta.get('checker', 'standard')
        custom_checker_src = options.get('custom_checker_src')
        # If custom checker is present, fall back to standard checking since we can't execute Perl
        if group_checker == 'custom' or custom_checker_src:
            group_checker = 'standard'
            # Note: We're falling back to standard checking - custom logic is not executed

        per_item_results = []
        raw_correct_flags = []
        for item in sorted_items:
            meta = item['meta']
            part_type = meta.get('part_type') or self._infer_part_type(meta.get('correct_value'))
            context = self.build_context(meta)
            context['checker'] = 'standard'
            context['options'] = dict(context.get('options', {}))
            student_answer = item.get('student_answer', '') or ''
            is_correct, message = self.check(
                student_answer,
                meta.get('correct_value', ''),
                part_type,
                context,
            )
            per_item_results.append({
                'answer_id': item['answer_id'],
                'correct': is_correct,
                'raw_correct': is_correct,
                'message': message,
                'student_answer': student_answer,
                'correct_answer': meta.get('correct_value', ''),
                'context': context,
                'answer_type': 'multi',
            })
            raw_correct_flags.append(is_correct)

        group_correct = all(raw_correct_flags)
        if not partial_credit and not group_correct:
            for entry in per_item_results:
                if entry['raw_correct']:
                    entry['message'] = 'MultiAnswer group requires all blanks to be correct.'
                entry['correct'] = False
            group_score = 0.0
        else:
            group_score = (
                sum(1 for entry in per_item_results if entry['correct']) / len(per_item_results)
                if per_item_results else 0.0
            )
            group_correct = all(entry['correct'] for entry in per_item_results)

        return {
            'items': per_item_results,
            'group_score': group_score,
            'group_correct': group_correct,
            'partial_credit': partial_credit,
        }




    def _infer_part_type(self, value: Any) -> str:
        """Best-effort type inference for MultiAnswer parts."""
        if value is None:
            return 'formula'
        answer_str = str(value).strip()
        if not answer_str:
            return 'formula'
        if ((answer_str.startswith('[') or answer_str.startswith('('))
                and (answer_str.endswith(']') or answer_str.endswith(')'))):
            return 'interval'
        if answer_str.startswith('(') and answer_str.endswith(')') and ',' in answer_str:
            return 'point'
        if answer_str.startswith('<') and answer_str.endswith('>'):
            return 'vector'
        if (
            any(op in answer_str for op in ['>=', '<=', '>', '<'])
            and any(var in answer_str for var in ['x', 'y', 'z', 't', 'r', 'theta'])
        ):
            return 'formula'
        try:
            float(answer_str)
            return 'number'
        except (ValueError, TypeError):
            pass
        if (
            any(char in answer_str for char in ['+', '-', '*', '/', '^', '(', ')'])
            or any(var in answer_str.lower() for var in ['x', 'y', 'z', 't', 'sin', 'cos', 'sqrt'])
        ):
            return 'formula'
        return 'string'


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

