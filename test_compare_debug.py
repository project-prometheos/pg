import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers
from pg.math.context import get_current_context

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/Algebra/PointAnswers.pg", seed=1234)

# Get the evaluator
list_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
student_answer = "((1, 0)), ((-1, 0))"

print(f"Evaluator: {list_eval}")
print(f"Evaluator string: {str(list_eval)}")
print(f"Student answer: {student_answer}")

# Try to get context and parse
context = get_current_context()
print(f"\nContext: {context}")

if context:
    try:
        student_obj = context.parse(student_answer)
        print(f"Parsed student: {student_obj}")
        print(f"Parsed type: {type(student_obj).__name__}")
        
        cmp_result = list_eval.compare(student_obj)
        print(f"Compare result: {cmp_result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No context available!")
    
# Check if we can compare the strings directly
print(f"\nDirect string comparison:")
print(f"  Evaluator str: '{str(list_eval)}'")
print(f"  Student str: '{student_answer}'")
print(f"  Equal: {str(list_eval) == student_answer}")

