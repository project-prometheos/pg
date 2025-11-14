"""
Pytest configuration and Hypothesis strategies for fuzz testing.
"""
import pytest
from hypothesis import strategies as st


# Basic numeric strategies
integers = st.integers(min_value=-1000, max_value=1000)
small_integers = st.integers(min_value=1, max_value=20)
non_zero_integers = st.integers(min_value=-100, max_value=100).filter(lambda x: x != 0)
floats = st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
positive_floats = st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)

# Random seeds
random_seeds = st.integers(min_value=1, max_value=999999)

# PG variable names
pg_variable_names = st.text(
    alphabet=st.characters(whitelist_categories=('Ll', 'Lu'), min_codepoint=ord('a'), max_codepoint=ord('z')),
    min_size=1,
    max_size=10
)

# Simple formulas
simple_formula_parts = st.sampled_from([
    "x",
    "x^2", 
    "x^3",
    "2*x",
    "3*x",
    "x + 1",
    "x - 1"
])

# Fraction components
fraction_numerators = st.integers(min_value=-100, max_value=100)
fraction_denominators = st.integers(min_value=1, max_value=100)


@st.composite
def fractions(draw):
    """Generate fraction tuples (numerator, denominator)."""
    num = draw(fraction_numerators)
    denom = draw(fraction_denominators)
    return (num, denom)


@st.composite
def pg_numeric_expressions(draw):
    """Generate simple PG numeric expressions."""
    a = draw(small_integers)
    b = draw(small_integers)
    op = draw(st.sampled_from(['+', '-', '*']))
    return f"{a} {op} {b}"


@st.composite
def vectors_2d(draw):
    """Generate 2D vectors."""
    x = draw(floats)
    y = draw(floats)
    return (x, y)


@st.composite
def vectors_3d(draw):
    """Generate 3D vectors."""
    x = draw(floats)
    y = draw(floats)
    z = draw(floats)
    return (x, y, z)


@st.composite
def intervals(draw):
    """Generate interval bounds."""
    a = draw(integers)
    b = draw(integers)
    # Ensure a < b
    if a >= b:
        a, b = b, a
    return (a, b)


# Pytest fixtures
@pytest.fixture(scope="session")
def fuzz_build_dir(tmp_path_factory):
    """Get temporary build directory for fuzz tests."""
    return tmp_path_factory.mktemp("fuzz_build")

