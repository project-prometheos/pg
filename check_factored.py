import requests
r = requests.get('http://localhost:8000/api/db/Algebra/FactoredPolynomial/render?seed=0')
data = r.json()
print('Status:', 'OK' if not data.get('errors') else 'ERROR')
print('Has statement:', bool(data.get('statement_html')))
print('Inputs:', len(data.get('inputs', [])))
if data.get('statement_html'):
    print('Statement preview:', data['statement_html'][:100])
if data.get('errors'):
    print('Error:', data['errors'][0][:300])
