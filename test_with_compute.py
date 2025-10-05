#!/usr/bin/env python3
"""Test with Compute() like real problems."""

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


# Real problem code (simplified)
pg_code = """
DOCUMENT()

Context('Numeric')
h = 3
k = 5
vertexform = Compute(f"(x-{h})^2-{k}")

BEGIN_PGML
The quadratic expression [`[$vertexform]`] is written in vertex form.
Now WITH math delimiters!
END_PGML

ENDDOCUMENT()
"""

print("="*70)
print("TESTING WITH Compute()")
print("="*70)

preprocessor = PGPreprocessor()
python_code = preprocessor.preprocess(pg_code).code

print("\nPreprocessed code:")
print(python_code)
print("\n" + "="*70)

sandbox = InProcessSandbox()
exec_result = sandbox.execute(python_code, seed=1234)

print(f"\nSuccess: {exec_result.success}")
print(f"Output: {exec_result.output_text[:200]}...")
print(f"Errors: {exec_result.errors if exec_result.errors else 'None'}")

# Check what vertexform is
if 'vertexform' in sandbox.namespace:
    vf = sandbox.namespace['vertexform']
    print(f"\nvertexform type: {type(vf)}")
    print(f"vertexform value: {vf}")
    print(f"vertexform str: {str(vf)}")
    print(f"vertexform repr: {repr(vf)}")
