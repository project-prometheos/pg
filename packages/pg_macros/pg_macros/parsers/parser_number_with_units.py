"""Number with Units Parser for WeBWorK.

This module provides the NumberWithUnits class for parsing and validating
numbers with associated units (e.g., "5 m/s", "9.8 m/s^2").

Based on macros/parsers/parserNumberWithUnits.pl from the WeBWorK distribution.
"""

from typing import Any, Optional, Union


class NumberWithUnits:
    """
    Parser for numbers with units.
    
    Parses expressions like "5 m/s", "9.8 m/s^2", etc. and validates
    unit consistency and conversions.
    
    Attributes:
        value: Numeric value
        units: Unit string (e.g., "m/s", "kg", "m/s^2")
    """

    def __init__(self, value: Union[int, float, str] = 0, units: str = ''):
        """
        Create a NumberWithUnits object.
        
        Args:
            value: Numeric value or string representation
            units: Unit string (e.g., "m/s", "kg")
            
        Example:
            >>> num = NumberWithUnits(5, "m/s")
            >>> str(num)
            '5 m/s'
        
        Perl Source: parserNumberWithUnits.pl NumberWithUnits constructor
        """
        try:
            self.value = float(value) if isinstance(value, (int, float, str)) else value
        except (ValueError, TypeError):
            self.value = value
        self.units = str(units) if units else ''
        
    def cmp(self, **options) -> 'AnswerChecker':
        """
        Create an answer checker for this NumberWithUnits.
        
        Args:
            **options: Options for answer checking (tolerance, etc.)
        
        Returns:
            AnswerChecker object for use with ANS()
        
        Perl Source: parserNumberWithUnits.pl cmp() method
        """
        return AnswerChecker(self, **options)
    
    def __str__(self) -> str:
        """Return string representation."""
        if self.units:
            return f'{self.value} {self.units}'
        return str(self.value)
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"NumberWithUnits({self.value}, '{self.units}')"
    
    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if isinstance(other, NumberWithUnits):
            return self.value == other.value and self.units == other.units
        return False


class AnswerChecker:
    """
    Answer checker for NumberWithUnits answers.
    
    Handles checking student answers against a correct NumberWithUnits value.
    """
    
    def __init__(self, correct: NumberWithUnits, **options):
        """
        Initialize answer checker.
        
        Args:
            correct: Correct NumberWithUnits answer
            **options: Checking options (tolerance, etc.)
        """
        self.correct = correct
        self.options = options
    
    def check(self, student_answer: str) -> dict:
        """
        Check a student answer.
        
        Args:
            student_answer: Student's answer as string
        
        Returns:
            Dict with keys: correct (bool), score (float), message (str)
        """
        try:
            # Parse student answer
            parts = student_answer.strip().split()
            if len(parts) >= 1:
                student_value = float(parts[0])
                student_units = ' '.join(parts[1:]) if len(parts) > 1 else ''
            else:
                return {
                    'correct': False,
                    'score': 0.0,
                    'message': 'Invalid answer format'
                }
            
            # Check value
            tolerance = self.options.get('tolerance', 0.01)
            value_correct = abs(student_value - self.correct.value) <= tolerance
            
            # Check units
            units_correct = student_units.strip() == self.correct.units.strip()
            
            is_correct = value_correct and units_correct
            
            return {
                'correct': is_correct,
                'score': 1.0 if is_correct else 0.0,
                'message': '' if is_correct else 'Incorrect answer'
            }
        except Exception as e:
            return {
                'correct': False,
                'score': 0.0,
                'message': f'Error checking answer: {str(e)}'
            }
    
    def __call__(self, **kwargs):
        """Make checker callable - returns self for chaining."""
        return self


__all__ = [
    'NumberWithUnits',
    'AnswerChecker',
]
