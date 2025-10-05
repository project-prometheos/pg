"""Test pg_translator service integration."""

from app.services.pg_translator_service import get_pg_translator_service
import sys
sys.path.insert(0, 'D:/pg/apps/backend')


# Test problem with symbolic math
test_problem = """
DOCUMENT();
loadMacros("PG.pl", "PGML.pl", "MathObjects.pl");

Context("Numeric");
Context()->flags->set(reduceConstants=>0);

$a = random(1, 5);
$b = random(1, 5);
$ans = Compute("pi/$a");

BEGIN_PGML
What is [`\\pi/[$a]`]?

Answer: [_____]{$ans}
END_PGML

BEGIN_PGML_SOLUTION
The answer is [`\\pi/[$a]`].
END_PGML_SOLUTION

ENDDOCUMENT();
"""

print("=" * 60)
print("Testing pg_translator service")
print("=" * 60)

# Get service
service = get_pg_translator_service()
print("[OK] Service initialized")

# Test rendering
print("\n1. Testing rendering with seed=42...")
try:
    result = service.render_problem(test_problem, seed=42)
    print(f"   ✓ Rendered successfully")
    print(f"   - Inputs: {result['inputs']}")
    print(f"   - Answers: {list(result['answers'].keys())}")
    print(f"   - Statement length: {len(result['statement_html'])} chars")
    print(f"   - Solution length: {len(result['solution_html'])} chars")
    print(f"   - Errors: {result['errors']}")
    print(f"   - Warnings: {result['warnings']}")

    # Check for symbolic answer
    for ans_id, ans_meta in result['answers'].items():
        print(f"\n   Answer {ans_id}:")
        print(f"   - Correct value: {ans_meta['correct_value']}")
        print(f"   - Type: {ans_meta['type']}")

        # Check if it's symbolic (should contain 'pi' not decimal)
        if 'pi' in ans_meta['correct_value'].lower() or 'π' in ans_meta['correct_value']:
            print(
                f"   ✓ SYMBOLIC MATH PRESERVED! ({ans_meta['correct_value']})")
        else:
            print(f"   ⚠ WARNING: May be numeric instead of symbolic")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test answer checking
print("\n2. Testing answer checking...")
try:
    # First get the correct answer
    result = service.render_problem(test_problem, seed=42)
    correct_answer = None
    answer_id = None

    for aid, ans_meta in result['answers'].items():
        answer_id = aid
        correct_answer = ans_meta['correct_value']
        break

    if answer_id and correct_answer:
        print(f"   Testing with answer_id: {answer_id}")

        # Test correct answer
        check_result = service.check_answers(
            test_problem,
            seed=42,
            student_inputs={answer_id: correct_answer}
        )

        print(f"   ✓ Check completed")
        print(f"   - All correct: {check_result['all_correct']}")
        print(f"   - Score: {check_result['score']}")

        for aid, res in check_result['results'].items():
            print(f"\n   Answer {aid}:")
            print(f"   - Correct: {res['correct']}")
            print(f"   - Message: {res['message']}")
            print(f"   - Student: {res['student_answer']}")
            print(f"   - Expected: {res['correct_answer']}")

        # Test incorrect answer
        print("\n   Testing incorrect answer...")
        check_result2 = service.check_answers(
            test_problem,
            seed=42,
            student_inputs={answer_id: "999"}
        )

        print(f"   - All correct: {check_result2['all_correct']}")
        print(f"   - Score: {check_result2['score']}")

        if not check_result2['all_correct']:
            print("   ✓ Correctly marked as incorrect")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Migration test complete!")
print("=" * 60)
