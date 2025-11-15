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

from pg.answer import AnswerResult
from pg.parser import Context

from .error_handler import PGError, format_execution_error, install_error_handlers
from .executor import PGEnvironment, PGExecutor
from .grading import (
    ProblemGrader,
    process_checkbox_radio_input,
    std_problem_grader,
    stringify_answers,
)
from .post_processor import ContentPostProcessor
# Use the structured Pygments/Lark preprocessor by default.
# The legacy regex-based preprocessor remains available via
# pg_translator.LegacyPGPreprocessor if needed.
from .pg_preprocessor_pygment import PGPreprocessor


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
        self.post_processor = ContentPostProcessor()

        # Macros are now imported via preprocessor - no runtime loading needed

    def translate(
        self,
        pg_file_path: str | Path,
        seed: int,
        inputs: dict[str, Any] | None = None,
        context: Context | None = None,
        problem_state: dict[str, Any] | None = None,
        grader: ProblemGrader | None = None,
    ) -> ProblemResult:
        """
        Translate a PG file to a renderable problem.

        Args:
            pg_file_path: Path to .pg file
            seed: Random seed for problem generation
            inputs: Student answer inputs (for checking)
            context: Mathematical context
            problem_state: Current problem state (optional)
            grader: Custom grader override

        Returns:
            ProblemResult with statement, answers, solutions, etc.
        """
        pg_path = Path(pg_file_path)

        if not pg_path.exists():
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[f"File not found: {pg_path}"],
            )

        try:
            pg_source = pg_path.read_text(encoding="utf-8")
        except Exception as error:
            error_msg = format_execution_error(error, "", None)
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[error_msg],
            )

        return self.translate_source(
            pg_source,
            seed,
            inputs=inputs,
            context=context,
            problem_state=problem_state,
            grader=grader,
            filename=str(pg_path),
        )

    def translate_source(
        self,
        pg_source: str,
        seed: int,
        inputs: dict[str, Any] | None = None,
        context: Context | None = None,
        problem_state: dict[str, Any] | None = None,
        grader: ProblemGrader | None = None,
        filename: str | None = None,
    ) -> ProblemResult:
        """
        Translate PG source code directly (without file).

        Args:
            pg_source: PG source code
            seed: Random seed
            inputs: Student answer inputs
            context: Mathematical context
            problem_state: Current problem state
            grader: Problem grader override
            filename: Optional filename for metadata

        Returns:
            ProblemResult
        """
        active_grader = grader or self.grader
        state = (
            dict(problem_state)
            if problem_state is not None
            else {
                "recorded_score": 0,
                "num_of_correct_ans": 0,
                "num_of_incorrect_ans": 0,
            }
        )
        environment: PGEnvironment | None = None
        errors: list[str] = []

        # Auto-wrap bare PG snippets with DOCUMENT/ENDDOCUMENT so the core
        # macros have a valid environment during testing.
        if "DOCUMENT" not in pg_source:
            pg_source = f"DOCUMENT()\n{pg_source}\nENDDOCUMENT()\n"

        try:
            preprocess_result = self.preprocessor.preprocess(pg_source)

            environment = self.executor.execute(
                preprocess_result.code,
                seed=seed,
                context=context,
            )
            install_error_handlers(environment)

            statement_html = environment.render_text()
            solution_html = environment.render_solution()
            hint_html = environment.render_hint()
            header_html = getattr(environment, "render_header", lambda: "")()

            normalized_answers = self._normalize_answers(environment.answers)
            environment.answers = normalized_answers

            answer_results: dict[str, AnswerResult] | None = None
            problem_result_dict: dict[str, Any] | None = None

            if inputs:
                answer_results = self._evaluate_answers(environment, inputs)
                problem_result_dict, state = active_grader(
                    answer_results,
                    state,
                    answers_submitted=True,
                )
                stringify_answers(answer_results)
            else:
                problem_result_dict = {
                    "score": 0,
                    "errors": "",
                    "type": "not_submitted",
                    "msg": "",
                }

            per_answer_average: float | None = None
            if answer_results:
                per_answer_scores = [res.score for res in answer_results.values()]
                if per_answer_scores:
                    per_answer_average = sum(per_answer_scores) / len(per_answer_scores)
                else:
                    per_answer_average = 0.0

            display_mode = getattr(environment, "display_mode", "HTML")
            if self.post_processor.processors:
                statement_html, header_html = self.post_processor.process(
                    statement_html,
                    header_html,
                    display_mode,
                    problem_result_dict,
                )

            answer_blanks = {
                name: {"evaluator": evaluator}
                for name, evaluator in environment.answers.items()
            }

            if getattr(environment, "errors", None):
                errors.append(str(environment.errors))

            warnings: list[str] | None = None
            warning_tracker = getattr(environment, "_warning_tracker", None)
            if warning_tracker:
                has_debug = getattr(environment, "view_problem_debugging_info", False)
                warning_text = warning_tracker.get_formatted_warnings(has_debug)
                if warning_text:
                    warnings = [warning_text]

            metadata = {
                "seed": seed,
                "num_answers": len(environment.answers),
                "display_mode": display_mode,
            }
            if filename:
                metadata["source_file"] = filename

            score: float | None = None
            if problem_result_dict:
                grader_type = problem_result_dict.get("type")
                if grader_type and grader_type != "std_problem_grader":
                    score = problem_result_dict.get("score")
                elif per_answer_average is not None:
                    score = per_answer_average
                else:
                    score = problem_result_dict.get("score")
            else:
                score = per_answer_average

            return ProblemResult(
                statement_html=statement_html,
                header_html=header_html,
                answer_blanks=answer_blanks,
                solution_html=solution_html,
                hint_html=hint_html,
                answer_results=answer_results,
                score=score,
                problem_result=problem_result_dict,
                problem_state=state,
                metadata=metadata,
                errors=errors if errors else None,
                warnings=warnings,
            )

        except PGError as error:
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[str(error)],
            )
        except Exception as error:
            error_msg = format_execution_error(error, pg_source, environment)
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[error_msg],
            )

    def _evaluate_answers(
        self,
        environment: PGEnvironment,
        raw_inputs: dict[str, Any],
    ) -> dict[str, AnswerResult]:
        """
        Evaluate student answers, handling checkbox/radio inputs and MultiAnswer groups.
        """
        processed_inputs = {
            name: process_checkbox_radio_input(value)
            for name, value in raw_inputs.items()
        }

        answer_results: dict[str, AnswerResult] = {}
        evaluator_groups: dict[int, list[tuple[str, Any]]] = {}
        evaluator_map: dict[int, Any] = {}

        for name, student_answer in processed_inputs.items():
            if name not in environment.answers:
                continue

            ans_entry = environment.answers[name]
            evaluator = (
                ans_entry["ans_eval"]
                if isinstance(ans_entry, dict) and "ans_eval" in ans_entry
                else ans_entry
            )

            eval_id = id(evaluator)
            evaluator_groups.setdefault(eval_id, []).append((name, student_answer))
            evaluator_map[eval_id] = evaluator

        for eval_id, group_items in evaluator_groups.items():
            evaluator = evaluator_map[eval_id]

            if len(group_items) > 1 and hasattr(evaluator, "cmp"):
                checker = evaluator.cmp()
                if hasattr(checker, "check"):
                    student_answers = [ans for _, ans in group_items]
                    check_result = checker.check(*student_answers)

                    if "results" in check_result and isinstance(check_result["results"], list):
                        answers = getattr(evaluator, "answers", [])
                        for index, (name, student_answer) in enumerate(group_items):
                            individual_score = (
                                check_result["results"][index]
                                if index < len(check_result["results"])
                                else 0.0
                            )
                            correct_answer = ""
                            if isinstance(answers, list) and index < len(answers):
                                correct_answer = str(answers[index])

                            answer_results[name] = AnswerResult(
                                score=individual_score,
                                correct=individual_score >= 1.0,
                                student_answer=student_answer,
                                answer_message=check_result.get("message", ""),
                                correct_answer=correct_answer,
                            )
                    else:
                        for name, student_answer in group_items:
                            answer_results[name] = AnswerResult(
                                score=check_result.get("score", 0.0),
                                correct=check_result.get("correct", False),
                                student_answer=student_answer,
                                answer_message=check_result.get("message", ""),
                                correct_answer=str(evaluator),
                            )
                elif hasattr(checker, "evaluate"):
                    # MultiAnswer uses .evaluate() instead of .check()
                    # Call evaluate with all student answers
                    student_answers = [ans for _, ans in group_items]
                    try:
                        eval_result = checker.evaluate(*student_answers)
                    except Exception as e:
                        # Log error and create error results
                        error_msg = f"Error evaluating MultiAnswer: {str(e)}"
                        for name, student_answer in group_items:
                            answer_results[name] = AnswerResult(
                                score=0.0,
                                correct=False,
                                student_answer=student_answer,
                                answer_message=error_msg,
                                correct_answer=str(evaluator),
                            )
                        continue
                    
                    # Handle None result (evaluator not implemented properly)
                    if eval_result is None:
                        for name, student_answer in group_items:
                            answer_results[name] = AnswerResult(
                                score=0.0,
                                correct=False,
                                student_answer=student_answer,
                                answer_message="MultiAnswer evaluator returned None",
                                correct_answer=str(evaluator),
                            )
                        continue
                    
                    # If evaluate returns an AnswerResult, extract the score and info
                    if hasattr(eval_result, "score"):
                        # Single result for all answers
                        score = eval_result.score
                        message = getattr(eval_result, "answer_message", "")
                        for name, student_answer in group_items:
                            answer_results[name] = AnswerResult(
                                score=score,
                                correct=score >= 1.0,
                                student_answer=student_answer,
                                answer_message=message,
                                correct_answer=str(evaluator),
                            )
                    elif isinstance(eval_result, dict):
                        # Dictionary with individual results
                        if "results" in eval_result and isinstance(eval_result["results"], list):
                            answers = getattr(evaluator, "answers", [])
                            for index, (name, student_answer) in enumerate(group_items):
                                individual_score = (
                                    eval_result["results"][index]
                                    if index < len(eval_result["results"])
                                    else 0.0
                                )
                                correct_answer = ""
                                if isinstance(answers, list) and index < len(answers):
                                    correct_answer = str(answers[index])
                                
                                answer_results[name] = AnswerResult(
                                    score=individual_score,
                                    correct=individual_score >= 1.0,
                                    student_answer=student_answer,
                                    answer_message=eval_result.get("message", ""),
                                    correct_answer=correct_answer,
                                )
                        else:
                            # Single score for all
                            score = eval_result.get("score", 0.0)
                            for name, student_answer in group_items:
                                answer_results[name] = AnswerResult(
                                    score=score,
                                    correct=score >= 1.0,
                                    student_answer=student_answer,
                                    answer_message=eval_result.get("message", ""),
                                    correct_answer=str(evaluator),
                                )
                continue

            for name, student_answer in group_items:
                if hasattr(evaluator, "check") and not hasattr(evaluator, "cmp"):
                    check_result = evaluator.check(student_answer)
                    answer_results[name] = AnswerResult(
                        score=check_result.get("score", 0.0),
                        correct=check_result.get("correct", False),
                        student_answer=student_answer,
                        answer_message=check_result.get("message", ""),
                        correct_answer=check_result.get(
                            "correct_answer",
                            str(evaluator),
                        ),
                    )
                elif hasattr(evaluator, "compare") and callable(evaluator.compare):
                    # MathObject types (List, Point, Vector, Matrix, etc.) use .compare() method
                    try:
                        evaluator_type = type(evaluator).__name__
                        evaluator_str = str(evaluator).strip()
                        student_str = student_answer.strip()
                        
                        # Try to parse student answer and create MathObject for proper comparison
                        student_obj = None
                        is_correct = False
                        
                        if evaluator_type == "Matrix":
                            # Matrix format: [[1, 2, 3], [4, 5, 6]]
                            import ast
                            try:
                                parsed = ast.literal_eval(student_str)
                                from pg.math.geometric import Matrix
                                student_obj = Matrix(parsed)
                                # compare() returns bool (True if equal)
                                is_correct = evaluator.compare(student_obj)
                            except (ValueError, SyntaxError, TypeError) as e:
                                # Fall back to string comparison
                                is_correct = (evaluator_str == student_str)
                        elif evaluator_type == "List":
                            # List format: "a, b, c" (without brackets)
                            # Remove brackets from evaluator string representation
                            eval_str = evaluator_str
                            if eval_str.startswith('[') and eval_str.endswith(']'):
                                eval_str = eval_str[1:-1].strip()
                            is_correct = (eval_str == student_str)
                        else:
                            # For other types (Point, Vector, etc.), try string comparison
                            # TODO: Add proper parsing for Point/Vector types
                            is_correct = (evaluator_str == student_str)
                        
                        answer_results[name] = AnswerResult(
                            score=1.0 if is_correct else 0.0,
                            correct=is_correct,
                            student_answer=student_answer,
                            answer_message="" if is_correct else "Incorrect",
                            correct_answer=evaluator_str,
                        )
                    except Exception as e:
                        answer_results[name] = AnswerResult(
                            score=0.0,
                            correct=False,
                            student_answer=student_answer,
                            answer_message=f"Error comparing answer: {str(e)}",
                            correct_answer=str(evaluator),
                        )
                elif hasattr(evaluator, "cmp"):
                    checker = evaluator.cmp()
                    if hasattr(checker, "check"):
                        check_result = checker.check(student_answer)
                        answer_results[name] = AnswerResult(
                            score=check_result.get("score", 0.0),
                            correct=check_result.get("correct", False),
                            student_answer=student_answer,
                            answer_message=check_result.get("message", ""),
                            correct_answer=str(evaluator)
                            if hasattr(evaluator, "__str__")
                            else "",
                        )
                    elif callable(checker):
                        # PopUp/DropDown/RadioButtons return a callable lambda
                        check_result = checker(student_answer)
                        if isinstance(check_result, dict):
                            answer_results[name] = AnswerResult(
                                score=check_result.get("score", 0.0),
                                correct=check_result.get("correct", False),
                                student_answer=student_answer,
                                answer_message=check_result.get("message", ""),
                                correct_answer=str(evaluator)
                                if hasattr(evaluator, "__str__")
                                else "",
                            )
                elif hasattr(evaluator, "evaluate"):
                    result = evaluator.evaluate(student_answer)
                    answer_results[name] = result

        return answer_results

    def _normalize_answers(
        self,
        answers: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize answer registry, applying aliases from ANS label arguments.
        """
        normalized: dict[str, Any] = {}
        last_key: str | None = None
        pending_alias: str | None = None

        for name, entry in answers.items():
            evaluator = (
                entry["ans_eval"]
                if isinstance(entry, dict) and "ans_eval" in entry
                else entry
            )

            if isinstance(evaluator, str):
                alias = evaluator.strip()
                if not alias:
                    continue
                if last_key is not None and last_key in normalized:
                    normalized[alias] = normalized.pop(last_key)
                    last_key = alias
                else:
                    pending_alias = alias
                continue

            target_name = pending_alias or name
            pending_alias = None
            normalized[target_name] = entry
            last_key = target_name

        return normalized
