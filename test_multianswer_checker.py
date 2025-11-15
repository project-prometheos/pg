import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/Multianswer.pg", seed=1234)

# Get the MultiAnswer object
multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
print(f"MultiAnswer type: {type(multi_eval).__name__}")
print(f"Has checker: {hasattr(multi_eval, 'checker')}")
print(f"Checker: {multi_eval.checker}")
print(f"Checker type: {type(multi_eval.checker)}")
print(f"Checker callable: {callable(multi_eval.checker)}")

print(f"\nCorrect answers: {multi_eval.correct_answers}")

if multi_eval.checker and callable(multi_eval.checker):
    print(f"\nTrying to call checker directly:")
    try:
        # The checker signature is: checker(correct, student, self)
        correct = multi_eval.correct_answers
        student = [correct[0], correct[1]]  # Use correct answers as student
        result = multi_eval.checker(correct, student, multi_eval)
        print(f"  Result: {result}")
        print(f"  Result type: {type(result)}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

