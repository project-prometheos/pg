"""
Macro registry for loadMacros() functionality.

Reference: Perl loadMacros system in PGloadfiles.pm
"""

import importlib
import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict


class MacroRegistry:
    """
    Registry for PG macros.

    Maps macro file names to Python modules/functions.
    Supports dynamic loading similar to Perl's loadMacros().
    """

    def __init__(self):
        self._macros: Dict[str, Dict[str, Any]] = {}
        self._loaded_files: set[str] = set()

    def register_file(self, filename: str, exports: Dict[str, Any]) -> None:
        """
        Register all exports from a macro file.

        Args:
            filename: Macro filename (e.g., "PGstandard.pl")
            exports: Dictionary of exported functions/values
        """
        self._macros[filename] = exports
        self._loaded_files.add(filename)

    def is_loaded(self, filename: str) -> bool:
        """Check if a macro file has been loaded."""
        return filename in self._loaded_files

    def load(self, filename: str) -> Dict[str, Any]:
        """
        Load a macro file and return its exports.

        Args:
            filename: Macro filename (e.g., "PGstandard.pl")

        Returns:
            Dictionary of exported functions/values

        Raises:
            ModuleNotFoundError: If macro not found
        """
        # Check if already registered
        if filename in self._macros:
            return self._macros[filename]

        # Try to import Python module
        # Map Perl macro names to Python modules
        module_map = {
            "PGstandard.pl": "pg_macros.core.pg_standard",
            "MathObjects.pl": "pg_macros.core.math_objects",
            "PGML.pl": "pg_macros.core.pgml",
            "PGanswermacros.pl": "pg_macros.answers.pg_answer_macros",
            "PGchoicemacros.pl": "pg_macros.ui.choice_macros",
            "niceTables.pl": "pg_macros.ui.nice_tables",
            "scaffold.pl": "pg_macros.ui.scaffold",
            "contextFraction.pl": "pg_macros.contexts",
        }

        python_module = module_map.get(filename)
        if not python_module:
            raise ModuleNotFoundError(f"Macro file not ported yet: {filename}")

        try:
            module = importlib.import_module(python_module)
            # Extract exported functions (those not starting with _)
            exports = {
                name: getattr(module, name)
                for name in dir(module)
                if not name.startswith('_') and callable(getattr(module, name))
            }
            self._macros[filename] = exports
            self._loaded_files.add(filename)
            return exports
        except ImportError as e:
            raise ModuleNotFoundError(f"Failed to load macro {filename}: {e}")

    def get_all_exports(self, *filenames: str) -> Dict[str, Any]:
        """
        Load multiple macro files and return combined exports.

        Args:
            *filenames: Macro filenames to load

        Returns:
            Combined dictionary of all exports
        """
        combined = {}
        for filename in filenames:
            exports = self.load(filename)
            combined.update(exports)
        return combined


# Global registry instance
_global_registry = MacroRegistry()


def load_macros(*filenames: str) -> Dict[str, Any]:
    """
    Load macro files (similar to Perl's loadMacros).

    Usage:
        exports = load_macros("PGstandard.pl", "MathObjects.pl")
        # Now use exports: exports['TEXT']("Hello")

    Or inject into namespace:
        globals().update(load_macros("PGstandard.pl"))
        # Now use directly: TEXT("Hello")

    Args:
        *filenames: Macro filenames to load

    Returns:
        Combined dictionary of exported functions
    """
    return _global_registry.get_all_exports(*filenames)


def register_macro_file(filename: str, exports: Dict[str, Any]) -> None:
    """
    Register a macro file manually.

    Args:
        filename: Macro filename
        exports: Dictionary of exported functions
    """
    _global_registry.register_file(filename, exports)
