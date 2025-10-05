"""Test string interpolation comprehensively."""

from pg_translator.pg_preprocessor_pygment import PGPreprocessor

test_cases = [
    # (input, expected_substring, description)
    ('$a = "Hello $name";', 'f"Hello {name}"', "Simple variable"),
    ('$b = "x^2+$c*x+$d";', 'f"x^2+{c}*x+{d}"', "Multiple variables"),
    ("$c = 'No $interpolation';", "'No $interpolation'", "Single quotes (no interpolation)"),
    ('$d = "No variables here";', '"No variables here"', "No variables"),
    ('$e = "$a + $b";', 'f"{a} + {b}"', "Variables with spaces"),
    ('$formula = Compute("(x-$h)^2-$k");', 'f"(x-{h})^2-{k}"', "Formula with variables"),
]

prep = PGPreprocessor()

print("=" * 70)
print("STRING INTERPOLATION TESTS")
print("=" * 70)

passed = 0
failed = 0

for input_code, expected, description in test_cases:
    result = prep.preprocess(input_code, use_sandbox_macros=False)
    output = result.code.strip()
    
    if expected in output:
        print(f"✅ {description}")
        print(f"   Input:  {input_code}")
        print(f"   Output: {output}")
        passed += 1
    else:
        print(f"❌ {description}")
        print(f"   Input:    {input_code}")
        print(f"   Expected: {expected}")
        print(f"   Output:   {output}")
        failed += 1
    print()

print("=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 70)
