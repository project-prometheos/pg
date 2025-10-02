"""Deterministic RNG wrapper enforcing injected randomness."""
from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Any


@dataclass(slots=True)
class RNG:
    """Small wrapper that exposes an explicit deterministic random source."""

    seed: int
    _random: Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._random = Random(self.seed)

    def randint(self, a: int, b: int) -> int:
        """Return a uniformly distributed integer."""

        return self._random.randint(a, b)

    def choice(self, seq: list[Any]) -> Any:
        """Return a deterministic choice from a sequence."""

        return self._random.choice(seq)

    def sample(self, population: list[Any], k: int) -> list[Any]:
        """Return a deterministic sample from a population."""

        return self._random.sample(population, k)
