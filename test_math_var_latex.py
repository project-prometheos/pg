#!/usr/bin/env python3
"""Test LaTeX conversion in math-embedded variables."""

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


# Test with formula that has exponentiation
pg_code = """
DOCUMENT()

Context('Numeric')
h = 3
k = 5
vertexform = Compute(f"(x-{h})^2-{k}")
expanded = Compute("x^2-6*x+4")

BEGIN_PGML
## Math Variable Interpolation Tests

1. Inside inline math: [`[$vertexform]`]
2. Inside display math: [``[$vertexform]``]
3. Multiple variables: [`[$vertexform] = [$expanded]`]
4. With text: The formula [`y = [$vertexform]`] represents a parabola.

END_PGML

ENDDOCUMENT()
"""

print("="*70)
print("TESTING LaTeX CONVERSION IN MATH")
print("="*70)

preprocessor = PGPreprocessor()
python_code = preprocessor.preprocess(pg_code).code

sandbox = InProcessSandbox()
exec_result = sandbox.execute(python_code, seed=1234)

print(f"\nSuccess: {exec_result.success}")
print(f"\nRendered Output:")
print(exec_result.output_text)

if exec_result.errors:
    print(f"\nErrors: {exec_result.errors}")

# Check variables
if 'vertexform' in sandbox.namespace:
    vf = sandbox.namespace['vertexform']
    print(f"\nvertexform string: {str(vf)}")
if 'expanded' in sandbox.namespace:
    ex = sandbox.namespace['expanded']
    print(f"expanded string: {str(ex)}")
