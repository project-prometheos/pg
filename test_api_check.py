"""Test answer checking via API."""
import requests

# Test with correct answer
r = requests.post('http://localhost:8000/api/db/Algebra/ExpandedPolynomial/check',
                  json={'seed': 0, 'inputs': {'AnSwEr0001': 'x^2-6*x+4'}})
data = r.json()

print('=== TEST 1: Correct answer (with variables) ===')
print(f'All correct: {data.get("all_correct")}')
print(f'Score: {data.get("score")}')
results = data.get('results', {})
print(f'Has results: {len(results) > 0}')
if 'AnSwEr0001' in results:
    print(f'Correct: {results["AnSwEr0001"].get("correct")}')
    print(f'Message: {results["AnSwEr0001"].get("message", "No message")}')
print()

# Test with wrong answer
r2 = requests.post('http://localhost:8000/api/db/Algebra/ExpandedPolynomial/check',
                   json={'seed': 0, 'inputs': {'AnSwEr0001': 'x^2+2x+1'}})
data2 = r2.json()

print('=== TEST 2: Wrong answer ===')
print(f'All correct: {data2.get("all_correct")}')
print(f'Score: {data2.get("score")}')
results2 = data2.get('results', {})
if 'AnSwEr0001' in results2:
    print(f'Correct: {results2["AnSwEr0001"].get("correct")}')
    print(f'Message: {results2["AnSwEr0001"].get("message", "No message")}')
