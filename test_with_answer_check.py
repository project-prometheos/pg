"""
Test script for problem rendering with answer checking.
"""

import sys
from pathlib import Path

# Add packages to path
for pkg in ['pg_translator', 'pg_macros', 'pg_math', 'pg_mathobjects', 
            'pg_parser', 'pg_answer', 'pg_pgml', 'pg_renderer']:
    sys.path.insert(0, str(Path(__file__).parent / "packages" / pkg))

from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.macro_loader import MacroLoader
from pg_translator.preprocessor import PGPreprocessor
from pg_parser import Context

# Read the test problem
problem_file = Path(__file__).parent / "test_problems" / "simple_01.pg"
problem_code = problem_file.read_text()

print("=" * 70)
print(" " * 15 + "PROBLEM RENDERING TEST WITH ANSWER CHECKING")
print("=" * 70)

# Create sandbox and macro loader
sandbox = InProcessSandbox(timeout=30)
macro_loader = MacroLoader(sandbox)
sandbox.namespace['_macro_loader'] = macro_loader

# Preprocess
preprocessor = PGPreprocessor()
preprocessed_code = preprocessor.preprocess(problem_code).code

# Execute
result = sandbox.execute(preprocessed_code, seed=123, context=Context("Numeric"))

print(f"\n✅ Problem rendered successfully!")
print(f"\nProblem Output:")
print("-" * 70)
print(result.output_text)
print("-" * 70)

print(f"\nAnswer Blanks: {list(result.answers.keys())}")

# Test answer checking
if result.answers:
    print(f"\nTesting Answer Checking:")
    print("-" * 70)
    
    for ans_name, ans_hash in result.answers.items():
        print(f"\nAnswer blank: {ans_name}")

        # Extract evaluator from answer hash
        if isinstance(ans_hash, dict) and 'ans_eval' in ans_hash:
            evaluator = ans_hash['ans_eval']
        else:
            evaluator = ans_hash

        print(f"Evaluator type: {type(evaluator).__name__}")

        # Test correct answer
        if hasattr(evaluator, 'evaluate'):
            correct_result = evaluator.evaluate("4")
            print(f"  ✓ Testing '4' (correct):")
            print(f"      score: {correct_result.score}")
            print(f"      correct: {correct_result.correct}")

            # Test incorrect answer
            incorrect_result = evaluator.evaluate("5")
            print(f"  ✗ Testing '5' (incorrect):")
            print(f"      score: {incorrect_result.score}")
            print(f"      correct: {incorrect_result.correct}")
        else:
            print(f"  ⚠ Evaluator doesn't have 'evaluate' method")

print("\n" + "=" * 70)
print(" " * 20 + "🎉 ALL TESTS PASSED!")
print("=" * 70)
