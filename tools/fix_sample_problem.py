#!/usr/bin/env python3
"""
Helper script to debug and fix sample problems.

Usage:
  python tools/fix_sample_problem.py --list-failing
  python tools/fix_sample_problem.py --convert NoSolution
  python tools/fix_sample_problem.py --test NoSolution
  python tools/fix_sample_problem.py --analyze NoSolution
  python tools/fix_sample_problem.py --batch-convert
"""

import sys
import argparse
import subprocess
from pathlib import Path

# Add packages to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))


def list_failing_problems():
    """Run tests and list all failing problems."""
    print("Running tests to identify failing problems...")
    print("=" * 70)
    
    cmd = [
        sys.executable,
        "-m", "pytest",
        str(project_root / "packages" / "pg_translator" / "tests" / "test_tutorial_sample_problems.py"),
        "-v", "--tb=line", "-x"  # Stop on first failure for quick feedback
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse output for FAILED lines
    failing = []
    for line in result.stdout.split('\n'):
        if 'FAILED' in line and 'test_tutorial_problem_renders' in line:
            # Extract problem name from: test_tutorial_problem_renders[ProblemName]
            parts = line.split('[')
            if len(parts) >= 2:
                problem_name = parts[1].split(']')[0]
                failing.append(problem_name)
    
    if failing:
        print(f"\nFound {len(failing)} failing problems:")
        for i, problem in enumerate(failing, 1):
            print(f"  {i:3d}. {problem}")
    else:
        print("\nNo failing problems found!")
    
    return failing


def convert_problem_to_python(problem_name: str, output_dir: str = None):
    """
    Convert a .pg file to preprocessed Python (.pypg).
    
    Args:
        problem_name: Name of problem (without .pg extension)
        output_dir: Optional output directory (default: same as .pg file)
    """
    from pg.translator import PGPreprocessor
    
    # Find the .pg file
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    pg_files = list(tutorial_dir.rglob(f"{problem_name}.pg"))
    
    if not pg_files:
        print(f"Error: Could not find {problem_name}.pg in tutorial/sample-problems/")
        return None
    
    if len(pg_files) > 1:
        print(f"Warning: Found multiple files named {problem_name}.pg:")
        for f in pg_files:
            print(f"  - {f}")
        print(f"Using: {pg_files[0]}")
    
    pg_file = pg_files[0]
    
    print(f"Converting: {pg_file}")
    print(f"Category: {pg_file.parent.name}")
    
    # Read and preprocess
    with open(pg_file, 'r', encoding='utf-8') as f:
        pg_code = f.read()
    
    preprocessor = PGPreprocessor()
    try:
        result = preprocessor.preprocess(pg_code, str(pg_file))
        
        # Determine output path
        if output_dir:
            output_path = Path(output_dir) / f"{problem_name}.pypg"
        else:
            output_path = pg_file.with_suffix('.pypg')
        
        # Write preprocessed Python
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.code)
        
        print(f"[OK] Converted to: {output_path}")
        print(f"  Lines: {len(result.code.splitlines())}")
        
        if hasattr(result, 'errors') and result.errors:
            print(f"  [WARN] Preprocessing warnings/errors:")
            for err in result.errors:
                print(f"    - {err}")
        
        return output_path
        
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_single_problem(problem_name: str):
    """Run pytest for a single problem."""
    print(f"Testing: {problem_name}")
    print("=" * 70)
    
    cmd = [
        sys.executable,
        "-m", "pytest",
        str(project_root / "packages" / "pg_translator" / "tests" / "test_tutorial_sample_problems.py"),
        f"::test_tutorial_problem_renders[{problem_name}]",
        "-v", "-s", "--tb=short"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def analyze_problem(problem_name: str):
    """Analyze a problem's errors in detail."""
    from pg.translator import PGTranslator
    
    # Find the .pg file
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    pg_files = list(tutorial_dir.rglob(f"{problem_name}.pg"))
    
    if not pg_files:
        print(f"Error: Could not find {problem_name}.pg")
        return
    
    pg_file = pg_files[0]
    
    print("=" * 70)
    print(f"Analyzing: {problem_name}.pg")
    print(f"Location: {pg_file}")
    print(f"Category: {pg_file.parent.name}")
    print("=" * 70)
    
    # Try to translate
    translator = PGTranslator()
    
    try:
        result = translator.translate(str(pg_file), seed=12345)
        
        print("\n[OK] Translation completed")
        
        if result.errors:
            print(f"\n[WARN] Errors found ({len(result.errors)}):")
            print("-" * 70)
            for i, err in enumerate(result.errors, 1):
                print(f"{i}. {err}")
                print()
        else:
            print("\n[OK] No errors!")
        
        if hasattr(result, 'statement_html') and result.statement_html:
            print(f"\n[OK] Generated HTML ({len(result.statement_html)} chars)")
            # Show first 200 chars
            preview = result.statement_html[:200]
            if len(result.statement_html) > 200:
                preview += "..."
            print(f"Preview: {preview}")
        
    except Exception as e:
        print(f"\n[ERROR] Translation failed with exception:")
        print("-" * 70)
        print(f"{type(e).__name__}: {e}")
        print()
        import traceback
        traceback.print_exc()
    
    # Also convert to see preprocessed code
    print("\n" + "=" * 70)
    print("Preprocessed Python code:")
    print("=" * 70)
    pypg_file = convert_problem_to_python(problem_name)
    
    if pypg_file and pypg_file.exists():
        with open(pypg_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\nShowing first 50 lines (total: {len(lines)}):")
        print("-" * 70)
        for i, line in enumerate(lines[:50], 1):
            print(f"{i:3d} | {line.rstrip()}")
        
        if len(lines) > 50:
            print(f"... ({len(lines) - 50} more lines)")


def batch_convert_all():
    """Convert all sample problems to .pypg files."""
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    pg_files = sorted(tutorial_dir.rglob("*.pg"))
    
    print(f"Found {len(pg_files)} .pg files")
    print("Converting all to .pypg...")
    print("=" * 70)
    
    success = 0
    failed = 0
    
    for pg_file in pg_files:
        problem_name = pg_file.stem
        try:
            result = convert_problem_to_python(problem_name)
            if result:
                success += 1
                print(f"[OK] {problem_name}")
            else:
                failed += 1
                print(f"[ERROR] {problem_name}")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {problem_name}: {e}")
    
    print("=" * 70)
    print(f"Results: {success} succeeded, {failed} failed")


def main():
    parser = argparse.ArgumentParser(
        description="Helper tool for debugging and fixing sample problems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all failing problems
  python tools/fix_sample_problem.py --list-failing
  
  # Convert a problem to Python
  python tools/fix_sample_problem.py --convert NoSolution
  
  # Test a single problem
  python tools/fix_sample_problem.py --test NoSolution
  
  # Analyze a problem in detail
  python tools/fix_sample_problem.py --analyze NoSolution
  
  # Convert all problems to .pypg
  python tools/fix_sample_problem.py --batch-convert
        """
    )
    
    parser.add_argument('--list-failing', action='store_true',
                       help='List all failing problems')
    parser.add_argument('--convert', metavar='PROBLEM',
                       help='Convert problem to .pypg Python file')
    parser.add_argument('--test', metavar='PROBLEM',
                       help='Run test for a single problem')
    parser.add_argument('--analyze', metavar='PROBLEM',
                       help='Analyze a problem in detail (errors + code)')
    parser.add_argument('--batch-convert', action='store_true',
                       help='Convert all problems to .pypg')
    parser.add_argument('--output-dir', metavar='DIR',
                       help='Output directory for converted files')
    
    args = parser.parse_args()
    
    if args.list_failing:
        list_failing_problems()
    
    elif args.convert:
        convert_problem_to_python(args.convert, args.output_dir)
    
    elif args.test:
        success = test_single_problem(args.test)
        sys.exit(0 if success else 1)
    
    elif args.analyze:
        analyze_problem(args.analyze)
    
    elif args.batch_convert:
        batch_convert_all()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
