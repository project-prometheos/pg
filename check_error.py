import requests
r = requests.get('http://localhost:8000/api/db/Algebra/AlgebraicFractionAnswer/render?seed=0')
data = r.json()
if data.get('errors'):
    print(data['errors'][0][:1000])
