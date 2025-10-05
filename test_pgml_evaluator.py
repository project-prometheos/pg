#!/usr/bin/env python3
"""Test PGML evaluator extraction."""

from pg_translator.preprocessor import PGPreprocessor
from pathlib import Path
import sys
sys.path.insert(0, "packages/pg_translator")

with open("webwork_ps1_pg/ps1-prob01.pg") as f:
    content = f.read()

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(content)

print("===== FULL PGML BLOCKS =====")
for i, line in enumerate(result.code.split("\n"), 1):
    print(f"{i:3}: {line}")
