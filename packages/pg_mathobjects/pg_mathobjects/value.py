"""
Base Value class for MathObjects.

All MathObjects (Real, Complex, Point, Vector, Formula, etc.) inherit from Value.
"""

from typing import Any, Optional
from abc import ABC, abstractmethod


class Value(ABC):
    """
    Base class for all MathObject values.

    All MathObjects share common functionality:
    - They belong to a Context
    - They can be compared for equality
    - They can provide answer checkers via cmp()
    - They have string and TeX representations
    """

    def __init__(self, context=None):
        """
        Initialize a Value.

        Args:
            context: The Context for this value (None = use current)
        """
        if context is None:
            from .context import get_current_context
            context = get_current_context()
        self.context = context

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the value."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """Python representation of the value."""
        pass

    def TeX(self) -> str:
        """LaTeX representation of the value."""
        return str(self)

    def string(self) -> str:
        """String representation (same as __str__)."""
        return str(self)

    @abstractmethod
    def cmp(self, **options):
        """
        Return an answer checker for this value.

        Returns:
            AnswerChecker object
        """
        pass

    def with_(self, **options):
        """
        Return a copy of this value with modified options.

        This is useful for setting answer checker options without
        modifying the original value.
        """
        # Create a shallow copy
        import copy
        new_value = copy.copy(self)
        # Store options
        if not hasattr(new_value, '_options'):
            new_value._options = {}
        new_value._options.update(options)
        return new_value
    
    def with_params(self, **options):
        """
        Alias for with_() - preprocessor converts ->with( to .with_params(
        """
        return self.with_(**options)
