"""Debug OPL problem rendering."""

from pg_translator.preprocessor import PGPreprocessor
from pg_translator import PGTranslator
from pg_translator.executor import PGExecutor
from pg_translator.in_process_sandbox import InProcessSandbox
from pathlib import Path

pg_file = Path("webwork_ps1_pg/ps1-prob01.pg")

with open(pg_file) as f:
    pg_code = f.read()

print("Original code:")
print(pg_code)
print("\n" + "="*60 + "\n")

# Check preprocessor output
preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_code)

print("Preprocessed code:")
print(result.code)
print("\n" + "="*60 + "\n")

# Try to translate
sandbox = InProcessSandbox(timeout=10)
executor = PGExecutor()
executor.sandbox = sandbox
translator = PGTranslator(executor=executor)

result = translator.translate_source(pg_code, seed=1234)

print("Statement HTML:", repr(result.statement_html))
print("Errors:", result.errors)
print("Warnings:", result.warnings)
print("Answer blanks:", result.answer_blanks)
