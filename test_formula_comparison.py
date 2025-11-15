import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/Multianswer.pg", seed=1234)

# Get the MultiAnswer object
multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
correct = multi_eval.correct_answers

print(f"Correct answers:")
for i, ans in enumerate(correct):
    print(f"  [{i}]: {ans} (type: {type(ans).__name__})")

# Test comparisons
print(f"\nTesting comparisons:")
f1 = correct[0]  # Formula(1 - x)
f2 = correct[1]  # Formula(x + 1)

print(f"f1: {f1}")
print(f"f2: {f2}")

# Test equality
print(f"\nf1 == f1: {f1 == f1}")
print(f"f1 == f2: {f1 == f2}")

# Try creating student formulas from strings
from pg.math.context import get_current_context
from pg.math.formula import Formula

context = get_current_context()
print(f"\nContext: {context}")

# Try to create Formula objects from strings
f1_student = Formula("1 - x")
f2_student = Formula("x + 1")

print(f"\nStudent formulas:")
print(f"  f1_student: {f1_student}")
print(f"  f2_student: {f2_student}")

print(f"\nComparing correct vs student:")
print(f"  f1 == f1_student: {f1 == f1_student}")
print(f"  f2 == f2_student: {f2 == f2_student}")

# Test the checker with Formula objects
print(f"\nCalling checker with Formula objects:")
try:
    result = multi_eval.checker(correct, [f1_student, f2_student], multi_eval)
    print(f"  Result: {result}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

