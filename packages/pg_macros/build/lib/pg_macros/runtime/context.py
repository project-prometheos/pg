"""Context management helpers for PG macro runtime."""

from __future__ import annotations

from contextlib import contextmanager
from threading import local
from typing import Iterator

from pg_math.context import Context as BaseContext


_thread_state = local()


def _get_stack() -> list[BaseContext]:
    stack = getattr(_thread_state, 'context_stack', None)
    if stack is None:
        stack = [BaseContext('Numeric')]
        _thread_state.context_stack = stack
    return stack


def Context(name: str = 'Numeric', **flags) -> BaseContext:
    """Return a context instance mirroring Perl Context() API."""
    ctx = BaseContext(name if name else 'Numeric')
    if flags:
        ctx.flags.update(flags)
    return ctx


def get_context() -> BaseContext:
    """Get the current active context."""
    return _get_stack()[-1]


def set_context(ctx: BaseContext | str) -> BaseContext:
    """Set the active context, returning the resolved object."""
    if isinstance(ctx, str):
        ctx = Context(ctx)
    stack = _get_stack()
    stack[-1] = ctx
    return ctx


def push_context(ctx: BaseContext | str) -> BaseContext:
    """Push a context onto the runtime stack."""
    if isinstance(ctx, str):
        ctx = Context(ctx)
    stack = _get_stack()
    stack.append(ctx)
    return ctx


def pop_context() -> BaseContext:
    """Pop the current context from the runtime stack."""
    stack = _get_stack()
    if len(stack) == 1:
        raise RuntimeError('Cannot pop the global Numeric context')
    return stack.pop()


@contextmanager
def using_context(ctx: BaseContext | str) -> Iterator[BaseContext]:
    """Context manager helper for temporarily switching context."""
    pushed = push_context(ctx)
    try:
        yield pushed
    finally:
        pop_context()


__all__ = [
    'Context',
    'get_context',
    'set_context',
    'push_context',
    'pop_context',
    'using_context',
]
