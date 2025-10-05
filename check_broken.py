"""Check specific broken problems."""

import requests

problems = [
    "Algebra/FactoredPolynomial",
    "Algebra/SimpleFactoring",
]

for problem in problems:
    print("=" * 70)
    print(f"Problem: {problem}")
    print("=" * 70)
    
    r = requests.get(f'http://localhost:8000/api/db/{problem}/render?seed=0')
    data = r.json()
    
    if data.get('errors'):
        print(data['errors'][0])
    print()
