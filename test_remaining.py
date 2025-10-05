#!/usr/bin/env python3
"""Test remaining problems."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'packages' / 'pg_translator'))
sys.path.insert(0, str(Path('.') / 'packages' / 'pg_pgml'))
sys.path.insert(0, str(Path('.') / 'packages' / 'pg_macros'))

from pg_translator import PGTranslator

problems = {
    'DoubleIntegral.pg': 'tutorial/sample-problems/IntegralCalc/DoubleIntegral.pg',
    'PeriodicAnswers.pg': 'tutorial/sample-problems/Trig/PeriodicAnswers.pg',
    'ProvingTrigIdentities.pg': 'tutorial/sample-problems/Trig/ProvingTrigIdentities.pg',
    'RecursiveSequence.pg': 'tutorial/sample-problems/Sequences/RecursiveSequence.pg',
}

for name, path in problems.items():
    print(f"\n=== {name} ===")
    try:
        from pg_translator.preprocessor import PGPreprocessor
        from pg_translator.in_process_sandbox import InProcessSandbox
        
        with open(path) as f:
            content = f.read()
        
        prep = PGPreprocessor()
        prep_result = prep.preprocess(content)
        
        sandbox = InProcessSandbox()
        exec_result = sandbox.execute(prep_result.code, 1234)
        
        print(f"Execution success: {exec_result.success}")
        print(f"Output: {len(exec_result.output_text)} chars")
        print(f"Answers: {len(exec_result.answers)}")
        if exec_result.errors:
            print(f"Errors: {exec_result.errors[:300]}")
    except Exception as e:
        import traceback
        print(f"Exception: {type(e).__name__}: {str(e)[:200]}")
        print(traceback.format_exc()[:500])
