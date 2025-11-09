#!/usr/bin/env python3
"""
OPL Corpus Selection Tool
Scans the Open Problem Library, parses loadMacros() calls,
and selects problems using only the target 10 macros.
"""
import re
import json
import sys
from pathlib import Path
from typing import Set, Dict, List, Any
from collections import defaultdict


# Target macros for parity testing
TARGET_MACROS = {
    "PGstandard.pl",
    "PGcourse.pl",
    "MathObjects.pl",
    "PGchoicemacros.pl",
    "PGML.pl",
    "PGgraphmacros.pl",
    "AnswerFormatHelp.pl",
    "parserPopUp.pl",
    "parserMultiAnswer.pl",
    "contextFraction.pl",
}


def extract_macros(pg_file: Path) -> Set[str]:
    """
    Parse loadMacros(...) call and return set of macro files.
    Handles various formats:
    - loadMacros("macro1.pl", "macro2.pl");
    - loadMacros('macro1.pl', 'macro2.pl');
    - loadMacros(
        "macro1.pl",
        "macro2.pl",
      );
    """
    try:
        content = pg_file.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return set()

    # Find loadMacros call (may span multiple lines)
    match = re.search(r'loadMacros\s*\((.*?)\)\s*;', content, re.DOTALL)
    if not match:
        return set()

    macro_str = match.group(1)

    # Extract quoted strings (double or single quotes)
    macros = set(re.findall(r'''["']([\w.-]+\.pl)["']''', macro_str))

    return macros


def categorize_problem(macros: Set[str]) -> str:
    """
    Categorize a problem based on its macro usage.
    Returns: 'target_only', 'mixed', 'other'
    """
    if not macros:
        return 'other'

    if macros.issubset(TARGET_MACROS):
        return 'target_only'
    elif macros & TARGET_MACROS:
        return 'mixed'
    else:
        return 'other'


def scan_opl_directory(opl_dir: Path, max_problems: int = None) -> Dict[str, Any]:
    """
    Scan OPL directory and categorize problems.
    Returns statistics and selected problems.
    """
    stats = {
        'total_scanned': 0,
        'target_only': 0,
        'mixed': 0,
        'other': 0,
        'parse_errors': 0,
    }

    problems_by_category = defaultdict(list)
    macro_usage_counts = defaultdict(int)
    problems_per_macro = defaultdict(list)

    print(f"Scanning {opl_dir}...", file=sys.stderr)

    for pg_file in opl_dir.rglob("*.pg"):
        stats['total_scanned'] += 1

        if max_problems and stats['total_scanned'] > max_problems:
            break

        if stats['total_scanned'] % 1000 == 0:
            print(f"  Scanned {stats['total_scanned']} files...", file=sys.stderr)

        try:
            macros = extract_macros(pg_file)
            category = categorize_problem(macros)

            stats[category] += 1

            problem_data = {
                'path': str(pg_file.relative_to(opl_dir)),
                'macros': sorted(macros),
                'category': category,
            }

            problems_by_category[category].append(problem_data)

            # Track macro usage
            for macro in macros:
                macro_usage_counts[macro] += 1
                if macro in TARGET_MACROS:
                    problems_per_macro[macro].append(problem_data)

        except Exception as e:
            stats['parse_errors'] += 1

    return {
        'stats': stats,
        'problems_by_category': dict(problems_by_category),
        'macro_usage_counts': dict(macro_usage_counts),
        'problems_per_macro': dict(problems_per_macro),
    }


def select_corpus(scan_results: Dict[str, Any], min_per_macro: int = 10) -> List[Dict[str, Any]]:
    """
    Select a balanced corpus ensuring minimum coverage per macro.
    """
    problems_per_macro = scan_results['problems_per_macro']

    # Start with problems that use only target macros
    selected_map = {}

    # First pass: select problems for each macro to meet minimum
    for macro in TARGET_MACROS:
        macro_problems = problems_per_macro.get(macro, [])

        # Filter to target_only category first
        target_only = [p for p in macro_problems if p['category'] == 'target_only']

        # Select up to min_per_macro
        for problem in target_only[:min_per_macro]:
            selected_map[problem['path']] = problem

    # Convert to list
    selected = list(selected_map.values())

    # Sort by path for reproducibility
    selected.sort(key=lambda p: p['path'])

    return selected


def main():
    if len(sys.argv) not in (3, 4):
        print(f"Usage: {sys.argv[0]} <opl_directory> <output.json> [max_files]", file=sys.stderr)
        print(f"\nExample:", file=sys.stderr)
        print(f"  {sys.argv[0]} ../webwork-open-problem-library parity_lab/build/corpus.json 5000", file=sys.stderr)
        sys.exit(1)

    opl_dir = Path(sys.argv[1])
    output = Path(sys.argv[2])
    max_problems = int(sys.argv[3]) if len(sys.argv) == 4 else None

    if not opl_dir.exists():
        print(f"Error: OPL directory not found: {opl_dir}", file=sys.stderr)
        print(f"Clone it with: git clone https://github.com/openwebwork/webwork-open-problem-library.git {opl_dir}", file=sys.stderr)
        sys.exit(1)

    # Scan OPL
    scan_results = scan_opl_directory(opl_dir, max_problems)

    # Select corpus
    selected = select_corpus(scan_results, min_per_macro=10)

    # Compute coverage
    coverage = defaultdict(int)
    for problem in selected:
        for macro in problem['macros']:
            if macro in TARGET_MACROS:
                coverage[macro] += 1

    # Prepare output
    output_data = {
        'total_selected': len(selected),
        'scan_stats': scan_results['stats'],
        'coverage': dict(coverage),
        'problems': selected,
        'target_macros': sorted(TARGET_MACROS),
    }

    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Print summary
    print(f"\n✓ Corpus selection complete", file=sys.stderr)
    print(f"  Output: {output}", file=sys.stderr)
    print(f"  Total scanned: {scan_results['stats']['total_scanned']}", file=sys.stderr)
    print(f"  Selected: {len(selected)} problems", file=sys.stderr)
    print(f"  Target-only problems: {scan_results['stats']['target_only']}", file=sys.stderr)
    print(f"\n  Coverage per macro:", file=sys.stderr)
    for macro in sorted(TARGET_MACROS):
        count = coverage.get(macro, 0)
        print(f"    {macro:30s} {count:4d} problems", file=sys.stderr)


if __name__ == "__main__":
    main()
