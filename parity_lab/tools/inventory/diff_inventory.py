#!/usr/bin/env python3
"""
Compare Perl and Python inventories and produce diff report.
Output: HTML table with added/removed/changed symbols, color-coded.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from html import escape


def normalize_name(name: str) -> str:
    """
    Normalize symbol names for comparison.
    Handles Perl camelCase vs Python snake_case conventions.
    """
    # For now, do exact match - we can add more sophisticated mapping later
    return name.lower()


def compare_params(perl_params: List[str], py_params: List[str]) -> tuple[bool, str]:
    """
    Compare parameter lists, accounting for Perl sigils ($, @, %) vs Python names.
    Returns (match: bool, details: str)
    """
    # Strip Perl sigils for comparison
    perl_clean = [p.lstrip('$@%') for p in perl_params]
    py_clean = [p for p in py_params]

    if perl_clean == py_clean:
        return True, ""

    # Show differences
    perl_set = set(perl_clean)
    py_set = set(py_clean)

    missing_in_py = perl_set - py_set
    extra_in_py = py_set - perl_set

    details = []
    if missing_in_py:
        details.append(f"Missing in Python: {', '.join(sorted(missing_in_py))}")
    if extra_in_py:
        details.append(f"Extra in Python: {', '.join(sorted(extra_in_py))}")

    return False, "; ".join(details)


def diff_symbols(perl_syms: Dict[str, Any], py_syms: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compare symbols between Perl and Python."""
    report = []

    all_names = set(perl_syms.keys()) | set(py_syms.keys())

    for name in sorted(all_names):
        if name in perl_syms and name not in py_syms:
            # Symbol in Perl but not Python
            report.append({
                "symbol": name,
                "status": "MISSING_IN_PYTHON",
                "severity": "high",
                "perl_type": perl_syms[name]["type"],
                "perl_params": perl_syms[name]["params"],
                "py_type": None,
                "py_params": None,
                "details": f"Perl has {len(perl_syms[name]['params'])} params"
            })

        elif name not in perl_syms and name in py_syms:
            # Symbol in Python but not Perl
            report.append({
                "symbol": name,
                "status": "ADDED_IN_PYTHON",
                "severity": "medium",
                "perl_type": None,
                "perl_params": None,
                "py_type": py_syms[name]["type"],
                "py_params": py_syms[name]["params"],
                "details": f"Python has {len(py_syms[name]['params'])} params"
            })

        else:
            # Symbol exists in both - compare details
            perl_sym = perl_syms[name]
            py_sym = py_syms[name]

            # Compare parameter lists
            params_match, param_details = compare_params(perl_sym["params"], py_sym["params"])

            if not params_match:
                report.append({
                    "symbol": name,
                    "status": "SIGNATURE_MISMATCH",
                    "severity": "high",
                    "perl_type": perl_sym["type"],
                    "perl_params": perl_sym["params"],
                    "py_type": py_sym["type"],
                    "py_params": py_sym["params"],
                    "details": param_details
                })
            else:
                # Check defaults
                perl_defaults = set(perl_sym.get("defaults", {}).keys())
                py_defaults = set(py_sym.get("defaults", {}).keys())

                if perl_defaults != py_defaults:
                    diff_defaults = (perl_defaults - py_defaults) | (py_defaults - perl_defaults)
                    report.append({
                        "symbol": name,
                        "status": "DEFAULT_MISMATCH",
                        "severity": "medium",
                        "perl_type": perl_sym["type"],
                        "perl_params": perl_sym["params"],
                        "py_type": py_sym["type"],
                        "py_params": py_sym["params"],
                        "details": f"Different defaults: {', '.join(sorted(diff_defaults))}"
                    })
                else:
                    # Full match
                    report.append({
                        "symbol": name,
                        "status": "OK",
                        "severity": "none",
                        "perl_type": perl_sym["type"],
                        "perl_params": perl_sym["params"],
                        "py_type": py_sym["type"],
                        "py_params": py_sym["params"],
                        "details": ""
                    })

    return report


def diff_inventories(perl_inv: Dict, py_inv: Dict) -> Dict[str, List[Dict[str, Any]]]:
    """Compare Perl and Python inventories for all files."""
    all_reports = {}

    for file_key in perl_inv.keys():
        perl_data = perl_inv[file_key]
        py_data = py_inv.get(file_key, {"symbols": []})

        # Build symbol dictionaries
        perl_syms = {s["name"]: s for s in perl_data.get("symbols", [])}
        py_syms = {s["name"]: s for s in py_data.get("symbols", [])}

        report = diff_symbols(perl_syms, py_syms)
        all_reports[file_key] = report

    return all_reports


def generate_html_report(reports: Dict[str, List[Dict]], output_path: Path):
    """Generate HTML report with color-coded diff table."""
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Perl-Python Macro Inventory Diff</title>",
        "<style>",
        "body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }",
        "h1 { color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }",
        "h2 { color: #0066cc; margin-top: 30px; background: #e6f2ff; padding: 10px; border-radius: 5px; }",
        ".summary { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
        ".summary-item { display: inline-block; margin: 10px 20px 10px 0; padding: 10px 15px; border-radius: 3px; }",
        ".summary-ok { background: #d4edda; color: #155724; }",
        ".summary-warn { background: #fff3cd; color: #856404; }",
        ".summary-error { background: #f8d7da; color: #721c24; }",
        "table { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
        "th, td { border: 1px solid #ddd; padding: 12px 8px; text-align: left; }",
        "th { background-color: #0066cc; color: white; font-weight: 600; position: sticky; top: 0; }",
        "tr:nth-child(even) { background-color: #f9f9f9; }",
        "tr:hover { background-color: #e6f2ff; }",
        ".OK { background-color: #d4edda; }",
        ".MISSING_IN_PYTHON { background-color: #f8d7da; font-weight: 600; }",
        ".ADDED_IN_PYTHON { background-color: #fff3cd; }",
        ".SIGNATURE_MISMATCH { background-color: #f8d7da; font-weight: 600; }",
        ".DEFAULT_MISMATCH { background-color: #fff3cd; }",
        ".status { font-weight: 600; text-transform: uppercase; font-size: 0.85em; }",
        ".severity-high { color: #d32f2f; }",
        ".severity-medium { color: #f57c00; }",
        ".severity-none { color: #388e3c; }",
        "code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Consolas', monospace; }",
        ".filter { margin: 20px 0; }",
        ".filter button { margin: 5px; padding: 8px 15px; border: none; border-radius: 3px; cursor: pointer; }",
        ".filter button:hover { opacity: 0.8; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Perl-Python Macro Inventory Diff Report</h1>",
    ]

    # Calculate summary statistics
    total_ok = 0
    total_missing = 0
    total_mismatch = 0
    total_added = 0

    for file_reports in reports.values():
        for item in file_reports:
            if item["status"] == "OK":
                total_ok += 1
            elif item["status"] == "MISSING_IN_PYTHON":
                total_missing += 1
            elif item["status"] in ("SIGNATURE_MISMATCH", "DEFAULT_MISMATCH"):
                total_mismatch += 1
            elif item["status"] == "ADDED_IN_PYTHON":
                total_added += 1

    # Summary section
    html_parts.extend([
        "<div class='summary'>",
        "<h3>Summary</h3>",
        f"<div class='summary-item summary-ok'>✓ Matching: {total_ok}</div>",
        f"<div class='summary-item summary-error'>✗ Missing in Python: {total_missing}</div>",
        f"<div class='summary-item summary-error'>⚠ Signature Mismatches: {total_mismatch}</div>",
        f"<div class='summary-item summary-warn'>+ Added in Python: {total_added}</div>",
        "</div>",
    ])

    # Per-file tables
    for file_key in sorted(reports.keys()):
        file_reports = reports[file_key]

        if not file_reports:
            continue

        # Count statuses for this file
        file_ok = sum(1 for r in file_reports if r["status"] == "OK")
        file_issues = len(file_reports) - file_ok

        html_parts.extend([
            f"<h2>{escape(file_key)} ({file_ok} OK, {file_issues} issues)</h2>",
            "<table>",
            "<tr>",
            "<th>Symbol</th>",
            "<th>Status</th>",
            "<th>Perl Type</th>",
            "<th>Perl Params</th>",
            "<th>Python Type</th>",
            "<th>Python Params</th>",
            "<th>Details</th>",
            "</tr>",
        ])

        for item in sorted(file_reports, key=lambda x: (x["status"] != "OK", x["symbol"])):
            status_class = item["status"]
            severity_class = f"severity-{item['severity']}"

            perl_params_str = ", ".join(item["perl_params"]) if item["perl_params"] else "—"
            py_params_str = ", ".join(item["py_params"]) if item["py_params"] else "—"

            html_parts.append(
                f"<tr class='{status_class}'>"
                f"<td><code>{escape(item['symbol'])}</code></td>"
                f"<td class='status {severity_class}'>{escape(item['status'].replace('_', ' '))}</td>"
                f"<td>{escape(str(item['perl_type'])) if item['perl_type'] else '—'}</td>"
                f"<td><code>{escape(perl_params_str)}</code></td>"
                f"<td>{escape(str(item['py_type'])) if item['py_type'] else '—'}</td>"
                f"<td><code>{escape(py_params_str)}</code></td>"
                f"<td>{escape(item['details'])}</td>"
                "</tr>"
            )

        html_parts.append("</table>")

    html_parts.extend([
        "</body>",
        "</html>",
    ])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <perl_inventory.json> <py_inventory.json> <output.html>", file=sys.stderr)
        sys.exit(1)

    perl_inv_path = Path(sys.argv[1])
    py_inv_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    # Load inventories
    try:
        with open(perl_inv_path) as f:
            perl_inv = json.load(f)
    except Exception as e:
        print(f"Error loading Perl inventory: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(py_inv_path) as f:
            py_inv = json.load(f)
    except Exception as e:
        print(f"Error loading Python inventory: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate diff
    reports = diff_inventories(perl_inv, py_inv)

    # Generate HTML report
    generate_html_report(reports, output_path)

    print(f"✓ Diff report written to {output_path}", file=sys.stderr)

    # Print summary to stderr
    total_files = len(reports)
    total_issues = sum(
        sum(1 for item in file_reports if item["status"] != "OK")
        for file_reports in reports.values()
    )

    print(f"  Files analyzed: {total_files}", file=sys.stderr)
    print(f"  Total issues found: {total_issues}", file=sys.stderr)


if __name__ == "__main__":
    main()
