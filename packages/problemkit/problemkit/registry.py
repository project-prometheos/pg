"""In-memory registry mapping identifiers to problem factories."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping

from .decorators import ProblemGenerator


@dataclass(slots=True)
class ProblemRegistry:
    """Registry storing authored problem factories."""

    problems: Dict[str, ProblemGenerator] = field(default_factory=dict)

    @classmethod
    def default(cls) -> "ProblemRegistry":
        from .samples import calculus

        registry = cls()
        registry.register(calculus.product_rule)
        return registry

    def register(self, generator: ProblemGenerator) -> None:
        identifier = getattr(generator, "__problem_id__", generator.__name__)
        self.problems[identifier] = generator

    def get(self, problem_id: str) -> ProblemGenerator | None:
        return self.problems.get(problem_id)

    def all(self) -> Mapping[str, ProblemGenerator]:  # pragma: no cover - simple proxy
        return dict(self.problems)

    def variant_id(self, problem_id: str, seed: int) -> str:
        """Return a reversible variant identifier.

        The scaffold uses a plain ``problem_id:seed`` representation to keep the
        solution endpoint simple. Production systems can swap this strategy for a
        hashed identifier by introducing a persistence adapter.
        """

        return f"{problem_id}:{seed}"


__all__ = ["ProblemRegistry"]
