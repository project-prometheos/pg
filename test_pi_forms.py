import requests

problem_id = "PS1/Problem-25"
seed = 0

# Test different forms of pi
test_cases = [
    ("3.14159", "numeric approximation"),
    ("pi", "lowercase pi"),
    ("Pi", "uppercase Pi"),
    ("π", "unicode pi symbol"),
    ("3.141592653589793", "high precision"),
]

print(f"Testing {problem_id} with different pi representations:")
print("=" * 70)

for answer, description in test_cases:
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
    print(f"{status} {description:25s} '{answer}'")
    print(f"   Score: {score}, Message: {message}")
    print()

print("=" * 70)
