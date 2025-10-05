from pg_translator import PGTranslator
from app.db import ProblemDB
import sys
sys.path.insert(0, 'apps/backend')


db = ProblemDB.get_instance()
prob = db.get_by_id('PS1/Problem-25')

t = PGTranslator()
result = t.translate_source(prob['pg_source'], seed=0)

evaluator = result.answer_blanks['AnSwEr0001']['evaluator']
print('Evaluator type:', type(evaluator).__name__)
print('Evaluator value:', evaluator)
print('Evaluator repr:', repr(evaluator))

# Check what methods it has
print('\nRelevant methods:')
for attr in ['string', 'to_string', 'TeX', 'check', 'cmp', 'evaluate']:
    if hasattr(evaluator, attr):
        print(f'  Has {attr}: True')
        if attr == 'string':
            try:
                print(f'    string() = {evaluator.string()}')
            except:
                pass
