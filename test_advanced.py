from pg_translator.pg_preprocessor_pygment import PGPreprocessor

pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

BEGIN_TEXT
What is the capital of France?
\\{ans_rule(20)\\}
END_TEXT

ANS(str_cmp("Paris", case_sensitive=False))

ENDDOCUMENT()
"""

p = PGPreprocessor()
r = p.preprocess(pg_code)
print("Preprocessed code:")
print(r.code)
