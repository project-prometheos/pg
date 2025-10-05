"""
Context system for MathObjects.

The Context controls what operations, variables, constants, and functions
are available when parsing and evaluating mathematical expressions.
"""

import math
from typing import Dict, Any, Optional, Set
from copy import deepcopy


class VariableManager:
    """Manages variables available in the context."""
    
    def __init__(self):
        self._variables: Dict[str, str] = {}  # name -> type
    
    def add(self, name: str, type_: str = 'Real'):
        """Add a variable to the context."""
        self._variables[name] = type_
    
    def remove(self, name: str):
        """Remove a variable from the context."""
        if name in self._variables:
            del self._variables[name]
    
    def are(self, **kwargs):
        """Set variables (replaces existing)."""
        self._variables = dict(kwargs)
    
    def get(self, name: str) -> Optional[str]:
        """Get variable type."""
        return self._variables.get(name)
    
    def list(self) -> list:
        """Get list of variable names."""
        return list(self._variables.keys())
    
    def copy(self):
        """Create a copy of this manager."""
        new_mgr = VariableManager()
        new_mgr._variables = self._variables.copy()
        return new_mgr


class ConstantManager:
    """Manages constants available in the context."""
    
    def __init__(self):
        self._constants: Dict[str, Any] = {}
    
    def add(self, name: str, value: Any):
        """Add a constant to the context."""
        self._constants[name] = value
    
    def set(self, name: str, value: Any):
        """Set a constant value."""
        self._constants[name] = value
    
    def get(self, name: str) -> Any:
        """Get constant value."""
        return self._constants.get(name)
    
    def remove(self, name: str):
        """Remove a constant from the context."""
        if name in self._constants:
            del self._constants[name]
    
    def list(self) -> list:
        """Get list of constant names."""
        return list(self._constants.keys())
    
    def copy(self):
        """Create a copy of this manager."""
        new_mgr = ConstantManager()
        new_mgr._constants = self._constants.copy()
        return new_mgr


class FunctionManager:
    """Manages functions available in the context."""
    
    def __init__(self):
        self._functions: Dict[str, dict] = {}
    
    def add(self, name: str, **options):
        """Add a function to the context."""
        self._functions[name] = options
    
    def set(self, name: str, **options):
        """Set function options."""
        if name in self._functions:
            self._functions[name].update(options)
        else:
            self._functions[name] = options
    
    def get(self, name: str) -> Optional[dict]:
        """Get function options."""
        return self._functions.get(name)
    
    def remove(self, name: str):
        """Remove a function from the context."""
        if name in self._functions:
            del self._functions[name]
    
    def list(self) -> list:
        """Get list of function names."""
        return list(self._functions.keys())
    
    def copy(self):
        """Create a copy of this manager."""
        new_mgr = FunctionManager()
        new_mgr._functions = deepcopy(self._functions)
        return new_mgr


class OperatorManager:
    """Manages operators available in the context."""
    
    def __init__(self):
        self._operators: Dict[str, dict] = {}
    
    def add(self, name: str, **options):
        """Add an operator to the context."""
        self._operators[name] = options
    
    def set(self, name: str, **options):
        """Set operator options."""
        if name in self._operators:
            self._operators[name].update(options)
        else:
            self._operators[name] = options
    
    def get(self, name: str) -> Optional[dict]:
        """Get operator options."""
        return self._operators.get(name)
    
    def remove(self, name: str):
        """Remove an operator from the context."""
        if name in self._operators:
            del self._operators[name]
    
    def list(self) -> list:
        """Get list of operator names."""
        return list(self._operators.keys())
    
    def copy(self):
        """Create a copy of this manager."""
        new_mgr = OperatorManager()
        new_mgr._operators = deepcopy(self._operators)
        return new_mgr


class ContextFlags:
    """Manages context flags/options."""
    
    def __init__(self):
        self._flags: Dict[str, Any] = {
            'tolerance': 0.001,
            'tolType': 'relative',
            'zeroLevel': 1e-14,
            'zeroLevelTol': 1e-12,
            'reduceConstants': 1,
            'reduceConstantFunctions': 1,
        }
    
    def set(self, **kwargs):
        """Set flag values."""
        self._flags.update(kwargs)
    
    def get(self, name: str) -> Any:
        """Get flag value."""
        return self._flags.get(name)
    
    def copy(self):
        """Create a copy of this flags object."""
        new_flags = ContextFlags()
        new_flags._flags = self._flags.copy()
        return new_flags


class ContextClass:
    """
    Context for parsing and evaluating mathematical expressions.
    
    The Context determines what operations, variables, constants, and
    functions are available, as well as how expressions are parsed and
    evaluated.
    """
    
    def __init__(self, name: str = 'Numeric'):
        self.name = name
        self.variables = VariableManager()
        self.constants = ConstantManager()
        self.functions = FunctionManager()
        self.operators = OperatorManager()
        self.flags = ContextFlags()
        
        # Initialize based on context name
        if name == 'Numeric':
            self._init_numeric()
        elif name.startswith('LimitedPolynomial'):
            self._init_limited_polynomial(strict=('-Strict' in name))
        elif name.startswith('PolynomialFactors'):
            self._init_polynomial_factors(strict=('-Strict' in name))
    
    def _init_numeric(self):
        """Initialize Numeric context with standard operations."""
        # Standard variables
        self.variables.add('x', 'Real')
        
        # Standard constants
        self.constants.add('pi', math.pi)
        self.constants.add('e', math.e)
        
        # Standard functions
        for func in ['sin', 'cos', 'tan', 'sec', 'csc', 'cot',
                     'asin', 'acos', 'atan', 'asec', 'acsc', 'acot',
                     'sinh', 'cosh', 'tanh', 'sech', 'csch', 'coth',
                     'asinh', 'acosh', 'atanh', 'asech', 'acsch', 'acoth',
                     'ln', 'log', 'log10', 'exp', 'sqrt', 'abs', 'int', 'sgn']:
            self.functions.add(func)
        
        # Standard operators
        for op in ['+', '-', '*', '/', '^', '**', '==', '!=', '<', '>', '<=', '>=']:
            self.operators.add(op)
    
    def _init_limited_polynomial(self, strict: bool = False):
        """Initialize LimitedPolynomial context."""
        # Start with Numeric base
        self._init_numeric()
        
        # Set polynomial validation flags
        self.flags.set(
            limitedPolynomial=True,
            strictCoefficients=strict,
            singlePowers=False
        )
        
        # In strict mode, disable some reductions
        if strict:
            self.flags.set(reduceConstants=False)
    
    def _init_polynomial_factors(self, strict: bool = False):
        """Initialize PolynomialFactors context."""
        # Start with LimitedPolynomial base
        self._init_limited_polynomial(strict=strict)
        
        # Set polynomial factors validation flags
        self.flags.set(
            polynomialFactors=True,
            strictPowers=True,  # Default in Perl version
            singleFactors=False,
            strictDivision=False
        )
        
        # In strict mode, set all strict flags
        if strict:
            self.flags.set(
                strictCoefficients=True,
                strictDivision=True,
                strictPowers=True,
                singlePowers=True,
                singleFactors=True,
                reduceConstants=False
            )

    
    def copy(self, name: Optional[str] = None) -> 'ContextClass':
        """Create a copy of this context."""
        new_context = ContextClass.__new__(ContextClass)
        new_context.name = name if name is not None else self.name
        new_context.variables = self.variables.copy()
        new_context.constants = self.constants.copy()
        new_context.functions = self.functions.copy()
        new_context.operators = self.operators.copy()
        new_context.flags = self.flags.copy()
        return new_context
    
    def __repr__(self):
        return f"Context('{self.name}')"


# Global context registry
_contexts: Dict[str, ContextClass] = {}
_current_context: Optional[ContextClass] = None


def Context(name: Optional[str] = None) -> ContextClass:
    """
    Get or set the current context.
    
    Args:
        name: Context name to switch to (None = get current)
    
    Returns:
        Current context
    
    Examples:
        >>> Context('Numeric')  # Switch to Numeric context
        >>> ctx = Context()     # Get current context
        >>> ctx.variables.add('t', 'Real')
    """
    global _current_context, _contexts
    
    if name is None:
        # Get current context
        if _current_context is None:
            # Create default Numeric context
            _current_context = _create_context('Numeric')
        return _current_context
    
    # Set/create context
    if name not in _contexts:
        _contexts[name] = _create_context(name)
    
    _current_context = _contexts[name]
    return _current_context


def _create_context(name: str) -> ContextClass:
    """Create a new context by name."""
    ctx = ContextClass(name)
    _contexts[name] = ctx
    return ctx


def get_current_context() -> ContextClass:
    """Get the current context (same as Context())."""
    return Context()
