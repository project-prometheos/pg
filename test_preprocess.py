from pg_translator.preprocessor import PGPreprocessor

pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

BEGIN_TEXT
What is 2 + 2?
$BR
Answer: \\{ans_rule(20)\\}
END_TEXT

ANS(num_cmp(4))

ENDDOCUMENT()
"""

p = PGPreprocessor()
r = p.preprocess(pg_code)
print("Preprocessed code:")
print(r.code)
