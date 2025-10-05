import requests

problems = [1, 2, 3, 5, 10]

print("Testing PS1 problems for LaTeX conversion:")
print("=" * 60)

for i in problems:
    problem_id = f"PS1/Problem-{i:02d}"
    try:
        r = requests.get(f'http://localhost:8000/api/db/{problem_id}/render?seed=0')
        data = r.json()
        
        statement = data['statement_html']
        has_raw_inline = '\\(' in statement
        has_raw_display = '\\[' in statement
        has_raw = has_raw_inline or has_raw_display
        
        status = '❌' if has_raw else '✅'
        print(f"{status} {problem_id}: Raw LaTeX = {has_raw}")
        
        if has_raw:
            # Show a snippet
            snippet = statement[:200].replace('\n', ' ')
            print(f"   Snippet: {snippet}...")
    except Exception as e:
        print(f"❌ {problem_id}: Error - {e}")

print("=" * 60)
