#!/usr/bin/env python3
"""Test parserFunction stub."""

from pg_translator.preprocessor import PGPreprocessor
from pg_translator.in_process_sandbox import InProcessSandbox
import sys
sys.path.insert(0, 'packages/pg_translator')
sys.path.insert(0, 'packages/pg_mathobjects')


# Load RecursiveSequence.pg
with open('tutorial/sample-problems/Sequences/RecursiveSequence.pg') as f:
    content = f.read()

# Preprocess
prep = PGPreprocessor()
prepped = prep.preprocess(content)

# Execute
sb = InProcessSandbox()
result = sb.execute(prepped.code, seed=1234)

print(f'Success: {result.success}')
print(f'Output: {len(result.output_text)} chars')
print(f'Answers: {len(result.answers)}')

if result.errors:
    print(f'\nErrors:')
    print(result.errors[:1000])

if result.output_text:
    print(f'\nOutput:')
    print(result.output_text[:500])
