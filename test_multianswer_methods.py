import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/Multianswer.pg", seed=1234)

# Get the evaluator
multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
print(f"MultiAnswer evaluator type: {type(multi_eval).__name__}")
print(f"\nDirect methods:")
print(f"  has .cmp(): {hasattr(multi_eval, 'cmp')}")
print(f"  has .check(): {hasattr(multi_eval, 'check')}")
print(f"  has .evaluate(): {hasattr(multi_eval, 'evaluate')}")
print(f"  has .compare(): {hasattr(multi_eval, 'compare')}")

print(f"\nTrying .cmp():")
try:
    checker = multi_eval.cmp()
    print(f"  checker type: {type(checker).__name__}")
    print(f"  checker is same object: {checker is multi_eval}")
    print(f"  checker has .check(): {hasattr(checker, 'check')}")
    print(f"  checker has .evaluate(): {hasattr(checker, 'evaluate')}")
    
    if hasattr(checker, 'check'):
        print(f"\nTrying check with both answers:")
        result = checker.check('1 - x', 'x + 1')
        print(f"  Result: {result}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\nAll methods on evaluator:")
methods = [m for m in dir(multi_eval) if not m.startswith('_')]
for m in methods:
    attr = getattr(multi_eval, m)
    if callable(attr):
        print(f"  {m}()")

