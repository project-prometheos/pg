#!/usr/bin/env python3
"""Debug AlgebraicFractionAnswer rendering."""

from pg_translator import PGTranslator
import sys
sys.path.insert(0, 'packages/pg_translator')


t = PGTranslator()
print('Translating AlgebraicFractionAnswer.pg...')

try:
    r = t.translate(
        'tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg', seed=1234)

    print(
        f'\nStatement HTML: {len(r.statement_html) if r.statement_html else 0} chars')
    print(f'Answer blanks: {len(r.answer_blanks)}')
    print(
        f'Solution HTML: {len(r.solution_html) if r.solution_html else 0} chars')
    print(f'Errors: {r.errors if hasattr(r, "errors") else "N/A"}')

    if r.statement_html:
        print(f'\nStatement content:\n{r.statement_html[:500]}')
    else:
        print('\nNO STATEMENT!')

    if r.answer_blanks:
        print(f'\nAnswers: {list(r.answer_blanks.keys())}')
except Exception as e:
    print(f'\nEXCEPTION: {e}')
    import traceback
    traceback.print_exc()
