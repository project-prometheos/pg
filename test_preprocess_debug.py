#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""Debug script to test preprocessing of BEGIN_PGML"""

"""Debug script to test preprocessing of BEGIN_PGML""""""Debug preprocessor output for a problem."""


import sys
from app.db import ProblemDBimport sysfrom pg_translator.preprocessor import PGPreprocessor
from app.db import ProblemDB
from pg_translator.preprocessor import PGPreprocessor
sys.path.insert(0, 'apps/backend')


sys.path.insert(0, 'apps/backend')import sys

# Get problem

db = ProblemDB.get_instance()from pathlib import Path

problem = db.get_by_id('Algebra/AlgebraicFractionAnswer')


print("=" * 80)

# Add packages to path
print("ORIGINAL PG SOURCE (last 1500 chars):")from pg_translator import PGPreprocessor

print("=" * 80)

print(problem['pg_source'][-1500:])sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))

print("=" * 80)

# Get problem

# Preprocess it

preprocessor = PGPreprocessor()db = ProblemDB.get_instance()

preprocessed = preprocessor.preprocess(problem['pg_source'])

problem = db.get_by_id('Algebra/AlgebraicFractionAnswer')file_path = "tutorial/sample-problems/Algebra/ExpandedPolynomial.pg"

print("\nPREPROCESSED CODE (last 1500 chars):")

print("=" * 80)

print(preprocessed[-1500:])

print("=" * 80)print("=" * 80)preprocessor = PGPreprocessor()


# Check if PGML() is in the preprocessed codeprint("ORIGINAL PG SOURCE (last 1500 chars):")with open(file_path, 'r', encoding='utf-8') as f:

if 'PGML(' in preprocessed:

    print("\n✓ PGML() function call found in preprocessed code")print("=" * 80)    perl_code = f.read()

    # Count how many times

    count = preprocessed.count('PGML(')print(problem['pg_source'][-1500:])

    print(f"  Found {count} PGML() calls")

else:
    print("=" * 80)python_code = preprocessor.preprocess(perl_code)

   print("\n✗ NO PGML() function calls found in preprocessed code!")


# Preprocess itprint("="*70)

preprocessor = PGPreprocessor()print("PREPROCESSED PYTHON CODE")

preprocessed = preprocessor.preprocess(problem['pg_source'])print("="*70)

print(python_code)

print("\nPREPROCESSED CODE (last 1500 chars):")print("="*70)

print("=" * 80)
print(preprocessed[-1500:])
print("=" * 80)

# Check if PGML() is in the preprocessed code
if 'PGML(' in preprocessed:
    print("\n✓ PGML() function call found in preprocessed code")
    # Count how many times
    count = preprocessed.count('PGML(')
    print(f"  Found {count} PGML() calls")
else:
    print("\n✗ NO PGML() function calls found in preprocessed code!")
