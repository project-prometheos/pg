#!/usr/bin/env python
"""Test PS1/Problem-02 API endpoint"""
import requests
import json

url = "http://localhost:8000/api/problems/PS1/Problem-02?seed=0"

print(f"Testing: {url}")
print("=" * 80)

try:
    resp = requests.get(url, timeout=5)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        statement = data.get('statement_tex', '')
        
        print("\nStatement (first 400 chars):")
        print("-" * 80)
        print(statement[:400])
        print("-" * 80)
        
        # Check conversion
        print("\n✓ Has $ delimiters:" if '$' in statement else "\n✗ Missing $ delimiters:", '$' in statement)
        print("✗ Has PGML \\(...\\):" if '\\(' in statement else "✓ No PGML \\(...\\):", '\\(' in statement)
        
        # Show full JSON for debugging
        print("\nFull response:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {resp.text}")
        
except Exception as e:
    print(f"Exception: {e}")
