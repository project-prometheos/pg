#!/usr/bin/env python
"""
Diagnose a single PG problem file for errors.

Shows:
1. The generated Python code from PGTranslator
2. The error message with context
3. The relevant section of the original .pg file
4. Suggested fixes

Usage:
    python diagnose_problem.py tutorial/sample-problems/Algebra/Problem.pg
    python diagnose_problem.py tutorial/sample-problems/Algebra/Problem.pg --show-full
"""

import sys
import traceback
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

# Add packages to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_answer"))
sys.path.insert(0, str(project_root / "packages" / "pg_parser"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))

from pg.translator import PGTranslator


def print_section(title: str, char: str = "="):
    """Print a formatted section header."""
    width = 80
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def print_subsection(title: str, char: str = "-"):
    """Print a formatted subsection header."""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}")


def truncate_text(text: str, max_lines: int = 20) -> str:
    """Truncate text to max lines, adding ellipsis if truncated."""
    lines = text.split('\n')
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
    return text


def extract_error_context(error_msg: str, original_code: str) -> Optional[str]:
    """Extract relevant context from error message and original code."""
    # Look for line number references in error
    lines = error_msg.split('\n')
    
    context = []
    for line in lines:
        # Look for patterns like "line 42" or "File ... line 42"
        if 'line' in line.lower():
            context.append(line)
    
    return '\n'.join(context) if context else None


def categorize_error(error_msg: str) -> str:
    """Categorize the error type."""
    keywords = {
        'SyntaxError': 'Syntax Error',
        'NameError': 'Name Error (undefined variable/function)',
        'AttributeError': 'Attribute Error (missing method/property)',
        'TypeError': 'Type Error',
        'ImportError': 'Import Error',
        'ModuleNotFoundError': 'Module Not Found Error',
        'KeyError': 'Key Error',
        'ValueError': 'Value Error',
        'FileNotFoundError': 'File Not Found Error',
        'RuntimeError': 'Runtime Error',
    }
    
    for keyword, category in keywords.items():
        if keyword in error_msg:
            return category
    
    return 'Unknown Error'


def suggest_fix(problem_name: str, error_category: str, error_msg: str) -> str:
    """Suggest a fix based on error type."""
    suggestions = {
        'Syntax Error': [
            "- Check PG syntax (missing semicolons, quotes, parentheses)",
            "- Look for PG3 vs Python3 syntax differences",
            "- Check macro loading syntax",
        ],
        'Name Error (undefined variable/function)': [
            "- Check if required macros are loaded with loadMacros()",
            "- Verify variable names are spelled correctly",
            "- Check if function is defined before use",
            "- Look for missing Answer object or checker setup",
        ],
        'Attribute Error (missing method/property)': [
            "- Check object type compatibility with Python version",
            "- Look for deprecated or renamed methods",
            "- Verify correct object initialization",
        ],
        'Type Error': [
            "- Check function argument types",
            "- Verify list/array indexing operations",
            "- Look for operations on incompatible types",
        ],
        'Import Error': [
            "- Check macro path in loadMacros()",
            "- Verify macro file exists",
            "- Check for circular dependencies",
        ],
    }
    
    suggestion_list = suggestions.get(error_category, [
        "- Review generated Python code",
        "- Compare with working similar problems",
    ])
    
    return '\n'.join(suggestion_list)


def diagnose_problem(problem_path: str, show_full: bool = False):
    """Diagnose a single PG problem."""
    
    problem_file = Path(problem_path)
    
    if not problem_file.exists():
        print(f"❌ Error: Problem file not found: {problem_path}")
        return False
    
    print_section(f"DIAGNOSING: {problem_file.name}")
    
    # Show basic info
    print(f"Path: {problem_file}")
    print(f"Size: {problem_file.stat().st_size} bytes")
    
    # Read original file
    try:
        original_code = problem_file.read_text()
        print(f"Lines: {len(original_code.split(chr(10)))}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Show first few lines of original
    print_subsection("Original PG File (first 20 lines)")
    lines = original_code.split('\n')
    print('\n'.join(f"{i+1:3d}: {line}" for i, line in enumerate(lines[:20])))
    if len(lines) > 20:
        print(f"... ({len(lines) - 20} more lines)")
    
    # Try to translate
    translator = PGTranslator()
    seed = 12345
    
    print_subsection("Translating to Python...")
    
    result = None
    generated_code = None
    error_occurred = False
    
    try:
        result = translator.translate(str(problem_file), seed=seed)
        
        # Try to get generated Python if available
        if hasattr(result, 'python_code'):
            generated_code = result.python_code
        
        print("✓ Translation completed (may have had execution errors)")
        
    except Exception as e:
        error_occurred = True
        print(f"✗ Translation failed: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
    
    # Show generated code
    if generated_code:
        print_subsection("Generated Python Code")
        code_lines = generated_code.split('\n')
        if show_full or len(code_lines) <= 50:
            print('\n'.join(f"{i+1:3d}: {line}" for i, line in enumerate(code_lines)))
        else:
            print('\n'.join(f"{i+1:3d}: {line}" for i, line in enumerate(code_lines[:50])))
            print(f"... ({len(code_lines) - 50} more lines)")
    
    # Show errors
    if result and result.errors:
        error_str = '\n'.join(result.errors) if isinstance(result.errors, list) else str(result.errors)
        
        print_subsection("Errors During Translation/Execution")
        error_lines = error_str.split('\n')
        print('\n'.join(error_lines[:100]))
        if len(error_lines) > 100:
            print(f"\n... ({len(error_lines) - 100} more lines)")
        
        # Categorize and suggest
        error_category = categorize_error(error_str)
        
        print_subsection("Error Analysis")
        print(f"Category: {error_category}")
        
        # Extract first error line
        for line in error_lines:
            if any(kw in line for kw in ['Error', 'error', 'Error:']):
                print(f"Key Error: {line}")
                break
        
        print_subsection("Suggested Fixes")
        print(suggest_fix(problem_file.stem, error_category, error_str))
    
    elif result and not result.errors:
        print_subsection("✓ No Critical Errors")
        print(f"Statement HTML length: {len(result.statement_html) if hasattr(result, 'statement_html') else 'N/A'}")
        return True
    
    # Summary
    print_section("SUMMARY", char="=")
    
    if result and not result.errors:
        print("✓ Problem PASSES - No critical errors detected")
        return True
    else:
        print("✗ Problem FAILS - Critical errors detected")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose a PG problem file for errors"
    )
    parser.add_argument(
        "problem",
        help="Path to problem file (e.g., tutorial/sample-problems/Algebra/Problem.pg)"
    )
    parser.add_argument(
        "--show-full",
        action="store_true",
        help="Show full generated code (not truncated)"
    )
    
    args = parser.parse_args()
    
    success = diagnose_problem(args.problem, show_full=args.show_full)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
