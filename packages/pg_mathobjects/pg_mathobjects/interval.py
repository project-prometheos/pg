"""
Interval MathObject for handling interval notation.
"""

import re
from typing import Union, Tuple
from .value import Value


class Interval(Value):
    """
    Interval MathObject - represents intervals like [a, b], (a, b), [a, b), (a, b].
    
    Supports:
    - Open intervals: (a, b)
    - Closed intervals: [a, b]
    - Half-open intervals: [a, b), (a, b]
    - Infinite intervals: (-inf, a], [b, inf), (-inf, inf)
    - Empty set: {}
    - Set notation: {a, b, c}
    - Union of intervals: (a, b) U [c, d]
    """

    def __init__(self, interval_str: str, context=None):
        """
        Create an Interval from string notation.

        Args:
            interval_str: String like "[1, 5]", "(-inf, 3)", "{1, 2, 3}", etc.
            context: The Context (None = use current)
        """
        super().__init__(context)
        self.original_str = interval_str.strip()
        self._parse_interval(self.original_str)

    def _parse_interval(self, interval_str: str):
        """Parse interval notation into internal representation."""
        interval_str = interval_str.strip()
        
        # Handle empty set
        if interval_str == '{}' or interval_str.upper() == 'NONE':
            self.is_empty = True
            self.intervals = []
            return
        
        self.is_empty = False
        
        # Handle unions (U or union)
        if ' U ' in interval_str or ' union ' in interval_str.lower():
            # Split by union and parse each interval
            parts = re.split(r'\s+[Uu](?:nion)?\s+', interval_str)
            self.intervals = []
            for part in parts:
                sub_interval = Interval(part, self.context)
                self.intervals.extend(sub_interval.intervals)
            return
        
        # Handle set notation {a, b, c}
        if interval_str.startswith('{') and interval_str.endswith('}'):
            self._parse_set(interval_str)
            return
        
        # Handle single interval notation
        self.intervals = [self._parse_single_interval(interval_str)]

    def _parse_set(self, set_str: str):
        """Parse set notation like {1, 2, 3}."""
        content = set_str[1:-1].strip()
        if not content:
            self.is_empty = True
            self.intervals = []
            return
        
        # Split by commas and convert to point intervals
        from .real import Real
        self.intervals = []
        for item in content.split(','):
            item = item.strip()
            value = self._parse_value(item)
            # Point interval [a, a]
            self.intervals.append({
                'left': value,
                'right': value,
                'left_closed': True,
                'right_closed': True,
                'is_point': True
            })

    def _parse_single_interval(self, interval_str: str) -> dict:
        """
        Parse a single interval like [a, b], (a, b), etc.
        
        Returns:
            dict with keys: left, right, left_closed, right_closed
        """
        # Match interval pattern: (open/closed) number, number (open/closed)
        pattern = r'([\[\(])\s*([^,]+)\s*,\s*([^\]\)]+)\s*([\]\)])'
        match = re.match(pattern, interval_str.strip())
        
        if not match:
            raise ValueError(f"Invalid interval notation: {interval_str}")
        
        left_bracket, left_val, right_val, right_bracket = match.groups()
        
        return {
            'left': self._parse_value(left_val),
            'right': self._parse_value(right_val),
            'left_closed': left_bracket == '[',
            'right_closed': right_bracket == ']',
            'is_point': False
        }

    def _parse_value(self, value_str: str) -> Union[float, str]:
        """
        Parse a boundary value (number or inf/-inf).
        
        Returns:
            float for numbers, 'inf' or '-inf' for infinities
        """
        value_str = value_str.strip()
        
        # Handle infinity
        if value_str.lower() in ('inf', 'infinity', '+inf', '+infinity'):
            return 'inf'
        if value_str.lower() in ('-inf', '-infinity'):
            return '-inf'
        
        # Try to parse as number
        try:
            return float(value_str)
        except ValueError:
            raise ValueError(f"Invalid interval boundary: {value_str}")

    def __str__(self) -> str:
        """String representation."""
        if self.is_empty:
            return '{}'
        
        if len(self.intervals) > 1:
            # Union of intervals
            parts = []
            for interval in self.intervals:
                parts.append(self._format_interval(interval))
            return ' U '.join(parts)
        
        return self._format_interval(self.intervals[0])

    def _format_interval(self, interval: dict) -> str:
        """Format a single interval as a string."""
        if interval.get('is_point'):
            return f"{{{self._format_value(interval['left'])}}}"
        
        left_bracket = '[' if interval['left_closed'] else '('
        right_bracket = ']' if interval['right_closed'] else ')'
        left_val = self._format_value(interval['left'])
        right_val = self._format_value(interval['right'])
        
        return f"{left_bracket}{left_val}, {right_val}{right_bracket}"

    def _format_value(self, value: Union[float, str]) -> str:
        """Format a boundary value."""
        if isinstance(value, str):
            return value
        if value == int(value):
            return str(int(value))
        return str(value)

    def __repr__(self) -> str:
        """Python representation."""
        return f'Interval("{self.original_str}")'

    def TeX(self) -> str:
        """LaTeX representation."""
        if self.is_empty:
            return r'\emptyset'
        
        if len(self.intervals) > 1:
            parts = []
            for interval in self.intervals:
                parts.append(self._format_interval_latex(interval))
            return r' \cup '.join(parts)
        
        return self._format_interval_latex(self.intervals[0])

    def _format_interval_latex(self, interval: dict) -> str:
        """Format a single interval as LaTeX."""
        if interval.get('is_point'):
            return rf"\{{{self._format_value_latex(interval['left'])}\}}"
        
        left_bracket = '[' if interval['left_closed'] else '('
        right_bracket = ']' if interval['right_closed'] else ')'
        left_val = self._format_value_latex(interval['left'])
        right_val = self._format_value_latex(interval['right'])
        
        return f"{left_bracket}{left_val}, {right_val}{right_bracket}"

    def _format_value_latex(self, value: Union[float, str]) -> str:
        """Format a boundary value for LaTeX."""
        if value == 'inf':
            return r'\infty'
        if value == '-inf':
            return r'-\infty'
        return self._format_value(value)

    def contains(self, x: Union[float, 'Real']) -> bool:
        """
        Check if a value is in the interval.
        
        Args:
            x: The value to check
            
        Returns:
            True if x is in the interval
        """
        if self.is_empty:
            return False
        
        # Extract numeric value
        if hasattr(x, 'value'):
            x = x.value
        x = float(x)
        
        # Check each interval in the union
        for interval in self.intervals:
            if self._contains_in_interval(x, interval):
                return True
        
        return False

    def _contains_in_interval(self, x: float, interval: dict) -> bool:
        """Check if x is in a single interval."""
        left = interval['left']
        right = interval['right']
        
        # Handle infinities
        if left == '-inf':
            left_ok = True
        elif interval['left_closed']:
            left_ok = x >= left
        else:
            left_ok = x > left
        
        if right == 'inf':
            right_ok = True
        elif interval['right_closed']:
            right_ok = x <= right
        else:
            right_ok = x < right
        
        return left_ok and right_ok

    def __eq__(self, other) -> bool:
        """
        Equality comparison.
        
        Two intervals are equal if they represent the same set.
        """
        if not isinstance(other, Interval):
            return False
        
        if self.is_empty and other.is_empty:
            return True
        
        if self.is_empty != other.is_empty:
            return False
        
        # Simplified comparison - just compare string representations
        # A proper implementation would normalize and compare intervals
        return str(self) == str(other)

    def cmp(self, **options):
        """
        Return an answer checker for this Interval.

        Returns:
            IntervalAnswerChecker
        """
        from .answer_checker import IntervalAnswerChecker
        return IntervalAnswerChecker(self, **options)
