"""Fraction context helpers mirroring contextFraction.pl."""

from __future__ import annotations

from typing import Any

from .runtime.context import Context, set_context


def _configure(name: str, **flags: Any):
    ctx = Context('Numeric')
    ctx.flags.set(
        allowDecimals=True,
        reduceFractions=True,
    )
    if flags:
        ctx.flags.set(**flags)
    ctx.flags.set(name=name)
    return set_context(ctx)


def contextFraction() -> object:
    return _configure(
        'Fraction',
        allowDecimals=True,
        reduceFractions=True,
        strictFractions=False,
        allowMixedNumbers=False,
        showMixedNumbers=False,
        requireProperFractions=False,
        studentsMustReduceFractions=False,
    )


def contextFractionNoDecimals() -> object:
    return _configure(
        'Fraction-NoDecimals',
        allowDecimals=False,
        reduceFractions=True,
        strictFractions=False,
        allowMixedNumbers=False,
        showMixedNumbers=False,
        requireProperFractions=False,
        studentsMustReduceFractions=False,
    )


def contextLimitedFraction() -> object:
    return _configure(
        'LimitedFraction',
        allowDecimals=False,
        reduceFractions=False,
        strictFractions=True,
        allowMixedNumbers=True,
        showMixedNumbers=True,
        requireProperFractions=False,
        studentsMustReduceFractions=True,
    )


def contextLimitedProperFraction() -> object:
    return _configure(
        'LimitedProperFraction',
        allowDecimals=False,
        reduceFractions=False,
        strictFractions=True,
        allowMixedNumbers=True,
        showMixedNumbers=True,
        requireProperFractions=True,
        studentsMustReduceFractions=True,
    )


def DisableDecimals() -> None:
    ctx = contextFraction()
    ctx.flags['allowDecimals'] = False


__exports__ = {
    'contextFraction': contextFraction,
    'contextFractionNoDecimals': contextFractionNoDecimals,
    'contextLimitedFraction': contextLimitedFraction,
    'contextLimitedProperFraction': contextLimitedProperFraction,
    'DisableDecimals': DisableDecimals,
}

__all__ = list(__exports__.keys())
