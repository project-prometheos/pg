#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, 'packages/pg_translator')
sys.path.insert(0, 'packages/problemkit')

from packages.pg_translator.pg_translator.pg_preprocessor_pygment import PGPreprocessor

# Get all tutorial problems
base_path = 'tutorial/sample-problems'
all_problems = []

for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('.pg'):
            problem_name = file[:-3]
            all_problems.append((problem_name, os.path.join(root, file)))

print(f"Found {len(all_problems)} problems total")

# Check each one and categorize errors
error_categories = {}
preprocessor = PGPreprocessor()

for problem_name, filepath in all_problems:  # Test all
    try:
        with open(filepath, 'r') as f:
            pg_code = f.read()
        
        result = preprocessor.preprocess(pg_code)
        py_code = result.code
        
        try:
            compile(py_code, '<string>', 'exec')
            # Success - don't categorize
        except SyntaxError as e:
            error_msg = str(e.msg)
            if 'map' in py_code:
                error_categories.setdefault('map_block', []).append(problem_name)
            elif 'for' in py_code and '(' in py_code.split('for')[1].split('{')[0] if 'for' in py_code else False:
                error_categories.setdefault('for_block', []).append(problem_name)
            elif 'does not match' in error_msg:
                error_categories.setdefault('brace_mismatch', []).append(problem_name)
            elif 'invalid' in error_msg:
                error_categories.setdefault('invalid_syntax', []).append(problem_name)
            else:
                error_categories.setdefault('other', []).append(problem_name)
    except Exception as e:
        error_categories.setdefault('processing_error', []).append(problem_name)

print("\nError categories:")
for category, problems in sorted(error_categories.items()):
    print(f"  {category}: {len(problems)} problems - {problems[:3]}...")
