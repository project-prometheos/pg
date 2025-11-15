#!/usr/bin/env python3
"""Test Vector creation in sandbox context."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path("d:/pg/packages")))

from pg.translator.pg_translator import PGTranslator

# Create a simple problem that uses non_zero_vector3D
problem_code = """
Context('Vector');
$U = non_zero_vector3D(-9, 9, 1);
$Uarray = $U->value;
"""

translator = PGTranslator()
# Translate directly to check sandbox behavior
result = translator.translate(problem_code, seed=12345)

print("Errors:")
print(result.errors)
print("\nOutput:")
print(result.output)
