#!/usr/bin/env python3
"""
Quick comparison tool for Perl vs Python outputs
"""
import json
import sys
from pathlib import Path

def compare_outputs(perl_json: Path, py_json: Path):
    """Compare two JSON output files."""
    with open(perl_json) as f:
        perl = json.load(f)
    with open(py_json) as f:
        py = json.load(f)
    
    print("=" * 60)
    print("PERL vs PYTHON OUTPUT COMPARISON")
    print("=" * 60)
    print()
    
    # Basic stats
    print("BASIC STATS:")
    print(f"  Perl HTML length:   {len(perl.get('html', ''))} chars")
    print(f"  Python HTML length: {len(py.get('html', ''))} chars")
    print(f"  Perl answers:       {len(perl.get('answers', []))}")
    print(f"  Python answers:     {len(py.get('answers', []))}")
    print(f"  Perl errors:         {len(perl.get('errors', []))}")
    print(f"  Python errors:       {len(py.get('errors', []))}")
    print()
    
    # Answer comparison
    perl_answers = {a['name']: a for a in perl.get('answers', [])}
    py_answers = {a['name']: a for a in py.get('answers', [])}
    
    print("ANSWERS:")
    all_names = set(perl_answers.keys()) | set(py_answers.keys())
    for name in sorted(all_names):
        if name in perl_answers and name in py_answers:
            print(f"  ✓ {name}: Both have answer")
        elif name in perl_answers:
            print(f"  ✗ {name}: Only in Perl")
        else:
            print(f"  ✗ {name}: Only in Python")
    print()
    
    # HTML preview
    print("HTML PREVIEW (first 200 chars):")
    print(f"  Perl:   {perl.get('html', '')[:200]}...")
    print(f"  Python: {py.get('html', '')[:200]}...")
    print()
    
    # Errors
    if perl.get('errors'):
        print("PERL ERRORS:")
        for err in perl['errors']:
            print(f"  ✗ {err[:100]}")
        print()
    
    if py.get('errors'):
        print("PYTHON ERRORS:")
        for err in py['errors']:
            print(f"  ✗ {err[:100]}")
        print()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <perl_json> <python_json>")
        sys.exit(1)
    
    compare_outputs(Path(sys.argv[1]), Path(sys.argv[2]))

