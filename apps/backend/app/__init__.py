"""Backend application package configuration."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the vendored packages are importable without installation.
_repo_root = Path(__file__).resolve().parents[2]

# Add packages directory to path for top-level macro modules (PG, PGstandard, PGML, etc.)
_packages_path = _repo_root / "packages"
if _packages_path.exists() and str(_packages_path) not in sys.path:
    sys.path.insert(0, str(_packages_path))

# Ensure the vendored problemkit package is importable without installation.
_problemkit_path = _repo_root / "packages" / "problemkit"
if _problemkit_path.exists():
    sys.path.append(str(_problemkit_path))
