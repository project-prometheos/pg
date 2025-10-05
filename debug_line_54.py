"""Debug the AlgebraicFractionAnswer preprocessing."""

from pathlib import Path
from pg_translator.pg_preprocessor_pygment import PGPreprocessor

pg_src = Path('tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg').read_text()

prep = PGPreprocessor()
result = prep.preprocess(pg_src, use_sandbox_macros=False)

print("Lines around line 54:")
lines = result.code.split('\n')
for i in range(50, min(60, len(lines))):
    print(f"{i+1:3d}: {lines[i]}")
