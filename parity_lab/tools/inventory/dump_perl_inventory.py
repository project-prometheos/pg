#!/usr/bin/env python3
"""
Extract symbols, signatures, defaults from Perl .pl macro files.
Uses regex parsing to extract subs, exported symbols, and POD documentation.

Output JSON schema:
{
  "file": "PGstandard.pl",
  "symbols": [
    {
      "name": "random",
      "type": "sub",
      "params": ["$min", "$max", "$step"],
      "defaults": {"step": 1},
      "pod": "Returns random number...",
      "line": 123
    }
  ],
  "globals": ["$PG_OUTPUT", "%PG_ANSWERS_HASH"],
  "exports": ["random", "non_zero_random"]
}
"""
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def extract_pod_for_sub(content: str, sub_name: str) -> str:
    """Extract POD documentation for a specific subroutine."""
    # Look for =item or =head2 entries matching the sub name
    pod_pattern = rf'=(?:item|head2)\s+(?:\w+\s+)?{re.escape(sub_name)}.*?\n(.*?)(?:=(?:item|head2|cut)|$)'
    match = re.search(pod_pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        pod_text = match.group(1).strip()
        # Clean up POD formatting
        pod_text = re.sub(r'\n\s+', ' ', pod_text)
        return pod_text[:200]  # Truncate for readability
    return ""


def extract_defaults(content: str, sub_start: int, sub_end: int) -> Dict[str, Any]:
    """
    Extract default values from subroutine body.
    Looks for patterns like: my $step = shift // 1;
    """
    sub_body = content[sub_start:sub_end]
    defaults = {}

    # Pattern: my $var = shift // default;
    for match in re.finditer(r'my\s+\$(\w+)\s*=\s*(?:shift|pop)\s*//\s*([^;]+);', sub_body):
        var_name = match.group(1)
        default_val = match.group(2).strip()
        defaults[var_name] = default_val

    # Pattern: my $var = defined $_[N] ? $_[N] : default;
    for match in re.finditer(r'my\s+\$(\w+)\s*=\s*defined\s+\$_\[\d+\]\s*\?\s*\$_\[\d+\]\s*:\s*([^;]+);', sub_body):
        var_name = match.group(1)
        default_val = match.group(2).strip()
        defaults[var_name] = default_val

    return defaults


def extract_params(content: str, sub_start: int, sub_end: int) -> List[str]:
    """
    Extract parameter names from subroutine body.
    Looks for patterns like: my ($a, $b, $c) = @_;
    """
    sub_body = content[sub_start:sub_end]
    params = []

    # Pattern: my ($var1, $var2, ...) = @_;
    match = re.search(r'my\s+\(([\$\@\%\w\s,]+)\)\s*=\s*\@_', sub_body)
    if match:
        param_str = match.group(1)
        params = [p.strip() for p in param_str.split(',')]
    else:
        # Pattern: my $var = shift; (multiple times)
        shift_matches = re.findall(r'my\s+(\$\w+)\s*=\s*shift', sub_body)
        params.extend(shift_matches)

    return params


def parse_perl_file(filepath: Path) -> Dict[str, Any]:
    """Parse a Perl .pl file and extract symbols, exports, globals."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return {
            "file": filepath.name,
            "symbols": [],
            "globals": [],
            "exports": [],
            "error": str(e)
        }

    symbols = []
    globals_set = set()
    exports = []

    # Extract exported symbols from @EXPORT, @EXPORT_OK, or our(...) declarations
    export_patterns = [
        r'our\s+\@EXPORT\s*=\s*qw\(([\w\s]+)\)',
        r'our\s+\@EXPORT_OK\s*=\s*qw\(([\w\s]+)\)',
        r'\@EXPORT\s*=\s*qw\(([\w\s]+)\)',
    ]
    for pattern in export_patterns:
        for match in re.finditer(pattern, content):
            exports.extend(match.group(1).split())

    # Extract subroutines
    # Pattern: sub NAME { ... } with brace matching
    sub_pattern = r'^sub\s+(\w+)\s*(?:\([^)]*\))?\s*\{'
    for match in re.finditer(sub_pattern, content, re.MULTILINE):
        sub_name = match.group(1)
        sub_start = match.end()

        # Skip private subs (starting with _)
        if sub_name.startswith('_'):
            continue

        # Find matching closing brace (simple heuristic - may not work for nested braces)
        brace_count = 1
        pos = sub_start
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1
        sub_end = pos

        params = extract_params(content, sub_start, sub_end)
        defaults = extract_defaults(content, sub_start, sub_end)
        pod = extract_pod_for_sub(content, sub_name)

        symbols.append({
            "name": sub_name,
            "type": "sub",
            "params": params,
            "defaults": defaults,
            "pod": pod,
            "line": content[:match.start()].count('\n') + 1
        })

    # Extract global variable references ($main::VAR, %main::HASH, etc.)
    global_pattern = r'\$(?:main::)?([A-Z_][A-Z_0-9]*)|%(?:main::)?([A-Z_][A-Z_0-9]*)'
    for match in re.finditer(global_pattern, content):
        if match.group(1):
            globals_set.add(f"${match.group(1)}")
        if match.group(2):
            globals_set.add(f"%{match.group(2)}")

    return {
        "file": filepath.name,
        "symbols": symbols,
        "globals": sorted(globals_set),
        "exports": sorted(set(exports)),
        "line_count": content.count('\n') + 1
    }


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <macro_dir> <output.json>", file=sys.stderr)
        sys.exit(1)

    macro_base = Path(sys.argv[1])
    output = Path(sys.argv[2])

    # Target macro files with their typical locations
    target_macros = {
        "PGstandard.pl": ["core", "."],
        "PGcourse.pl": [".", "core"],
        "MathObjects.pl": ["core", "."],
        "PGchoicemacros.pl": ["ui", "core", "."],
        "PGML.pl": ["core", "."],
        "PGgraphmacros.pl": ["graph", "core", "."],
        "AnswerFormatHelp.pl": ["deprecated", "ui", "core", "."],
        "parserPopUp.pl": ["parsers", "core", "."],
        "parserMultiAnswer.pl": ["parsers", "core", "."],
        "contextFraction.pl": ["contexts", "core", "."],
    }

    inventory = {}
    found_count = 0

    for macro_name, search_dirs in target_macros.items():
        macro_path = None

        # Search in multiple directories
        for subdir in search_dirs:
            candidate = macro_base / subdir / macro_name
            if candidate.exists():
                macro_path = candidate
                break

        if macro_path:
            print(f"Processing {macro_name}...", file=sys.stderr)
            inventory[macro_name] = parse_perl_file(macro_path)
            found_count += 1
        else:
            print(f"Warning: {macro_name} not found", file=sys.stderr)
            inventory[macro_name] = {
                "file": macro_name,
                "symbols": [],
                "globals": [],
                "exports": [],
                "error": "File not found"
            }

    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w') as f:
        json.dump(inventory, f, indent=2)

    print(f"\n✓ Perl inventory written to {output}", file=sys.stderr)
    print(f"  Found {found_count}/{len(target_macros)} macro files", file=sys.stderr)

    # Print summary
    total_symbols = sum(len(data["symbols"]) for data in inventory.values())
    print(f"  Total symbols extracted: {total_symbols}", file=sys.stderr)


if __name__ == "__main__":
    main()
