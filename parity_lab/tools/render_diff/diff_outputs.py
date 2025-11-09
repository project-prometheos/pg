#!/usr/bin/env python3
"""
Output Diff Engine
Compares JSON outputs from Perl and Python runtimes and reports differences.
Applies normalization rules for whitespace, HTML entities, numeric tolerances, etc.
"""
import json
import sys
import re
import html
from pathlib import Path
from typing import Any, Dict, List, Tuple
from difflib import unified_diff


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.
    - Decode HTML entities
    - Collapse whitespace runs
    - Trim leading/trailing whitespace
    - Normalize line endings
    """
    if not isinstance(text, str):
        return str(text)

    # Decode HTML entities
    text = html.unescape(text)

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Collapse multiple spaces/tabs to single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Collapse multiple newlines
    text = re.sub(r'\n\n+', '\n\n', text)

    # Trim each line
    text = '\n'.join(line.strip() for line in text.split('\n'))

    # Trim overall
    text = text.strip()

    return text


def normalize_number(val: Any, tolerance: float = 1e-9) -> Any:
    """
    Normalize numeric values for comparison with tolerance.
    Returns rounded value for floats, original value otherwise.
    """
    if isinstance(val, (int, float)):
        # Round to avoid floating point precision issues
        if abs(val) < tolerance:
            return 0.0
        return round(val, 9)
    return val


def compare_numbers(a: Any, b: Any, tolerance: float = 1e-9) -> bool:
    """Compare two values as numbers with tolerance."""
    try:
        a_num = float(a)
        b_num = float(b)
        return abs(a_num - b_num) < tolerance
    except (ValueError, TypeError):
        return a == b


def diff_text_detailed(text1: str, text2: str, label1: str = "Perl", label2: str = "Python") -> List[str]:
    """Generate unified diff of two text strings."""
    lines1 = text1.splitlines(keepends=False)
    lines2 = text2.splitlines(keepends=False)

    return list(unified_diff(
        lines1,
        lines2,
        fromfile=label1,
        tofile=label2,
        lineterm='',
        n=3  # context lines
    ))


def compare_answers(perl_answers: List[Dict], py_answers: List[Dict]) -> List[Dict[str, Any]]:
    """Compare answer lists from Perl and Python outputs."""
    diffs = []

    # Build dictionaries by name
    perl_ans_dict = {ans['name']: ans for ans in perl_answers}
    py_ans_dict = {ans['name']: ans for ans in py_answers}

    all_names = sorted(set(perl_ans_dict.keys()) | set(py_ans_dict.keys()))

    for name in all_names:
        if name not in perl_ans_dict:
            diffs.append({
                "type": "answer",
                "name": name,
                "issue": "missing_in_perl",
                "severity": "high",
            })
        elif name not in py_ans_dict:
            diffs.append({
                "type": "answer",
                "name": name,
                "issue": "missing_in_python",
                "severity": "high",
            })
        else:
            perl_ans = perl_ans_dict[name]
            py_ans = py_ans_dict[name]

            # Compare score
            if not compare_numbers(perl_ans.get('score', 0), py_ans.get('score', 0)):
                diffs.append({
                    "type": "answer",
                    "name": name,
                    "field": "score",
                    "issue": "score_mismatch",
                    "severity": "high",
                    "perl_value": perl_ans.get('score', 0),
                    "python_value": py_ans.get('score', 0),
                })

            # Compare correct flag
            perl_correct = bool(perl_ans.get('correct', False))
            py_correct = bool(py_ans.get('correct', False))
            if perl_correct != py_correct:
                diffs.append({
                    "type": "answer",
                    "name": name,
                    "field": "correct",
                    "issue": "correct_flag_mismatch",
                    "severity": "high",
                    "perl_value": perl_correct,
                    "python_value": py_correct,
                })

            # Compare message (normalized)
            perl_msg = normalize_text(perl_ans.get('message', ''))
            py_msg = normalize_text(py_ans.get('message', ''))
            if perl_msg != py_msg:
                diffs.append({
                    "type": "answer",
                    "name": name,
                    "field": "message",
                    "issue": "message_mismatch",
                    "severity": "medium",
                    "perl_value": perl_msg[:100],
                    "python_value": py_msg[:100],
                })

    return diffs


def diff_outputs(perl_output: Dict, py_output: Dict) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Compare Perl and Python outputs.
    Returns (all_match: bool, differences: List[Dict])
    """
    diffs = []

    # Compare TeX output
    perl_tex = normalize_text(perl_output.get('tex', ''))
    py_tex = normalize_text(py_output.get('tex', ''))

    if perl_tex != py_tex:
        diff_lines = diff_text_detailed(perl_tex, py_tex, "Perl TeX", "Python TeX")
        diffs.append({
            "type": "tex",
            "issue": "content_mismatch",
            "severity": "high",
            "diff": diff_lines[:50],  # Limit diff lines
            "perl_length": len(perl_tex),
            "python_length": len(py_tex),
        })

    # Compare HTML output
    perl_html = normalize_text(perl_output.get('html', ''))
    py_html = normalize_text(py_output.get('html', ''))

    if perl_html != py_html:
        diff_lines = diff_text_detailed(perl_html, py_html, "Perl HTML", "Python HTML")
        diffs.append({
            "type": "html",
            "issue": "content_mismatch",
            "severity": "high",
            "diff": diff_lines[:50],  # Limit diff lines
            "perl_length": len(perl_html),
            "python_length": len(py_html),
        })

    # Compare answers
    answer_diffs = compare_answers(
        perl_output.get('answers', []),
        py_output.get('answers', [])
    )
    diffs.extend(answer_diffs)

    # Check for errors
    perl_errors = perl_output.get('errors', [])
    py_errors = py_output.get('errors', [])

    if perl_errors and not py_errors:
        diffs.append({
            "type": "error",
            "issue": "perl_has_errors_python_does_not",
            "severity": "high",
            "perl_errors": perl_errors,
        })
    elif py_errors and not perl_errors:
        diffs.append({
            "type": "error",
            "issue": "python_has_errors_perl_does_not",
            "severity": "high",
            "python_errors": py_errors,
        })
    elif perl_errors and py_errors:
        # Both have errors - compare them
        if normalize_text(str(perl_errors)) != normalize_text(str(py_errors)):
            diffs.append({
                "type": "error",
                "issue": "different_errors",
                "severity": "medium",
                "perl_errors": perl_errors,
                "python_errors": py_errors,
            })

    return len(diffs) == 0, diffs


def print_diff_report(diffs: List[Dict[str, Any]], verbose: bool = True):
    """Print human-readable diff report to stderr."""
    if not diffs:
        print("✓ No differences found - outputs match!", file=sys.stderr)
        return

    print(f"\n❌ Found {len(diffs)} difference(s):\n", file=sys.stderr)

    for i, diff in enumerate(diffs, 1):
        severity = diff.get('severity', 'unknown')
        severity_symbol = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢',
        }.get(severity, '⚪')

        print(f"{severity_symbol} Difference {i} [{severity.upper()}]:", file=sys.stderr)
        print(f"   Type: {diff.get('type', 'unknown')}", file=sys.stderr)
        print(f"   Issue: {diff.get('issue', 'unknown')}", file=sys.stderr)

        if 'name' in diff:
            print(f"   Answer: {diff['name']}", file=sys.stderr)
        if 'field' in diff:
            print(f"   Field: {diff['field']}", file=sys.stderr)

        if 'perl_value' in diff or 'python_value' in diff:
            print(f"   Perl:   {diff.get('perl_value', 'N/A')}", file=sys.stderr)
            print(f"   Python: {diff.get('python_value', 'N/A')}", file=sys.stderr)

        if verbose and 'diff' in diff:
            print(f"   Unified diff (first 20 lines):", file=sys.stderr)
            for line in diff['diff'][:20]:
                print(f"     {line}", file=sys.stderr)

        if 'perl_errors' in diff:
            print(f"   Perl errors: {diff['perl_errors']}", file=sys.stderr)
        if 'python_errors' in diff:
            print(f"   Python errors: {diff['python_errors']}", file=sys.stderr)

        print("", file=sys.stderr)


def main():
    if len(sys.argv) not in (3, 4):
        print(f"Usage: {sys.argv[0]} <perl_output.json> <py_output.json> [--verbose]", file=sys.stderr)
        sys.exit(1)

    perl_json_path = Path(sys.argv[1])
    py_json_path = Path(sys.argv[2])
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Load JSON files
    try:
        with open(perl_json_path) as f:
            perl_output = json.load(f)
    except Exception as e:
        print(f"Error loading Perl output: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(py_json_path) as f:
            py_output = json.load(f)
    except Exception as e:
        print(f"Error loading Python output: {e}", file=sys.stderr)
        sys.exit(1)

    # Compare outputs
    all_match, diffs = diff_outputs(perl_output, py_output)

    # Print report
    print_diff_report(diffs, verbose=verbose)

    # Write detailed diff to JSON for programmatic use
    diff_json_path = perl_json_path.parent / "diff_report.json"
    with open(diff_json_path, 'w') as f:
        json.dump({
            "all_match": all_match,
            "difference_count": len(diffs),
            "differences": diffs,
        }, f, indent=2)

    if all_match:
        print(f"✓ Outputs match! Detailed report: {diff_json_path}", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"❌ Outputs differ. Detailed report: {diff_json_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
