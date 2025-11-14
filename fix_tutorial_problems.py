#!/usr/bin/env python3
"""
Systematically fix tutorial sample problems.

This script:
1. Identifies failing problems
2. Converts each to .pypg to see generated Python
3. Attempts to fix the issue
4. Tests the fix
5. Moves to the next problem
"""

import sys
import subprocess
from pathlib import Path

# Add packages to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))

from pg.translator import PGPreprocessor, PGTranslator


def get_failing_problems():
    """Extract list of failing problems from recent test run."""
    output = []
    
    # Run test with compact output
    cmd = [
        sys.executable,
        "-m", "pytest",
        str(project_root / "packages" / "pg_translator" / "tests" / "test_tutorial_sample_problems.py"),
        "-v", "--tb=no", "-q"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse for FAILED lines
    failing = []
    for line in result.stdout.split('\n'):
        if 'FAILED' in line and 'test_tutorial_problem_renders' in line:
            # Extract problem name
            if '[' in line and ']' in line:
                start = line.index('[') + 1
                end = line.index(']', start)
                problem_name = line[start:end]
                failing.append(problem_name)
    
    return failing


def analyze_problem(problem_name: str):
    """Analyze a problem and show its errors."""
    print("=" * 80)
    print(f"ANALYZING: {problem_name}")
    print("=" * 80)
    
    # Find the .pg file
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    pg_files = list(tutorial_dir.rglob(f"{problem_name}.pg"))
    
    if not pg_files:
        print(f"[X] Could not find {problem_name}.pg")
        return None
    
    pg_file = pg_files[0]
    print(f"File: {pg_file.relative_to(project_root)}")
    print(f"Category: {pg_file.parent.name}")
    
    # Read source
    with open(pg_file, 'r', encoding='utf-8') as f:
        pg_source = f.read()
    
    # Try preprocessing
    print("\n--- PREPROCESSING ---")
    preprocessor = PGPreprocessor()
    try:
        result = preprocessor.preprocess(pg_source, str(pg_file))
        print(f"[OK] Preprocessing succeeded ({len(result.code)} chars)")
        
        # Save preprocessed code
        pypg_file = pg_file.with_suffix('.pypg')
        with open(pypg_file, 'w', encoding='utf-8') as f:
            f.write(result.code)
        print(f"Saved to: {pypg_file.relative_to(project_root)}")
        
        # Show first 60 lines
        lines = result.code.split('\n')
        print(f"\nFirst 60 lines of {len(lines)} total:")
        print("-" * 80)
        for i, line in enumerate(lines[:60], 1):
            print(f"{i:3d} | {line}")
        if len(lines) > 60:
            print(f"... ({len(lines) - 60} more lines)")
        
    except Exception as e:
        print(f"[X] Preprocessing failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Try translation
    print("\n--- TRANSLATION ---")
    translator = PGTranslator()
    try:
        trans_result = translator.translate(str(pg_file), seed=12345)
        
        if trans_result.errors:
            print(f"[X] Translation had {len(trans_result.errors)} error(s):")
            for i, err in enumerate(trans_result.errors, 1):
                print(f"\n{i}. {err}")
        else:
            print("[OK] Translation succeeded!")
        
        return {
            'pg_file': pg_file,
            'pypg_file': pypg_file,
            'preprocessed_code': result.code,
            'errors': trans_result.errors if hasattr(trans_result, 'errors') else []
        }
        
    except Exception as e:
        print(f"[X] Translation failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'pg_file': pg_file,
            'pypg_file': pypg_file if 'pypg_file' in locals() else None,
            'preprocessed_code': result.code if 'result' in locals() else None,
            'errors': [str(e)]
        }


def test_problem(problem_name: str):
    """Test a single problem."""
    cmd = [
        sys.executable,
        "-m", "pytest",
        str(project_root / "packages" / "pg_translator" / "tests" / "test_tutorial_sample_problems.py"),
        f"::test_tutorial_problem_renders[{problem_name}]",
        "-v", "--tb=short"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    passed = result.returncode == 0
    
    if passed:
        print(f"[OK] Test PASSED for {problem_name}")
    else:
        print(f"[X] Test FAILED for {problem_name}")
        # Show error snippet
        for line in result.stdout.split('\n'):
            if 'Error' in line or 'Failed' in line:
                print(f"  {line}")
    
    return passed


def main():
    print("Finding failing problems...")
    failing = get_failing_problems()
    
    if not failing:
        print("[OK] No failing problems found!")
        return
    
    print(f"\nFound {len(failing)} failing problems:")
    for i, name in enumerate(failing, 1):
        print(f"  {i:2d}. {name}")
    
    print("\n" + "=" * 80)
    print("SYSTEMATIC ANALYSIS")
    print("=" * 80)
    
    # Analyze each problem
    for i, problem_name in enumerate(failing, 1):
        print(f"\n\n[{i}/{len(failing)}] ", end="")
        info = analyze_problem(problem_name)
        
        if info and i < len(failing):
            input("\nPress Enter to continue to next problem...")


if __name__ == '__main__':
    main()
