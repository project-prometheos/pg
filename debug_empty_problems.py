"""Debug why some problems have empty statements."""

import requests

problems = [
    "Calculus/AnswerUpToMultiple",
    "Algebra/DifferenceQuotient", 
    "Algebra/FunctionComposition",
]

for problem in problems:
    print("=" * 70)
    print(f"Problem: {problem}")
    print("=" * 70)
    
    r = requests.get(f'http://localhost:8000/api/db/{problem}/render?seed=0')
    data = r.json()
    
    print(f"Errors: {len(data.get('errors', []))}")
    if data.get('errors'):
        for i, err in enumerate(data.get('errors', [])[:2]):
            print(f"\nError {i+1}:")
            print(err[:500])
    
    print(f"\nWarnings: {len(data.get('warnings', []))}")
    if data.get('warnings'):
        for i, warn in enumerate(data.get('warnings', [])[:2]):
            print(f"  Warning {i+1}: {warn[:100]}")
    
    print(f"\nStatement HTML: {len(data.get('statement_html', ''))} chars")
    if data.get('statement_html'):
        print(f"  Preview: {data['statement_html'][:100]}")
    
    print(f"Answer blanks: {len(data.get('inputs', []))}")
    print(f"Answers dict: {len(data.get('answers', {}))}")
    print()
