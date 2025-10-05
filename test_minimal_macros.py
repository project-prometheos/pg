#!/usr/bin/env python3
"""
Minimal test: Just check if pg_macros core functions exist
"""

import sys
from pathlib import Path

repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "packages" / "pg_macros"))

print("Checking pg_macros.core...")
try:
    from pg_macros.core import pg_core
    print(f"✅ pg_core module imported")
    print(
        f"   Functions: {[name for name in dir(pg_core) if not name.startswith('_')][:10]}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\nChecking PGEnvironment...")
try:
    from pg_macros.core.pg_core import PGEnvironment, get_environment, set_environment, TEXT
    env = PGEnvironment()
    print(f"✅ PGEnvironment created: {env}")
    set_environment(env)
    print(f"✅ Environment set")

    TEXT("Hello World!")
    body = env.get_body_text()
    print(f"✅ TEXT() works! Body: '{body}'")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Core macros are working!")
