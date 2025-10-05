"""
Tests for Context flag system.

Validates that context flags work correctly across different contexts and
affect behavior as expected.

Ported from pg_mathobjects for Perl parity migration.
"""

import pytest
from pg_math import Context, Formula, Real


class TestContextFlagsBasic:
    """Test basic flag operations."""

    def test_default_flags(self):
        """Verify default flag values"""
        ctx = Context('Numeric')
        assert ctx.flags.get('tolerance') == 0.001
        assert ctx.flags.get('tolType') == 'relative'
        assert ctx.flags.get('zeroLevel') == 1e-14
        assert ctx.flags.get('zeroLevelTol') == 1e-12
        assert ctx.flags.get('reduceConstants') == 1
        assert ctx.flags.get('reduceConstantFunctions') == 1

    def test_set_flags(self):
        """Set and retrieve flags"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.01)
        assert ctx.flags.get('tolerance') == 0.01

    def test_flag_copy(self):
        """Flags copied with context"""
        ctx1 = Context('Numeric')
        ctx1.flags.set(tolerance=0.01)

        ctx2 = ctx1.copy()
        assert ctx2.flags.get('tolerance') == 0.01

        # Modifying ctx2 shouldn't affect ctx1
        ctx2.flags.set(tolerance=0.001)
        assert ctx1.flags.get('tolerance') == 0.01
        assert ctx2.flags.get('tolerance') == 0.001

    def test_get_nonexistent(self):
        """Returns None for undefined flags"""
        ctx = Context('Numeric')
        assert ctx.flags.get('nonexistent') is None

    def test_multiple_flags(self):
        """Set multiple flags at once"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.01, tolType='absolute')
        assert ctx.flags.get('tolerance') == 0.01
        assert ctx.flags.get('tolType') == 'absolute'


class TestToleranceFlags:
    """Test tolerance-related flags."""

    def test_relative_tolerance_default(self):
        """Default relative tolerance in comparisons"""
        ctx = Context('Numeric')
        r1 = Real(1.0)
        r2 = Real(1.0005)  # Within 0.001 relative tolerance
        r3 = Real(1.002)   # Outside 0.001 relative tolerance

        assert r1 == r2  # Within tolerance
        assert r1 != r3  # Outside tolerance

    def test_absolute_tolerance(self):
        """Switch to absolute tolerance"""
        ctx = Context('Numeric')
        ctx.flags.set(tolType='absolute', tolerance=0.01)

        r1 = Real(1.0, ctx)
        r2 = Real(1.005, ctx)  # Within 0.01 absolute
        r3 = Real(1.02, ctx)   # Outside 0.01 absolute

        assert r1 == r2
        assert r1 != r3

    def test_custom_tolerance(self):
        """Custom tolerance value"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.1, tolType='relative')

        r1 = Real(1.0, ctx)
        r2 = Real(1.05, ctx)  # Within 0.1 relative (5%)
        r3 = Real(1.15, ctx)  # Outside 0.1 relative (15%)

        assert r1 == r2
        assert r1 != r3

    def test_near_zero_handling(self):
        """zeroLevel threshold behavior"""
        ctx = Context('Numeric')
        # Default zeroLevel is 1e-14

        r1 = Real(1e-15, ctx)  # Below zeroLevel
        r2 = Real(0.0, ctx)

        # Near zero values should be considered equal to zero
        assert r1 == r2

    def test_tolerance_in_comparison(self):
        """Real equality uses context tolerance"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.0001, tolType='relative')

        r1 = Real(100.0)
        r2 = Real(100.005)  # 0.005% difference, within 0.0001 relative

        assert r1 == r2

    def test_tolerance_in_formula_eval(self):
        """Tolerance affects formula evaluation comparisons"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.01)

        f = Formula('x**2', ['x'], ctx)
        result = f.eval(x=3)

        # Result should equal 9 within tolerance
        assert result == Real(9.0)
        assert result == Real(9.005)  # Within 1% relative

    def test_different_contexts_different_tolerances(self):
        """Different tolerance settings affect comparisons"""
        # Test with strict tolerance
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.001)

        r1 = Real(1.0, ctx)
        r2 = Real(1.05, ctx)  # 5% difference, > 0.1% tolerance

        assert r1 != r2

        # Change to loose tolerance
        ctx.flags.set(tolerance=0.1)

        r3 = Real(1.0, ctx)
        r4 = Real(1.05, ctx)  # 5% difference, < 10% tolerance

        assert r3 == r4

    def test_tolerance_persistence(self):
        """Tolerance persists across formula operations"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.01, tolType='relative')

        f1 = Formula('x', ['x'], ctx)
        f2 = Formula('2*x', ['x'], ctx)

        result1 = f1.eval(x=1.0)
        result2 = f2.eval(x=0.5)

        # Both should equal 1.0
        assert result1 == result2


class TestReduceFlags:
    """Test reduce flags."""

    def test_reduce_constants_default(self):
        """reduceConstants is on by default"""
        ctx = Context('Numeric')
        assert ctx.flags.get('reduceConstants') == 1

    def test_reduce_constants_affects_simplification(self):
        """reduceConstants flag affects constant simplification"""
        ctx = Context('Numeric')

        # With reduceConstants on (default)
        f1 = Formula('2 + 3', ['x'], ctx)
        # Sympy will simplify this to 5
        assert '5' in str(f1) or float(f1.eval(x=0)) == 5

    def test_reduce_constants_off(self):
        """Turning off reduceConstants"""
        ctx = Context('Numeric')
        ctx.flags.set(reduceConstants=0)

        # Note: This may not affect sympy's automatic simplification
        # but the flag is available for custom code
        assert ctx.flags.get('reduceConstants') == 0

    def test_reduce_constant_functions_default(self):
        """reduceConstantFunctions is on by default"""
        ctx = Context('Numeric')
        assert ctx.flags.get('reduceConstantFunctions') == 1

    def test_formula_uses_reduce_flags(self):
        """Formula respects reduce flags"""
        ctx = Context('Numeric')

        # This is more of a documentation test - the flags exist
        # and can be checked by Formula/answer checking code
        f = Formula('sin(0)', ['x'], ctx)
        # Sympy may or may not simplify this
        # But the flag is available
        assert ctx.flags.get('reduceConstantFunctions') == 1


class TestSpecializedContextFlags:
    """Test flags in specialized contexts."""

    def test_limited_polynomial_flags(self):
        """LimitedPolynomial sets specific flags"""
        ctx = Context('LimitedPolynomial')
        assert ctx.flags.get('limitedPolynomial') is True
        assert ctx.flags.get('strictCoefficients') is False

    def test_limited_polynomial_strict_flags(self):
        """LimitedPolynomial-Strict sets strict flags"""
        ctx = Context('LimitedPolynomial-Strict')
        assert ctx.flags.get('limitedPolynomial') is True
        assert ctx.flags.get('strictCoefficients') is True
        assert ctx.flags.get('reduceConstants') == 0

    def test_polynomial_factors_flags(self):
        """PolynomialFactors sets specific flags"""
        ctx = Context('PolynomialFactors')
        assert ctx.flags.get('polynomialFactors') is True
        assert ctx.flags.get('strictPowers') is True
        assert ctx.flags.get('singleFactors') is False

    def test_polynomial_factors_strict_flags(self):
        """PolynomialFactors-Strict sets all strict flags"""
        ctx = Context('PolynomialFactors-Strict')
        assert ctx.flags.get('polynomialFactors') is True
        assert ctx.flags.get('strictCoefficients') is True
        assert ctx.flags.get('strictPowers') is True
        assert ctx.flags.get('singleFactors') is True
        assert ctx.flags.get('strictDivision') is True
        assert ctx.flags.get('singlePowers') is True

    def test_flags_not_leaked(self):
        """Flags don't affect other contexts"""
        ctx1 = Context('PolynomialFactors')
        ctx2 = Context('Numeric')

        # ctx1 has polynomialFactors flag
        assert ctx1.flags.get('polynomialFactors') is True

        # ctx2 should not
        assert ctx2.flags.get('polynomialFactors') is None

    def test_context_switch_flags(self):
        """Flags change when switching contexts"""
        ctx1 = Context('Numeric')
        assert ctx1.flags.get('limitedPolynomial') is None

        ctx2 = Context('LimitedPolynomial')
        assert ctx2.flags.get('limitedPolynomial') is True

        # Switch back
        ctx3 = Context('Numeric')
        assert ctx3.flags.get('limitedPolynomial') is None

    def test_custom_flag_persistence(self):
        """User-set flags persist"""
        ctx = Context('Numeric')
        ctx.flags.set(customFlag='test_value')

        assert ctx.flags.get('customFlag') == 'test_value'

        # Copy preserves custom flags
        ctx2 = ctx.copy()
        assert ctx2.flags.get('customFlag') == 'test_value'


class TestFlagInteractions:
    """Test interactions between different flags."""

    def test_tolerance_with_zero_level(self):
        """Tolerance and zeroLevel work together"""
        ctx = Context('Numeric')
        ctx.flags.set(zeroLevel=1e-10, tolerance=0.001)

        # Near zero (below zeroLevel)
        r1 = Real(1e-11, ctx)
        r2 = Real(0.0, ctx)
        assert r1 == r2

        # Not near zero
        r3 = Real(1.0, ctx)
        r4 = Real(1.001, ctx)
        assert r3 == r4  # Within relative tolerance

    def test_strict_mode_reduces_constants_off(self):
        """Strict modes turn off constant reduction"""
        ctx = Context('LimitedPolynomial-Strict')
        assert ctx.flags.get('reduceConstants') == 0

        ctx2 = Context('PolynomialFactors-Strict')
        assert ctx2.flags.get('reduceConstants') == 0

    def test_copying_preserves_all_flags(self):
        """Context.copy() preserves all flags"""
        ctx1 = Context('PolynomialFactors')
        ctx1.flags.set(
            tolerance=0.01,
            tolType='absolute',
            customFlag='value'
        )

        ctx2 = ctx1.copy()

        # All flags preserved
        assert ctx2.flags.get('polynomialFactors') is True
        assert ctx2.flags.get('tolerance') == 0.01
        assert ctx2.flags.get('tolType') == 'absolute'
        assert ctx2.flags.get('customFlag') == 'value'


class TestFlagValidation:
    """Test flag value validation and edge cases."""

    def test_tolerance_positive(self):
        """Tolerance should be positive"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.01)
        assert ctx.flags.get('tolerance') > 0

    def test_tol_type_values(self):
        """tolType accepts 'relative' or 'absolute'"""
        ctx = Context('Numeric')

        ctx.flags.set(tolType='relative')
        assert ctx.flags.get('tolType') == 'relative'

        ctx.flags.set(tolType='absolute')
        assert ctx.flags.get('tolType') == 'absolute'

    def test_zero_level_small(self):
        """zeroLevel should be very small"""
        ctx = Context('Numeric')
        assert ctx.flags.get('zeroLevel') < 1e-10

    def test_boolean_flags(self):
        """Boolean flags work correctly"""
        ctx = Context('LimitedPolynomial')

        # Can be True/False or 1/0
        ctx.flags.set(limitedPolynomial=True)
        assert ctx.flags.get('limitedPolynomial') is True

        ctx.flags.set(limitedPolynomial=1)
        assert ctx.flags.get('limitedPolynomial') == 1

    def test_flag_override(self):
        """Later set() calls override previous values"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.01)
        assert ctx.flags.get('tolerance') == 0.01

        ctx.flags.set(tolerance=0.001)
        assert ctx.flags.get('tolerance') == 0.001
