#!/usr/bin/env python3
"""Check what's in the PGML block."""

from pg_translator.preprocessor import PGPreprocessor
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))


pg_code = """
DOCUMENT()

h = 3
k = 5
$vertexform = Compute("(x-$h)^2-$k")

BEGIN_PGML
The value is [$vertexform].
END_PGML

ENDDOCUMENT()
"""

print("="*70)
print("CHECKING PGML BLOCK CONTENT")
print("="*70)

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_code)

print("\nText blocks:")
for i, (block_type, content) in enumerate(result.text_blocks):
    print(f"\nBlock {i} ({block_type}):")
    print(repr(content))

print("\n" + "="*70)
print("Preprocessed Python code:")
print("="*70)
print(result.code)
