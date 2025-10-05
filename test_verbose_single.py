#!/usr/bin/env python3
"""Quick verbose test of a single problem."""

from pg_translator import PGTranslator
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))


file_path = "tutorial/sample-problems/Algebra/ExpandedPolynomial.pg"
translator = PGTranslator()
result = translator.translate(file_path, seed=1234)

print("="*70)
print(f"Testing: {file_path}")
print("="*70)
print(
    f"\nStatement HTML: {len(result.statement_html) if result.statement_html else 0} chars")
if result.statement_html:
    print(result.statement_html)
else:
    print("  NONE")

print(
    f"\nAnswer Blanks: {len(result.answer_blanks) if result.answer_blanks else 0}")
if result.answer_blanks:
    for i, blank in enumerate(result.answer_blanks, 1):
        print(f"  {i}. Name: {blank.get('name')}")
        print(f"     Correct: {blank.get('correct_ans')}")
else:
    print("  NONE")

print(
    f"\nSolution HTML: {len(result.solution_html) if result.solution_html else 0} chars")
if result.solution_html:
    print(result.solution_html)
else:
    print("  NONE")

print(f"\nHint HTML: {len(result.hint_html) if result.hint_html else 0} chars")
if result.hint_html:
    print(result.hint_html)
else:
    print("  NONE")

print("\n" + "="*70)
print("Raw result object attributes:")
print("="*70)
print(f"statement_html: {result.statement_html!r}")
print(f"answer_blanks: {result.answer_blanks!r}")
print(f"solution_html: {result.solution_html!r}")
print(f"hint_html: {result.hint_html!r}")
