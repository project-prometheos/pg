"""Debug what evaluator is returned."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'pg_translator'))

from pg_translator.translator import PGTranslator

pg_src = Path('tutorial/sample-problems/Algebra/SimpleFactoring.pg').read_text()
translator = PGTranslator()
result = translator.translate_source(pg_src, seed=123)

print("Answer blanks:")
for blank_id, blank_data in result.answer_blanks.items():
    print(f"\n{blank_id}:")
    print(f"  Type: {type(blank_data['evaluator'])}")
    print(f"  Value: {blank_data['evaluator']}")
    print(f"  Has cmp: {hasattr(blank_data['evaluator'], 'cmp')}")
    print(f"  Has check: {hasattr(blank_data['evaluator'], 'check')}")
    
    # Try calling cmp() if it exists
    if hasattr(blank_data['evaluator'], 'cmp'):
        checker = blank_data['evaluator'].cmp()
        print(f"  Checker type: {type(checker)}")
        print(f"  Checker has check: {hasattr(checker, 'check')}")
