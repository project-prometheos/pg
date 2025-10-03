"""Tests for PG executor."""

import pytest

from pg_math import Formula, Real
from pg_parser import Context
from pg_translator.executor import PGExecutor


def test_execute_simple_code():
    """Test executing simple Python code."""
    code = """
a = 2
b = 3
c = a + b
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert env.seed == 123


def test_execute_text_accumulation():
    """Test text accumulation."""
    code = """
pg_env.add_text("Hello")
pg_env.add_text(" World")
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert len(env.text_segments) == 2
    assert env.text_segments[0] == "Hello"
    assert env.text_segments[1] == " World"


def test_execute_pgml_accumulation():
    """Test PGML text accumulation."""
    code = """
pg_env.add_pgml_text("Problem statement")
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert len(env.pgml_segments) == 1
    assert env.pgml_segments[0] == "Problem statement"


def test_execute_random_function():
    """Test random() function."""
    code = """
x = random(0, 10)
pg_env.variables['x'] = x
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    # Should have generated a number
    assert 'x' in env.variables
    assert 0 <= env.variables['x'] < 10


def test_execute_formula_function():
    """Test Formula() function."""
    code = """
f = Formula("x^2 + 1")
pg_env.variables['f'] = f
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert 'f' in env.variables
    assert isinstance(env.variables['f'], Formula)


def test_execute_real_function():
    """Test Real() function."""
    code = """
r = Real(3.14)
pg_env.variables['r'] = r
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert 'r' in env.variables
    assert isinstance(env.variables['r'], Real)
    assert env.variables['r'].value == 3.14


def test_execute_answer_registration():
    """Test answer registration with ANS()."""
    code = """
from pg_answer.evaluators.numeric import NumericEvaluator

ans = NumericEvaluator(correct_answer=42, tolerance=0.01)
ANS(ans, "answer1")
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert "answer1" in env.answers
    assert env.answers["answer1"].correct_answer == 42


def test_execute_num_cmp():
    """Test num_cmp() function."""
    code = """
evaluator = num_cmp(42, tolerance=0.01)
ANS(evaluator, "num_answer")
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert "num_answer" in env.answers


def test_execute_fun_cmp():
    """Test fun_cmp() function."""
    code = """
evaluator = fun_cmp("x^2", variables=["x"])
ANS(evaluator, "fun_answer")
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert "fun_answer" in env.answers


def test_execute_str_cmp():
    """Test str_cmp() function."""
    code = """
evaluator = str_cmp("correct", case_sensitive=True)
ANS(evaluator, "str_answer")
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert "str_answer" in env.answers


def test_execute_render_text():
    """Test rendering accumulated text."""
    code = """
pg_env.add_text("Plain text")
pg_env.add_pgml_text("PGML: [$x]")
pg_env.variables['x'] = Real(5)
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    html = env.render_text()
    assert "Plain text" in html
    assert "PGML:" in html


def test_execute_syntax_error():
    """Test handling syntax errors."""
    code = """
this is not valid python
"""

    executor = PGExecutor()
    with pytest.raises(SyntaxError):
        executor.execute(code, seed=123)


def test_execute_runtime_error():
    """Test handling runtime errors."""
    code = """
x = undefined_variable
"""

    executor = PGExecutor()
    with pytest.raises(RuntimeError):
        executor.execute(code, seed=123)


def test_execute_safe_builtins_only():
    """Test that unsafe built-ins are not available."""
    code = """
# Try to open a file (should fail)
f = open('/etc/passwd', 'r')
"""

    executor = PGExecutor()
    with pytest.raises(RuntimeError):
        # Should fail because 'open' is not in safe builtins
        executor.execute(code, seed=123)


def test_execute_solution_and_hint():
    """Test solution and hint accumulation."""
    code = """
pg_env.add_solution("This is the solution")
pg_env.add_hint("This is a hint")
"""

    executor = PGExecutor()
    env = executor.execute(code, seed=123)

    assert env.render_solution() == "This is the solution"
    assert env.render_hint() == "This is a hint"
