#!/usr/bin/env python3
"""Debug preprocessor output for a problem."""

from pg_translator.preprocessor import PGPreprocessor
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))


file_path = "tutorial/sample-problems/Algebra/ExpandedPolynomial.pg"

preprocessor = PGPreprocessor()
with open(file_path, 'r', encoding='utf-8') as f:
    perl_code = f.read()

python_code = preprocessor.preprocess(perl_code)

print("="*70)
print("PREPROCESSED PYTHON CODE")
print("="*70)
print(python_code)
print("="*70)
