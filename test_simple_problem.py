#!/usr/bin/env python3
"""
Test: Can we use pg_macros directly to create a problem?
"""

import sys
from pathlib import Path

# Add packages
repo_root = Path(__file__).parent
for pkg in ["pg_macros", "pg_math", "pg_answer"]:
    sys.path.insert(0, str(repo_root / "packages" / pkg))

# Import macros directly
from pg_macros.core import (
    TEXT, ANS, DOCUMENT, ENDDOCUMENT,
    ans_rule, PGEnvironment, set_environment
)
from pg_macros.answers import num_cmp

print("=" * 60)
print("TEST: Simple PG Problem Using Macros Directly")
print("=" * 60)

# Create environment
env = PGEnvironment()
set_environment(env)

# Problem code
DOCUMENT()

TEXT("What is 2 + 2? ")
TEXT(ans_rule(20))

ANS(num_cmp(4))

TEXT("<br/><br/>What is 3 * 7? ")
TEXT(ans_rule(20))

ANS(num_cmp(21))

result = ENDDOCUMENT()

# Display results
print("\n✅ PROBLEM GENERATED SUCCESSFULLY!\n")
print("Body Text:")
print("-" * 60)
print(env.get_body_text())
print("-" * 60)

print("\nAnswers:")
for i, (name, evaluator) in enumerate(env.answers.items(), 1):
    print(f"  Answer {i} ({name}): {evaluator}")

print("\n" + "=" * 60)
print("🎉 SUCCESS! Macros work end-to-end!")
print("=" * 60)
