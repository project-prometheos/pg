"""Test formula answer checking with SymPy."""

from pg_renderer.checkers.formula import FormulaChecker


def test_simple_equivalence():
    """Test basic algebraic equivalence."""
    checker = FormulaChecker()
    
    # Expanded vs factored
    is_correct, msg = checker.check("(x-1)(x+2)", "x^2 + x - 2")
    assert is_correct, f"Should be correct: {msg}"
    
    # Same expression, different order
    is_correct, msg = checker.check("x^2 - 2 + x", "x^2 + x - 2")
    assert is_correct, f"Should be correct: {msg}"


def test_implicit_multiplication():
    """Test that implicit multiplication works."""
    checker = FormulaChecker()
    
    is_correct, msg = checker.check("2x + 4", "2*x + 4")
    assert is_correct, f"Should be correct: {msg}"
    
    is_correct, msg = checker.check("(x+1)(x-1)", "x^2 - 1")
    assert is_correct, f"Should be correct: {msg}"


def test_power_notation():
    """Test that ^ is converted to **."""
    checker = FormulaChecker()
    
    is_correct, msg = checker.check("x^2 + 2*x + 1", "(x+1)^2")
    assert is_correct, f"Should be correct: {msg}"


def test_incorrect_answer():
    """Test that incorrect answers are rejected."""
    checker = FormulaChecker()
    
    is_correct, msg = checker.check("x^2 + x + 1", "x^2 + x - 2")
    assert not is_correct, "Should be incorrect"


def test_up_to_constant():
    """Test checking up to constant multiple."""
    checker = FormulaChecker(mode='up_to_constant')
    
    # 2x + 4 = 2(x + 2), should be correct when checking up to constant
    is_correct, msg = checker.check("2x + 4", "x + 2")
    assert is_correct, f"Should be correct up to constant: {msg}"
    
    # (x-1)(x+2) = x^2 + x - 2, should be correct (factor of 1)
    is_correct, msg = checker.check("(x-1)(x+2)", "x^2 + x - 2")
    assert is_correct, f"Should be correct: {msg}"


def test_up_to_additive_constant():
    """Test checking up to additive constant."""
    checker = FormulaChecker(mode='up_to_additive_constant')

    # e^x + pi should be correct when compared to e^x up to additive constant
    is_correct, msg = checker.check("e^x + pi", "e^x")
    assert is_correct, f"Should be correct up to additive constant: {msg}"

    # Not additive-constant equivalent
    is_correct, msg = checker.check("x^2 + x", "x^2 + 1")
    assert not is_correct, "Should be incorrect for non-constant difference"


def test_syntax_error():
    """Test that syntax errors are caught."""
    checker = FormulaChecker()
    
    is_correct, msg = checker.check("x +* 2", "x + 2")
    assert not is_correct, "Should reject syntax error"
    assert "syntax" in msg.lower() or "parse" in msg.lower() or "error" in msg.lower()


def test_multiple_variables():
    """Test expressions with multiple variables."""
    checker = FormulaChecker()
    
    is_correct, msg = checker.check("xy + x + y", "x*y + x + y")
    assert is_correct, f"Should be correct: {msg}"


if __name__ == '__main__':
    # Run tests
    test_simple_equivalence()
    test_implicit_multiplication()
    test_power_notation()
    test_incorrect_answer()
    test_up_to_constant()
    test_syntax_error()
    test_multiple_variables()
    
    print("All tests passed!")

