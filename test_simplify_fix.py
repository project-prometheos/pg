#!/usr/bin/env python3
"""Test if the Simplify = {} issue is fixed."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.') / "packages" / "pg_translator"))

from pg.translator.pg_preprocessor_pygment import PGPreprocessor

# Test PGML block with Answer = [_]
test_pgml = """BEGIN_PGML
Simplify [``\\frac{6}{4}``].

Answer = [_]{$answer->cmp()}
END_PGML"""

test_code = f"""
DOCUMENT();
$answer = Compute('3/2');
{test_pgml}
ENDDOCUMENT();
"""

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(test_code, standalone=True)

print("=== PREPROCESSED CODE (checking for 'Simplify = {{}}') ===")
print()
# Find and show the PGML block
lines = result.code.split('\n')
in_block = False
for i, line in enumerate(lines):
    if 'PGML_BLOCK' in line:
        in_block = True
    if in_block:
        print(f"{i:3d}: {line}")
        if "'''" in line and i > 5:  # Show until end of block
            break

print()
if 'Simplify = {}' in result.code:
    print("[FAILED] 'Simplify = {}' still present in output")
    sys.exit(1)
else:
    print("[PASSED] 'Simplify = {}' has been removed!")
    sys.exit(0)
