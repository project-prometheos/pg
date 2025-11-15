import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/VectorCalc/VectorLineSegment1.pg", seed=1234)

multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
vector_ans = multi_eval.answers[0]  # First answer is a Vector

print(f"Vector answer: {vector_ans}")
print(f"Vector type: {type(vector_ans).__name__}")

# Get the checker
checker = vector_ans.cmp()
print(f"\nChecker: {checker}")
print(f"Checker type: {type(checker).__name__}")
print(f"Checker module: {type(checker).__module__}")

# Check what methods it has
print(f"\nChecker methods:")
methods = [m for m in dir(checker) if not m.startswith('_')]
for m in methods:
    attr = getattr(checker, m)
    if callable(attr):
        print(f"  {m}()")

# Try to find the source
import inspect
try:
    source_file = inspect.getfile(type(checker))
    print(f"\nSource file: {source_file}")
except:
    pass

