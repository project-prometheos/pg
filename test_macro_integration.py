#!/usr/bin/env python3
"""
Quick test: Can we load macros and render a simple problem?
"""

import sys
from pathlib import Path

# Add packages to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "packages" / "pg_macros"))
sys.path.insert(0, str(repo_root / "packages" / "pg_translator"))
sys.path.insert(0, str(repo_root / "packages" / "pg_math"))
sys.path.insert(0, str(repo_root / "packages" / "pg_answer"))

from pg_translator.sandbox import Sandbox
from pg_translator.macro_loader import MacroLoader

# Create sandbox
sandbox = Sandbox()

# Create macro loader
loader = MacroLoader(sandbox)

# Load core macros
print("Loading PG core macros...")
error = loader.unrestricted_load("pg_core.py")
if error:
    print(f"ERROR: {error}")
    sys.exit(1)

print("✅ pg_core.py loaded")

# Load basic macros
print("Loading PG basic macros...")
error = loader.unrestricted_load("pg_basic_macros.py")
if error:
    print(f"ERROR: {error}")
    sys.exit(1)

print("✅ pg_basic_macros.py loaded")

# Try to use TEXT() function
print("\nTesting TEXT() function...")
try:
    TEXT = sandbox.namespace.get("TEXT")
    if TEXT is None:
        print("❌ TEXT not found in namespace")
        sys.exit(1)
    
    print("✅ TEXT function found")
    
    # Try to call it
    get_environment = sandbox.namespace.get("get_environment")
    if get_environment is None:
        print("❌ get_environment not found")
        sys.exit(1)
    
    env = get_environment()
    print(f"✅ Environment created: {env}")
    
    # Call TEXT
    TEXT("Hello from PG!")
    TEXT(" This is a test.")
    
    # Get the accumulated text
    body = env.get_body_text()
    print(f"\n✅ Generated text: {body}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try ans_rule
print("\nTesting ans_rule() function...")
try:
    ans_rule = sandbox.namespace.get("ans_rule")
    if ans_rule is None:
        print("❌ ans_rule not found")
        sys.exit(1)
    
    print("✅ ans_rule function found")
    
    html = ans_rule(20)
    print(f"✅ Generated HTML: {html}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("🎉 SUCCESS! Macro system is working!")
print("="*60)
