# Type Checking Support for PG Packages

## What Changed

Added `py.typed` marker files to all PG packages to enable type checking with Mypy and other type checkers.

### Files Added
- `packages/pg/py.typed`
- `packages/pg/math/py.typed`
- `packages/pg/pgml/py.typed`
- `packages/pg/macros/py.typed`
- `packages/pg/answer/py.typed`
- `packages/pg/parser/py.typed`

### Metadata Updated
Updated `pyproject.toml` files to include `py.typed` markers in package distributions:
- `packages/pg/math/pyproject.toml`
- `packages/pg/pgml/pyproject.toml`
- `packages/pg/macros/pyproject.toml`
- `packages/pg/answer/pyproject.toml`
- `packages/pg/parser/pyproject.toml`

## How to Enable Type Checking

### 1. Reinstall PG Packages

For the type markers to take effect, reinstall the packages in development mode:

```powershell
# From repository root
python -m pip install -e packages/pg/math
python -m pip install -e packages/pg/pgml
python -m pip install -e packages/pg/macros
python -m pip install -e packages/pg/answer
python -m pip install -e packages/pg/parser
```

### 2. Configure VS Code (if using)

Add to `.vscode/settings.json`:

```json
{
  "python.analysis.extraPaths": [
    "${workspaceFolder}/packages"
  ],
  "python.analysis.typeCheckingMode": "basic"
}
```

### 3. Suppress Wildcard Import Warnings

For generated `.py` files from pg-convert, the wildcard imports (`from pg.* import *`) are intentional and match PG's Perl semantics.

Add to the top of generated files to suppress linter warnings:

```python
# pylint: disable=wildcard-import,unused-wildcard-import,undefined-variable
# mypy: ignore-errors
```

Or add a `.pylintrc` or `pyproject.toml` configuration to ignore these patterns for specific directories.

## What This Fixes

### Before
```
⚠ Mypy: Skipping analyzing "pg.mathobjects": missing library stubs or py.typed marker
⚠ Pylint: Unable to import 'pg.mathobjects'
⚠ Mypy: Name "Context" is not defined
```

### After
✅ Type checkers recognize pg packages as typed
✅ Proper import resolution
✅ Code completion and type hints work correctly

## Note on Generated Code

Generated `.py` files from `pg-convert --standalone` are meant to be executable scripts, not library code. It's normal to have some linter warnings for:

- Wildcard imports (intentional for PG semantics)
- Module-level code execution
- Dynamic variable usage

These files are optimized for WeBWorK problem authoring, not for strict type checking.

