#!/usr/bin/env python3
"""Debug PGML translation."""

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))

from pg_translator import PGTranslator

# Test real PGML file
with open("webwork_ps1_pg/ps1-prob01.pg", "r", encoding="utf-8") as f:
    pg_code = f.read()

print("Input PG code:")
print(pg_code)
print("\n" + "="*60 + "\n")

translator = PGTranslator()

# Step 1: Preprocess
from pg_translator.preprocessor import PGPreprocessor
preprocessor = PGPreprocessor()
prep_result = preprocessor.preprocess(pg_code, use_sandbox_macros=True)

print("Preprocessed Python code:")
print(prep_result.code)
print("\n" + "="*60 + "\n")

# Step 2: Translate
# Save to temp file first (translator expects file path)
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.pg', delete=False, encoding='utf-8') as f:
    f.write(pg_code)
    temp_file = f.name

try:
    result = translator.translate(temp_file, seed=1234)
finally:
    Path(temp_file).unlink()

print("Result:")
print(f"Statement HTML: {result.statement_html}")
print(f"Answer blanks: {result.answer_blanks}")
print(f"Solution: {result.solution_html}")
print(f"Hint: {result.hint_html}")
print(f"Errors: {result.errors}")
