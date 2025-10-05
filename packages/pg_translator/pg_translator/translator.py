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

from .error_handler import PGError, format_execution_error, install_error_handlers
from .executor import PGEnvironment, PGExecutor
from .grading import (
    ProblemGrader,
    avg_problem_grader,
    process_checkbox_radio_input,
    std_problem_grader,
    stringify_answers,
)
from .macro_loader import MacroLoader
from .post_processor import ContentPostProcessor
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

    problem_result: dict[str, Any] | None = None
    """Grading result details"""

    problem_state: dict[str, Any] | None = None
    """Problem state (attempts, recorded score, etc.)"""

    header_html: str | None = None
    """Header HTML (CSS, JS, etc.)"""

    errors: list[str] | None = None
    """Execution errors"""

    warnings: list[str] | None = None
    """Warning messages"""


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
        grader: ProblemGrader | None = None,
    ):
        """
        Initialize translator.

        Args:
            preprocessor: PG preprocessor (creates default if None)
            executor: PG executor (creates default if None)
            grader: Problem grader (uses std_problem_grader if None)
        """
        self.preprocessor = preprocessor or PGPreprocessor()
        self.executor = executor or PGExecutor()
        self.grader = grader or std_problem_grader
        self.macro_loader = MacroLoader(self.executor.sandbox)
        self.post_processor = ContentPostProcessor()

        # Try to load core macros (if available)
        try:
            self.macro_loader.unrestricted_load("PG.pl")
        except:
            pass  # PG.pl not yet ported

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

            # Collect any execution errors from environment
            if env.errors:
                errors.append(env.errors)

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
                        # Extract evaluator from answer hash entry
                        ans_entry = env.answers[name]
                        if isinstance(ans_entry, dict) and "ans_eval" in ans_entry:
                            evaluator = ans_entry["ans_eval"]
                        else:
                            evaluator = ans_entry

                        # Check if it's a MathObject (Formula, Real, etc.) - need to call .cmp() first
                        if hasattr(evaluator, 'cmp'):
                            checker = evaluator.cmp()
                            # Now call check() method
                            if hasattr(checker, 'check'):
                                check_result = checker.check(student_answer)
                                # Convert dict to AnswerResult
                                result = AnswerResult(
                                    score=check_result.get('score', 0.0),
                                    correct=check_result.get('correct', False),
                                    student_answer=student_answer,
                                    answer_message=check_result.get(
                                        'message', ''),
                                    correct_answer=str(evaluator) if hasattr(
                                        evaluator, '__str__') else '',
                                )
                                answer_results[name] = result
                                scores.append(result.score)
                        elif hasattr(evaluator, 'check') and not hasattr(evaluator, 'cmp'):
                            # It's an AnswerChecker object (like FormulaAnswerChecker from .cmp() call)
                            check_result = evaluator.check(student_answer)
                            # Convert dict to AnswerResult
                            result = AnswerResult(
                                score=check_result.get('score', 0.0),
                                correct=check_result.get('correct', False),
                                student_answer=student_answer,
                                answer_message=check_result.get('message', ''),
                                correct_answer=check_result.get(
                                    'correct_answer', str(evaluator)),
                            )
                            answer_results[name] = result
                            scores.append(result.score)
                        elif hasattr(evaluator, 'evaluate'):
                            # It's already an answer checker - call evaluate directly
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

            # Collect any execution errors from environment
            if env.errors:
                errors.append(env.errors)

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

                # Group answer blanks by their evaluator (for MultiAnswer)
                # id(evaluator) -> [(name, student_answer), ...]
                evaluator_groups: dict[int, list[tuple[str, str]]] = {}
                # id(evaluator) -> evaluator
                evaluator_map: dict[int, Any] = {}

                for name, student_answer in inputs.items():
                    if name in env.answers:
                        # Extract evaluator from answer hash entry
                        ans_entry = env.answers[name]
                        if isinstance(ans_entry, dict) and "ans_eval" in ans_entry:
                            evaluator = ans_entry["ans_eval"]
                        else:
                            evaluator = ans_entry

                        # Group by evaluator object identity
                        eval_id = id(evaluator)
                        if eval_id not in evaluator_groups:
                            evaluator_groups[eval_id] = []
                            evaluator_map[eval_id] = evaluator
                        evaluator_groups[eval_id].append(
                            (name, student_answer))

                # Check each group
                for eval_id, group_items in evaluator_groups.items():
                    evaluator = evaluator_map[eval_id]

                    # Check if it's a MultiAnswer (multiple blanks with same evaluator)
                    if len(group_items) > 1 and hasattr(evaluator, 'cmp'):
                        # MultiAnswer case - check all answers together
                        checker = evaluator.cmp()
                        if hasattr(checker, 'check'):
                            # Extract student answers in order
                            student_answers = [ans for _, ans in group_items]

                            # Call check with all student answers
                            check_result = checker.check(*student_answers)

                            # MultiAnswer checker returns results for all blanks
                            if 'results' in check_result and isinstance(check_result['results'], list):
                                # Individual results for each blank
                                for i, (name, student_ans) in enumerate(group_items):
                                    individual_score = check_result['results'][i] if i < len(
                                        check_result['results']) else 0.0
                                    result = AnswerResult(
                                        score=individual_score,
                                        correct=individual_score >= 1.0,
                                        student_answer=student_ans,
                                        answer_message=check_result.get(
                                            'message', ''),
                                        correct_answer=str(evaluator.answers[i]) if hasattr(
                                            evaluator, 'answers') and i < len(evaluator.answers) else '',
                                    )
                                    answer_results[name] = result
                                    scores.append(individual_score)
                            else:
                                # Fallback: same result for all blanks
                                for name, student_ans in group_items:
                                    result = AnswerResult(
                                        score=check_result.get('score', 0.0),
                                        correct=check_result.get(
                                            'correct', False),
                                        student_answer=student_ans,
                                        answer_message=check_result.get(
                                            'message', ''),
                                        correct_answer=str(evaluator),
                                    )
                                    answer_results[name] = result
                                    scores.append(result.score)
                    else:
                        # Single answer or regular evaluator - check individually
                        for name, student_answer in group_items:
                            # Check if it's already a checker (has check method directly)
                            if hasattr(evaluator, 'check') and not hasattr(evaluator, 'cmp'):
                                # It's an AnswerChecker object (from .cmp() call)
                                check_result = evaluator.check(student_answer)
                                result = AnswerResult(
                                    score=check_result.get('score', 0.0),
                                    correct=check_result.get('correct', False),
                                    student_answer=student_answer,
                                    answer_message=check_result.get(
                                        'message', ''),
                                    correct_answer=check_result.get('correct_answer', str(
                                        evaluator)) if hasattr(evaluator, '__str__') else '',
                                )
                                answer_results[name] = result
                                scores.append(result.score)
                            # Check if it's a MathObject (Formula, Real, etc.) - need to call .cmp() first
                            elif hasattr(evaluator, 'cmp'):
                                checker = evaluator.cmp()
                                # Now call check() method
                                if hasattr(checker, 'check'):
                                    check_result = checker.check(
                                        student_answer)
                                    # Convert dict to AnswerResult
                                    result = AnswerResult(
                                        score=check_result.get('score', 0.0),
                                        correct=check_result.get(
                                            'correct', False),
                                        student_answer=student_answer,
                                        answer_message=check_result.get(
                                            'message', ''),
                                        correct_answer=str(evaluator) if hasattr(
                                            evaluator, '__str__') else '',
                                    )
                                    answer_results[name] = result
                                    scores.append(result.score)
                            elif hasattr(evaluator, 'evaluate'):
                                # It's already an answer checker - call evaluate directly
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
