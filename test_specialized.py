import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()

# Test a few specialized types
problems = [
    "tutorial/sample-problems/IntegralCalc/DoubleIntegral.pg",
    "tutorial/sample-problems/ProblemTechniques/FormulasToConstants.pg",
    "tutorial/sample-problems/Parametric/ParametricEquationAnswers.pg",
]

for problem in problems:
    print("=" * 60)
    print(f"Testing {problem.split('/')[-1]}")
    print("=" * 60)
    
    try:
        result = translator.translate(problem, seed=1234)
        print(f"Answer blanks: {list(result.answer_blanks.keys())}")
        
        for name, info in result.answer_blanks.items():
            evaluator = info['evaluator']['ans_eval']
            print(f"\n{name}:")
            print(f"  Type: {type(evaluator).__name__}")
            print(f"  String: {str(evaluator)[:100]}")
        
        correct_answers = extract_correct_answers(result)
        print(f"\nExtracted answers: {correct_answers}")
        
        if correct_answers:
            check_result = translator.translate(problem, seed=1234, inputs=correct_answers)
            print(f"Check score: {check_result.score}")
            if check_result.answer_results:
                for name, ans_result in check_result.answer_results.items():
                    print(f"  {name}: score={ans_result.score}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")

