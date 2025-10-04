"""Application service bridging HTTP requests with the domain problem kit."""
from __future__ import annotations

import re
from dataclasses import dataclass

from ..schemas.problem import InputSpec, ProblemResponse
from problemkit.registry import ProblemRegistry

_REGISTRY = ProblemRegistry.default()


class ProblemNotFoundError(KeyError):
    """Raised when the requested problem cannot be located in the registry."""


def _pgml_to_markdown(pgml_text: str) -> str:
    """
    Convert PGML to Markdown with math delimiters.

    PGML uses \(...\) for inline math and \[...\] for display math.
    We convert these to $ ... $ and $$ ... $$ for markdown/KaTeX rendering.
    """
    # Convert PGML inline math \(...\) to $ ... $
    pgml_text = re.sub(r'\\\((.*?)\\\)', r'$\1$', pgml_text, flags=re.DOTALL)

    # Convert PGML display math \[...\] to $$ ... $$
    pgml_text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', pgml_text, flags=re.DOTALL)

    # Convert backtick math [` ... `] to $ ... $
    pgml_text = re.sub(r'\[`([^`]+)`\]', r'$\1$', pgml_text)

    # Convert code-fenced math [``` ... ```] to display math
    pgml_text = re.sub(r'\[```(.*?)```\]', r'$$\1$$',
                       pgml_text, flags=re.DOTALL)

    # Convert answer blanks [_]{...} to [____]
    pgml_text = re.sub(r'\[_\]\{[^}]+\}', r'[____]', pgml_text)

    return pgml_text


@dataclass(slots=True)
class ProblemService:
    """High-level orchestration layer for building problem responses."""

    registry: ProblemRegistry

    def generate_problem(self, problem_id: str, seed: int) -> ProblemResponse:
        problem = self.registry.get(problem_id)
        if problem is None:
            raise ProblemNotFoundError(f"Unknown problem id '{problem_id}'")

        instance = problem(seed=seed)

        # Convert PGML to markdown-compatible format
        statement_tex = _pgml_to_markdown(instance.statement_tex)
        solution_tex = _pgml_to_markdown(instance.solution_tex)

        return ProblemResponse(
            variant_id=self.registry.variant_id(problem_id, seed),
            problem_id=problem_id,
            seed=seed,
            statement_tex=statement_tex,
            inputs=[InputSpec.model_validate(
                i.model_dump()) for i in instance.inputs],
            solution_tex=solution_tex,
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
