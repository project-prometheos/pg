import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

# Add detailed debug output
original_evaluate = PGTranslator._evaluate_answers

def debug_evaluate(self, environment, raw_inputs):
    from pg.answer import AnswerResult
    
    print(f"\n=== _evaluate_answers called ===")
    print(f"raw_inputs: {raw_inputs}")
    
    processed_inputs = {
        name: raw_inputs[name]
        for name, value in raw_inputs.items()
    }
    
    answer_results = {}
    evaluator_groups = {}
    evaluator_map = {}
    
    # Group by evaluator
    for name, student_answer in processed_inputs.items():
        if name not in environment.answers:
            continue
        
        ans_entry = environment.answers[name]
        evaluator = (
            ans_entry["ans_eval"]
            if isinstance(ans_entry, dict) and "ans_eval" in ans_entry
            else ans_entry
        )
        
        eval_id = id(evaluator)
        evaluator_groups.setdefault(eval_id, []).append((name, student_answer))
        evaluator_map[eval_id] = evaluator
    
    print(f"\nEvaluator groups: {len(evaluator_groups)}")
    for eval_id, group_items in evaluator_groups.items():
        evaluator = evaluator_map[eval_id]
        print(f"\nGroup with {len(group_items)} items:")
        print(f"  Items: {[(n, a) for n, a in group_items]}")
        print(f"  Evaluator type: {type(evaluator).__name__}")
        print(f"  Has .cmp(): {hasattr(evaluator, 'cmp')}")
        
        # Check if multi-item with .cmp()
        if len(group_items) > 1 and hasattr(evaluator, "cmp"):
            print(f"  -> Multi-item .cmp() branch")
            checker = evaluator.cmp()
            print(f"     Checker type: {type(checker).__name__}")
            print(f"     Checker has .check(): {hasattr(checker, 'check')}")
            print(f"     Checker has .evaluate(): {hasattr(checker, 'evaluate')}")
            
            if hasattr(checker, "check"):
                print(f"     -> Will call checker.check()")
            elif hasattr(checker, "evaluate"):
                print(f"     -> Checker has .evaluate() but not .check() - will skip!")
        else:
            print(f"  -> Single-item branch (len={len(group_items)})")
    
    # Now call the original
    return original_evaluate(self, environment, raw_inputs)

PGTranslator._evaluate_answers = debug_evaluate

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/Multianswer.pg", seed=1234)
correct_answers = extract_correct_answers(result)

print("=" * 60)
print("CHECKING PHASE")
print("=" * 60)

check_result = translator.translate(
    "tutorial/sample-problems/ProblemTechniques/Multianswer.pg",
    seed=1234,
    inputs=correct_answers
)

print(f"\nFinal answer_results: {check_result.answer_results}")

