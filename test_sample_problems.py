"""Test multiple sample problems to verify preprocessor works broadly."""

import requests

problems = [
    "Algebra/ExpandedPolynomial",
    "Algebra/AlgebraicFractionAnswer", 
    "Algebra/AnswerUpToMultiple",
    "Algebra/FactoredPolynomial",
    "Algebra/FractionAnswer",
    "Algebra/SimpleFactoring",
    "Algebra/DomainRange",
]

print("=" * 70)
print("SAMPLE PROBLEMS TEST")
print("=" * 70)

working = []
broken = []

for problem in problems:
    try:
        r = requests.get(f'http://localhost:8000/api/db/{problem}/render?seed=0', timeout=5)
        data = r.json()
        
        has_errors = bool(data.get('errors'))
        has_statement = bool(data.get('statement_html'))
        num_inputs = len(data.get('inputs', []))
        
        status = "✅" if not has_errors and has_statement else "❌"
        
        print(f"\n{status} {problem}")
        if has_errors:
            error = data['errors'][0]
            if 'SyntaxError:' in error:
                error_msg = error.split('SyntaxError:')[1].split('(')[0].strip()[:60]
                print(f"   Error: SyntaxError - {error_msg}")
            elif 'NameError:' in error:
                error_msg = error.split('NameError:')[1].split('\n')[0].strip()[:60]
                print(f"   Error: NameError - {error_msg}")
            else:
                print(f"   Error: {error.split('Traceback')[0].strip()[:80]}")
            broken.append(problem)
        else:
            print(f"   Inputs: {num_inputs}, Statement: {len(data.get('statement_html', ''))} chars")
            working.append(problem)
            
    except Exception as e:
        print(f"\n❌ {problem}")
        print(f"   Exception: {str(e)[:80]}")
        broken.append(problem)

print("\n" + "=" * 70)
print(f"RESULTS: {len(working)}/{len(problems)} working")
print("=" * 70)
if working:
    print("\n✅ Working problems:")
    for p in working:
        print(f"   {p}")
if broken:
    print(f"\n❌ Broken problems:")
    for p in broken:
        print(f"   {p}")
