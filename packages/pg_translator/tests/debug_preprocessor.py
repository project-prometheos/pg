"""Debug preprocessor output."""

from pathlib import Path
from pg_translator.preprocessor import PGPreprocessor

# Load the .pg file
test_file = Path(__file__).parent / "problems" / "random_addition.pg"
pg_source = test_file.read_text()

print("=== ORIGINAL PG SOURCE ===")
print(pg_source)
print()

# Preprocess
preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_source)

print("=== PREPROCESSED PYTHON CODE ===")
print(result.code)
print()

print("=== TEXT BLOCKS ===")
for i, (block_type, content) in enumerate(result.text_blocks):
    print(f"Block {i}: {block_type}")
    print(content[:200])
    print()
