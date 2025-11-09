#!/usr/bin/env python3
"""
Extract symbols, signatures, defaults from Python pg_macros package.
Uses inspect module to introspect functions, classes, type hints.

Output JSON schema (matches Perl inventory for diffing):
{
  "file": "PGstandard.pl",  # Maps to Python module
  "symbols": [
    {
      "name": "random",
      "type": "function",
      "params": ["min", "max", "step"],
      "defaults": {"step": "1"},
      "doc": "Returns random number...",
      "line": 45
    }
  ],
  "globals": [],
  "exports": ["random", "non_zero_random"]
}
"""
import inspect
import json
import sys
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Any, get_type_hints


def extract_signature(obj) -> tuple[List[str], Dict[str, str]]:
    """Extract parameter names and defaults from a function or class."""
    try:
        sig = inspect.signature(obj)
    except (ValueError, TypeError):
        return [], {}

    params = []
    defaults = {}

    for name, param in sig.parameters.items():
        # Skip self, cls
        if name in ('self', 'cls'):
            continue

        params.append(name)

        if param.default is not inspect.Parameter.empty:
            # Repr the default value
            try:
                defaults[name] = repr(param.default)
            except Exception:
                defaults[name] = str(param.default)

    return params, defaults


def get_source_line(obj) -> int:
    """Get line number where object is defined."""
    try:
        return inspect.getsourcelines(obj)[1]
    except (TypeError, OSError):
        return 0


def parse_python_module(module_name: str) -> Dict[str, Any]:
    """Parse a Python module and extract symbols."""
    try:
        mod = importlib.import_module(module_name)
    except ImportError as e:
        return {
            "file": module_name,
            "symbols": [],
            "globals": [],
            "exports": [],
            "error": f"Import failed: {e}"
        }

    symbols = []
    exports = []

    # Get all public symbols
    all_symbols = getattr(mod, '__all__', None)
    if all_symbols:
        exports = list(all_symbols)

    # Inspect all members
    for name, obj in inspect.getmembers(mod):
        # Skip private members
        if name.startswith('_'):
            continue

        # Skip imported modules
        if inspect.ismodule(obj):
            continue

        # For parity testing, we want ALL exported symbols, even if re-exported
        # So we check __all__ or accept everything that's not from builtins/stdlib
        if hasattr(obj, '__module__'):
            obj_module = obj.__module__
            # Skip builtins and standard library (but keep pg_macros.* even if re-exported)
            if obj_module and not obj_module.startswith('pg_macros'):
                # Allow if it's in __all__ (explicitly exported)
                if all_symbols and name not in all_symbols:
                    continue
                # Otherwise skip stdlib/builtins
                if obj_module in ('builtins', '__builtin__') or '.' not in obj_module:
                    continue

        if inspect.isfunction(obj):
            params, defaults = extract_signature(obj)
            doc = inspect.getdoc(obj) or ""

            symbols.append({
                "name": name,
                "type": "function",
                "params": params,
                "defaults": defaults,
                "doc": doc[:200] if doc else "",  # Truncate for readability
                "line": get_source_line(obj)
            })

        elif inspect.isclass(obj):
            # For classes, extract __init__ signature
            params, defaults = extract_signature(obj)
            doc = inspect.getdoc(obj) or ""

            # Also check for __init__ specifically
            if hasattr(obj, '__init__'):
                init_params, init_defaults = extract_signature(obj.__init__)
                if init_params:
                    params = init_params
                    defaults = init_defaults

            symbols.append({
                "name": name,
                "type": "class",
                "params": params,
                "defaults": defaults,
                "doc": doc[:200] if doc else "",
                "line": get_source_line(obj)
            })

    # If no explicit exports, assume all public symbols are exported
    if not exports:
        exports = [s["name"] for s in symbols]

    return {
        "file": module_name,
        "symbols": symbols,
        "globals": [],  # Python doesn't have Perl-style package globals
        "exports": sorted(exports),
        "module_doc": inspect.getdoc(mod)[:200] if inspect.getdoc(mod) else ""
    }


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <output.json>", file=sys.stderr)
        sys.exit(1)

    output = Path(sys.argv[1])

    # Map Perl filenames to actual Python module names
    # Use package-level __init__.py exports where available (they aggregate submodules)
    module_map = {
        "PGstandard.pl": "pg_macros.core",  # Aggregates pg_core + pg_standard via __init__
        "PGcourse.pl": "pg_macros.core.pg_basic_macros",  # Course-specific macros
        "MathObjects.pl": "pg_macros.core.math_objects",
        "PGchoicemacros.pl": "pg_macros.choice",  # Package-level exports
        "PGML.pl": "pg_macros.core.pgml",
        "PGgraphmacros.pl": "pg_macros.graph",  # May not exist yet
        "AnswerFormatHelp.pl": "pg_macros.answers",  # Package-level exports
        "parserPopUp.pl": "pg_macros.parsers.parser_popup",
        "parserMultiAnswer.pl": "pg_macros.parsers",  # Package-level exports
        "contextFraction.pl": "pg_macros.contexts",
    }

    inventory = {}
    found_count = 0

    for pl_name, py_module in module_map.items():
        print(f"Processing {py_module}...", file=sys.stderr)
        result = parse_python_module(py_module)
        inventory[pl_name] = result

        if "error" not in result:
            found_count += 1

    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w') as f:
        json.dump(inventory, f, indent=2)

    print(f"\n✓ Python inventory written to {output}", file=sys.stderr)
    print(f"  Successfully introspected {found_count}/{len(module_map)} modules", file=sys.stderr)

    # Print summary
    total_symbols = sum(len(data["symbols"]) for data in inventory.values() if "symbols" in data)
    print(f"  Total symbols extracted: {total_symbols}", file=sys.stderr)


if __name__ == "__main__":
    main()
