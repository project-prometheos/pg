"""Debug preprocessor output."""

from pg_translator.preprocessor import PGPreprocessor

pg_code = """
BEGIN_PGML
Add: [$a] + [$b]
END_PGML
"""

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_code)

print("Preprocessed code:")
print(result.code)
print("\nText blocks:")
for block_type, content in result.text_blocks:
    print(f"  {block_type}: {repr(content[:50])}")
