"""Test answer checking directly."""

from pathlib import Path
from packages.pg_translator.pg_translator import PGTranslator
import sys
# Force reimport
for mod in list(sys.modules.keys()):
    if 'pg_' in mod or 'packages' in mod:
        del sys.modules[mod]


pg_src = Path(
    'tutorial/sample-problems/Algebra/ExpandedPolynomial.pg').read_text()
t = PGTranslator()

print("=== Testing with inputs ===")
result = t.translate_source(pg_src, seed=0, inputs={'AnSwEr0001': 'x^2-6x+4'})

print(f"\nAnswer results: {result.answer_results}")
print(f"Score: {result.score}")
print(f"Answer blanks: {list(result.answer_blanks.keys())}")
print(f"Metadata: {result.metadata}")
