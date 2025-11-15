import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()

# Test problems with Score None
problems = [
    "tutorial/sample-problems/DiffCalc/LinearApprox.pg",
    "tutorial/sample-problems/DiffEq/GeneralSolutionODE.pg",
    "tutorial/sample-problems/Parametric/VectorParametricLines.pg",
    "tutorial/sample-problems/ProblemTechniques/CustomAnswerListChecker.pg",
]

for problem in problems:
    print("=" * 60)
    print(f"Testing {problem.split('/')[-1]}")
    print("=" * 60)
    
    try:
        result = translator.translate(problem, seed=1234)
        print(f"Answer blanks: {list(result.answer_blanks.keys())}")
        
        correct_answers = extract_correct_answers(result)
        print(f"Extracted answers: {correct_answers}")
        
        if correct_answers:
            check_result = translator.translate(problem, seed=1234, inputs=correct_answers)
            print(f"Check score: {check_result.score}")
            if check_result.answer_results:
                for name, ans_result in check_result.answer_results.items():
                    print(f"  {name}: score={ans_result.score}, msg={ans_result.answer_message}")
            else:
                print("  No answer_results")
            if check_result.errors:
                print(f"  Errors: {check_result.errors}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")

