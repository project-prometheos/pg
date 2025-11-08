"""Reproducible RNG helpers mirroring Perl PG random behavior."""

from __future__ import annotations

import random
from typing import Optional

from pg_macros.core.pg_core import get_environment, PGEnvironment


_module_rng = random.Random(12345)


def _current_env() -> Optional[PGEnvironment]:
    try:
        return get_environment()
    except RuntimeError:
        return None


def get_rng() -> random.Random:
    """Return RNG tied to current PG environment or module-level fallback."""
    env = _current_env()
    if env is not None:
        return env.rng
    return _module_rng


def seed_rng(seed: int) -> int:
    """Seed the active RNG and return the applied seed."""
    rng = get_rng()
    rng.seed(seed)
    return seed


__all__ = ['get_rng', 'seed_rng']
