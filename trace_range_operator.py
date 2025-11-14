import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))

from pg.translator.pg_preprocessor_pygment import PGPreprocessor

# Test range operator conversion
source_lines = [
    "@indices = (0 .. 5);",
    "@shuffle = (0 .. $#answers);",
]

source = "\n".join(source_lines)
print("Input source:")
for i, line in enumerate(source_lines, 1):
    print(f"{i:2d}: {line}")

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(source)

print("\n\nOutput lines:")
out_lines = result.code.split('\n')
for i, line in enumerate(out_lines, 1):
    if line.strip():
        print(f"{i:2d}: {line}")
