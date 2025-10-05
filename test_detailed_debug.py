#!/usr/bin/env python3
"""Debug execution with detailed error catching."""

from pg_translator.preprocessor import PGPreprocessor
from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator import PGTranslator
import sys
from pathlib import Path
import traceback

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))


file_path = "tutorial/sample-problems/Algebra/ExpandedPolynomial.pg"

print("="*70)
print("TESTING WITH DETAILED ERROR TRACKING")
print("="*70)

try:
    translator = PGTranslator()
    result = translator.translate(file_path, seed=1234)

    print(f"\nTranslation SUCCESS")
    print(
        f"Statement: {len(result.statement_html) if result.statement_html else 0} chars")
    print(
        f"Answers: {len(result.answer_blanks) if result.answer_blanks else 0}")
    print(
        f"Solution: {len(result.solution_html) if result.solution_html else 0} chars")

except Exception as e:
    print(f"\nTranslation FAILED:")
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

# Now try manual execution to see what's happening
print("\n" + "="*70)
print("MANUAL EXECUTION WITH SANDBOX")
print("="*70)


preprocessor = PGPreprocessor()
with open(file_path, 'r', encoding='utf-8') as f:
    perl_code = f.read()

preprocess_result = preprocessor.preprocess(perl_code)
python_code = preprocess_result.code

print("\nRunning in sandbox...")
try:
    sandbox = InProcessSandbox()
    exec_result = sandbox.execute(python_code, seed=1234)

    print(f"\nExecution SUCCESS")
    print(f"Success flag: {exec_result.success}")
    print(f"Output text: {len(exec_result.output_text)} chars")
    if exec_result.output_text:
        print(f"  {exec_result.output_text[:200]}...")
    print(f"Answers: {len(exec_result.answers)} evaluators")
    if exec_result.answers:
        for name, ans in list(exec_result.answers.items())[:3]:
            print(f"  {name}: {ans}")
    print(
        f"Solution: {len(exec_result.solution_text) if exec_result.solution_text else 0} chars")
    print(f"Errors: {exec_result.errors if exec_result.errors else 'None'}")

except Exception as e:
    print(f"\nExecution FAILED:")
    print(f"Error: {e}")
    traceback.print_exc()
