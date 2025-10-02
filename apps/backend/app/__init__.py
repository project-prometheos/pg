"""Backend application package configuration."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the vendored problemkit package is importable without installation.
_repo_root = Path(__file__).resolve().parents[2]
_problemkit_path = _repo_root / "packages" / "problemkit"
if _problemkit_path.exists():
    sys.path.append(str(_problemkit_path))
