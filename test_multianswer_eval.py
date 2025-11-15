import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/Multianswer.pg", seed=1234)

# Get the evaluator
multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
checker = multi_eval.cmp()

print(f"Checker type: {type(checker).__name__}")
print(f"Checker has .evaluate(): {hasattr(checker, 'evaluate')}")

# Try calling evaluate
print(f"\nTrying evaluate with both answers:")
try:
    result = checker.evaluate('1 - x', 'x + 1')
    print(f"  Result type: {type(result)}")
    print(f"  Result: {result}")
    if hasattr(result, "__dict__"):
        print(f"  Result dict: {result.__dict__}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

