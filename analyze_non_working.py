#!/usr/bin/env python3
"""Analyze why tutorial problems don't render."""

import os
os.environ['PYPG_DISABLE_LOGGING'] = '1'

from pg_translator import PGTranslator
from pathlib import Path

# Test a sample of non-working problems
problem_samples = [
    'tutorial/sample-problems/Algebra/FractionAnswer.pg',
    'tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg',
    'tutorial/sample-problems/DiffCalc/LinearApprox.pg',
    'tutorial/sample-problems/ProblemTechniques/SimplePopUp.pg',
    'tutorial/sample-problems/ProblemTechniques/Percent.pg',
]

for prob in problem_samples:
    print(f"\n{'='*70}")
    print(f"Testing: {Path(prob).name}")
    print(f"{'='*70}")
    
    translator = PGTranslator()
    result = translator.translate(prob, seed=1234)
    
    print(f"Statement: {len(result.statement_html or '')} chars")
    print(f"Answers: {len(result.answer_blanks or {})}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    
    # Try to read the preprocessed code
    from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor
    preprocessor = PGPreprocessor()
    with open(prob, 'r', encoding='utf-8') as f:
        original = f.read()
    
    preprocessed_result = preprocessor.preprocess(original, prob)
    processed = preprocessed_result.code
    
    # Show a snippet of the processed code around line 50-70
    lines = processed.split('\n')
    if len(lines) > 50:
        print(f"\nProcessed code (lines 50-70):")
        for i, line in enumerate(lines[49:70], 50):
            print(f"{i:3d}: {line[:80]}")
