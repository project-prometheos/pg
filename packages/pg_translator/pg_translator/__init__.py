"""
pg_translator - PG problem file translator and executor

Executes .pg problem files safely, collecting problem text, answers, solutions, and hints.

Reference: lib/WeBWorK/PG/Translator.pm in legacy Perl codebase
"""

# Default to the structured Pygments/Lark preprocessor. The legacy
# regex-driven implementation is still available as LegacyPGPreprocessor
# if needed.
from .pg_preprocessor_pygment import PGPreprocessor, convert_pg_file
from .preprocessor import PGPreprocessor as LegacyPGPreprocessor
from .executor import PGExecutor, PGEnvironment
from .translator import PGTranslator, ProblemResult

__all__ = [
    "PGPreprocessor",
    "LegacyPGPreprocessor",
    "convert_pg_file",
    "PGExecutor",
    "PGEnvironment",
    "PGTranslator",
    "ProblemResult",
]
