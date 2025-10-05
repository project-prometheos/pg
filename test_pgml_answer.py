"""Debug PGML answer blank registration."""

from pg_translator import PGTranslator
from pg_translator.executor import PGExecutor
from pg_translator.in_process_sandbox import InProcessSandbox

pg_code = """
DOCUMENT()
loadMacros("PG.pl")

from pg_answer import num_cmp

answer = 42

BEGIN_PGML
What is the meaning of life? [_]{num_cmp(answer)}
END_PGML

ENDDOCUMENT()
"""

sandbox = InProcessSandbox(timeout=10)
executor = PGExecutor()
executor.sandbox = sandbox
translator = PGTranslator(executor=executor)

result = translator.translate_source(pg_code, seed=1234)

print("Statement HTML:", repr(result.statement_html))
print("Answer blanks:", result.answer_blanks)
print("Errors:", result.errors)
print("Warnings:", result.warnings)
