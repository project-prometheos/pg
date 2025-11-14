"""
Units Context for WeBWorK - Phase 1 Implementation

This module provides a minimal implementation of the Units context sufficient
for basic problems like AnswerWithUnits.pg.

Phase 1 includes:
- Basic Units context registration
- withUnitsFor() method for length and time
- assignUnits() method for variables
- Basic unit constants (ft, m, s, etc.)

Reference: macros/contexts/contextUnits.pl (2263 lines)

TODO Phase 2:
- Full unit categories (angles, volume, mass, etc.)
- Unit conversions
- Formula with units support
- Unit arithmetic
"""

from typing import Any, Dict, List, Optional
from pg.math.context import Context, get_context


# Unit definitions for length and time (Phase 1)
UNIT_DEFINITIONS = {
    'length': {
        # Fundamental: meters
        'm': {'value': 1.0, 'fundamental': 'm', 'aliases': ['meter', 'meters']},
        'cm': {'value': 0.01, 'fundamental': 'm', 'aliases': ['centimeter', 'centimeters']},
        'mm': {'value': 0.001, 'fundamental': 'm', 'aliases': ['millimeter', 'millimeters']},
        'km': {'value': 1000.0, 'fundamental': 'm', 'aliases': ['kilometer', 'kilometers']},
        # Imperial
        'ft': {'value': 0.3048, 'fundamental': 'm', 'aliases': ['foot', 'feet']},
        'in': {'value': 0.0254, 'fundamental': 'm', 'aliases': ['inch', 'inches']},
        'mi': {'value': 1609.34, 'fundamental': 'm', 'aliases': ['mile', 'miles']},
        'yd': {'value': 0.9144, 'fundamental': 'm', 'aliases': ['yard', 'yards']},
    },
    'time': {
        # Fundamental: seconds
        's': {'value': 1.0, 'fundamental': 's', 'aliases': ['sec', 'second', 'seconds']},
        'ms': {'value': 0.001, 'fundamental': 's', 'aliases': ['millisecond', 'milliseconds']},
        'min': {'value': 60.0, 'fundamental': 's', 'aliases': ['minute', 'minutes']},
        'hr': {'value': 3600.0, 'fundamental': 's', 'aliases': ['hour', 'hours']},
        'day': {'value': 86400.0, 'fundamental': 's', 'aliases': ['days']},
    },
}


class UnitsContext(Context):
    """
    Extended Context class with Units support.
    
    Provides methods for:
    - withUnitsFor(category1, category2, ...) - enable unit categories
    - assignUnits(var => unit) - assign units to variables
    """
    
    def __init__(self, name: str = 'Units'):
        """Initialize a Units context."""
        super().__init__(name)
        
        # Track which unit categories are enabled
        self._enabled_units: Dict[str, bool] = {}
        
        # Track variable unit assignments
        self._variable_units: Dict[str, str] = {}
        
        # Store unit definitions
        self._unit_defs: Dict[str, dict] = {}
    
    def withUnitsFor(self, *categories: str) -> 'UnitsContext':
        """
        Enable units for one or more categories.
        
        Args:
            *categories: Category names like 'length', 'time', etc.
        
        Returns:
            self (for method chaining)
        
        Example:
            >>> Context('Units').withUnitsFor('length', 'time')
        """
        for category in categories:
            if category in UNIT_DEFINITIONS:
                self._enabled_units[category] = True
                # Add units as constants to the context
                self._add_units_from_category(category)
            else:
                # Warn but don't fail for unknown categories (Phase 2)
                print(f"Warning: Unit category '{category}' not yet implemented")
        
        return self
    
    def _add_units_from_category(self, category: str) -> None:
        """Add all units from a category as constants."""
        if category not in UNIT_DEFINITIONS:
            return
        
        for unit_name, unit_info in UNIT_DEFINITIONS[category].items():
            # Add the main unit name
            self.constants.add(unit_name, unit_info['value'])
            self._unit_defs[unit_name] = unit_info
            
            # Mark it as a unit (for identification)
            const_obj = self.constants.get(unit_name)
            if isinstance(const_obj, dict):
                const_obj['isUnit'] = True
            
            # Add aliases
            for alias in unit_info.get('aliases', []):
                self.constants.add(alias, unit_info['value'])
                self._unit_defs[alias] = unit_info
    
    def assignUnits(self, *args, **kwargs) -> 'UnitsContext':
        """
        Assign units to variables.
        
        Can be called as:
        - assignUnits(t='s', x='m')  # kwargs
        - assignUnits({'t': 's', 'x': 'm'})  # dict
        
        Args:
            *args: Optional dict of variable=>unit mappings
            **kwargs: variable=unit keyword arguments
        
        Returns:
            self (for method chaining)
        
        Example:
            >>> Context('Units').assignUnits(t='s', x='ft')
            >>> Context().assignUnits({'t': 's'})
        """
        # Handle dict argument
        if args and isinstance(args[0], dict):
            for var_name, unit in args[0].items():
                self._variable_units[var_name] = unit
        
        # Handle keyword arguments
        for var_name, unit in kwargs.items():
            self._variable_units[var_name] = unit
        
        return self
    
    def addUnits(self, *unit_names: str) -> 'UnitsContext':
        """
        Add specific named units to the context.
        
        Args:
            *unit_names: Names of units to add
        
        Returns:
            self (for method chaining)
        
        Example:
            >>> Context('Units').addUnits('m', 'cm', 'ft')
        """
        for unit_name in unit_names:
            # Search for the unit in all categories
            for category, units in UNIT_DEFINITIONS.items():
                if unit_name in units:
                    unit_info = units[unit_name]
                    self.constants.add(unit_name, unit_info['value'])
                    self._unit_defs[unit_name] = unit_info
                    break
        
        return self
    
    def removeUnits(self, *unit_names: str) -> 'UnitsContext':
        """
        Remove specific units from the context.
        
        Args:
            *unit_names: Names of units to remove
        
        Returns:
            self (for method chaining)
        
        Example:
            >>> Context('Units').withUnitsFor('length').removeUnits('ft', 'in')
        """
        for unit_name in unit_names:
            self.constants.remove(unit_name)
            if unit_name in self._unit_defs:
                del self._unit_defs[unit_name]
        
        return self
    
    def getVariableUnit(self, var_name: str) -> Optional[str]:
        """Get the unit assigned to a variable."""
        return self._variable_units.get(var_name)
    
    def isUnit(self, name: str) -> bool:
        """Check if a name is a registered unit."""
        return name in self._unit_defs


def Context_Units() -> UnitsContext:
    """
    Get or create the Units context.
    
    This is a helper function that creates a UnitsContext instance.
    
    Returns:
        UnitsContext instance
    
    Example:
        >>> ctx = Context_Units()
        >>> ctx.withUnitsFor('length', 'time')
    """
    # Check if we already have a Units context
    from pg.math.context import _contexts
    
    if 'Units' not in _contexts:
        ctx = UnitsContext('Units')
        _contexts['Units'] = ctx
        return ctx
    
    return _contexts['Units']


# Register Units context creation
def _patch_context_creation():
    """Patch the Context creation to support 'Units'."""
    import pg.math.context as context_module
    
    original_get_context = context_module.get_context
    
    def patched_get_context(name: Optional[str] = None) -> Context:
        if name == 'Units':
            return Context_Units()
        return original_get_context(name)
    
    context_module.get_context = patched_get_context


# Apply the patch when this module is imported
_patch_context_creation()


__all__ = [
    'UnitsContext',
    'Context_Units',
    'UNIT_DEFINITIONS',
]

