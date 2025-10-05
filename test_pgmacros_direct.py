"""
Direct test of pg_macros functions to verify they work.
"""

print("=" * 70)
print("TEST: Direct pg_macros Function Calls")
print("=" * 70)

# Test importing pg_macros functions
try:
    from pg_macros.core.pg_core import DOCUMENT, TEXT, ANS, ENDDOCUMENT, get_environment
    from pg_macros.core.pg_basic_macros import ans_rule
    from pg_answer.evaluators.numeric import NumericEvaluator

    # Stub for beginproblem (not yet implemented)
    def beginproblem():
        return ""

    print("\n✅ Successfully imported pg_macros functions")

    # Test creating a problem
    print("\n▶️  Creating problem...")

    DOCUMENT()
    TEXT(beginproblem())

    a = 7
    b = 3
    answer = a + b

    TEXT("<h2>Simple Addition Problem</h2>")
    TEXT(f"<p>Calculate {a} + {b}.</p>")
    TEXT(f"<p>Answer: {ans_rule(20)}</p>")

    # Use NumericEvaluator directly
    evaluator = NumericEvaluator(correct_answer=answer)
    ANS(evaluator)

    # Get results
    text, header, post_header, answers_hash, flags = ENDDOCUMENT()

    print("✅ Problem created successfully!")

    # Display results
    print("\n" + "=" * 70)
    print("GENERATED HTML:")
    print("=" * 70)
    print(text)

    print("\n" + "=" * 70)
    print("ANSWERS:")
    print("=" * 70)
    for name, ans_entry in answers_hash.items():
        print(f"\nAnswer: {name}")
        if isinstance(ans_entry, dict) and 'ans_eval' in ans_entry:
            evaluator = ans_entry['ans_eval']
            print(f"  Evaluator: {type(evaluator).__name__}")
            if hasattr(evaluator, 'correct_answer'):
                print(f"  Correct answer: {evaluator.correct_answer}")
        else:
            print(f"  Direct evaluator: {type(ans_entry).__name__}")
            if hasattr(ans_entry, 'correct_answer'):
                print(f"  Correct answer: {ans_entry.correct_answer}")

    print("\n" + "=" * 70)
    print("🎉 Direct pg_macros test SUCCESSFUL!")
    print("=" * 70)
    print("""
This proves pg_macros functions work when called directly.
The issue is getting them to work inside pg_translator's sandbox.
""")

except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
