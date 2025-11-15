import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()

# Test with a simple problem that we know works
result = translator.translate("tutorial/sample-problems/Algebra/ExpandedPolynomial.pg", seed=1234)

print("ExpandedPolynomial (working):")
print(f"  answer_blanks keys: {list(result.answer_blanks.keys())}")

# Get the environment to check environment.answers
if hasattr(result, 'problem_state') and result.problem_state:
    env_answers = result.problem_state.get('environment_answers', {})
    print(f"  environment.answers keys: {list(env_answers.keys()) if env_answers else 'N/A'}")

# Now test with PointAnswers
result2 = translator.translate("tutorial/sample-problems/Algebra/PointAnswers.pg", seed=1234)

print("\nPointAnswers (not working):")
print(f"  answer_blanks keys: {list(result2.answer_blanks.keys())}")

if hasattr(result2, 'problem_state') and result2.problem_state:
    env_answers = result2.problem_state.get('environment_answers', {})
    print(f"  environment.answers keys: {list(env_answers.keys()) if env_answers else 'N/A'}")

# Try to extract from answer_blanks directly
print("\nChecking answer_blanks structure:")
for name, info in result2.answer_blanks.items():
    print(f"  {name}: {info.keys() if isinstance(info, dict) else type(info)}")
    if isinstance(info, dict) and 'evaluator' in info:
        eval_info = info['evaluator']
        print(f"    evaluator: {eval_info.keys() if isinstance(eval_info, dict) else type(eval_info)}")

