"""Test simple numeric problems."""

import sys
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker


def test_simple_addition():
    """Test basic addition problem."""
    pg_source = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
Context("Numeric");
$a = 2;
$b = 3;
$answer = $a + $b;
BEGIN_PGML
What is [$a] + [$b]?
Answer: [_____]{$answer}
END_PGML
ENDDOCUMENT();
"""
    renderer = PGRenderer()
    result = renderer.render(pg_source, seed=0)
    
    assert '2' in result['statement_html']
    assert '3' in result['statement_html']
    assert len(result['inputs']) == 1
    assert result['answers'][result['inputs'][0]]['correct_value'] == '5'
    assert len(result['errors']) == 0


def test_random_values():
    """Test random value generation."""
    pg_source = """
loadMacros("PGML.pl");
Context("Numeric");
$a = random(1, 5, 1);
$b = random(2, 6, 1);
$answer = $a + $b;
BEGIN_PGML
The sum of [$a] and [$b] is [$answer].

Answer: [_____]{$answer}
END_PGML
"""
    renderer = PGRenderer()
    
    # Test determinism with same seed
    result1 = renderer.render(pg_source, seed=42)
    result2 = renderer.render(pg_source, seed=42)
    assert result1['statement_html'] == result2['statement_html']
    assert result1['answers'][result1['inputs'][0]]['correct_value'] == result2['answers'][result2['inputs'][0]]['correct_value']
    
    # Test variation with different seed
    result3 = renderer.render(pg_source, seed=123)
    # With different seeds, answers should be different
    assert result1['answers'][result1['inputs'][0]]['correct_value'] != result3['answers'][result3['inputs'][0]]['correct_value']


def test_answer_checking():
    """Test answer checker."""
    checker = AnswerChecker(tolerance=0.01)
    
    # Exact match
    is_correct, msg = checker.check("5", "5", "number")
    assert is_correct
    
    # Within tolerance
    is_correct, msg = checker.check("5.001", "5.0", "number")
    assert is_correct
    
    # Outside tolerance
    is_correct, msg = checker.check("6", "5", "number")
    assert not is_correct


def test_multiple_operations():
    """Test multiple mathematical operations."""
    pg_source = """
$a = 10;
$b = 3;
$sum = $a + $b;
$diff = $a - $b;
$prod = $a * $b;
$quot = $a / $b;
BEGIN_PGML
Sum: [$sum]
Diff: [$diff]
Prod: [$prod]
Quot: [$quot]
END_PGML
"""
    renderer = PGRenderer()
    result = renderer.render(pg_source, seed=0)
    
    assert '13' in result['statement_html']  # sum
    assert '7' in result['statement_html']   # diff
    assert '30' in result['statement_html']  # prod
    assert len(result['errors']) == 0


def test_power_operator():
    """Test power operator conversion."""
    pg_source = """
$a = 2;
$b = 3;
$power = $a ^ $b;
BEGIN_PGML
[$a] to the power of [$b] is [$power]
END_PGML
"""
    renderer = PGRenderer()
    result = renderer.render(pg_source, seed=0)
    
    assert '8' in result['statement_html']  # 2^3 = 8
    assert len(result['errors']) == 0


if __name__ == '__main__':
    # Run tests
    test_simple_addition()
    print("[PASS] test_simple_addition")
    
    test_random_values()
    print("[PASS] test_random_values")
    
    test_answer_checking()
    print("[PASS] test_answer_checking")
    
    test_multiple_operations()
    print("[PASS] test_multiple_operations")
    
    test_power_operator()
    print("[PASS] test_power_operator")
    
    print("\nAll tests passed!")

