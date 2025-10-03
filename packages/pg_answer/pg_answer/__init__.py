"""
pg_answer - Answer evaluation framework for WeBWorK PG problems

Provides pluggable answer checking system with:
- Type-specific evaluators
- Fuzzy comparison with tolerances
- Partial credit support
- Custom grading strategies

Reference: lib/AnswerHash.pm and lib/AnswerEvaluator.pm in legacy Perl codebase
"""

from .answer_hash import AnswerResult
from .evaluator import AnswerEvaluator, EvaluatorRegistry
from .graders import AverageGrader, Grader, StandardGrader

__all__ = [
    "AnswerResult",
    "AnswerEvaluator",
    "EvaluatorRegistry",
    "Grader",
    "StandardGrader",
    "AverageGrader",
]
