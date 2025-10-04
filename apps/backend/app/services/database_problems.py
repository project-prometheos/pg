"""Enhanced problem service that loads from database."""
from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, create_session_factory

from app.models.database import Problem, create_database_engine
from app.services.problems import ProblemService, ProblemNotFoundError
from app.schemas.problem import ProblemResponse, InputSpec


class DatabaseProblemService(ProblemService):
    """Problem service that loads problems from SQLite database."""

    def __init__(self, database_url: str = "sqlite:///problems.db"):
        self.engine = create_database_engine(database_url)
        self.SessionLocal = create_session_factory(self.engine)

        # Fallback to original registry-based service
        from problemkit.registry import ProblemRegistry
        self.fallback_registry = ProblemRegistry.default()

    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    def generate_problem(self, problem_id: str, seed: int) -> ProblemResponse:
        """Generate problem from database or fallback to registry."""
        try:
            # Try to load from database first
            return self._load_from_database(problem_id, seed)
        except ProblemNotFoundError:
            # Fallback to original registry
            return self._load_from_registry(problem_id, seed)

    def _load_from_database(self, problem_id: str, seed: int) -> ProblemResponse:
        """Load problem from database."""
        with self.get_session() as session:
            problem = session.query(Problem).filter(
                Problem.id == problem_id).first()

            if not problem:
                raise ProblemNotFoundError(
                    f"Problem '{problem_id}' not found in database")

            # Parse PG source to extract inputs and answers
            inputs, answers = self._parse_pg_source(problem.pg_source, seed)

            # Generate statement and solution from PG source
            statement_tex = self._extract_statement(problem.pg_source)
            solution_tex = self._extract_solution(problem.pg_source)

            return ProblemResponse(
                variant_id=f"{problem_id}:{seed}",
                problem_id=problem_id,
                seed=seed,
                statement_tex=statement_tex,
                inputs=inputs,
                solution_tex=solution_tex,
                meta={
                    "source": "database",
                    "file_path": problem.file_path,
                    "name": problem.name,
                    "description": problem.description,
                    "types": [pt.type for pt in problem.types],
                    "subjects": [ps.subject for ps in problem.subjects],
                    "categories": [pc.category for pc in problem.categories],
                    "keywords": [pk.keyword for pk in problem.keywords],
                    "macros": [pm.macro for pm in problem.macros]
                }
            )

    def _load_from_registry(self, problem_id: str, seed: int) -> ProblemResponse:
        """Fallback to original registry-based loading."""
        problem = self.fallback_registry.get(problem_id)
        if problem is None:
            raise ProblemNotFoundError(f"Unknown problem id '{problem_id}'")

        instance = problem(seed=seed)
        return ProblemResponse(
            variant_id=self.fallback_registry.variant_id(problem_id, seed),
            problem_id=problem_id,
            seed=seed,
            statement_tex=instance.statement_tex,
            inputs=[InputSpec.model_validate(
                i.model_dump()) for i in instance.inputs],
            solution_tex=instance.solution_tex,
            meta=instance.meta,
        )

    def _parse_pg_source(self, pg_source: str, seed: int) -> tuple[list[InputSpec], dict]:
        """Parse PG source to extract inputs and answers."""
        # This is a simplified parser - in production you'd want a more robust solution
        import re

        inputs = []
        answers = {}

        # Find answer blanks in PGML
        answer_pattern = r'\[_\]\{([^}]+)\}'
        answer_matches = re.findall(answer_pattern, pg_source)

        for i, answer_expr in enumerate(answer_matches):
            # Extract answer expression (simplified)
            answer_name = f"ans{i+1}"

            # Create input spec
            inputs.append(InputSpec(
                name=answer_name,
                type="math",
                label=f"Answer {i+1}"
            ))

            # Store answer (this would need proper evaluation in production)
            answers[answer_name] = answer_expr

        return inputs, answers

    def _extract_statement(self, pg_source: str) -> str:
        """Extract problem statement from PG source."""
        import re

        # Look for BEGIN_PGML ... END_PGML blocks
        pattern = r'BEGIN_PGML\s*\n(.*?)\nEND_PGML'
        match = re.search(pattern, pg_source, re.DOTALL)

        if match:
            statement = match.group(1).strip()
            # Convert PGML to LaTeX (simplified)
            statement = self._pgml_to_latex(statement)
            return statement

        return "Problem statement not found"

    def _extract_solution(self, pg_source: str) -> str:
        """Extract solution from PG source."""
        import re

        # Look for BEGIN_PGML_SOLUTION ... END_PGML_SOLUTION blocks
        pattern = r'BEGIN_PGML_SOLUTION\s*\n(.*?)\nEND_PGML_SOLUTION'
        match = re.search(pattern, pg_source, re.DOTALL)

        if match:
            solution = match.group(1).strip()
            # Convert PGML to LaTeX (simplified)
            solution = self._pgml_to_latex(solution)
            return solution

        return "Solution not found"

    def _pgml_to_latex(self, pgml_text: str) -> str:
        """Convert PGML to LaTeX/Markdown (simplified conversion)."""
        import re

        # PGML uses \(...\) for inline math and \[...\] for display math
        # Convert PGML inline math \(...\) to $ ... $
        pgml_text = re.sub(r'\\\((.*?)\\\)', r'$\1$',
                           pgml_text, flags=re.DOTALL)

        # Convert PGML display math \[...\] to $$ ... $$
        pgml_text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$',
                           pgml_text, flags=re.DOTALL)

        # Convert backtick math [` ... `] to $ ... $
        pgml_text = re.sub(r'\[`([^`]+)`\]', r'$\1$', pgml_text)

        # Convert code-fenced math [``` ... ```] to display math
        pgml_text = re.sub(r'\[```(.*?)```\]', r'$$\1$$',
                           pgml_text, flags=re.DOTALL)

        # Convert answer blanks [_]{...} to input placeholders
        pgml_text = re.sub(r'\[_\]\{[^}]+\}', r'[____]', pgml_text)

        # Convert bold **text** (already markdown-compatible)
        # Convert italics *text* (already markdown-compatible)

        # Don't convert line breaks to \\ - keep normal newlines for markdown

        return pgml_text

    def list_available_problems(self) -> list[dict]:
        """List all available problems from database."""
        with self.get_session() as session:
            problems = session.query(Problem).all()

            result = []
            for problem in problems:
                result.append({
                    "id": problem.id,
                    "name": problem.name,
                    "description": problem.description,
                    "file_path": problem.file_path,
                    "types": [pt.type for pt in problem.types],
                    "subjects": [ps.subject for ps in problem.subjects],
                    "categories": [pc.category for pc in problem.categories],
                    "keywords": [pk.keyword for pk in problem.keywords],
                    "macros": [pm.macro for pm in problem.macros],
                    "created_at": problem.created_at.isoformat(),
                    "updated_at": problem.updated_at.isoformat()
                })

            return result


# Global instance
_database_problem_service: Optional[DatabaseProblemService] = None


def get_database_problem_service() -> DatabaseProblemService:
    """Get global database problem service instance."""
    global _database_problem_service
    if _database_problem_service is None:
        _database_problem_service = DatabaseProblemService()
    return _database_problem_service


def generate_problem_from_database(problem_id: str, seed: int) -> ProblemResponse:
    """Convenience function for database problem generation."""
    service = get_database_problem_service()
    return service.generate_problem(problem_id, seed)
