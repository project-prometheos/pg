"""
Context system for MathObjects.

The Context controls what operations, variables, constants, and functions
are available when parsing and evaluating mathematical expressions.

Reference: lib/Context.pm in legacy Perl codebase
"""

import math
from typing import Dict, Any, Optional, Set
from copy import deepcopy
from dataclasses import dataclass


class VariableManager:
    """Manages variables available in the context."""

    def __init__(self):
        self._variables: Dict[str, dict] = {}  # name -> {type, options}

    def add(self, name: str = None, type_: str = 'Real', **kwargs):
        """
        Add a variable to the context.

        Supports both forms:
        - add('k', 'Real') - positional
        - add(k='Real') - keyword (from Perl-style code)
        """
        if name is not None:
            # Positional form: add('k', 'Real')
            self._variables[name] = {'type': type_, 'options': {}}
        elif kwargs:
            # Keyword form: add(k='Real')
            for var_name, var_type in kwargs.items():
                self._variables[var_name] = {'type': var_type, 'options': {}}

    def set(self, name: str = None, **options):
        """
        Set variable options (e.g., limits).

        Supports both forms:
        - set('x', limits=[2, 3]) - positional name with keyword options
        - set(x={'limits': [2, 3]}) - keyword form (from Perl-style code)
        """
        if name is not None:
            # Positional form: set('x', limits=[2, 3])
            if name in self._variables:
                self._variables[name]['options'].update(options)
            else:
                # Create variable if it doesn't exist
                self._variables[name] = {'type': 'Real', 'options': options}
        elif options:
            # Keyword form: set(x={'limits': [2, 3]})
            for var_name, var_options in options.items():
                if isinstance(var_options, dict):
                    if var_name in self._variables:
                        self._variables[var_name]['options'].update(var_options)
                    else:
                        self._variables[var_name] = {'type': 'Real', 'options': var_options}

    def remove(self, name: str):
        """Remove a variable from the context."""
        if name in self._variables:
            del self._variables[name]

    def are(self, **kwargs):
        """Set variables (replaces existing)."""
        self._variables = {name: {'type': type_, 'options': {}} for name, type_ in kwargs.items()}

    def get(self, name: str) -> Optional[dict]:
        """Get variable info (type and options)."""
        return self._variables.get(name)

    def list(self) -> list:
        """Get list of variable names."""
        return list(self._variables.keys())

    def copy(self):
        """Create a copy of this manager."""
        new_mgr = VariableManager()
        new_mgr._variables = {k: v.copy() for k, v in self._variables.items()}
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

    def undefine(self, *names):
        """Undefine (remove) one or more functions."""
        for name in names:
            self.remove(name)

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

    def undefine(self, *names):
        """Undefine (remove) one or more operators."""
        for name in names:
            self.remove(name)

    def list(self) -> list:
        """Get list of operator names."""
        return list(self._operators.keys())

    def copy(self):
        """Create a copy of this manager."""
        new_mgr = OperatorManager()
        new_mgr._operators = deepcopy(self._operators)
        return new_mgr


@dataclass
class StringConfig:
    """Configuration for a string value in the context."""
    value: str
    alias: str | None = None
    case_sensitive: bool = False


class StringsManager:
    """Manager for string values in a context."""

    def __init__(self):
        self._strings: Dict[str, StringConfig] = {}

    def add(self, **strings: dict) -> None:
        """
        Add strings to the context.

        Args:
            **strings: String names with optional configuration dicts
                      e.g., add(none={}, N={'alias': 'none'})
        """
        for name, config in strings.items():
            if config is None:
                config = {}

            alias = config.get('alias')
            case_sensitive = config.get('caseSensitive', False)

            self._strings[name] = StringConfig(
                value=name,
                alias=alias,
                case_sensitive=case_sensitive
            )

    def get(self, name: str) -> Optional[StringConfig]:
        """Get a string configuration."""
        return self._strings.get(name)

    def list(self) -> list:
        """Get list of string names."""
        return list(self._strings.keys())

    def copy(self):
        """Create a copy of this manager."""
        new_mgr = StringsManager()
        new_mgr._strings = {k: StringConfig(v.value, v.alias, v.case_sensitive)
                            for k, v in self._strings.items()}
        return new_mgr


class ContextFlags:
    """
    Manages context flags/options.

    Flags control parsing, evaluation, and reduction behavior.
    Reference: lib/Context/Flags.pm
    """

    def __init__(self):
        self._flags: Dict[str, Any] = {
            # Comparison tolerances
            'tolerance': 0.001,
            'tolType': 'relative',
            'zeroLevel': 1e-14,
            'zeroLevelTol': 1e-12,

            # Reduction flags
            'reduceConstants': 1,
            'reduceConstantFunctions': 1,

            # Polynomial validation flags (Week 5) - not set by default
            # These are only set when using specialized contexts
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


class Context:
    """
    Context for parsing and evaluating mathematical expressions.

    The Context determines what operations, variables, constants, and
    functions are available, as well as how expressions are parsed and
    evaluated.

    Reference: lib/Context.pm (lines 1-500) in legacy Perl codebase
    """

    def __init__(self, name: str = 'Numeric'):
        """
        Create a new Context.

        Args:
            name: Context name (Numeric, Complex, Point, Vector, Interval, LimitedPolynomial, etc.)
        """
        self.name = name
        self.variables = VariableManager()
        self.constants = ConstantManager()
        self.functions = FunctionManager()
        self.operators = OperatorManager()
        self.strings = StringsManager()
        self.flags = ContextFlags()

        # Initialize based on context name
        if name == 'Numeric':
            self._init_numeric()
        elif name == 'Complex':
            self._init_complex()
        elif name == 'Point':
            self._init_point()
        elif name == 'Vector':
            self._init_vector()
        elif name == 'Interval':
            self._init_interval()
        elif name == 'Fraction':
            self._init_fraction()
        elif name == 'Fraction-NoDecimals':
            self._init_fraction_no_decimals()
        elif name == 'LimitedFraction':
            self._init_limited_fraction()
        elif name == 'LimitedProperFraction':
            self._init_limited_proper_fraction()
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

    def _init_complex(self):
        """Initialize Complex context."""
        self._init_numeric()
        # Add imaginary constant
        self.constants.add('i', 1j)

    def _init_point(self):
        """Initialize Point context."""
        self._init_numeric()
        # Add y, z variables for 2D/3D points
        self.variables.add('y', 'Real')
        self.variables.add('z', 'Real')

    def _init_vector(self):
        """Initialize Vector context."""
        # Same as Point but with vector operations
        self._init_point()

    def _init_interval(self):
        """Initialize Interval context for interval notation."""
        # Start with Numeric base
        self._init_numeric()

        # Add infinity constant for interval endpoints
        self.constants.add('inf', float('inf'))
        self.constants.add('infinity', float('inf'))

    def _init_fraction(self):
        """
        Initialize Fraction context.

        General context allowing fractions mixed with reals.

        Reference: contextFraction.pl::Init
        """
        # Start with Numeric base
        self._init_numeric()

        # Fraction-specific flags
        self.flags.set(
            reduceFractions=True,
            strictFractions=False,
            allowMixedNumbers=False,
            requireProperFractions=False,
            requirePureFractions=False,
            showMixedNumbers=False,
            fractionTolerance=1e-10,
            contFracMaxDen=10**8,
        )

    def _init_fraction_no_decimals(self):
        """
        Initialize Fraction-NoDecimals context.

        Like Fraction but decimal numbers cannot be typed explicitly.

        Reference: contextFraction.pl::Init
        """
        self._init_fraction()
        # Flag that decimals are not allowed
        self.flags.set(noDecimals=True)

    def _init_limited_fraction(self):
        """
        Initialize LimitedFraction context.

        Only division and negation allowed, no other operations or functions.
        Mixed numbers enabled (e.g., "2 1/2" = 2 + 1/2).

        Reference: contextFraction.pl::Init
        """
        # Start with Numeric base
        self._init_numeric()

        # Strict fraction flags
        self.flags.set(
            reduceFractions=True,
            strictFractions=True,
            allowMixedNumbers=True,
            requireProperFractions=False,
            requirePureFractions=False,
            showMixedNumbers=True,
            fractionTolerance=1e-10,
            contFracMaxDen=10**8,
            reduceConstants=False,
            noDecimals=True,
        )

        # Only allow division and negation operators
        # Undefine all other operators
        for op in ['+', '-', '*', '**', '^']:
            self.operators.undefine(op)

        # Undefine all functions
        for func in self.functions.list():
            self.functions.undefine(func)

    def _init_limited_proper_fraction(self):
        """
        Initialize LimitedProperFraction context.

        Like LimitedFraction but requires proper fractions.

        Reference: contextFraction.pl::Init
        """
        self._init_limited_fraction()
        self.flags.set(requireProperFractions=True)

    def _init_limited_polynomial(self, strict: bool = False):
        """Initialize LimitedPolynomial context (Week 5 feature)."""
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
        """Initialize PolynomialFactors context (Week 5 feature)."""
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

    def copy(self, name: Optional[str] = None) -> 'Context':
        """
        Create a copy of this context.

        Args:
            name: Optional new name for the copied context

        Returns:
            New Context instance with copied settings
        """
        new_context = Context.__new__(Context)
        new_context.name = name if name is not None else self.name
        new_context.variables = self.variables.copy()
        new_context.constants = self.constants.copy()
        new_context.functions = self.functions.copy()
        new_context.operators = self.operators.copy()
        new_context.strings = self.strings.copy()
        new_context.flags = self.flags.copy()
        return new_context

    def __eq__(self, other):
        """Check if two contexts are the same instance."""
        if not isinstance(other, Context):
            return False
        return self is other

    def __ne__(self, other):
        """Check if two contexts are different instances."""
        return not self.__eq__(other)

    def __repr__(self):
        return f"Context('{self.name}')"


# Global context registry (singleton pattern for named contexts)
_contexts: Dict[str, Context] = {}
_current_context: Optional[Context] = None


def get_context(name: Optional[str] = None) -> Context:
    """
    Get or set the current context.

    Args:
        name: Context name to switch to (None = get current)

    Returns:
        Current context

    Examples:
        >>> ctx = get_context('Numeric')  # Switch to Numeric context
        >>> ctx = get_context()           # Get current context
        >>> ctx.variables.add('t', 'Real')

    Note: This is the main API for getting contexts, matching Perl's Context() function.
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


def _create_context(name: str) -> Context:
    """Create a new context by name (internal - creates actual Context instance)."""
    # Direct instantiation to avoid recursion
    ctx = Context.__new__(Context)
    ctx.__init__(name)
    _contexts[name] = ctx
    return ctx


def get_current_context() -> Context:
    """
    Get the current context.

    Returns:
        Current context (creates Numeric if none exists)
    """
    return get_context()
