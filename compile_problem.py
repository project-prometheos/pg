#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'packages/pg_translator')
sys.path.insert(0, 'packages/problemkit')

from packages.pg_translator.pg_translator.pg_preprocessor_pygment import PGPreprocessor

problem = sys.argv[1]

base = 'tutorial/sample-problems'

import os

path = None
for root, _, files in os.walk(base):
    if f'{problem}.pg' in files:
        path = os.path.join(root, f'{problem}.pg')
        break

if not path:
    raise SystemExit(f'Problem {problem} not found')

with open(path, 'r') as f:
    pg_code = f.read()

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_code)

try:
    compile(result.code, '<string>', 'exec')
    print(f'{problem}: OK')
except SyntaxError as exc:
    print(f'{problem}: SyntaxError {exc}')
    if exc.text:
        print(exc.text)
        print(' ' * (exc.offset - 1) + '^')
