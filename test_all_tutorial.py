#!/usr/bin/env python3
"""Test all tutorial sample problems."""

from pathlib import Path
from pg_translator import PGTranslator
import os
os.environ['PYPG_DISABLE_LOGGING'] = '1'


tutorial_dir = Path('tutorial/sample-problems')
all_problems = sorted(tutorial_dir.rglob('*.pg'))

print(f"Testing {len(all_problems)} tutorial problems...\n")

results = []
working = []
with_stmt = []
with_ans = []
errors = []

for i, prob_path in enumerate(all_problems, 1):
    translator = PGTranslator()
    result = translator.translate(str(prob_path), seed=1234)

    has_stmt = len(result.statement_html or '') > 0
    has_ans = len(result.answer_blanks or {}) > 0
    has_error = bool(result.errors)

    if has_stmt and has_ans:
        working.append(prob_path)
    if has_stmt:
        with_stmt.append(prob_path)
    if has_ans:
        with_ans.append(prob_path)
    if has_error:
        errors.append(
            (prob_path, result.errors[0] if result.errors else 'Unknown'))

    # Print progress every 20 problems
    if i % 20 == 0:
        print(f"Tested {i}/{len(all_problems)}...")

print(f"\n{'='*70}")
print(f"RESULTS: {len(all_problems)} total problems")
print(f"{'='*70}")
print(
    f"✅ Full rendering (stmt + ans): {len(working)}/{len(all_problems)} ({len(working)*100//len(all_problems)}%)")
print(
    f"📄 With statement:              {len(with_stmt)}/{len(all_problems)} ({len(with_stmt)*100//len(all_problems)}%)")
print(
    f"📝 With answers:                {len(with_ans)}/{len(all_problems)} ({len(with_ans)*100//len(all_problems)}%)")
print(
    f"❌ With errors:                 {len(errors)}/{len(all_problems)} ({len(errors)*100//len(all_problems)}%)")

if working:
    print(f"\n{'='*70}")
    print(f"WORKING PROBLEMS ({len(working)} total):")
    print(f"{'='*70}")
    for prob in working[:50]:  # Show first 50
        rel_path = prob.relative_to('tutorial/sample-problems')
        print(f"  ✅ {rel_path}")
    if len(working) > 50:
        print(f"  ... and {len(working) - 50} more")

print()
