from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor

p = PGPreprocessor()
with open('tutorial/sample-problems/Algebra/FractionAnswer.pg', 'r', encoding='utf-8') as f:
    orig = f.read()

result = p.preprocess(orig, 'FractionAnswer.pg')
lines = result.code.split('\n')

print("Lines with 'cmp' or PGML:")
for i, line in enumerate(lines, 1):
    if 'cmp' in line.lower() or 'PGML' in line:
        print(f'{i:3d}: {line}')
