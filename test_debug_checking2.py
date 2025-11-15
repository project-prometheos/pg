import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

# Monkey-patch to add detailed debug output
original_evaluate = PGTranslator._evaluate_answers

def debug_evaluate(self, environment, raw_inputs):
    from pg.answer import AnswerResult
    
    print(f"\n=== _evaluate_answers called ===")
    processed_inputs = {
        name: raw_inputs[name]  # Simplified for debug
        for name, value in raw_inputs.items()
    }
    
    answer_results = {}
    evaluator_groups = {}
    evaluator_map = {}
    
    for name, student_answer in processed_inputs.items():
        print(f"\nProcessing {name}: {student_answer}")
        if name not in environment.answers:
            print(f"  -> NOT in environment.answers, skipping")
            continue
        
        print(f"  -> Found in environment.answers")
        ans_entry = environment.answers[name]
        evaluator = (
            ans_entry["ans_eval"]
            if isinstance(ans_entry, dict) and "ans_eval" in ans_entry
            else ans_entry
        )
        print(f"  -> Evaluator type: {type(evaluator).__name__}")
        print(f"  -> Has .cmp(): {hasattr(evaluator, 'cmp')}")
        print(f"  -> Has .check(): {hasattr(evaluator, 'check')}")
        print(f"  -> Has .evaluate(): {hasattr(evaluator, 'evaluate')}")
        
        eval_id = id(evaluator)
        evaluator_groups.setdefault(eval_id, []).append((name, student_answer))
        evaluator_map[eval_id] = evaluator
    
    print(f"\nEvaluator groups: {len(evaluator_groups)}")
    for eval_id, group_items in evaluator_groups.items():
        evaluator = evaluator_map[eval_id]
        print(f"\nGroup with {len(group_items)} items:")
        print(f"  Items: {group_items}")
        print(f"  Evaluator: {type(evaluator).__name__}")
        
        # Check which branch will be taken
        if len(group_items) > 1 and hasattr(evaluator, "cmp"):
            print(f"  -> Taking multi-item .cmp() branch")
        elif hasattr(evaluator, "check") and not hasattr(evaluator, "cmp"):
            print(f"  -> Taking .check() branch")
            for name, student_answer in group_items:
                try:
                    check_result = evaluator.check(student_answer)
                    print(f"    check_result: {check_result}")
                except Exception as e:
                    print(f"    Error calling check(): {e}")
        elif hasattr(evaluator, "cmp"):
            print(f"  -> Taking single .cmp() branch")
            for name, student_answer in group_items:
                try:
                    checker = evaluator.cmp()
                    print(f"    checker: {type(checker).__name__}")
                    if hasattr(checker, "check"):
                        check_result = checker.check(student_answer)
                        print(f"    check_result: {check_result}")
                except Exception as e:
                    print(f"    Error: {e}")
        elif hasattr(evaluator, "evaluate"):
            print(f"  -> Taking .evaluate() branch")
            for name, student_answer in group_items:
                try:
                    result = evaluator.evaluate(student_answer)
                    print(f"    result: {result}")
                except Exception as e:
                    print(f"    Error: {e}")
        else:
            print(f"  -> No matching branch!")
    
    # Now call the original
    return original_evaluate(self, environment, raw_inputs)

PGTranslator._evaluate_answers = debug_evaluate

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/Algebra/PointAnswers.pg", seed=1234)
correct_answers = extract_correct_answers(result)

print("=" * 60)
print("CHECKING PHASE")
print("=" * 60)

check_result = translator.translate(
    "tutorial/sample-problems/Algebra/PointAnswers.pg",
    seed=1234,
    inputs=correct_answers
)

print(f"\nFinal answer_results: {check_result.answer_results}")

