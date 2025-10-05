#!/usr/bin/env python3
"""Debug prob02."""

import sys
sys.path.insert(0, "packages/pg_translator")
from pg_translator.preprocessor import PGPreprocessor

with open("webwork_ps1_pg/ps1-prob02.pg") as f:
    content = f.read()

print("=== ORIGINAL ===")
print(content)
print("\n=== PREPROCESSING ===")

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(content)

print("=== PREPROCESSED ===")
for i, line in enumerate(result.code.split("\n"), 1):
    if "PGML" in line or "pgml" in line:
        print(f"{i:3}: {line}")
