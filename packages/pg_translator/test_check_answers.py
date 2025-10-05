"""
Test that answer checking works for AnswerUpToMultiple problem.
"""
from pg_translator.translator import PGTranslator

def test_answer_check():
    translator = PGTranslator()
    
    # Render problem
    result = translator.translate(
        'd:/pg/tutorial/sample-problems/Algebra/AnswerUpToMultiple.pg',
        seed=3157
    )
    
    print("=== Render Result ===")
    print(f"Statement HTML length: {len(result.statement_html)}")
    print(f"answer_blanks keys: {list(result.answer_blanks.keys())}")
    if result.errors:
        print(f"Errors: {result.errors}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")
    
    # Check what's in answer_blanks
    for name, blank in result.answer_blanks.items():
        print(f"\n{name}:")
        print(f"  Type: {type(blank)}")
        print(f"  Value: {blank}")
        if hasattr(blank, 'check'):
            print(f"  Has check method: True")
        if hasattr(blank, 'cmp'):
            print(f"  Has cmp method: True")
        if hasattr(blank, 'evaluate'):
            print(f"  Has evaluate method: True")
    
    # Now try checking an answer
    if result.answer_blanks:
        print("\n=== Checking Answer ===")
        check_result = translator.translate(
            'd:/pg/tutorial/sample-problems/Algebra/AnswerUpToMultiple.pg',
            inputs={'AnSwEr0001': 'x^2-x-2'},
            seed=3157
        )
        
        print(f"Check result:")
        print(f"  answer_results: {check_result.answer_results}")
        print(f"  score: {check_result.score}")
        if check_result.answer_results:
            for name, result in check_result.answer_results.items():
                print(f"  {name}:")
                print(f"    correct: {result.correct}")
                print(f"    score: {result.score}")
                print(f"    message: {result.answer_message}")

if __name__ == '__main__':
    test_answer_check()
