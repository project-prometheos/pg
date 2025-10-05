#!/usr/bin/env python3
"""
Test answer evaluation - checking student submissions.

This tests the complete grading pipeline:
1. Student submits answers
2. Answer evaluators check them
3. Scores and feedback are generated
"""

import sys
from pathlib import Path

# Add packages to path
repo_root = Path(__file__).parent
for pkg in ["pg_macros", "pg_math", "pg_answer"]:
    sys.path.insert(0, str(repo_root / "packages" / pkg))

from pg_macros.core.pg_core import DOCUMENT, TEXT, ANS, ENDDOCUMENT, get_environment
from pg_macros.core.pg_basic_macros import ans_rule
from pg_macros.answers.pg_answer_macros import num_cmp

print("=" * 70)
print("TEST: Answer Evaluation - Grading Student Submissions")
print("=" * 70)

# Setup
globals()['envir'] = {"problemSeed": 123, "displayMode": "HTML"}

# Create problem
DOCUMENT()

TEXT("<h2>Test Problem for Grading</h2>")
TEXT("<p>What is 2 + 2?</p>")
TEXT("<p>Answer: ", ans_rule(20), "</p>")

# Register answer with evaluator
evaluator = num_cmp(4, tolerance=0.01)
ANS(evaluator)

ENDDOCUMENT()

env = get_environment()

print("\n✅ Problem created with 1 answer")

# Test the evaluator directly
print("\n" + "=" * 70)
print("TESTING ANSWER EVALUATOR:")
print("=" * 70)

# Get the registered evaluator
answer_name = list(env.answers_hash.keys())[0]
registered_eval = env.answers_hash[answer_name]['ans_eval']

print(f"\nAnswer name: {answer_name}")
print(f"Evaluator: {registered_eval}")
print(f"Correct answer: {registered_eval.correct_answer}")

# Test different student submissions
test_cases = [
    ("4", "Exact correct answer"),
    ("4.0", "Correct with decimal"),
    ("4.001", "Within tolerance"),
    ("5", "Wrong answer"),
    ("3.5", "Close but not within tolerance"),
    ("abc", "Invalid input"),
    ("", "Empty input"),
]

print("\n" + "=" * 70)
print("STUDENT SUBMISSION TESTS:")
print("=" * 70)

for student_answer, description in test_cases:
    print(f"\n{description}:")
    print(f"  Student answer: '{student_answer}'")
    
    try:
        # Call the evaluator's evaluate method
        result = registered_eval.evaluate(student_answer)
        
        # Display results (AnswerResult object)
        if hasattr(result, 'score'):
            status = "✅ CORRECT" if result.correct else "❌ INCORRECT"
            print(f"  Status: {status}")
            print(f"  Score: {result.score}")
            if hasattr(result, 'message') and result.message:
                print(f"  Message: {result.message}")
            elif hasattr(result, 'error_message') and result.error_message:
                print(f"  Error: {result.error_message}")
        elif isinstance(result, dict):
            score = result.get('score', 0)
            correct = result.get('correct', False)
            message = result.get('message', '')
            
            status = "✅ CORRECT" if correct else "❌ INCORRECT"
            print(f"  Status: {status}")
            print(f"  Score: {score}")
            if message:
                print(f"  Message: {message}")
        else:
            print(f"  Result: {result}")
            
    except Exception as e:
        print(f"  ⚠️  Error: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("🎉 Answer evaluation testing complete!")
print("=" * 70)
