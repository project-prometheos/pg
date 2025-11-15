import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/Algebra/ExpandedPolynomial.pg", seed=1234)

for name, info in result.answer_blanks.items():
    evaluator = info['evaluator']['ans_eval']
    print(f"{name}:")
    print(f"  Type: {type(evaluator).__name__}")
    print(f"  Has cmp: {hasattr(evaluator, 'cmp')}")
    print(f"  Has check: {hasattr(evaluator, 'check')}")
    print(f"  Has compare: {hasattr(evaluator, 'compare')}")
    print(f"  Has evaluate: {hasattr(evaluator, 'evaluate')}")
    if hasattr(evaluator, 'cmp'):
        checker = evaluator.cmp()
        print(f"  Checker type: {type(checker).__name__}")
        print(f"  Checker has check: {hasattr(checker, 'check')}")
        print(f"  Checker callable: {callable(checker)}")

