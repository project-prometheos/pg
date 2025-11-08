"""Answer registration helpers bridging to PG core."""

from __future__ import annotations

from typing import Any

from pg_macros.core import pg_core


def queue_answer(*evaluators: Any) -> None:
    """Register implicit answers mirroring Perl ANS."""
    pg_core.ANS(*evaluators)


def register_named_answer(name: str, evaluator: Any) -> None:
    """Register explicitly labeled answer."""
    pg_core.NAMED_ANS(name, evaluator)


def record_answer_name(name: str, value: str = '') -> str:
    """Record answer label for later binding."""
    return pg_core.RECORD_ANS_NAME(name, value)


def record_implicit_answer_name(name: str) -> str:
    """Record implicit answer placeholder."""
    return pg_core.RECORD_IMPLICIT_ANS_NAME(name)


def new_answer_name() -> str:
    """Generate unique answer name."""
    return pg_core.NEW_ANS_NAME()


__all__ = [
    'queue_answer',
    'register_named_answer',
    'record_answer_name',
    'record_implicit_answer_name',
    'new_answer_name',
]
