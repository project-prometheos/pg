"""Tests for macro registry system."""

import pytest
from pg_macros import MacroRegistry, load_macros


def test_create_registry():
    """Test creating a registry."""
    registry = MacroRegistry()
    assert registry is not None


def test_register_file():
    """Test registering a macro file."""
    registry = MacroRegistry()
    
    exports = {
        "TEXT": lambda x: x,
        "ANS": lambda x: None
    }
    
    registry.register_file("test.pl", exports)
    loaded = registry.load("test.pl")
    
    assert "TEXT" in loaded
    assert "ANS" in loaded


def test_load_pgstandard():
    """Test loading PGstandard.pl."""
    exports = load_macros("PGstandard.pl")
    
    assert "TEXT" in exports
    assert "ANS" in exports
    assert "image" in exports
    assert callable(exports["TEXT"])


def test_load_mathobjects():
    """Test loading MathObjects.pl."""
    exports = load_macros("MathObjects.pl")
    
    assert "Compute" in exports
    assert callable(exports["Compute"])


def test_load_multiple_macros():
    """Test loading multiple macro files."""
    exports = load_macros("PGstandard.pl", "MathObjects.pl")
    
    assert "TEXT" in exports
    assert "Compute" in exports


def test_text_function():
    """Test TEXT function."""
    exports = load_macros("PGstandard.pl")
    TEXT = exports["TEXT"]
    
    result = TEXT("Hello", " ", "World")
    assert result == "Hello World"


def test_image_function():
    """Test image function."""
    exports = load_macros("PGstandard.pl")
    image_func = exports["image"]
    
    result = image_func("test.png", width="100", alt="Test")
    assert "test.png" in result
    assert "width" in result
    assert "alt" in result


def test_ans_rule_function():
    """Test ans_rule function."""
    exports = load_macros("PGstandard.pl")
    ans_rule = exports["ans_rule"]
    
    result = ans_rule(30)
    assert "input" in result
    assert "30" in result


def test_compute_function():
    """Test Compute function."""
    exports = load_macros("MathObjects.pl")
    Compute = exports["Compute"]
    
    # Should create a formula or evaluate
    result = Compute("2 + 3")
    assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
