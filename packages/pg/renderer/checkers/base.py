"""Base answer checker interface."""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any


class AnswerChecker(ABC):
    """Base class for all answer checkers."""
    
    def __init__(self, tolerance: float = 0.01):
        """
        Initialize answer checker.
        
        Args:
            tolerance: Numeric tolerance for comparisons
        """
        self.tolerance = tolerance
    
    @abstractmethod
    def check(
        self,
        student_answer: str,
        correct_answer: str,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Check if student answer matches correct answer.
        
        Args:
            student_answer: The student's submitted answer
            correct_answer: The correct answer to compare against
            context: Additional context (variables, checker mode, etc.)
        
        Returns:
            (is_correct, feedback_message)
        """
        pass
    
    def _close_enough(self, val1: float, val2: float) -> bool:
        """Check if two numeric values are close enough."""
        return abs(val1 - val2) < self.tolerance

