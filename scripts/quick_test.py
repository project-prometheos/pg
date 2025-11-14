#!/usr/bin/env python
"""
Quick test harness for a single problem.

Faster than running full pytest for quick iteration during debugging.

Usage:
    python quick_test.py tutorial/sample-problems/Algebra/Problem.pg
    python quick_test.py tutorial/sample-problems/Algebra/Problem.pg --seed 999
"""

import sys
from pathlib import Path
import argparse

# Add packages to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_answer"))
sys.path.insert(0, str(project_root / "packages" / "pg_parser"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))

from pg.translator import PGTranslator


def quick_test(problem_path: str, seed: int = 12345, verbose: bool = True):
    """Quick test of a single problem."""
    
    problem_file = Path(problem_path)
    
    if not problem_file.exists():
        print(f"❌ Error: {problem_path} not found")
        return False
    
    if verbose:
        print(f"\n📋 Testing: {problem_file.name}")
        print(f"   Path: {problem_file}")
        print(f"   Seed: {seed}\n")
    
    translator = PGTranslator()
    
    try:
        result = translator.translate(str(problem_file), seed=seed)
        
        # Check for errors
        if result.errors:
            error_str = '\n'.join(result.errors) if isinstance(result.errors, list) else str(result.errors)
            
            # Check for fatal errors
            fatal_keywords = [
                'SyntaxError', 'NameError', 'AttributeError',
                'TypeError', 'ImportError', 'ModuleNotFoundError',
                'File not found',
            ]
            
            has_fatal = any(keyword in error_str for keyword in fatal_keywords)
            
            if has_fatal:
                print("❌ FAILED - Critical error:\n")
                # Show just the key error line
                for line in error_str.split('\n'):
                    if any(kw in line for kw in fatal_keywords):
                        print(f"   {line}")
                        break
                
                if verbose and len(error_str) < 500:
                    print("\nFull error:")
                    print(error_str)
                
                return False
            else:
                print("⚠️  WARNING - Non-fatal error:\n")
                print(error_str[:500])
                if len(error_str) > 500:
                    print(f"\n... ({len(error_str) - 500} more chars)")
                return False
        
        # Check output
        if not hasattr(result, 'statement_html'):
            print("⚠️  WARNING - Missing statement_html")
            return False
        
        html = result.statement_html if result.statement_html else ""
        
        if not html:
            print("⚠️  WARNING - No statement HTML generated")
            return False
        
        print(f"✅ PASSED")
        print(f"   Statement HTML: {len(html)} characters")
        return True
    
    except Exception as e:
        print(f"❌ EXCEPTION:\n   {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Quick test a single PG problem")
    parser.add_argument("problem", help="Path to .pg file")
    parser.add_argument("--seed", type=int, default=12345, help="Random seed")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    success = quick_test(args.problem, seed=args.seed, verbose=not args.quiet)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
