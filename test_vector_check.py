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
print(f"Has .cmp(): {hasattr(vector_ans, 'cmp')}")
print(f"Has .compare(): {hasattr(vector_ans, 'compare')}")

# Test the checker
if hasattr(vector_ans, 'cmp'):
    checker = vector_ans.cmp()
    print(f"\nChecker: {checker}")
    print(f"Checker type: {type(checker).__name__}")
    print(f"Checker has .check(): {hasattr(checker, 'check')}")
    
    student_answer = '<(4, 0) + t * <-4, 2>>'
    print(f"\nStudent answer: {student_answer}")
    
    if hasattr(checker, 'check'):
        result = checker.check(student_answer)
        print(f"Check result: {result}")
    else:
        print("Checker doesn't have .check() method")

