import requests

problem_id = "PS1/Problem-25"
seed = 0

# Test various mathematical expressions that should evaluate to pi
test_cases = [
    ("pi", "symbolic pi"),
    ("Pi", "uppercase Pi"),
    ("π", "unicode pi"),
    ("3.141592653589793", "numeric pi"),
    ("2*pi/2", "expression: 2π/2"),
    ("pi*1", "expression: π×1"),
    ("arccos(-1)", "arccos(-1) = π"),
    ("2*arcsin(1)", "2×arcsin(1) = π"),
    ("4*arctan(1)", "4×arctan(1) = π"),
]

print(f"Testing {problem_id} with various expressions:")
print("=" * 70)

for answer, description in test_cases:
    try:
        r = requests.post(
            f'http://localhost:8000/api/db/{problem_id}/check',
            json={'seed': seed, 'inputs': {'AnSwEr0001': answer}}
        )
        data = r.json()

        result = data['results']['AnSwEr0001']
        correct = result['correct']
        score = result['score']
        message = result.get('message', '')

        status = '✅' if correct else '❌'
        print(f"{status} {description:30s} '{answer}'")
        if not correct and message:
            print(f"   Message: {message}")
    except Exception as e:
        print(f"❌ {description:30s} '{answer}' - Error: {e}")

print("=" * 70)
