"""Numeric answer checker."""

from typing import Tuple, Dict, Any
from .base import AnswerChecker


class NumericChecker(AnswerChecker):
    """Check numeric answers with tolerance."""
    
    def check(
        self,
        student_answer: str,
        correct_answer: str,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Check if student's numeric answer matches correct answer.
        
        Args:
            student_answer: String representation of number
            correct_answer: String representation of correct number
            context: Additional context (not used for numeric)
        
        Returns:
            (is_correct, feedback_message)
        """
        try:
            student_val = float(student_answer.strip())
        except (ValueError, AttributeError):
            return False, "Please enter a valid number."
        
        try:
            correct_val = float(str(correct_answer).strip())
        except (ValueError, AttributeError):
            return False, "Internal error: invalid correct answer format."
        
        if self._close_enough(student_val, correct_val):
            return True, "Correct!"
        else:
            return False, f"Incorrect. Your answer: {student_val}, Expected: {correct_val}"

