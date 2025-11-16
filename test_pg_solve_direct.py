#!/usr/bin/env python3
"""Test pg_solve directly to verify answer checking works."""
import sys
from pathlib import Path

# Setup path like pg_solve does
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))

# Disable logging
import os
os.environ['PYPG_DISABLE_LOGGING'] = '1'

from pg.translator import PGTranslator

def strip_html(html_text):
    """Remove HTML tags for terminal display."""
    import re
    html_text = html_text.replace('\\\\(', '\\(')
    html_text = html_text.replace('\\\\)', '\\)')
    html_text = html_text.replace('\\\\[', '\\[')
    html_text = html_text.replace('\\\\]', '\\]')
    html_text = re.sub(r'\[[^\].]*\\_[^\].]*\]', '___', html_text)
    text = re.sub(r'<[^>]+>', '', html_text)
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ')
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

# Test
print("=" * 70)
print("TESTING PG_SOLVE DIRECTLY")
print("=" * 70)

problem_file = "tutorial/sample-problems/Algebra/FractionAnswer.pg"
seed = 12345
translator = PGTranslator()

print(f"\nProblem: {Path(problem_file).name}")
print(f"Seed: {seed}\n")

# First translation - render problem
print("Step 1: Rendering problem...")
result = translator.translate(problem_file, seed=seed)

if result.errors:
    print(f"ERROR: {result.errors}")
    sys.exit(1)

print(f"  Answer blanks: {len(result.answer_blanks)}")
for name, spec in result.answer_blanks.items():
    print(f"    - {name}: {type(spec)}")
    if isinstance(spec, dict):
        print(f"      Keys: {list(spec.keys())}")

# Display problem
print(f"\nProblem statement:")
print(strip_html(result.statement_html))

# Simulate user input
print(f"\nStep 2: Simulating user answer '3/2'...")
user_answers = {"AnSwEr0001": "3/2"}

# Second translation - check answers
print("Step 3: Checking answers...")
result2 = translator.translate(problem_file, seed=seed, inputs=user_answers)

print(f"  Errors: {result2.errors}")
print(f"  Answer results: {result2.answer_results}")

if result2.answer_results:
    print("\n  ✓✓✓ ANSWER CHECKING WORKS! ✓✓✓\n")
    for name, ans_result in result2.answer_results.items():
        print(f"  Answer {name}:")
        print(f"    Score: {ans_result.score}")
        print(f"    Correct: {ans_result.correct}")
        if ans_result.answer_message:
            print(f"    Message: {ans_result.answer_message}")
else:
    print("\n  ✗✗✗ ANSWER CHECKING FAILED! ✗✗✗")
    print(f"  Result object: {result2}")

print("\n" + "=" * 70)
