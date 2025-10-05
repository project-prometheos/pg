import os
os.environ['PYPG_DISABLE_LOGGING'] = '1'

from pg_translator import PGTranslator
from pathlib import Path

test_dir = Path('webwork_ps1_pg')
results = []

for pg_file in sorted(test_dir.glob('*.pg')):
    translator = PGTranslator()
    result = translator.translate(str(pg_file), seed=1234)
    
    has_stmt = len(result.statement_html or '') > 0
    has_ans = len(result.answer_blanks or {}) > 0
    has_error = bool(result.errors)
    
    results.append({
        'file': pg_file.name,
        'stmt': has_stmt,
        'ans': has_ans,
        'error': has_error,
        'errors': result.errors[:1] if result.errors else None
    })

for r in results:
    marker = '***' if r['error'] else '   '
    print(f"{marker} {r['file']:40s} stmt:{r['stmt']:<5} ans:{r['ans']:<5} err:{r['error']}")
    if r['error'] and r['errors']:
        print(f"    ERROR: {r['errors'][0][:100]}")

stmt_count = sum(1 for r in results if r['stmt'])
ans_count = sum(1 for r in results if r['ans'])
print(f'\nTotals: {stmt_count}/{len(results)} statements ({stmt_count*100//len(results)}%), {ans_count}/{len(results)} answers ({ans_count*100//len(results)}%)')
