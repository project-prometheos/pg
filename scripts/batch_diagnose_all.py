#!/usr/bin/env python
"""
Batch diagnose all failing PG problems and categorize errors.

Creates a detailed report of all problems grouped by error type.

Usage:
    python batch_diagnose_all.py
    python batch_diagnose_all.py --limit 10  # Test first 10 problems
    python batch_diagnose_all.py --category "NameError"  # Only specific category
    
Output:
    - problems_diagnostic_report.txt - Detailed findings
    - problems_diagnostic_summary.json - Structured data
    - problems_by_error_type.txt - Quick reference
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import argparse

# Add packages to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_answer"))
sys.path.insert(0, str(project_root / "packages" / "pg_parser"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))

from pg.translator import PGTranslator


def get_error_category(error_msg: str) -> str:
    """Categorize error type."""
    if not error_msg:
        return "NoError"
    
    keywords = {
        'SyntaxError': 'SyntaxError',
        'NameError': 'NameError',
        'AttributeError': 'AttributeError',
        'TypeError': 'TypeError',
        'ImportError': 'ImportError',
        'ModuleNotFoundError': 'ModuleNotFoundError',
        'KeyError': 'KeyError',
        'ValueError': 'ValueError',
        'FileNotFoundError': 'FileNotFoundError',
        'RuntimeError': 'RuntimeError',
        'IndentationError': 'IndentationError',
        'ZeroDivisionError': 'ZeroDivisionError',
    }
    
    for keyword, category in keywords.items():
        if keyword in error_msg:
            return category
    
    return "OtherError"


def extract_error_snippet(error_msg: str, max_len: int = 200) -> str:
    """Extract the most relevant error line."""
    if not error_msg:
        return ""
    
    lines = error_msg.split('\n')
    for line in lines:
        if 'Error' in line:
            return line[:max_len]
    
    return lines[0][:max_len] if lines else ""


def collect_problems() -> List[Path]:
    """Collect all .pg files from tutorial/sample-problems."""
    tutorial_dir = project_root / "tutorial" / "sample-problems"
    problems = sorted(tutorial_dir.rglob("*.pg"))
    return problems


def diagnose_problem(problem_file: Path, translator: PGTranslator, seed: int = 12345) -> Dict:
    """Diagnose a single problem."""
    result = {
        'name': problem_file.name,
        'path': str(problem_file.relative_to(project_root)),
        'category': problem_file.parent.name,
        'status': 'unknown',
        'error_type': None,
        'error_snippet': None,
        'errors_full': None,
        'has_output': False,
    }
    
    try:
        translation_result = translator.translate(str(problem_file), seed=seed)
        
        if translation_result.errors:
            error_str = '\n'.join(translation_result.errors) if isinstance(translation_result.errors, list) else str(translation_result.errors)
            
            result['errors_full'] = error_str
            result['error_type'] = get_error_category(error_str)
            result['error_snippet'] = extract_error_snippet(error_str)
            
            # Check for fatal errors
            fatal_keywords = [
                'SyntaxError', 'NameError', 'AttributeError',
                'TypeError', 'ImportError', 'ModuleNotFoundError',
                'File not found',
            ]
            
            if any(keyword in error_str for keyword in fatal_keywords):
                result['status'] = 'failed'
            else:
                result['status'] = 'warning'
        else:
            if hasattr(translation_result, 'statement_html') and translation_result.statement_html:
                result['status'] = 'passed'
                result['has_output'] = True
            else:
                result['status'] = 'no_output'
    
    except Exception as e:
        result['status'] = 'exception'
        result['error_type'] = 'Exception'
        result['error_snippet'] = str(e)[:200]
        result['errors_full'] = str(e)
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Batch diagnose all tutorial problems"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit to first N problems"
    )
    parser.add_argument(
        "--category",
        help="Only problems from specific category (e.g., 'Algebra')"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output during processing"
    )
    
    args = parser.parse_args()
    
    # Collect problems
    problems = collect_problems()
    
    if args.category:
        problems = [p for p in problems if p.parent.name == args.category]
    
    if args.limit:
        problems = problems[:args.limit]
    
    print(f"Diagnosing {len(problems)} problems...")
    print(f"(Total tutorial problems: {len(collect_problems())})\n")
    
    # Diagnose each problem
    translator = PGTranslator()
    results: List[Dict] = []
    
    categories_found = defaultdict(int)
    errors_by_type: Dict[str, List[str]] = defaultdict(list)
    
    for i, problem_file in enumerate(problems, 1):
        if args.verbose:
            print(f"[{i}/{len(problems)}] {problem_file.name}...", end=' ', flush=True)
        
        result = diagnose_problem(problem_file, translator)
        results.append(result)
        
        categories_found[result['category']] += 1
        if result['error_type']:
            errors_by_type[result['error_type']].append(result['name'])
        
        status_symbol = {
            'passed': '✓',
            'warning': '⚠',
            'failed': '✗',
            'no_output': '○',
            'exception': '⚡',
            'unknown': '?',
        }.get(result['status'], '?')
        
        if args.verbose:
            print(f"{status_symbol} {result['error_type'] or 'OK'}")
    
    # Generate report
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] == 'failed')
    warnings = sum(1 for r in results if r['status'] == 'warning')
    no_output = sum(1 for r in results if r['status'] == 'no_output')
    exceptions = sum(1 for r in results if r['status'] == 'exception')
    
    print(f"\n{'='*80}")
    print(f"DIAGNOSTIC SUMMARY")
    print(f"{'='*80}")
    print(f"Total Problems: {len(results)}")
    print(f"✓ Passed:      {passed} ({100*passed/len(results):.1f}%)")
    print(f"⚠ Warnings:    {warnings} ({100*warnings/len(results):.1f}%)")
    print(f"✗ Failed:      {failed} ({100*failed/len(results):.1f}%)")
    print(f"○ No Output:   {no_output}")
    print(f"⚡ Exceptions: {exceptions}")
    
    print(f"\n{'='*80}")
    print(f"ERROR BREAKDOWN (Failures)")
    print(f"{'='*80}")
    
    # Group failures by error type
    failures = [r for r in results if r['status'] == 'failed']
    failures_by_type: Dict[str, List[Dict]] = defaultdict(list)
    
    for failure in failures:
        error_type = failure['error_type'] or 'Unknown'
        failures_by_type[error_type].append(failure)
    
    for error_type in sorted(failures_by_type.keys()):
        error_problems = failures_by_type[error_type]
        print(f"\n{error_type}: {len(error_problems)} problems")
        print("-" * 80)
        
        for i, problem in enumerate(error_problems[:5], 1):
            print(f"  {i}. {problem['name']}")
            print(f"     {problem['error_snippet']}")
        
        if len(error_problems) > 5:
            print(f"  ... and {len(error_problems) - 5} more")
    
    # Write detailed report
    report_file = project_root / "problems_diagnostic_report.txt"
    with open(report_file, 'w') as f:
        f.write("DETAILED DIAGNOSTIC REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        f.write(f"Summary:\n")
        f.write(f"  Total: {len(results)}\n")
        f.write(f"  Passed: {passed}\n")
        f.write(f"  Warnings: {warnings}\n")
        f.write(f"  Failed: {failed}\n\n")
        
        f.write(f"Failures by Error Type:\n")
        f.write("-" * 80 + "\n")
        
        for error_type in sorted(failures_by_type.keys()):
            error_problems = failures_by_type[error_type]
            f.write(f"\n{error_type}: {len(error_problems)}\n")
            f.write("-" * 40 + "\n")
            
            for problem in sorted(error_problems, key=lambda p: p['name']):
                f.write(f"  {problem['name']}\n")
                f.write(f"    Category: {problem['category']}\n")
                f.write(f"    Error: {problem['error_snippet']}\n")
                if problem['errors_full'] and len(problem['errors_full']) > 200:
                    f.write(f"    Full Error:\n")
                    for line in problem['errors_full'].split('\n')[:20]:
                        f.write(f"      {line}\n")
                f.write(f"\n")
    
    print(f"\n✓ Detailed report written to: {report_file}")
    
    # Write JSON summary
    json_file = project_root / "problems_diagnostic_summary.json"
    with open(json_file, 'w') as f:
        json.dump({
            'summary': {
                'total': len(results),
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'no_output': no_output,
                'exceptions': exceptions,
            },
            'categories': dict(categories_found),
            'errors_by_type': {
                error_type: {
                    'count': len(problems),
                    'problems': [p['name'] for p in problems[:10]]
                }
                for error_type, problems in failures_by_type.items()
            },
            'all_results': results,
        }, f, indent=2)
    
    print(f"✓ JSON summary written to: {json_file}")
    
    # Write quick reference by error type
    quick_ref_file = project_root / "problems_by_error_type.txt"
    with open(quick_ref_file, 'w') as f:
        f.write("PROBLEMS GROUPED BY ERROR TYPE\n")
        f.write("=" * 80 + "\n\n")
        
        for error_type in sorted(failures_by_type.keys()):
            problems = failures_by_type[error_type]
            f.write(f"{error_type} ({len(problems)} problems)\n")
            f.write("-" * 80 + "\n")
            
            for problem in sorted(problems, key=lambda p: p['name']):
                f.write(f"  - {problem['path']}\n")
            
            f.write("\n")
    
    print(f"✓ Quick reference written to: {quick_ref_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
