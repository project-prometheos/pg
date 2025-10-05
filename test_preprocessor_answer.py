"""Check preprocessor output for answer blank code."""

from pg_translator.preprocessor import PGPreprocessor

pg_code = """
DOCUMENT()
loadMacros("PG.pl")

from pg_answer import num_cmp

answer = 42

BEGIN_PGML
What is the meaning of life? [_]{num_cmp(answer)}
END_PGML

ENDDOCUMENT()
"""

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_code)

print("Preprocessed code:")
print(result.code)
