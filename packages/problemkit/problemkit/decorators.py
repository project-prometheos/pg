"""Problem authoring decorator providing metadata and deterministic seeding."""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Protocol

from .models import ProblemInstance
from .rng import RNG


class ProblemGenerator(Protocol):
    """Protocol describing the callable stored in the registry."""

    def __call__(self, *, seed: int) -> ProblemInstance:  # pragma: no cover - typing aid
        ...


def problem(*, id: str, vars: list[str], tags: list[str]) -> Callable[[Callable[..., ProblemInstance]], Callable[..., ProblemInstance]]:
    """Decorator used by authors to declare a deterministic problem factory."""

    def decorator(func: Callable[..., ProblemInstance]) -> Callable[..., ProblemInstance]:
        @wraps(func)
        def wrapper(*args: Any, seed: int, **kwargs: Any) -> ProblemInstance:
            rng = RNG(seed)
            return func(*args, seed=seed, rng=rng, **kwargs)

        setattr(wrapper, "__problem_id__", id)
        setattr(wrapper, "__problem_vars__", vars)
        setattr(wrapper, "__problem_tags__", tags)
        return wrapper

    return decorator
