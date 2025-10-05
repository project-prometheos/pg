"""Quick test of PGML functionality."""

from pg_translator import PGTranslator
from pg_translator.executor import PGExecutor
from pg_translator.in_process_sandbox import InProcessSandbox

pg_code = """
DOCUMENT()
loadMacros("PG.pl")

a = 5
b = 3

BEGIN_PGML
Add: [$a] + [$b]
END_PGML

ENDDOCUMENT()
"""

sandbox = InProcessSandbox(timeout=10)
executor = PGExecutor()
executor.sandbox = sandbox
translator = PGTranslator(executor=executor)

result = translator.translate_source(pg_code, seed=1234)

print("Statement HTML:", repr(result.statement_html))
print("Errors:", result.errors)
print("Warnings:", result.warnings)
