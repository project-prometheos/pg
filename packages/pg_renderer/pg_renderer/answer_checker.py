"""Check student answers against correct values."""

import re
from typing import Tuple, Dict, Any

# Import new checker system
from .checkers import NumericChecker, FormulaChecker
from .checkers.base import AnswerChecker as BaseChecker


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
        self.formula_checker_standard = FormulaChecker(tolerance=tolerance, mode='standard')
        self.formula_checker_constant = FormulaChecker(tolerance=tolerance, mode='up_to_constant')
    
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
            # Check if it's an inequality (contains comparison operators)
            if any(op in student_answer for op in ['>=', '<=', '>', '<']):
                # For inequalities, use normalized string comparison
                return self._check_inequality(student_answer, correct_answer)
            
            # Regular formula checking
            checker_mode = context.get('checker', 'standard')
            if checker_mode == 'up_to_constant':
                return self.formula_checker_constant.check(student_answer, correct_answer, context)
            elif checker_mode == 'up_to_additive_constant':
                checker = FormulaChecker(tolerance=self.tolerance, mode='up_to_additive_constant')
                return checker.check(student_answer, correct_answer, context)
            else:
                return self.formula_checker_standard.check(student_answer, correct_answer, context)
        elif answer_type == 'interval':
            # For intervals, use normalized string comparison for now
            return self._check_interval(student_answer, correct_answer)
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
    
    def _check_inequality(self, student: str, correct: str) -> Tuple[bool, str]:
        """
        Check inequality answer by normalizing and comparing.
        
        Examples: "x >= 4", "y <= -2", "t > 0"
        """
        # Normalize: remove all whitespace
        student_norm = re.sub(r'\s+', '', student.strip())
        correct_norm = re.sub(r'\s+', '', correct.strip())
        
        if student_norm == correct_norm:
            return True, "Correct!"
        
        # Also try with spaces around operators for readability
        student_norm2 = re.sub(r'\s*([><=]+)\s*', r'\1', student.strip())
        correct_norm2 = re.sub(r'\s*([><=]+)\s*', r'\1', correct.strip())
        
        if student_norm2 == correct_norm2:
            return True, "Correct!"
        
        return False, f"Your inequality doesn't match. Expected: {correct}"
    
    def _check_interval(self, student: str, correct: str) -> Tuple[bool, str]:
        """
        Check interval notation by normalizing and comparing.
        
        Examples: "[1, 5)", "(-inf, 2]", "[0, inf)"
        """
        # Normalize: remove all whitespace
        student_norm = student.strip().replace(' ', '')
        correct_norm = correct.strip().replace(' ', '')
        
        # Handle various forms of infinity
        student_norm = student_norm.replace('infinity', 'inf').replace('∞', 'inf')
        correct_norm = correct_norm.replace('infinity', 'inf').replace('∞', 'inf')
        
        if student_norm == correct_norm:
            return True, "Correct!"
        
        return False, f"Your interval doesn't match. Expected: {correct}"

