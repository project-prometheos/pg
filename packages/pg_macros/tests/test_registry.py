"""Tests for macro registry."""

import pytest

from pg_macros import MacroRegistry, loadMacros


def test_registry_list_available():
    """Test listing available macros."""
    available = MacroRegistry.list_available()

    assert "PGstandard.pl" in available
    assert "MathObjects.pl" in available
    assert "PGML.pl" in available
    assert "PGanswermacros.pl" in available


def test_registry_load_pgstandard():
    """Test loading PGstandard.pl."""
    exports = MacroRegistry.load_macro_file("PGstandard.pl")

    assert "TEXT" in exports
    assert "ANS" in exports
    assert "NAMED_ANS" in exports
    assert "image" in exports
    assert "htmlLink" in exports


def test_registry_load_mathobjects():
    """Test loading MathObjects.pl."""
    exports = MacroRegistry.load_macro_file("MathObjects.pl")

    assert "Real" in exports
    assert "Complex" in exports
    assert "Formula" in exports
    assert "Compute" in exports


def test_registry_load_pgml():
    """Test loading PGML.pl."""
    exports = MacroRegistry.load_macro_file("PGML.pl")

    assert "PGML" in exports


def test_registry_load_answer_macros():
    """Test loading PGanswermacros.pl."""
    exports = MacroRegistry.load_macro_file("PGanswermacros.pl")

    assert "num_cmp" in exports
    assert "fun_cmp" in exports
    assert "str_cmp" in exports


def test_registry_load_choice_macros():
    """Test loading PGchoicemacros.pl."""
    exports = MacroRegistry.load_macro_file("PGchoicemacros.pl")

    assert "MultipleChoice" in exports
    assert "TrueFalse" in exports
    assert "new_multiple_choice" in exports


def test_registry_caching():
    """Test that modules are cached."""
    # Load once
    exports1 = MacroRegistry.load_macro_file("PGstandard.pl")

    # Load again - should return cached version
    exports2 = MacroRegistry.load_macro_file("PGstandard.pl")

    assert exports1 is exports2


def test_registry_unknown_macro():
    """Test loading unknown macro file."""
    with pytest.raises(ImportError, match="not found"):
        MacroRegistry.load_macro_file("UnknownMacro.pl")


def test_load_macros_single():
    """Test loadMacros with single file."""
    macros = loadMacros("PGstandard.pl")

    assert "TEXT" in macros
    assert "ANS" in macros


def test_load_macros_multiple():
    """Test loadMacros with multiple files."""
    macros = loadMacros("PGstandard.pl", "MathObjects.pl", "PGML.pl")

    # From PGstandard
    assert "TEXT" in macros
    assert "ANS" in macros

    # From MathObjects
    assert "Real" in macros
    assert "Formula" in macros

    # From PGML
    assert "PGML" in macros


def test_load_macros_answer_macros():
    """Test loadMacros with answer macros."""
    macros = loadMacros("PGanswermacros.pl")

    assert "num_cmp" in macros
    assert "fun_cmp" in macros
    assert "str_cmp" in macros

    # Test that functions are callable
    assert callable(macros["num_cmp"])
    assert callable(macros["fun_cmp"])


def test_registry_register_custom():
    """Test registering custom macro mapping."""
    from pg_macros import register_macro_file

    # Register custom mapping
    register_macro_file("CustomMacro.pl", "pg_macros.core.pg_standard")

    # Should now be available
    available = MacroRegistry.list_available()
    assert "CustomMacro.pl" in available
