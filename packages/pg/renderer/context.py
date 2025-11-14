"""MathObjects Context system."""

from typing import Dict, Any


class Context:
    """
    Simplified Context system for MathObjects.
    
    In full PG, Context manages:
    - Variables (x, y, z, etc.)
    - Constants (pi, e, etc.)
    - Functions (sin, cos, etc.)
    - Operators and their precedence
    
    For MVP, we just track the context name.
    """
    
    def __init__(self, name: str = "Numeric"):
        self.name = name
        self.variables: Dict[str, str] = {}
        self.constants: Dict[str, Any] = {}
        
        # Set defaults based on context
        if name == "Numeric":
            self.variables = {'x': 'Real'}
        elif name == "Fraction":
            self.variables = {'x': 'Real'}
        elif name == "Complex":
            self.variables = {'z': 'Complex'}
    
    def __repr__(self) -> str:
        return f"Context('{self.name}')"

