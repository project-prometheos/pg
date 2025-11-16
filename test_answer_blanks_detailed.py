#!/usr/bin/env python3
"""Detailed test of answer blanks throughout the pipeline."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
import os
os.environ['PYPG_DISABLE_LOGGING'] = '1'

from pg.translator import PGTranslator

problem_file = "tutorial/sample-problems/Algebra/FractionAnswer.pg"
translator = PGTranslator()

print("=" * 70)
print("DETAILED ANSWER BLANKS TEST")
print("=" * 70)

# Patch the executor to see what's in environment.answers
original_render_text = None

def patch_executor():
    from pg.translator.executor import PGEnvironment
    global original_render_text
    original_render_text = PGEnvironment.render_text

    def new_render_text(self):
        result = original_render_text(self)
        print("\n[PATCH] In PGEnvironment.render_text():")
        print(f"  environment.answers keys: {list(self.answers.keys())}")
        for name, entry in self.answers.items():
            print(f"    {name}: type={type(entry)}, ", end="")
            if isinstance(entry, dict):
                print(f"keys={list(entry.keys())}")
                if 'options' in entry:
                    print(f"           options={entry['options']}")
            else:
                print(f"value={entry}")
        return result

    PGEnvironment.render_text = new_render_text

patch_executor()

print("\nTranslating problem...")
result = translator.translate(problem_file, seed=75965)

print(f"\nAfter translate():")
print(f"  result.answer_blanks keys: {list(result.answer_blanks.keys())}")
for name, entry in result.answer_blanks.items():
    print(f"    {name}: type={type(entry)}")
    if isinstance(entry, dict):
        print(f"      keys={list(entry.keys())}")
        if 'options' in entry:
            print(f"      options={entry['options']}")
        else:
            print(f"      ✗ NO OPTIONS KEY!")
    else:
        print(f"      value={entry}")

print("\n" + "=" * 70)
