#!/usr/bin/env python3
"""
Fix common issues in tutorial sample problems.

This script identifies patterns in failing problems and applies fixes.
"""

import sys
import re
from pathlib import Path

# Add packages to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))


COMMON_FIXES = [
    {
        'name': 'Missing String import',
        'pattern': r"name 'String' is not defined",
        'fix': 'Add String to imports in preprocessor or MathObjects'
    },
    {
        'name': 'Perl map syntax',
        'pattern': r'map \{.*?\}.*?\.\.',
        'fix': 'Convert Perl map to Python list comprehension'
    },
    {
        'name': 'Unclosed dict in lambda',
        'pattern': r'\{\s*[\'"].*?[\'"]\s*:\s*lambda.*?\)',
        'fix': 'Close dictionary properly'
    },
    {
        'name': 'Missing re module',
        'pattern': r"name 're' is not defined",
        'fix': 'Add re import'
    },
    {
        'name': 'Undefined variable x3',
        'pattern': r"name 'x3' is not defined",
        'fix': 'Check variable naming in preprocessor'
    },
    {
        'name': 'String concatenation with int',
        'pattern': r'can only concatenate str \(not "int"\)',
        'fix': 'Add str() conversion'
    },
    {
        'name': 'Missing add_dataset method',
        'pattern': r"'Plot' object has no attribute 'add_dataset'",
        'fix': 'Update Plot implementation'
    },
    {
        'name': 'Matrix object not callable',
        'pattern': r"'Matrix' object is not callable",
        'fix': 'Fix Matrix construction syntax'
    },
    {
        'name': 'Missing install_problem_grader',
        'pattern': r"name 'install_problem_grader' is not defined",
        'fix': 'Add problem grader function'
    },
]


def categorize_error(error_msg: str) -> dict:
    """Categorize an error message."""
    for fix_info in COMMON_FIXES:
        if re.search(fix_info['pattern'], error_msg):
            return fix_info
    return {'name': 'Unknown', 'pattern': None, 'fix': 'Manual investigation needed'}


def analyze_errors(test_output_file: Path):
    """Analyze test failures and categorize errors."""
    if not test_output_file.exists():
        print(f"Test output file not found: {test_output_file}")
        return
    
    with open(test_output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract error patterns
    error_pattern = re.compile(
        r'test_tutorial_problem_renders\[(\w+)\].*?'
        r'Failed: Problem \1\.pg failed with errors:\s*'
        r'((?:.*?Error.*?\n)+)',
        re.MULTILINE | re.DOTALL
    )
    
    problems_by_error = {}
    
    for match in error_pattern.finditer(content):
        problem_name = match.group(1)
        error_text = match.group(2)
        
        category = categorize_error(error_text)
        error_type = category['name']
        
        if error_type not in problems_by_error:
            problems_by_error[error_type] = []
        
        problems_by_error[error_type].append({
            'problem': problem_name,
            'error': error_text.strip(),
            'fix': category['fix']
        })
    
    # Print summary
    print("=" * 80)
    print("ERROR CATEGORIZATION SUMMARY")
    print("=" * 80)
    print()
    
    for error_type, problems in sorted(problems_by_error.items(), key=lambda x: -len(x[1])):
        print(f"\n{error_type} ({len(problems)} problems)")
        print("-" * 80)
        print(f"Fix: {problems[0]['fix']}")
        print(f"\nAffected problems:")
        for p in problems:
            print(f"  - {p['problem']}")
    
    print("\n" + "=" * 80)
    print(f"Total unique error types: {len(problems_by_error)}")
    print(f"Total failing problems: {sum(len(p) for p in problems_by_error.values())}")
    print("=" * 80)
    
    return problems_by_error


def main():
    test_output = project_root / "test_failures.txt"
    
    if not test_output.exists():
        print(f"Running tests to generate {test_output}...")
        import subprocess
        cmd = [
            sys.executable,
            "-m", "pytest",
            str(project_root / "packages" / "pg_translator" / "tests" / "test_tutorial_sample_problems.py"),
            "-v", "--tb=short"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        test_output.write_text(result.stdout + "\n" + result.stderr, encoding='utf-8')
    
    analyze_errors(test_output)


if __name__ == '__main__':
    main()
