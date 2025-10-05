"""Test MultiAnswer handling."""

from packages.pg_translator.pg_translator.in_process_sandbox import InProcessSandbox
from packages.pg_translator.pg_translator import PGTranslator
from pathlib import Path

pg_src = Path(
    'tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg').read_text()
t = PGTranslator()

# Also check what's in the PG environment variables
sandbox = InProcessSandbox()
exec_result = sandbox.execute(pg_src, seed=0)
print('Variables in sandbox:')
if 'multians' in exec_result.variables:
    ma = exec_result.variables['multians']
    print(f'  multians type: {type(ma).__name__}')
    print(f'  multians class: {ma.__class__}')
    print(
        f'  multians attributes: {[a for a in dir(ma) if not a.startswith("_")]}')
print()

result = t.translate_source(pg_src, seed=0)

print('Answer blanks:')
for aid, val in result.answer_blanks.items():
    print(f'\n{aid}:')
    print(f'  Type: {type(val).__name__}')
    print(f'  Value: {val}')
    print(f'  Has cmp: {hasattr(val, "cmp")}')
    print(f'  Has check: {hasattr(val, "check")}')
    if hasattr(val, '__class__'):
        print(f'  Class: {val.__class__}')
        print(
            f'  Methods: {[m for m in dir(val) if not m.startswith("_")][:10]}')

print('\n\nTrying to check answers:')
inputs = {
    'AnSwEr0001': '8y-9',
    'AnSwEr0002': 'y-1'
}

result_with_check = t.translate_source(pg_src, seed=0, inputs=inputs)
print(f'\nAnswer results: {result_with_check.answer_results}')
