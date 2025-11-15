import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.math.geometric import Vector
from pg.math.formula import Formula

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/VectorCalc/VectorLineSegment1.pg", seed=1234)

multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
vector_ans = multi_eval.answers[0]

print(f"Vector answer: {vector_ans}")
print(f"Type: {type(vector_ans).__name__}")
print(f"Is Vector: {isinstance(vector_ans, Vector)}")
print(f"Is Formula: {isinstance(vector_ans, Formula)}")

# Try to create a Vector from the string
student_str = '<(4, 0) + t * <-4, 2>>'
print(f"\nStudent string: {student_str}")

# Try parsing as Formula first
try:
    from pg.math.context import get_current_context
    context = get_current_context()
    print(f"Context: {context}")
    
    # Try creating a Formula
    formula = Formula(student_str)
    print(f"Formula created: {formula}")
    print(f"Formula type: {type(formula).__name__}")
except Exception as e:
    print(f"Formula creation error: {e}")

# Try using ast.literal_eval for simple vectors
import ast
try:
    # For simple vectors like <1, 2, 3>
    # Remove angle brackets and parse
    if student_str.startswith('<') and student_str.endswith('>'):
        inner = student_str[1:-1]
        print(f"\nInner: {inner}")
        # This is a parametric equation, not a simple vector
except Exception as e:
    print(f"Parse error: {e}")

