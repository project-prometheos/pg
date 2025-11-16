#!/usr/bin/env python3
"""Check if logging is disabled."""
import os
print(f"PYPG_DISABLE_LOGGING = {os.environ.get('PYPG_DISABLE_LOGGING', 'NOT SET')}")
