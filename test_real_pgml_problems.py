#!/usr/bin/env python3
"""
Test real PGML .pg files with pg_translator.

Tests that we can process .pg files using BEGIN_PGML...END_PGML syntax.
"""

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))

from pg_translator import PGTranslator


def test_pgml_file(file_path: str, seed: int = 1234) -> bool:
    """
    Test a single PGML .pg file.
    
    Args:
        file_path: Path to .pg file
        seed: Random seed
    
    Returns:
        True if test passes, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Testing: {file_path}")
    print(f"{'='*60}\n")
    
    try:
        # Read problem file
        with open(file_path, 'r', encoding='utf-8') as f:
            pg_code = f.read()
        
        # Translate problem
        translator = PGTranslator()
        result = translator.translate(pg_code, seed=seed)
        
        # Display statement HTML
        print("[STATEMENT]")
        print(result.statement_html[:500])
        if len(result.statement_html) > 500:
            print(f"... ({len(result.statement_html)} chars total)")
        print()
        
        # Display answers
        if result.answer_blanks:
            print("[ANSWERS]")
            for ans_id, ans_data in result.answer_blanks.items():
                if isinstance(ans_data, dict):
                    print(f"{ans_id}:")
                    print(f"  Type: {ans_data.get('type', 'Unknown')}")
                    correct = ans_data.get('correct_ans')
                    if correct is not None:
                        print(f"  Correct: {correct}")
                else:
                    print(f"{ans_id}: {ans_data}")
            print()
        else:
            print("[ANSWERS] None found")
            print()
        
        # Display solution if present
        if result.solution_html:
            print("[SOLUTION]")
            print(result.solution_html[:300])
            if len(result.solution_html) > 300:
                print("...")
            print()
        
        # Display hint if present
        if result.hint_html:
            print("[HINT]")
            print(result.hint_html[:300])
            if len(result.hint_html) > 300:
                print("...")
            print()
        
        # Test answer checking if we have answers
        if result.answer_blanks:
            print("[ANSWER CHECK]")
            # Get first answer's correct value
            first_ans_id = list(result.answer_blanks.keys())[0]
            first_ans = result.answer_blanks[first_ans_id]
            
            if isinstance(first_ans, dict):
                correct = first_ans.get('correct_ans')
                if correct is not None:
                    print(f"Testing with correct answer: {correct}")
                    # We need the evaluator to check
                    evaluator = first_ans.get('evaluator')
                    if evaluator:
                        check_result = evaluator(str(correct))
                        print(f"{first_ans_id}: {check_result.is_correct} (score: {check_result.score})")
                    else:
                        print("No evaluator available")
                else:
                    print("No correct answer available")
            print()
        
        print("[OK] Test passed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test PGML problems from webwork_ps1_pg/."""
    
    # Test files from webwork_ps1_pg
    test_files = [
        "webwork_ps1_pg/ps1-prob01.pg",
        "webwork_ps1_pg/ps1-prob02.pg",
        "webwork_ps1_pg/ps1-prob10.pg",
    ]
    
    passed = 0
    failed = 0
    
    for file_path in test_files:
        try:
            if test_pgml_file(file_path):
                passed += 1
            else:
                failed += 1
        except FileNotFoundError:
            print(f"[SKIP] File not found: {file_path}")
            continue
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Passed: {passed}/{passed+failed}")
    print(f"Failed: {failed}/{passed+failed}")
    
    if failed == 0:
        print("[OK] All tests passed!")
    else:
        print(f"[FAIL] {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
