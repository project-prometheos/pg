"""Check student answers against correct values."""

import re
from typing import Tuple


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

