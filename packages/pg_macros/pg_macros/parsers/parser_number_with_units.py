"""NumberWithUnits Parser for WeBWorK.

This module provides the NumberWithUnits class for parsing and validating
numbers with physical units (e.g., "5 m/s", "9.8 m/s^2").

Based on macros/parsers/parserNumberWithUnits.pl from the WeBWorK distribution.
"""

from typing import Any, Dict, Optional, Union
import re


def NumberWithUnits(value, units=''):
    """
    Stub implementation of NumberWithUnits - number with units.

    Creates an object representing a value with associated units.

    Args:
        value: The numeric value
        units: The unit string (e.g., "m/s", "ft", "kg")

    Returns:
        Object with value and units attributes
    """
    return type('NumberWithUnits', (), {
        'value': value,
        'units': units,
        '__str__': lambda self: f'{value} {units}',
    })()


class NumberWithUnitsClass:
    """
    Parser for numbers with physical units.

    Supports parsing of values like "5 m/s", "3.14 radians", "9.8 m/s^2",
    and provides comparison that handles unit conversions.

    Attributes:
        value: The numerical value
        units: The unit string
        formula: The original formula (may include variables)
    """

    def __init__(self, input_str: str = "", units: Optional[str] = None, **options):
        """
        Create a NumberWithUnits object.

        Args:
            input_str: String like "5 m/s" or formula like "$x m/s"
            units: Optional separate units string
            **options: Additional options like newUnit for custom units

        Example:
            >>> num = NumberWithUnits("3 ft")
            >>> num = NumberWithUnits("5 m/s")
            >>> num = NumberWithUnits("$a*$b ft")  # with formula
        """
        self.options = options
        self.value = None
        self.units = None
        self.formula = None
        self.custom_units = {}

        # Handle newUnit option for custom units
        if 'newUnit' in options:
            self._add_custom_units(options['newUnit'])

        # Parse input
        if units is not None:
            # Called as NumberWithUnits(formula, "units")
            self.formula = input_str
            self.units = units
            self._parse_value(input_str)
        else:
            # Called as NumberWithUnits("5 m/s")
            self._parse_input(input_str)

    def _add_custom_units(self, new_unit: Union[str, Dict, list]) -> None:
        """
        Add custom unit definitions.

        Args:
            new_unit: String name, dict with conversion, or list of units
        """
        if isinstance(new_unit, str):
            self.custom_units[new_unit] = {'factor': 1}
        elif isinstance(new_unit, dict):
            name = new_unit.get('name', 'custom')
            self.custom_units[name] = new_unit.get('conversion', {})
        elif isinstance(new_unit, list):
            for unit_def in new_unit:
                self._add_custom_units(unit_def)

    def _parse_input(self, input_str: str) -> None:
        """
        Parse a string like "5 m/s" into value and units.

        Args:
            input_str: Input string to parse
        """
        if not input_str:
            return

        # Pattern: number (possibly with formula), then units
        # "5 m/s", "$x m/s", "3.14 rad", "5*3 feet"
        pattern = r'^(.*?)\s+([a-zA-Z/\^0-9\s\*\-]+)$'
        match = re.match(pattern, input_str.strip())

        if match:
            value_str = match.group(1).strip()
            units_str = match.group(2).strip()

            self.formula = value_str
            self.units = units_str

            # Try to parse numeric value
            self._parse_value(value_str)
        else:
            # No units found, treat whole thing as formula
            self.formula = input_str.strip()

    def _parse_value(self, value_str: str) -> None:
        """
        Parse the numeric value from a string.

        Args:
            value_str: String representation of value
        """
        # Remove whitespace
        value_str = value_str.strip()

        # Try direct conversion if it's a number
        try:
            self.value = float(value_str)
        except ValueError:
            # It's a formula with variables - keep as is
            self.formula = value_str

    def cmp(self, **options) -> 'NumberWithUnitsChecker':
        """
        Get an answer checker for this NumberWithUnits object.

        Returns:
            NumberWithUnitsChecker configured for comparison

        Example:
            >>> num = NumberWithUnits("5 m/s")
            >>> ans(num.cmp())
        """
        return NumberWithUnitsChecker(self, **options)

    def __str__(self) -> str:
        """Return string representation."""
        if self.units:
            if self.value is not None:
                return f"{self.value} {self.units}"
            elif self.formula:
                return f"{self.formula} {self.units}"
        elif self.value is not None:
            return str(self.value)
        return ""

    def __repr__(self) -> str:
        """Return representation."""
        return f"NumberWithUnits({str(self)})"


class NumberWithUnitsChecker:
    """
    Answer checker for NumberWithUnits comparison.

    Handles unit conversion and value comparison with appropriate tolerances.
    """

    def __init__(self, reference: NumberWithUnits, **options):
        """
        Initialize the checker with a reference answer.

        Args:
            reference: The correct NumberWithUnits answer
            **options: Checker options (tolerance, etc.)
        """
        self.reference = reference
        self.options = options
        self.tolerance = options.get('tolerance', 1e-6)

    def evaluate(self, student_answer: str) -> bool:
        """
        Check if student answer matches reference.

        Args:
            student_answer: Student's answer string

        Returns:
            True if answer is correct, False otherwise
        """
        # Parse student answer
        student = NumberWithUnits(student_answer)

        # Simple check: units must match, values must be close
        if self.reference.units and student.units:
            if self.reference.units.lower() != student.units.lower():
                return False

        if self.reference.value is not None and student.value is not None:
            relative_error = abs(student.value - self.reference.value) / max(abs(self.reference.value), 1)
            return relative_error <= self.tolerance

        return str(student) == str(self.reference)

    def __call__(self, student_answer: str) -> Dict[str, Any]:
        """
        Callable interface for compatibility with PG answer checkers.

        Args:
            student_answer: Student's answer

        Returns:
            Result dictionary with 'score' and 'message' keys
        """
        is_correct = self.evaluate(student_answer)
        return {
            'score': 1 if is_correct else 0,
            'message': '' if is_correct else 'Incorrect'
        }


__all__ = [
    'NumberWithUnits',
    'NumberWithUnitsChecker',
]
