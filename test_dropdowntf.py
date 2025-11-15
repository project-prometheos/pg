import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/SimplePopUp.pg", seed=1234)

tf_eval = result.answer_blanks['AnSwEr0005']['evaluator']['ans_eval']
print(f"DropDownTF:")
print(f"  correct: {tf_eval.correct}")
print(f"  correct type: {type(tf_eval.correct)}")
print(f"  correct str: {str(tf_eval.correct)}")

# Test the checker
checker = tf_eval.cmp()
print(f"\nTesting checker:")
print(f"  checker('True'): {checker('True')}")
print(f"  checker('T'): {checker('T')}")
print(f"  checker(True): {checker(True)}")
print(f"  checker('False'): {checker('False')}")

