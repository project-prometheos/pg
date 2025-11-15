import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/Parametric/ParametricEquationAnswers.pg", seed=1234)

multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
print(f"MultiAnswer: {multi_eval}")
print(f"Answers: {multi_eval.answers}")

# Test MultiAnswer.check() directly
student_answers = ['cos(t)', 'sin(t)', '0', '1.0471975511965976']
print(f"\nStudent answers: {student_answers}")

check_result = multi_eval.check(*student_answers)
print(f"Check result: {check_result}")

# Check each answer individually
print(f"\nChecking each answer individually:")
for i, (correct, student) in enumerate(zip(multi_eval.answers, student_answers)):
    print(f"\n[{i}] Correct: {correct} (type: {type(correct).__name__})")
    print(f"    Student: {student}")
    
    if hasattr(correct, 'cmp'):
        checker = correct.cmp()
        print(f"    Checker: {type(checker).__name__}")
        if hasattr(checker, 'check'):
            result = checker.check(student)
            print(f"    Result: {result}")
        else:
            print(f"    Checker doesn't have .check()")

