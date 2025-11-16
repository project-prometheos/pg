#!/usr/bin/env python3
"""Test the HTML output rendering."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.') / "packages" / "pg_translator"))
import os
os.environ['PYPG_DISABLE_LOGGING'] = '1'

from pg.translator import PGTranslator

problem_file = "tutorial/sample-problems/Algebra/FractionAnswer.pg"
translator = PGTranslator()

result = translator.translate(problem_file, seed=75965)

print("=" * 70)
print("HTML STATEMENT (first 1000 chars)")
print("=" * 70)
print(result.statement_html[:1000])
print("\n" + "=" * 70)
print("\nChecking for 'Simplify = {}'...")
if "Simplify = {}" in result.statement_html:
    print("[FAILED] 'Simplify = {}' still in HTML output")
else:
    print("[PASSED] 'Simplify = {}' not found in HTML output")
