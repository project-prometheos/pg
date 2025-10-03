"""
Tests for subprocess-based sandbox.
"""

import pytest

from pg_parser import Context
from pg_translator.sandbox import Sandbox


def test_sandbox_basic_execution():
    """Test basic code execution in sandbox."""
    sandbox = Sandbox(timeout=5)
    code = """
TEXT("Hello, World!")
"""
    result = sandbox.execute(code, seed=42)

    assert result.success
    assert result.text_segments == ["Hello, World!"]
    assert result.errors == ""


def test_sandbox_with_variables():
    """Test execution with variable assignment."""
    sandbox = Sandbox(timeout=5)
    code = """
x = 5
y = 10
TEXT(f"x + y = {x + y}")
"""
    result = sandbox.execute(code, seed=42)

    assert result.success
    assert result.text_segments == ["x + y = 15"]


def test_sandbox_with_pg_math():
    """Test execution with PG math objects."""
    sandbox = Sandbox(timeout=5)
    code = """
a = Real(3)
b = Real(4)
c = a + b
TEXT(f"Result: {c}")
"""
    result = sandbox.execute(code, seed=42)

    assert result.success
    assert len(result.text_segments) == 1
    assert "Result:" in result.text_segments[0]


def test_sandbox_pgml():
    """Test PGML accumulation."""
    sandbox = Sandbox(timeout=5)
    code = """
PGML(\"\"\"
Solve for x:

[```x^2 + 1 = 0```]
\"\"\")
"""
    result = sandbox.execute(code, seed=42)

    assert result.success
    assert len(result.pgml_segments) == 1
    assert "x^2 + 1 = 0" in result.pgml_segments[0]


def test_sandbox_solution_and_hint():
    """Test solution and hint accumulation."""
    sandbox = Sandbox(timeout=5)
    code = """
TEXT("Problem statement")
SOLUTION("This is the solution")
HINT("This is a hint")
"""
    result = sandbox.execute(code, seed=42)

    assert result.success
    assert result.text_segments == ["Problem statement"]
    assert result.solution_segments == ["This is the solution"]
    assert result.hint_segments == ["This is a hint"]


def test_sandbox_answers():
    """Test answer registration."""
    sandbox = Sandbox(timeout=5)
    code = """
from pg_answer.evaluators.numeric import NumericEvaluator
ans = NumericEvaluator(42)
ANS(ans)
"""
    result = sandbox.execute(code, seed=42)

    assert result.success
    assert len(result.answers) == 1
    assert "AnSwEr0000" in result.answers


def test_sandbox_named_answer():
    """Test named answer registration."""
    sandbox = Sandbox(timeout=5)
    code = """
from pg_answer.evaluators.numeric import NumericEvaluator
NAMED_ANS("myAnswer", NumericEvaluator(42))
"""
    result = sandbox.execute(code, seed=42)

    assert result.success
    assert "myAnswer" in result.answers


def test_sandbox_error_handling():
    """Test error capture in sandbox."""
    sandbox = Sandbox(timeout=5)
    code = """
raise ValueError("Test error")
"""
    result = sandbox.execute(code, seed=42)

    assert not result.success or result.errors != ""
    assert "ValueError" in result.errors
    assert "Test error" in result.errors


def test_sandbox_timeout():
    """Test timeout protection."""
    sandbox = Sandbox(timeout=1)
    code = """
import time
time.sleep(10)  # This should timeout
"""
    result = sandbox.execute(code, seed=42)

    assert not result.success
    assert "timed out" in result.errors.lower()


def test_sandbox_no_variable_restrictions():
    """Test that underscore variables work (unlike RestrictedPython)."""
    sandbox = Sandbox(timeout=5)
    code = """
_env = {"key": "value"}
_block_ = "test"
TEXT(f"Env: {_env}, Block: {_block_}")
"""
    result = sandbox.execute(code, seed=42)

    assert result.success
    assert result.text_segments
    assert "Env:" in result.text_segments[0]


def test_sandbox_random_seed():
    """Test that random seed is consistent."""
    sandbox = Sandbox(timeout=5)
    code = """
import random
val = random.randint(1, 100)
TEXT(f"Random: {val}")
"""

    # Execute twice with same seed
    result1 = sandbox.execute(code, seed=42)
    result2 = sandbox.execute(code, seed=42)

    assert result1.success
    assert result2.success
    assert result1.text_segments == result2.text_segments

    # Execute with different seed
    result3 = sandbox.execute(code, seed=99)
    assert result3.success
    # May or may not be different, but should execute successfully


def test_sandbox_context():
    """Test context parameter."""
    sandbox = Sandbox(timeout=5)
    code = """
# Context should be available as pg_env.context
TEXT(f"Context: {pg_env.context.name}")
"""

    context = Context("Complex")
    result = sandbox.execute(code, seed=42, context=context)

    assert result.success
    assert "Complex" in result.text_segments[0]
