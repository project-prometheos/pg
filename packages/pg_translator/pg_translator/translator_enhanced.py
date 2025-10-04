"""
Enhanced PG Translator with full feature set.

This extends the base translator with:
- Macro loading
- Error handling
- Answer processing with checkbox/radio support
- Problem grading with partial credit
- Post-processing hooks
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pg_answer import AnswerResult
from pg_parser import Context

from .error_handler import PGError, format_execution_error, install_error_handlers
from .grading import (
    ProblemGrader,
    process_checkbox_radio_input,
    std_problem_grader,
    stringify_answers,
)
from .macro_loader import MacroLoader
from .post_processor import ContentPostProcessor
from .preprocessor import PGPreprocessor
from .translator import PGTranslator, ProblemResult


class EnhancedPGTranslator(PGTranslator):
    """
    Enhanced translator with complete Translator.pm feature parity.

    Adds:
    - Comprehensive error handling
    - Checkbox/radio button processing
    - Problem grading with state tracking
    - Post-processing hooks
    - Macro loading
    """

    def translate(
        self,
        pg_file_path: str | Path,
        seed: int,
        inputs: dict[str, str] | None = None,
        context: Context | None = None,
        problem_state: dict[str, Any] | None = None,
        grader: ProblemGrader | None = None,
    ) -> ProblemResult:
        """
        Translate PG file with full feature set.

        Args:
            pg_file_path: Path to .pg file
            seed: Random seed
            inputs: Student answer inputs
            context: Mathematical context
            problem_state: Current problem state
            grader: Custom grader (uses instance grader if None)

        Returns:
            Enhanced ProblemResult
        """
        # Use provided grader or instance grader
        active_grader = grader or self.grader

        # Initialize problem state
        if problem_state is None:
            problem_state = {
                "recorded_score": 0,
                "num_of_correct_ans": 0,
                "num_of_incorrect_ans": 0,
            }

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

            # 2. Translate source with full processing
            return self.translate_source(
                pg_source,
                seed,
                inputs,
                context,
                problem_state,
                active_grader,
                filename=str(pg_file_path),
            )

        except Exception as e:
            error_msg = format_execution_error(e, "", None)
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[error_msg],
            )

    def translate_source(
        self,
        pg_source: str,
        seed: int,
        inputs: dict[str, str] | None = None,
        context: Context | None = None,
        problem_state: dict[str, Any] | None = None,
        grader: ProblemGrader | None = None,
        filename: str | None = None,
    ) -> ProblemResult:
        """
        Translate PG source with full processing.

        Args:
            pg_source: PG source code
            seed: Random seed
            inputs: Student answer inputs
            context: Mathematical context
            problem_state: Problem state
            grader: Problem grader
            filename: Source filename (for error messages)

        Returns:
            Enhanced ProblemResult
        """
        # Use provided grader or instance grader
        active_grader = grader or self.grader

        # Initialize problem state
        if problem_state is None:
            problem_state = {
                "recorded_score": 0,
                "num_of_correct_ans": 0,
                "num_of_incorrect_ans": 0,
            }

        try:
            # 1. Preprocess
            preprocess_result = self.preprocessor.preprocess(pg_source)

            # 2. Execute with error handling
            try:
                env = self.executor.execute(
                    preprocess_result.code,
                    seed=seed,
                    context=context,
                )

                # Install error handlers
                warning_handler, error_handler = install_error_handlers(env)

            except Exception as e:
                error_msg = format_execution_error(e, pg_source, None)
                return ProblemResult(
                    statement_html="",
                    answer_blanks={},
                    errors=[error_msg],
                )

            # 3. Process answers (if inputs provided)
            answer_results: dict[str, AnswerResult] | None = None
            problem_result_dict: dict[str, Any] | None = None

            if inputs:
                answer_results = self._process_answers(env, inputs)

                # 4. Grade problem
                problem_result_dict, problem_state = active_grader(
                    answer_results,
                    problem_state,
                    answers_submitted=True,
                )

                # 5. Stringify answers for serialization
                stringify_answers(answer_results)
            else:
                # No inputs, just initialize result
                problem_result_dict = {
                    "score": 0,
                    "errors": "",
                    "type": "not_submitted",
                    "msg": "",
                }

            # 6. Render content
            statement_html = env.render_text()
            solution_html = env.render_solution()
            hint_html = env.render_hint()
            header_html = getattr(env, "render_header", lambda: "")()

            # 7. Post-process content
            display_mode = getattr(env, "display_mode", "HTML")

            if self.post_processor.processors:
                statement_html, header_html = self.post_processor.process(
                    statement_html,
                    header_html,
                    display_mode,
                    problem_result_dict,
                )

            # 8. Collect answer blanks
            answer_blanks = {
                name: {"evaluator": evaluator}
                for name, evaluator in env.answers.items()
            }

            # 9. Get warnings
            warnings = []
            if hasattr(env, "_warning_tracker"):
                has_debug = getattr(env, "view_problem_debugging_info", False)
                warning_text = env._warning_tracker.get_formatted_warnings(has_debug)  # type: ignore
                if warning_text:
                    warnings.append(warning_text)

            # 10. Build result
            return ProblemResult(
                statement_html=statement_html,
                header_html=header_html,
                answer_blanks=answer_blanks,
                solution_html=solution_html,
                hint_html=hint_html,
                answer_results=answer_results,
                score=problem_result_dict.get("score") if problem_result_dict else None,
                problem_result=problem_result_dict,
                problem_state=problem_state,
                metadata={
                    "seed": seed,
                    "num_answers": len(env.answers),
                    "display_mode": display_mode,
                },
                warnings=warnings if warnings else None,
            )

        except PGError as e:
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[str(e)],
            )
        except Exception as e:
            error_msg = format_execution_error(e, pg_source, None)
            return ProblemResult(
                statement_html="",
                answer_blanks={},
                errors=[error_msg],
            )

    def _process_answers(
        self,
        env: Any,
        inputs: dict[str, str]
    ) -> dict[str, AnswerResult]:
        """
        Process student answers with checkbox/radio support.

        Args:
            env: PG environment
            inputs: Raw student inputs

        Returns:
            Evaluated answer results
        """
        answer_results = {}

        for ans_name, evaluator in env.answers.items():
            if ans_name in inputs:
                # Get student response
                student_response = inputs[ans_name]

                # Process checkbox/radio format
                student_response = process_checkbox_radio_input(student_response)

                # Evaluate
                try:
                    result = evaluator.evaluate(student_response)
                    answer_results[ans_name] = result
                except Exception as e:
                    # Create error result
                    answer_results[ans_name] = AnswerResult(
                        score=0,
                        correct=False,
                        student_answer=str(student_response),
                        correct_answer="",
                        ans_message=f"Error evaluating answer: {e}",
                    )

        return answer_results
