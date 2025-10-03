"""
Macro Registry - Dynamic macro loading system.

Provides loadMacros() function similar to Perl PG:
- Maps Perl macro filenames to Python modules
- Dynamically imports and caches macro implementations
- Returns functions to caller's namespace

Reference: PGcore.pl::loadMacros (lines 200-250)
"""

from __future__ import annotations

import importlib
from typing import Any, Callable


class MacroRegistry:
    """
    Central registry for PG macros.

    Maps Perl macro filenames (e.g., "PGstandard.pl") to Python module paths.
    """

    # Mapping: Perl filename -> Python module path
    _file_to_module: dict[str, str] = {
        # Core macros
        "PGstandard.pl": "pg_macros.core.pg_standard",
        "MathObjects.pl": "pg_macros.core.math_objects",
        "PGML.pl": "pg_macros.core.pgml",
        # Answer macros
        "PGanswermacros.pl": "pg_macros.answers.pg_answer_macros",
        "PGnumericalmacros.pl": "pg_macros.answers.pg_numerical_macros",
        # Choice macros
        "PGchoicemacros.pl": "pg_macros.choice.pg_choice_macros",
        # Parser macros
        "parserPopUp.pl": "pg_macros.parsers.parser_popup",
        "parserRadioButtons.pl": "pg_macros.parsers.parser_radio_buttons",
        "parserCheckboxes.pl": "pg_macros.parsers.parser_checkboxes",
    }

    # Cache: module path -> loaded module
    _loaded_modules: dict[str, Any] = {}

    # Cache: filename -> exported functions
    _exports: dict[str, dict[str, Callable]] = {}

    @classmethod
    def register_mapping(cls, perl_filename: str, python_module: str) -> None:
        """
        Register a mapping from Perl filename to Python module.

        Args:
            perl_filename: Perl macro filename (e.g., "MyMacro.pl")
            python_module: Python module path (e.g., "pg_macros.custom.my_macro")
        """
        cls._file_to_module[perl_filename] = python_module

    @classmethod
    def load_macro_file(cls, filename: str) -> dict[str, Callable]:
        """
        Load a macro file and return its exported functions.

        Args:
            filename: Perl macro filename (e.g., "PGstandard.pl")

        Returns:
            Dictionary of exported functions

        Raises:
            ImportError: If macro file not found
        """
        # Check cache
        if filename in cls._exports:
            return cls._exports[filename]

        # Get Python module path
        if filename not in cls._file_to_module:
            raise ImportError(
                f"Macro file '{filename}' not found. "
                f"Available: {', '.join(cls._file_to_module.keys())}"
            )

        module_path = cls._file_to_module[filename]

        # Load module
        if module_path not in cls._loaded_modules:
            try:
                module = importlib.import_module(module_path)
                cls._loaded_modules[module_path] = module
            except ImportError as e:
                raise ImportError(
                    f"Failed to import {module_path} for {filename}: {e}"
                ) from e

        module = cls._loaded_modules[module_path]

        # Extract exports (functions marked for export)
        exports = {}
        if hasattr(module, "__exports__"):
            # Module explicitly defines exports
            for name in module.__exports__:
                if hasattr(module, name):
                    exports[name] = getattr(module, name)
        else:
            # Export all public functions (not starting with _)
            for name in dir(module):
                if not name.startswith("_"):
                    attr = getattr(module, name)
                    if callable(attr):
                        exports[name] = attr

        # Cache and return
        cls._exports[filename] = exports
        return exports

    @classmethod
    def list_available(cls) -> list[str]:
        """List all available macro files."""
        return sorted(cls._file_to_module.keys())


def loadMacros(*filenames: str) -> dict[str, Callable]:
    """
    Load PG macro files (Perl-compatible function).

    Mimics Perl's loadMacros() function:
    - Accepts one or more macro filenames
    - Returns all exported functions

    Args:
        *filenames: Macro filenames (e.g., "PGstandard.pl", "PGML.pl")

    Returns:
        Combined dictionary of all exported functions

    Example:
        >>> macros = loadMacros("PGstandard.pl", "PGML.pl")
        >>> macros['TEXT']("Hello")  # Use TEXT function
    """
    all_exports: dict[str, Callable] = {}

    for filename in filenames:
        exports = MacroRegistry.load_macro_file(filename)
        all_exports.update(exports)

    return all_exports


def register_macro_file(filename: str, python_module: str) -> None:
    """
    Register a custom macro file mapping.

    Args:
        filename: Perl macro filename
        python_module: Python module path
    """
    MacroRegistry.register_mapping(filename, python_module)
