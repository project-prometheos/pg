"""Comprehensive test of multiple problems."""

import requests

problems = [
    "Algebra/ExpandedPolynomial",
    "Algebra/AlgebraicFractionAnswer",
    "Calculus/AnswerUpToMultiple",
]

print("=" * 70)
print("PROBLEM STATUS WITH PYGMENT PREPROCESSOR")
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
        
        status = "✅ OK" if not has_errors and has_statement else "❌ ERROR"
        
        print(f"\n{problem}:")
        print(f"  Status: {status}")
        print(f"  Statement: {has_statement}")
        print(f"  Inputs: {num_inputs}")
        
        if has_errors:
            error = data['errors'][0]
            # Extract just the error type
            if 'SyntaxError:' in error:
                error_msg = error.split('SyntaxError:')[1].split('(')[0].strip()
                print(f"  Error: SyntaxError - {error_msg}")
            elif 'NameError:' in error:
                error_msg = error.split('NameError:')[1].split('\n')[0].strip()
                print(f"  Error: NameError - {error_msg}")
            else:
                print(f"  Error: {error[:80]}")
            broken.append(problem)
        else:
            working.append(problem)
            
    except Exception as e:
        print(f"\n{problem}:")
        print(f"  Status: ❌ FAILED TO TEST")
        print(f"  Error: {str(e)[:80]}")
        broken.append(problem)

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✅ Working: {len(working)}/{len(problems)}")
for p in working:
    print(f"   - {p}")
print(f"\n❌ Broken: {len(broken)}/{len(problems)}")
for p in broken:
    print(f"   - {p}")
