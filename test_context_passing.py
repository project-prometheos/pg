#!/usr/bin/env python3
"""Debug context passing in PGML."""

from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.preprocessor import PGPreprocessor
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))


# Simple test with variable
pg_code = """
DOCUMENT()

h = 3
k = 5
vertexform = f"(x-{h})^2-{k}"

pgml_text = '''
The value is [$vertexform].
'''
result = PGML(pgml_text)
TEXT(result)

ENDDOCUMENT()
"""

print("="*70)
print("TESTING CONTEXT PASSING")
print("="*70)

preprocessor = PGPreprocessor()
python_code = preprocessor.preprocess(pg_code).code

print("\nPreprocessed code:")
print(python_code)
print("\n" + "="*70)

sandbox = InProcessSandbox()
exec_result = sandbox.execute(python_code, seed=1234)

print(f"\nSuccess: {exec_result.success}")
print(f"Output: {exec_result.output_text}")
print(f"Errors: {exec_result.errors if exec_result.errors else 'None'}")

# Check namespace
print(f"\nNamespace keys: {list(sandbox.namespace.keys())[:20]}")
print(f"vertexform value: {sandbox.namespace.get('vertexform', 'NOT FOUND')}")
print(f"h value: {sandbox.namespace.get('h', 'NOT FOUND')}")
print(f"k value: {sandbox.namespace.get('k', 'NOT FOUND')}")
