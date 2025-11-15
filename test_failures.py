import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()

# Test a few failing problems
failing_problems = [
    "tutorial/sample-problems/Algebra/PointAnswers.pg",
    "tutorial/sample-problems/Algebra/StringOrOtherType.pg",
    "tutorial/sample-problems/LinearAlgebra/MatrixAnswer2.pg",
    "tutorial/sample-problems/ProblemTechniques/CustomAnswerListChecker.pg",
]

for problem in failing_problems:
    print("=" * 70)
    print(f"Testing: {problem.split('/')[-1]}")
    print("=" * 70)
    
    try:
        result = translator.translate(problem, seed=1234)
        print(f"Answer blanks: {list(result.answer_blanks.keys())}")
        
        # Check evaluator types
        for name, info in result.answer_blanks.items():
            evaluator = info['evaluator']['ans_eval']
            print(f"\n{name}:")
            print(f"  Type: {type(evaluator).__name__}")
            print(f"  Has cmp: {hasattr(evaluator, 'cmp')}")
            print(f"  Has check: {hasattr(evaluator, 'check')}")
            print(f"  Has compare: {hasattr(evaluator, 'compare')}")
            print(f"  Evaluator: {evaluator}")
        
        correct_answers = extract_correct_answers(result)
        print(f"\nExtracted answers: {correct_answers}")
        
        if correct_answers:
            check_result = translator.translate(problem, seed=1234, inputs=correct_answers)
            print(f"\nCheck score: {check_result.score}")
            if check_result.answer_results:
                for name, ans_result in check_result.answer_results.items():
                    print(f"\n  {name}:")
                    print(f"    score={ans_result.score}")
                    print(f"    correct={ans_result.correct}")
                    print(f"    error_flag={ans_result.error_flag}")
                    if ans_result.error_flag:
                        print(f"    ERROR: {ans_result.error_message}")
                    if ans_result.answer_message:
                        print(f"    message: {ans_result.answer_message}")
                    print(f"    student_value={ans_result.student_value}")
                    print(f"    correct_value={ans_result.correct_value}")
                    print(f"    typeError={ans_result.typeError}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")

