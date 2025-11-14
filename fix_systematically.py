#!/usr/bin/env python
"""Fix sample problems systematically by category."""
import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_answer"))
sys.path.insert(0, str(project_root / "packages" / "pg_parser"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))

from pg.translator import PGTranslator

def diagnose_problem(problem_path):
    """Diagnose a single problem."""
    translator = PGTranslator()
    try:
        result = translator.translate(str(problem_path), seed=12345)
        if result.errors:
            return {
                'errors': result.errors,
                'status': 'failed'
            }
        else:
            return {
                'errors': [],
                'status': 'passed'
            }
    except Exception as e:
        return {
            'errors': [str(e)],
            'status': 'error'
        }

def fix_syntax_errors():
    """Fix SyntaxError problems - line continuation and bracket issues."""
    fixes = [
        {
            'file': 'GraphsInTables.pg',
            'issue': 'unexpected character after line continuation character',
            'action': 'Check for backslash in wrong place, use proper continuation'
        },
        {
            'file': 'Images.pg',
            'issue': 'unexpected character after line continuation character',
            'action': 'Check for backslash in wrong place'
        },
        {
            'file': 'GraphToolCustomChecker.pg',
            'issue': 'bracket mismatch {vs )',
            'action': 'Fix nested brackets in GraphTool string'
        },
        {
            'file': 'TableOfValues.pg',
            'issue': 'invalid syntax line 23',
            'action': 'Check line 23 for syntax issues'
        },
        {
            'file': 'ParametricPlot.pg',
            'issue': 'invalid syntax line 61',
            'action': 'Check line 61 syntax'
        },
    ]
    
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    
    for fix in fixes:
        pg_file = None
        for p in tutorial_dir.rglob(fix['file']):
            pg_file = p
            break
        
        if not pg_file:
            print(f"Skip: {fix['file']} not found")
            continue
        
        print(f"\nFix: {fix['file']}")
        print(f"  Issue: {fix['issue']}")
        print(f"  Action: {fix['action']}")
        
        # Read file
        content = pg_file.read_text()
        
        # Show a snippet
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '\\' in line and i < len(lines):
                print(f"    Line {i}: {line[:80]}")
                if i < len(lines):
                    print(f"    Line {i+1}: {lines[i][:80]}")

def fix_typeerror_concat():
    """Fix TypeError: can only concatenate str (not "int") to str."""
    problems = [
        'GraphShading.pg',
        'GraphShadingPlot.pg', 
        'LayoutTable.pg',
        'SeriesTest.pg'
    ]
    
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    
    for problem in problems:
        pg_file = None
        for p in tutorial_dir.rglob(problem):
            pg_file = p
            break
        
        if not pg_file:
            continue
        
        print(f"\nFix: {problem} (str + int concat)")
        
        # Diagnose to get error details
        result = diagnose_problem(pg_file)
        for err in result['errors']:
            # Extract line number
            if 'line' in err.lower():
                print(f"  {err[:150]}")

def fix_nameerror_missing():
    """Fix NameError problems - missing variables/functions."""
    problems = {
        'StringOrOtherType.pg': 'String not defined - need macro load',
        'PrimesInFormulas.pg': 're not defined - need regex import',
        'QuadrilateralGraphTool.pg': 'x3 not defined - variable scope',
        'TriangleGraphTool.pg': 'x3 not defined - variable scope',
        'RiemannSums.pg': 'x not defined - variable scope',
        'ManyMultipleChoice.pg': 'install_problem_grader not defined',
        'Matching.pg': 'install_problem_grader not defined',
        'Scaffolding.pg': 'Scaffold not defined - need macro'
    }
    
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    
    for problem, desc in problems.items():
        pg_file = None
        for p in tutorial_dir.rglob(problem):
            pg_file = p
            break
        
        if not pg_file:
            continue
            
        print(f"\nFix: {problem}")
        print(f"  {desc}")

def fix_attributeerror():
    """Fix AttributeError - missing methods."""
    problems = {
        'RiemannSumPlot.pg': "Plot.add_dataset method missing",
        'CustomAnswerListChecker.pg': "List.cmp method missing"
    }
    
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    
    for problem, desc in problems.items():
        pg_file = None
        for p in tutorial_dir.rglob(problem):
            pg_file = p
            break
        
        if not pg_file:
            continue
            
        print(f"\nFix: {problem}")
        print(f"  {desc}")

if __name__ == '__main__':
    print("="*70)
    print("SYSTEMATIC FIX PLAN")
    print("="*70)
    
    print("\n1. SYNTAX ERRORS (25 problems) - String/Bracket issues")
    fix_syntax_errors()
    
    print("\n\n2. TYPE ERRORS (9 problems) - Type concatenation")
    fix_typeerror_concat()
    
    print("\n\n3. NAME ERRORS (8 problems) - Missing variables/macros")
    fix_nameerror_missing()
    
    print("\n\n4. ATTRIBUTE ERRORS (2 problems) - Missing methods")
    fix_attributeerror()
    
    print("\n" + "="*70)
    print("Summary: 44 total problems to fix")
    print("="*70)
