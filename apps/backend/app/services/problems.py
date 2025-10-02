"""Application service bridging HTTP requests with the domain problem kit."""
from __future__ import annotations

from dataclasses import dataclass

from ..schemas.problem import InputSpec, ProblemResponse
from problemkit.registry import ProblemRegistry

_REGISTRY = ProblemRegistry.default()


class ProblemNotFoundError(KeyError):
    """Raised when the requested problem cannot be located in the registry."""


@dataclass(slots=True)
class ProblemService:
    """High-level orchestration layer for building problem responses."""

    registry: ProblemRegistry

    def generate_problem(self, problem_id: str, seed: int) -> ProblemResponse:
        problem = self.registry.get(problem_id)
        if problem is None:
            raise ProblemNotFoundError(f"Unknown problem id '{problem_id}'")

        instance = problem(seed=seed)
        return ProblemResponse(
            variant_id=self.registry.variant_id(problem_id, seed),
            problem_id=problem_id,
            seed=seed,
            statement_tex=instance.statement_tex,
            inputs=[InputSpec.model_validate(i.model_dump()) for i in instance.inputs],
            solution_tex=instance.solution_tex,
            meta=instance.meta,
        )


def generate_problem(problem_id: str, seed: int) -> ProblemResponse:
    """Convenience function used by routers to avoid wiring dependencies yet."""

    service = ProblemService(registry=_REGISTRY)
    return service.generate_problem(problem_id=problem_id, seed=seed)


def registry_decode_variant(variant_id: str) -> tuple[str, int]:
    """Decode a reversible variant identifier into ``(problem_id, seed)``."""

    try:
        problem_id, seed_raw = variant_id.split(":", maxsplit=1)
        return problem_id, int(seed_raw)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError("Malformed variant identifier") from exc
