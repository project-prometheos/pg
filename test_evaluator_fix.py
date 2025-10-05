"""Test if evaluator objects are being captured correctly."""

import sys
import importlib

# Force reimport of all pg modules
for mod in list(sys.modules.keys()):
    if 'pg_' in mod or 'packages' in mod:
        del sys.modules[mod]

from packages.pg_translator.pg_translator import PGTranslator
from pathlib import Path

pg_src = Path('tutorial/sample-problems/Algebra/ExpandedPolynomial.pg').read_text()
t = PGTranslator()
result = t.translate_source(pg_src, seed=0)

print("=== ANSWER BLANKS ===")
print(f"Answer blanks keys: {list(result.answer_blanks.keys())}")

evaluator = result.answer_blanks['AnSwEr0001']['evaluator']
print(f"\n=== EVALUATOR INFO ===")
print(f"Evaluator type: {type(evaluator)}")
print(f"Evaluator class: {evaluator.__class__.__name__}")
print(f"Has cmp: {hasattr(evaluator, 'cmp')}")
print(f"Has evaluate: {hasattr(evaluator, 'evaluate')}")

if hasattr(evaluator, 'cmp'):
    print("\n=== SUCCESS: Evaluator object captured! ===")
    # Try to create an answer evaluator
    cmp_result = evaluator.cmp()
    print(f"cmp() result type: {type(cmp_result)}")
    print(f"cmp() result has evaluate: {hasattr(cmp_result, 'evaluate')}")
else:
    print(f"\n=== FAILURE: Still a string: {evaluator} ===")
