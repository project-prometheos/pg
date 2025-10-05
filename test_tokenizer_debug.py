from packages.pg_pgml.pg_pgml.tokenizer import PGMLTokenizer
from packages.pg_pgml.pg_pgml import PGMLParser

text = r'Answer = [_]{$answer->cmp()}{15}'
print('Original:', repr(text))

tokenizer = PGMLTokenizer(text)
tokens = list(tokenizer.tokenize())

print('\nTokens:')
for t in tokens:
    if t.type.name != 'EOF':
        print(f'  {t.type.name:20s} | {repr(t.value)}')

print('\nParsed:')
doc = PGMLParser.parse_text(text)
answer_blank = doc.blocks[0].content[1]  # First is TEXT, second is ANSWER_BLANK
print(f'  Width: {answer_blank.width}')
print(f'  Evaluator code: {repr(answer_blank.evaluator_code)}')
