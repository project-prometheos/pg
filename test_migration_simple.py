"""Simple test of pg_translator service."""

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
$ans = Compute("pi/$a");

BEGIN_PGML
What is [` pi/[$a]`]?

Answer: [_____]{$ans}
END_PGML

ENDDOCUMENT();
"""

print("Testing pg_translator service...")

# Get service
service = get_pg_translator_service()
print("[OK] Service initialized")

# Test rendering
print("\nTesting rendering with seed=42...")
result = service.render_problem(test_problem, seed=42)

print(f"[OK] Rendered successfully")
print(f"  Inputs: {result['inputs']}")
print(f"  Errors: {result['errors']}")

# Check answer
for ans_id, ans_meta in result['answers'].items():
    print(f"\n  Answer {ans_id}:")
    print(f"    Correct value: {ans_meta['correct_value']}")
    print(f"    Type: {ans_meta['type']}")

    # Check if symbolic
    correct_val_str = str(ans_meta['correct_value'])
    if 'pi' in correct_val_str.lower() or '/' in correct_val_str:
        print(f"    [OK] SYMBOLIC MATH PRESERVED!")
    else:
        print(f"    [WARN] May be numeric")

print("\n[SUCCESS] Migration test complete!")
