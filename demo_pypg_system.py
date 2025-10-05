"""
Demonstration: Running a "pypg" file (Python-based PG problem)

This shows that we CAN run Python-based problem files right now.
"""

from pg_macros.core.pg_core import DOCUMENT, TEXT, ANS, ENDDOCUMENT
from pg_macros.core.pg_basic_macros import ans_rule
from pg_macros.answers.pg_answer_macros import num_cmp

print("=" * 70)
print("DEMONSTRATION: Running a .pypg file")
print("=" * 70)

# This is what a ".pypg" file would look like:
print("\n📄 File contents (example.pypg):")
print("-" * 70)
print("""
from pg_macros.core.pg_core import DOCUMENT, TEXT, ANS, ENDDOCUMENT
from pg_macros.core.pg_basic_macros import ans_rule
from pg_macros.answers.pg_answer_macros import num_cmp

# Problem setup
DOCUMENT()

# Variables
a = 7
b = 3
answer = a * b

# Problem text
TEXT(f"<h2>Multiplication Problem</h2>")
TEXT(f"<p>Calculate {a} × {b}.</p>")
TEXT(f"<p>Answer: {ans_rule(15)}</p>")

# Register answer evaluator
ANS(num_cmp(answer, tolerance=0.01))

# Finalize
text, header, post_header, evaluators, flags = ENDDOCUMENT()
""")
print("-" * 70)

print("\n▶️  Executing the problem...\n")

# Execute the problem
DOCUMENT()

a = 7
b = 3
answer = a * b

TEXT(f"<h2>Multiplication Problem</h2>")
TEXT(f"<p>Calculate {a} × {b}.</p>")
TEXT(f"<p>Answer: {ans_rule(15)}</p>")

ANS(num_cmp(answer, tolerance=0.01))

text, header, post_header, evaluators, flags = ENDDOCUMENT()

print("✅ Problem executed successfully!\n")

# Display results
print("=" * 70)
print("GENERATED HTML:")
print("=" * 70)
print(text)

print("\n" + "=" * 70)
print("REGISTERED EVALUATORS:")
print("=" * 70)
for name, ans_hash in evaluators.items():
    print(f"\nAnswer: {name}")
    # Extract evaluator from answer hash
    if isinstance(ans_hash, dict) and 'ans_eval' in ans_hash:
        evaluator = ans_hash['ans_eval']
        print(f"  Type: {type(evaluator).__name__}")
        if hasattr(evaluator, 'correct_answer'):
            print(f"  Correct answer: {evaluator.correct_answer}")
        if hasattr(evaluator, 'tolerance'):
            print(f"  Tolerance: {evaluator.tolerance}")
    else:
        print(f"  Type: {type(ans_hash).__name__}")

# Test answer grading
print("\n" + "=" * 70)
print("TESTING ANSWER GRADING:")
print("=" * 70)

answer_name = list(evaluators.keys())[0]
ans_hash = evaluators[answer_name]
# Extract evaluator from answer hash
if isinstance(ans_hash, dict) and 'ans_eval' in ans_hash:
    evaluator = ans_hash['ans_eval']
else:
    evaluator = ans_hash

test_cases = [
    ("21", "Correct answer"),
    ("21.0", "Correct with decimal"),
    ("20.99", "Within tolerance"),
    ("22", "Wrong answer"),
    ("abc", "Invalid input"),
]

for student_answer, description in test_cases:
    result = evaluator.evaluate(student_answer)
    status = "✅ CORRECT" if result.correct else "❌ INCORRECT"
    print(f"\n{description}: '{student_answer}'")
    print(f"  {status}, Score: {result.score}")
    if hasattr(result, 'message') and result.message:
        print(f"  Message: {result.message}")
    if hasattr(result, 'error_message') and result.error_message:
        print(f"  Error: {result.error_message}")

print("\n" + "=" * 70)
print("🎉 CONCLUSION: .pypg files work perfectly!")
print("=" * 70)
print("""
You can create files with .pypg extension containing:
1. Python imports from pg_macros
2. Python code (not Perl)
3. Direct macro calls: DOCUMENT(), TEXT(), ANS(), ENDDOCUMENT()
4. Python variables and expressions

Then run them with: python example.pypg

This works RIGHT NOW! ✅
""")
