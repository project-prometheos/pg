"""
Real number MathObject.
"""

from typing import Union
from .value import Value


class Real(Value):
    """
    Real number MathObject.
    
    Represents a real number with context-aware operations.
    """
    
    def __init__(self, value: Union[int, float, str], context=None):
        """
        Create a Real number.
        
        Args:
            value: The numeric value
            context: The Context (None = use current)
        """
        super().__init__(context)
        if isinstance(value, str):
            value = float(value)
        self.value = float(value)
    
    def __str__(self) -> str:
        """String representation."""
        # Format nicely - remove unnecessary decimals
        if self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)
    
    def __repr__(self) -> str:
        """Python representation."""
        return f"Real({self.value})"
    
    def TeX(self) -> str:
        """LaTeX representation."""
        return str(self)
    
    # Arithmetic operations
    def __add__(self, other):
        """Addition."""
        if isinstance(other, (int, float)):
            return Real(self.value + other, self.context)
        elif isinstance(other, Real):
            return Real(self.value + other.value, self.context)
        return NotImplemented
    
    def __radd__(self, other):
        """Right addition."""
        return self.__add__(other)
    
    def __sub__(self, other):
        """Subtraction."""
        if isinstance(other, (int, float)):
            return Real(self.value - other, self.context)
        elif isinstance(other, Real):
            return Real(self.value - other.value, self.context)
        return NotImplemented
    
    def __rsub__(self, other):
        """Right subtraction."""
        if isinstance(other, (int, float)):
            return Real(other - self.value, self.context)
        return NotImplemented
    
    def __mul__(self, other):
        """Multiplication."""
        if isinstance(other, (int, float)):
            return Real(self.value * other, self.context)
        elif isinstance(other, Real):
            return Real(self.value * other.value, self.context)
        return NotImplemented
    
    def __rmul__(self, other):
        """Right multiplication."""
        return self.__mul__(other)
    
    def __truediv__(self, other):
        """Division."""
        if isinstance(other, (int, float)):
            return Real(self.value / other, self.context)
        elif isinstance(other, Real):
            return Real(self.value / other.value, self.context)
        return NotImplemented
    
    def __rtruediv__(self, other):
        """Right division."""
        if isinstance(other, (int, float)):
            return Real(other / self.value, self.context)
        return NotImplemented
    
    def __pow__(self, other):
        """Exponentiation."""
        if isinstance(other, (int, float)):
            return Real(self.value ** other, self.context)
        elif isinstance(other, Real):
            return Real(self.value ** other.value, self.context)
        return NotImplemented
    
    def __rpow__(self, other):
        """Right exponentiation."""
        if isinstance(other, (int, float)):
            return Real(other ** self.value, self.context)
        return NotImplemented
    
    def __neg__(self):
        """Negation."""
        return Real(-self.value, self.context)
    
    def __abs__(self):
        """Absolute value."""
        return Real(abs(self.value), self.context)
    
    # Comparison operations
    def __eq__(self, other):
        """Equality comparison with tolerance."""
        if isinstance(other, (int, float)):
            other_value = float(other)
        elif isinstance(other, Real):
            other_value = other.value
        else:
            return False
        
        # Use context tolerance and zeroLevel
        tolerance = self.context.flags.get('tolerance')
        tol_type = self.context.flags.get('tolType')
        zero_level = self.context.flags.get('zeroLevel') or 1e-14
        
        if tol_type == 'relative':
            # Relative tolerance
            if abs(self.value) < zero_level:  # Near zero
                return abs(other_value) < tolerance
            return abs(self.value - other_value) / abs(self.value) < tolerance
        else:
            # Absolute tolerance
            return abs(self.value - other_value) < tolerance
    
    def __ne__(self, other):
        """Not equal."""
        return not self.__eq__(other)
    
    def __lt__(self, other):
        """Less than."""
        if isinstance(other, (int, float)):
            return self.value < other
        elif isinstance(other, Real):
            return self.value < other.value
        return NotImplemented
    
    def __le__(self, other):
        """Less than or equal."""
        if isinstance(other, (int, float)):
            return self.value <= other
        elif isinstance(other, Real):
            return self.value <= other.value
        return NotImplemented
    
    def __gt__(self, other):
        """Greater than."""
        if isinstance(other, (int, float)):
            return self.value > other
        elif isinstance(other, Real):
            return self.value > other.value
        return NotImplemented
    
    def __ge__(self, other):
        """Greater than or equal."""
        if isinstance(other, (int, float)):
            return self.value >= other
        elif isinstance(other, Real):
            return self.value >= other.value
        return NotImplemented
    
    # Answer checker
    def cmp(self, **options):
        """
        Return an answer checker for this Real number.
        
        Options:
            tolerance: Tolerance for comparison (default from context)
            tolType: 'relative' or 'absolute'
        
        Returns:
            RealAnswerChecker
        """
        from .answer_checker import RealAnswerChecker
        return RealAnswerChecker(self, **options)
