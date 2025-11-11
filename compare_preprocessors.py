"""
Comprehensive comparison test between regex and grammar-based preprocessors.

This script:
1. Finds all .pg files in the tutorial directory
2. Preprocesses each with both approaches
3. Compares outputs and reports differences
4. Generates a detailed report
"""

from itertools import filterfalse
import sys
from pathlib import Path
from difflib import unified_diff
from collections import defaultdict

from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor as RegexPreprocessor
from packages.pg_translator.pg_translator.pg_preprocessor_pygment import PGPreprocessor as GrammarPreprocessor


def compare_outputs(regex_output: str, grammar_output: str, filename: str) -> dict:
    """Compare two preprocessor outputs and return differences."""
    regex_lines = regex_output.strip().split('\n')
    grammar_lines = grammar_output.strip().split('\n')

    result = {
        'filename': filename,
        'identical': regex_output.strip() == grammar_output.strip(),
        'regex_lines': len(regex_lines),
        'grammar_lines': len(grammar_lines),
        'diff': None
    }

    if not result['identical']:
        diff = list(unified_diff(
            regex_lines,
            grammar_lines,
            fromfile=f'{filename} (regex)',
            tofile=f'{filename} (grammar)',
            lineterm=''
        ))
        result['diff'] = '\n'.join(diff[:50])  # First 50 lines of diff

    return result


def test_file(pg_file: Path, regex_proc: RegexPreprocessor, grammar_proc: GrammarPreprocessor) -> dict:
    """Test a single PG file with both preprocessors."""
    print(f"Testing: {pg_file.name}...", end=' ')

    try:
        pg_source = pg_file.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"[SKIP] Cannot read file: {e}")
        return {'filename': pg_file.name, 'status': 'read_error', 'error': str(e)}

    # Test regex preprocessor
    try:
        regex_result = regex_proc.preprocess(
            pg_source, use_sandbox_macros=filterfalse)
        regex_output = regex_result.code
        regex_error = None
    except Exception as e:
        regex_output = ""
        regex_error = str(e)

    # Test grammar preprocessor
    try:
        grammar_result = grammar_proc.preprocess(
            pg_source, use_sandbox_macros=False)
        grammar_output = grammar_result.code
        grammar_error = None
    except Exception as e:
        grammar_output = ""
        grammar_error = str(e)

    # Determine status
    if regex_error and grammar_error:
        print("[BOTH FAIL]")
        return {
            'filename': pg_file.name,
            'status': 'both_fail',
            'regex_error': regex_error,
            'grammar_error': grammar_error
        }
    elif regex_error:
        print("[REGEX FAIL]")
        return {
            'filename': pg_file.name,
            'status': 'regex_fail',
            'regex_error': regex_error,
            'grammar_success': True
        }
    elif grammar_error:
        print("[GRAMMAR FAIL]")
        return {
            'filename': pg_file.name,
            'status': 'grammar_fail',
            'grammar_error': grammar_error,
            'regex_success': True
        }
    else:
        # Both succeeded - compare outputs
        comparison = compare_outputs(
            regex_output, grammar_output, pg_file.name)
        if comparison['identical']:
            print("[IDENTICAL]")
            comparison['status'] = 'identical'
        else:
            print("[DIFFERENT]")
            comparison['status'] = 'different'
        return comparison


def generate_report(results: list) -> str:
    """Generate a summary report from test results."""
    stats = defaultdict(int)

    for result in results:
        stats[result.get('status', 'unknown')] += 1

    total = len(results)

    report = [
        "=" * 80,
        "PREPROCESSOR COMPARISON REPORT",
        "=" * 80,
        "",
        f"Total files tested: {total}",
        "",
        "Results:",
        f"  [OK] Identical outputs:     {stats['identical']:3d} ({100*stats['identical']//total if total else 0}%)",
        f"  [!=] Different outputs:     {stats['different']:3d} ({100*stats['different']//total if total else 0}%)",
        f"  [X]  Grammar failures:      {stats['grammar_fail']:3d} ({100*stats['grammar_fail']//total if total else 0}%)",
        f"  [X]  Regex failures:        {stats['regex_fail']:3d} ({100*stats['regex_fail']//total if total else 0}%)",
        f"  [X]  Both failed:           {stats['both_fail']:3d} ({100*stats['both_fail']//total if total else 0}%)",
        f"  [?]  Read errors:           {stats['read_error']:3d} ({100*stats['read_error']//total if total else 0}%)",
        "",
        "=" * 80,
    ]

    # Show files with differences
    different = [r for r in results if r.get('status') == 'different']
    if different:
        report.extend([
            "",
            f"FILES WITH DIFFERENT OUTPUTS ({len(different)}):",
            "-" * 80,
        ])
        for result in different[:10]:  # Show first 10
            report.append(f"  • {result['filename']}")
            report.append(
                f"    Regex: {result['regex_lines']} lines, Grammar: {result['grammar_lines']} lines")

    # Show grammar failures
    grammar_fails = [r for r in results if r.get('status') == 'grammar_fail']
    if grammar_fails:
        report.extend([
            "",
            f"GRAMMAR PREPROCESSOR FAILURES ({len(grammar_fails)}):",
            "-" * 80,
        ])
        for result in grammar_fails[:5]:  # Show first 5
            report.append(f"  • {result['filename']}")
            error = result.get('grammar_error', 'Unknown error')
            report.append(f"    Error: {error[:100]}...")

    return '\n'.join(report)


def main():
    """Main test runner."""
    print("=" * 80)
    print("COMPREHENSIVE PREPROCESSOR COMPARISON TEST")
    print("=" * 80)
    print()

    # Find tutorial PG files
    tutorial_dir = Path('d:/pg/tutorial')
    if not tutorial_dir.exists():
        print(f"Error: Tutorial directory not found: {tutorial_dir}")
        return

    pg_files = list(tutorial_dir.rglob('*.pg'))
    print(f"Found {len(pg_files)} PG files in tutorial directory")
    print()

    # Limit to first 20 for quick testing
    pg_files = pg_files[:20]
    print(f"Testing first {len(pg_files)} files...")
    print()

    # Initialize preprocessors
    regex_proc = RegexPreprocessor()
    grammar_proc = GrammarPreprocessor()

    # Test each file
    results = []
    for pg_file in pg_files:
        result = test_file(pg_file, regex_proc, grammar_proc)
        results.append(result)

    print()

    # Generate and display report
    report = generate_report(results)
    print(report)

    # Save detailed results
    output_file = Path('d:/pg/preprocessor_comparison_results.txt')
    with output_file.open('w', encoding='utf-8') as f:
        f.write(report)
        f.write('\n\n')
        f.write('=' * 80)
        f.write('\nDETAILED DIFFERENCES\n')
        f.write('=' * 80)
        f.write('\n\n')

        for result in results:
            if result.get('status') == 'different' and result.get('diff'):
                f.write(f"\n{'=' * 80}\n")
                f.write(f"File: {result['filename']}\n")
                f.write(f"{'=' * 80}\n")
                f.write(result['diff'])
                f.write('\n\n')

    print()
    print(f"Detailed results saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()
