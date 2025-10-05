"""Debug full preprocessor output."""

from pg_translator.preprocessor import PGPreprocessor

pg_code = """
DOCUMENT()
loadMacros("PG.pl")

a = 5
b = 3

BEGIN_PGML
Add: [$a] + [$b]
END_PGML

ENDDOCUMENT()
"""

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_code)

print("Preprocessed code:")
print(result.code)
print("\n" + "="*60)
