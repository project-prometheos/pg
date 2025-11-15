import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/VectorCalc/VectorLineSegment1.pg", seed=1234)

correct_answers = extract_correct_answers(result)
print(f"Extracted answers: {correct_answers}")

# Check what the Vector looks like
multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
vector_ans = multi_eval.answers[0]
print(f"\nVector answer: {vector_ans}")
print(f"Vector string: {str(vector_ans)}")
print(f"Vector to_string: {vector_ans.to_string() if hasattr(vector_ans, 'to_string') else 'N/A'}")

