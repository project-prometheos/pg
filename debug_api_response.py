"""Debug API response."""
import requests
import json

r = requests.post('http://localhost:8000/api/db/Algebra/ExpandedPolynomial/check',
                  json={'seed': 0, 'inputs': {'AnSwEr0001': 'x^2-6*x+4'}})

print('Status:', r.status_code)
print('Response text:', r.text)
print()
print('Parsed JSON:')
print(json.dumps(r.json(), indent=2))
