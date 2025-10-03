"""Tests for PGstandard.pl macros."""

import pytest
from pg_macros import load_macros


def test_text_function():
    """Test TEXT function."""
    exports = load_macros("PGstandard.pl")
    TEXT = exports["TEXT"]
    
    result = TEXT("Hello", " ", "World")
    assert result == "Hello World"
    
    # Multiple arguments
    result = TEXT("A", "B", "C")
    assert result == "ABC"


def test_image_function():
    """Test image function."""
    exports = load_macros("PGstandard.pl")
    image = exports["image"]
    
    # Basic image
    result = image("test.png")
    assert "test.png" in result
    assert "img" in result
    
    # With attributes
    result = image("test.png", width="100", height="50", alt="Test Image")
    assert "width=\"100\"" in result
    assert "height=\"50\"" in result
    assert "alt=\"Test Image\"" in result


def test_ans_rule():
    """Test ans_rule function."""
    exports = load_macros("PGstandard.pl")
    ans_rule = exports["ans_rule"]
    
    # Default width
    result = ans_rule()
    assert "input" in result
    
    # Custom width
    result = ans_rule(30)
    assert "30" in result


def test_bold_italic():
    """Test formatting functions."""
    exports = load_macros("PGstandard.pl")
    bold = exports["bold"]
    italic = exports["italic"]
    
    assert "**text**" == bold("text")
    assert "*text*" == italic("text")


def test_random():
    """Test random number generation."""
    exports = load_macros("PGstandard.pl")
    random = exports["random"]
    
    # Generate 10 random numbers
    for _ in range(10):
        r = random(0, 10)
        assert 0 <= r <= 10
    
    # With step
    r = random(0, 10, step=2)
    assert r in [0, 2, 4, 6, 8, 10]


def test_non_zero_random():
    """Test non-zero random."""
    exports = load_macros("PGstandard.pl")
    non_zero_random = exports["non_zero_random"]
    
    # Should not be zero
    for _ in range(10):
        r = non_zero_random(-5, 5)
        assert r != 0
        assert -5 <= r <= 5


def test_list_random():
    """Test list_random."""
    exports = load_macros("PGstandard.pl")
    list_random = exports["list_random"]
    
    items = [1, 2, 3, 4, 5]
    for _ in range(10):
        r = list_random(*items)
        assert r in items


def test_shuffle():
    """Test shuffle."""
    exports = load_macros("PGstandard.pl")
    shuffle = exports["shuffle"]
    
    items = [1, 2, 3, 4, 5]
    shuffled = shuffle(*items)
    
    # Should have same elements
    assert set(shuffled) == set(items)
    assert len(shuffled) == len(items)


def test_random_subset():
    """Test random_subset."""
    exports = load_macros("PGstandard.pl")
    random_subset = exports["random_subset"]
    
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    subset = random_subset(3, *items)
    
    assert len(subset) == 3
    for item in subset:
        assert item in items


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

