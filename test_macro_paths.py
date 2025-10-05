#!/usr/bin/env python3
"""
Test macro search paths and loading
"""

import sys
from pathlib import Path

# Add packages to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "packages" / "pg_macros"))
sys.path.insert(0, str(repo_root / "packages" / "pg_translator"))

from pg_translator.sandbox import Sandbox
from pg_translator.macro_loader import MacroLoader

# Create sandbox and loader
sandbox = Sandbox()
loader = MacroLoader(sandbox)

print("Macro search paths:")
for path in loader.search_paths:
    print(f"  {path}")
    if path.exists():
        print(f"    ✅ Exists")
        # List files
        if path.is_dir():
            py_files = list(path.glob("*.py"))
            if py_files:
                print(f"    Python files: {[f.name for f in py_files[:5]]}")
    else:
        print(f"    ❌ Does not exist")

# Try to find pg_core
print("\nSearching for pg_core...")
found = loader.find_macro("pg_core.py")
print(f"  Result: {found}")

# Try alternative names
for name in ["pg_core", "core/pg_core", "core/pg_core.py"]:
    found = loader.find_macro(name)
    print(f"  Trying '{name}': {found}")

# Show where pg_macros is actually installed
print("\nActual pg_macros location:")
import pg_macros
print(f"  {Path(pg_macros.__file__).parent}")
