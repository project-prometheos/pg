"""Check preprocessed Formula creation."""

from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor

pg_code = '''
$a = 8;
$b = 9;
$c = 1;
$num = Formula("$a y - $b");
$den = Formula("y - $c");
'''

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_code)

print("Preprocessed code:")
print(result.code)
