"""Check what the MultiAnswer correct answers are."""

from packages.pg_translator.pg_translator import PGTranslator
from pathlib import Path

pg_src = Path('tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg').read_text()
t = PGTranslator()
result = t.translate_source(pg_src, seed=0)

# Get the MultiAnswer object
multians = result.answer_blanks['AnSwEr0001']['evaluator']
print(f"MultiAnswer type: {type(multians).__name__}")
print(f"Has answers: {hasattr(multians, 'answers')}")
if hasattr(multians, 'answers'):
    print(f"Number of answers: {len(multians.answers)}")
    for i, ans in enumerate(multians.answers):
        print(f"\nAnswer {i}:")
        print(f"  Type: {type(ans).__name__}")
        print(f"  Value: {ans}")
        if hasattr(ans, 'evaluate'):
            try:
                # Try to evaluate with seed context
                print(f"  Evaluated: {ans.evaluate({})}")
            except Exception as e:
                print(f"  Evaluate error: {e}")

# Try checking with correct answers
print("\n" + "="*60)
print("Testing with correct answers:")
inputs = {
    'AnSwEr0001': '8y-9',
    'AnSwEr0002': 'y-1'
}

result_check = t.translate_source(pg_src, seed=0, inputs=inputs)
print(f"\nResults: {result_check.answer_results}")
print(f"Score: {result_check.score}")
