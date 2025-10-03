"""
PG Translator - Coordinate problem file translation pipeline.

Orchestrates:
1. Load .pg file
2. Preprocess (BEGIN_TEXT expansion, etc.)
3. Execute in sandbox
4. Render text (PGML → HTML)
5. Collect answers
6. Check answers (if inputs provided)

Reference: Translator.pm::translate() (lines 679-794)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pg_answer import AnswerResult, EvaluatorRegistry
from pg_parser import Context

from .executor import PGEnvironment, PGExecutor
from .preprocessor import PGPreprocessor


@dataclass
class ProblemResult:
    """
    Result of translating a PG problem.

    Contains all generated content and answer checking results.
    """

    statement_html: str
    """Problem statement HTML"""

    answer_blanks: dict[str, Any]
    """Answer blank information by name"""

    solution_html: str | None = None
    """Solution HTML (if available)"""

    hint_html: str | None = None
    """Hint HTML (if available)"""

    metadata: dict[str, Any] | None = None
    """Problem metadata"""

    answer_results: dict[str, AnswerResult] | None = None
    """Answer checking results (if inputs provided)"""

    score: float | None = None
    """Overall problem score (if answers checked)"""

    errors: list[str] | None = None
    """Execution errors"""


class PGTranslator:
    """
    Translate PG problem files to renderable problems.

    Coordinates the entire pipeline:
    - Preprocessing
    - Safe execution
    - Text rendering
    - Answer checking
    """

    def __init__(
        self,
        preprocessor: PGPreprocessor | None = None,
        executor: PGExecutor | None = None,
    ):
        """
        Initialize translator.

        Args:
            preprocessor: PG preprocessor (creates default if None)
            executor: PG executor (creates default if None)
        """
        self.preprocessor = preprocessor or PGPreprocessor()
        self.executor = executor or PGExecutor()

    def translate(
        self,
        pg_file_path: str | Path,
        seed: int,
        inputs: dict[str, str] | None = None,
        context: Context | None = None,
    ) -> ProblemResult:
        """
        Translate a PG file to a problem.

        Args:
            pg_file_path: Path to .pg file
            seed: Random seed for problem generation
            inputs: Student answer inputs (for checking)
            context: Mathematical context (defaults to Numeric)

        Returns:
            ProblemResult with statement, answers, solutions, etc.
        """
        errors: list[str] = []

        try:
            # 1. Load .pg file
            pg_file_path = Path(pg_file_path)
            if not pg_file_path.exists():
                return ProblemResult(
                    statement_html="",
                    answer_blanks={},
                    errors=[f"File not found: {pg_file_path}"],
                )

            pg_source = pg_file_path.read_text(encoding="utf-8")

            # 2. Preprocess
            preprocess_result = self.preprocessor.preprocess(pg_source)

            # 3. Execute in sandbox
            try:
                env = self.executor.execute(
                    preprocess_result.code,
                    seed=seed,
                    context=context,
                )
            except (SyntaxError, RuntimeError) as e:
                return ProblemResult(
                    statement_html="",
                    answer_blanks={},
                    errors=[f"Execution error: {e}"],
                )

            # 4. Render text
            statement_html = env.render_text()
            solution_html = env.render_solution()
            hint_html = env.render_hint()

            # 5. Collect answer blanks
            answer_blanks = {
                name: {"evaluator": evaluator}
                for name, evaluator in env.answers.items()
            }

            # 6. Check answers (if inputs provided)
            answer_results: dict[str, AnswerResult] | None = None
            score: float | None = None

            if inputs:
                answer_results = {}
                scores: list[float] = []

                for name, student_answer in inputs.items():
                    if name in env.answers:
                        evaluator = env.answers[name]
                        # Get correct answer from evaluator
                        correct_answer = getattr(evaluator, "correct_answer", "")
                        result = evaluator.evaluate(student_answer)
                        answer_results[name] = result
                        scores.append(result.score)

                # Calculate overall score (average)
                if scores:
                    score = sum(scores) / len(scores)

            # 7. Return result
            return ProblemResult(
                statement_html=statement_html,
                answer_blanks=answer_blanks,
                solution_html=solution_html,
                hint_html=hint_html,
                answer_results=answer_results,
                score=score,
                metadata={
                    "seed": seed,
                    "num_answers": len(env.answers),
                },
                errors=errors if errors else None,
            )

        except Exception as e:
            # Catch-all for unexpected errors
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[f"Unexpected error: {e}"],
            )

    def translate_source(
        self,
        pg_source: str,
        seed: int,
        inputs: dict[str, str] | None = None,
        context: Context | None = None,
    ) -> ProblemResult:
        """
        Translate PG source code directly (without file).

        Args:
            pg_source: PG source code
            seed: Random seed
            inputs: Student answer inputs
            context: Mathematical context

        Returns:
            ProblemResult
        """
        errors: list[str] = []

        try:
            # 1. Preprocess
            preprocess_result = self.preprocessor.preprocess(pg_source)

            # 2. Execute
            try:
                env = self.executor.execute(
                    preprocess_result.code,
                    seed=seed,
                    context=context,
                )
            except (SyntaxError, RuntimeError) as e:
                return ProblemResult(
                    statement_html="",
                    answer_blanks={},
                    errors=[f"Execution error: {e}"],
                )

            # 3. Render
            statement_html = env.render_text()
            solution_html = env.render_solution()
            hint_html = env.render_hint()

            # 4. Collect answers
            answer_blanks = {
                name: {"evaluator": evaluator}
                for name, evaluator in env.answers.items()
            }

            # 5. Check answers (if inputs provided)
            answer_results: dict[str, AnswerResult] | None = None
            score: float | None = None

            if inputs:
                answer_results = {}
                scores: list[float] = []

                for name, student_answer in inputs.items():
                    if name in env.answers:
                        evaluator = env.answers[name]
                        result = evaluator.evaluate(student_answer)
                        answer_results[name] = result
                        scores.append(result.score)

                if scores:
                    score = sum(scores) / len(scores)

            return ProblemResult(
                statement_html=statement_html,
                answer_blanks=answer_blanks,
                solution_html=solution_html,
                hint_html=hint_html,
                answer_results=answer_results,
                score=score,
                metadata={"seed": seed, "num_answers": len(env.answers)},
                errors=errors if errors else None,
            )

        except Exception as e:
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[f"Unexpected error: {e}"],
            )
