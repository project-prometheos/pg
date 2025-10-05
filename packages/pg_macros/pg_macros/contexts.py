"""
Context-related macro stubs for PG problems.

Provides stub implementations for various context macros like:
- contextFraction.pl
- contextIntegerFunctions.pl
- contextLimitedPolynomial.pl
etc.
"""

from pg_math.context import Context as BaseContext


def Context(name: str = 'Numeric'):
    """
    Load or switch to a context.

    Common contexts:
    - 'Numeric' (default)
    - 'Fraction', 'Fraction-NoDecimals'
    - 'LimitedFraction', 'LimitedProperFraction'
    - 'Complex'
    - 'Point', 'Vector', 'Matrix'
    - 'Interval'
    - 'String'

    For now, most specialized contexts just return the base Numeric context
    with appropriate flags set.
    """
    # Get the base context
    ctx = BaseContext(name if name == 'Numeric' else 'Numeric')

    # Set context-specific flags
    if 'Fraction' in name:
        # Fraction contexts should not allow decimals
        if 'NoDecimals' in name:
            ctx.flags['allowDecimals'] = False
        ctx.flags['reduceFractions'] = True

        if 'Limited' in name:
            ctx.flags['strictFractions'] = True

        if 'Proper' in name:
            ctx.flags['requireProperFractions'] = True

    return ctx


# Export for macro loading
__all__ = ['Context']
