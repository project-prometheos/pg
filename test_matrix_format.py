import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/LinearAlgebra/MatrixAnswer2.pg", seed=1234)

matrix_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']

print(f"Matrix evaluator: {matrix_eval}")
print(f"Type: {type(matrix_eval).__name__}")
print(f"\nString representations:")
print(f"  str(): {str(matrix_eval)}")
if hasattr(matrix_eval, 'string'):
    try:
        print(f"  string(): {matrix_eval.string()}")
    except:
        print(f"  string(): (error)")
if hasattr(matrix_eval, 'to_string'):
    try:
        print(f"  to_string(): {matrix_eval.to_string()}")
    except:
        print(f"  to_string(): (error)")

# Test what the student answer format should be
student_answer = "[[1, 2, 3], [4, 5, 6]]"
print(f"\nStudent answer: {student_answer}")
print(f"Evaluator str: {str(matrix_eval)}")
print(f"Match: {str(matrix_eval) == student_answer}")

# Check if Matrix has a compare method that works differently
if hasattr(matrix_eval, 'compare'):
    print(f"\nTrying compare() with string parsing:")
    try:
        from pg.math.context import get_current_context
        from pg.math.matrix import Matrix
        
        context = get_current_context()
        print(f"  Context: {context}")
        
        # Try to create a Matrix from the student string
        # Matrix format: [[1, 2, 3], [4, 5, 6]]
        # This should be parsed as a list of lists
        import ast
        parsed = ast.literal_eval(student_answer)
        print(f"  Parsed student: {parsed}")
        
        student_matrix = Matrix(parsed)
        print(f"  Student matrix: {student_matrix}")
        
        cmp_result = matrix_eval.compare(student_matrix)
        print(f"  Compare result: {cmp_result}")
        print(f"  Are equal: {cmp_result == 0}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

