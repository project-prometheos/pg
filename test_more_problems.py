#!/usr/bin/env python3
"""Test additional tutorial problems to find more working ones."""

from pathlib import Path
from pg_translator import PGTranslator
import os
os.environ['PYPG_DISABLE_LOGGING'] = '1'


# Test problems from various categories
test_problems = [
    # Algebra
    'tutorial/sample-problems/Algebra/FormulaAnswer.pg',
    'tutorial/sample-problems/Algebra/AbsoluteValue.pg',
    'tutorial/sample-problems/Algebra/PointAnswer.pg',

    # Diff Calc
    'tutorial/sample-problems/DiffCalc/TangentLine.pg',
    'tutorial/sample-problems/DiffCalc/DerivativeViaLimitDef.pg',

    # Integral Calc
    'tutorial/sample-problems/IntegralCalc/DefiniteIntegral.pg',
    'tutorial/sample-problems/IntegralCalc/VolumeDisc.pg',

    # Trig
    'tutorial/sample-problems/Trig/TrigIdentities.pg',
    'tutorial/sample-problems/Trig/TrigDegrees.pg',

    # Sequences
    'tutorial/sample-problems/Sequences/ExplicitSequence.pg',
    'tutorial/sample-problems/Sequences/SeriesTest.pg',

    # Problem Techniques
    'tutorial/sample-problems/ProblemTechniques/Percent.pg',
    'tutorial/sample-problems/ProblemTechniques/SimplePopUp.pg',
    'tutorial/sample-problems/ProblemTechniques/NumericalTolerance.pg',
]

results = []
for prob in test_problems:
    prob_path = Path(prob)
    if not prob_path.exists():
        print(f"SKIP {prob} (not found)")
        continue

    translator = PGTranslator()
    result = translator.translate(str(prob), seed=1234)

    has_stmt = len(result.statement_html or '') > 0
    has_ans = len(result.answer_blanks or {}) > 0
    has_error = bool(result.errors)

    status = '✅' if (has_stmt and has_ans) else '⚠️' if has_stmt else '❌'
    print(f"{status} {prob_path.name:40s} stmt:{has_stmt:<5} ans:{has_ans:<5} err:{has_error}")

    if has_error and result.errors:
        print(f"   ERROR: {result.errors[0][:80]}")

    results.append({
        'file': str(prob),
        'stmt': has_stmt,
        'ans': has_ans,
        'error': has_error
    })

print(
    f"\nWorking problems: {sum(1 for r in results if r['stmt'] and r['ans'])}/{len(results)}")
print(f"With statement: {sum(1 for r in results if r['stmt'])}/{len(results)}")
print(f"With answers: {sum(1 for r in results if r['ans'])}/{len(results)}")
