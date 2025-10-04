#!/usr/bin/env python
"""Test the API endpoint to verify PS1/Problem-02 loads correctly"""
import requests
import json

url = "http://localhost:8000/api/problems/PS1/Problem-02?seed=123"

print(f"Testing URL: {url}")
print("=" * 80)

try:
    resp = requests.get(url, timeout=5)
    print(f"Status Code: {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        print("\n✓ SUCCESS! Problem loaded successfully")
        print("\nStatement preview:")
        print("-" * 80)
        statement = data.get('statement_tex', '')
        # Show first 300 chars
        print(statement[:300])
        if len(statement) > 300:
            print("...")
        print("-" * 80)

        # Check for proper math conversion
        if '$\\cot(x)' in statement:
            print("\n✓ Math properly converted to $ delimiters")
        else:
            print("\n✗ Math NOT converted properly")

        if '[____]' in statement:
            print("✓ Answer blanks properly converted")
        else:
            print("✗ Answer blanks NOT converted properly")

    else:
        print(f"\n✗ ERROR: {resp.status_code}")
        print(resp.text)

except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend server on port 8000")
    print("Make sure the backend is running: cd apps/backend && python -m uvicorn app.main:app --reload")
except Exception as e:
    print(f"✗ Error: {e}")
