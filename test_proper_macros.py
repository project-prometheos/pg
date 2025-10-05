#!/usr/bin/env python3
"""
Proper test: Use pg_macros with correct API
"""

from pg_macros.core.pg_basic_macros import ans_rule
from pg_macros.core.pg_core import PGEnvironment, get_environment, set_environment, TEXT, DOCUMENT, ENDDOCUMENT
import sys
from pathlib import Path

repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "packages" / "pg_macros"))


print("=" * 70)
print("TEST: Creating a Simple PG Problem with Macros")
print("=" * 70)

# Create environment with settings
envir = {
    "problemSeed": 123,
    "displayMode": "HTML",
    "showPartialCorrectAnswers": 1,
    "ANSWER_PREFIX": "AnSwEr",
}

# Put envir in globals so DOCUMENT() can find it
globals()['envir'] = envir

print("\n✅ Environment settings prepared\n")

# Start problem - this will create PGEnvironment
DOCUMENT()
print("✅ DOCUMENT() called (environment auto-created)")

# Get the environment created by DOCUMENT()
env = get_environment()
print(f"✅ Environment retrieved: {env}")

# Add problem text
TEXT("<h3>Simple Arithmetic Problem</h3>")
TEXT("<p>What is 2 + 2?</p>")
TEXT("<p>Answer: ")
TEXT(ans_rule(20))
TEXT("</p>")

print("✅ TEXT() and ans_rule() called")

# End problem
result = ENDDOCUMENT()
print("✅ ENDDOCUMENT() called")

# Display results
print("\n" + "=" * 70)
print("GENERATED PROBLEM:")
print("=" * 70)
print(env.get_text())
print("=" * 70)

print("\n✅ SUCCESS! Problem generated using macros!")
print("\nNext step: Add answer evaluation (num_cmp)")
