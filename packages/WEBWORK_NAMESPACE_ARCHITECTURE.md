# WeBWorK Namespace Package Refactoring

## Overview

This document describes the refactoring from flat, top-level barrel modules to a unified `webwork` namespace package. This improves package discoverability, provides a professional API surface, and enables easier third-party usage.

## The Problem (Before)

Previously, the PG system used top-level barrel modules scattered in the `packages/` directory:

```
packages/
├── PG.py              # Core PG functionality
├── PGstandard.py      # Standard macros
├── PGML.py            # Markup language
├── MathObjects.py     # Math objects
├── PGcourse.py        # Course config
├── PGbasicmacros.py   # Basic macros
├── PGanswermacros.py  # Answer macros
├── parserPopUp.py     # UI components
└── ... (11+ more modules)
```

**Issues:**
- No namespace clarity - looks like random modules
- Hard to discover via `pip install`
- Difficult for third-party developers - unclear what to import
- Flat structure doesn't scale as functionality grows
- PyPI registration is awkward with top-level modules

## The Solution (After)

All core functionality is now available via the unified `webwork` namespace:

```
packages/
└── webwork/
    ├── webwork/
    │   ├── __init__.py           # Composite barrel export
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── pg.py             # Core functions (DOCUMENT, TEXT, ANS, etc.)
    │   │   ├── pgml.py           # PGML rendering
    │   │   ├── pgstandard.py     # Standard macros
    │   │   └── pgcourse.py       # Course setup
    │   └── math/
    │       ├── __init__.py
    │       └── objects.py        # Math objects (Context, Compute, Formula, etc.)
    ├── pyproject.toml            # Modern Python packaging
    └── README.md                 # Package documentation
```

## Key Features

### 1. Single Import Entry Point

```python
# OLD (fragmented)
from PGstandard import *
from PGML import *
from MathObjects import *

# NEW (unified)
from webwork import *
```

### 2. Organized Submodules (For Explicit Imports)

```python
# Import just what you need
from webwork.core import DOCUMENT, TEXT, ANS
from webwork.math import Context, Compute, Formula
```

### 3. Backwards Compatibility

Old imports still work with deprecation warnings:

```python
# Still works, but shows deprecation warning
from PGstandard import *
from PGML import *
from MathObjects import *
```

### 4. PyPI Distribution

```bash
# Install for third-party users
pip install webwork-pg

# Create your own problem
python myproblem.pyg
```

## Architecture Details

### webwork/__init__.py

The main entry point re-exports all core functionality:

```python
from .core import *      # PG core functions, PGML, etc.
from .math import *      # Math objects and contexts
```

Provides over 40 commonly-used items in `__all__` for IDE autocompletion.

### webwork/core/

**pg.py** - Core PG functionality
- DOCUMENT(), ENDDOCUMENT()
- TEXT(), BEGIN_TEXT/END_TEXT
- ANS(), NAMED_ANS(), LABELED_ANS()
- SOLUTION(), HINT(), COMMENT()
- random(), non_zero_random(), list_random()
- Installation/grading functions

**pgml.py** - PG Markup Language
- PGML() function for markup-based authoring
- BEGIN_PGML/END_PGML support

**pgstandard.py** - Standard macros collection
- Combination of pg.py + pgml.py + pgbasicmacros + answer macros
- HTML formatting (BR, PAR, BBOLD, etc.)
- Answer comparison functions (num_cmp, fun_cmp, etc.)

**pgcourse.py** - Course-specific configuration
- Provides loadMacros() for additional macro loading

### webwork/math/

**objects.py** - Mathematical objects
- Context() - Configure mathematical domain
- Compute() - Parse and evaluate expressions
- Formula() - Create formulas with differentiation
- Vector, Point, Matrix, Interval - Math types
- String, List, Set, Fraction - Container types

## How It Works Internally

### 1. Path Management

Each submodule adds the `packages/` directory to sys.path to access top-level barrel modules:

```python
# In webwork/core/pg.py
import sys
from pathlib import Path

_packages_dir = Path(__file__).parent.parent.parent.parent
if str(_packages_dir) not in sys.path:
    sys.path.insert(0, str(_packages_dir))

from PG import *  # Now finds d:\pg\packages\PG.py
```

### 2. Barrel Module Chain

```
webwork/__init__.py
    -> webwork/core/__init__.py
        -> webwork/core/pgstandard.py
            -> packages/PGstandard.py
                -> pg_macros/PGstandard.py (actual implementation)
```

### 3. Translator Integration

The pg_translator was updated to generate `from webwork import *` in converted .pyg files:

**In pg_preprocessor_pygment.py:**
- Standalone mode adds `from webwork import *` before DOCUMENT()
- loadMacros() with barrel modules (PGstandard, PGML, etc.) generates single `from webwork import *`
- Avoids duplicate imports

## Usage Examples

### For Problem Authors

```python
# Convert and run existing Perl PG problems
$ pypg convert problem.pg problem.pyg

# Or create new Python-native problems
from webwork import *

DOCUMENT()

Context("Numeric")
a = random(2, 10)
answer = Compute(f"{a}*x + 1")

BEGIN_PGML
Find the derivative of [``y = [$a]x + 1``]
[_]{$answer}
END_PGML

ENDDOCUMENT()
```

### For Third-Party Developers

```bash
# Install the package
pip install webwork-pg

# Create problems that use webwork
python myproblem.pyg
```

### For Library Developers

```python
# Create custom macro libraries on top of webwork
from webwork import *

def my_custom_macro():
    return DOCUMENT()

# Export for use by others
__all__ = ["my_custom_macro"]
```

## Migration Path

### Old Code (Still Works)

```python
# With deprecation warnings
from PGstandard import *
from PGML import *
from MathObjects import *

DOCUMENT()
# ... problem code ...
ENDDOCUMENT()
```

### New Code (Recommended)

```python
# Single import, future-proof
from webwork import *

DOCUMENT()
# ... problem code ...
ENDDOCUMENT()
```

### For Explicit Imports

```python
# If you prefer explicit imports
from webwork.core import DOCUMENT, TEXT, ANS, PGML
from webwork.math import Context, Compute, Formula

DOCUMENT()
# ... problem code ...
ENDDOCUMENT()
```

## Implementation Details

### File Structure

```
packages/
├── webwork/                              # NEW namespace package
│   ├── pyproject.toml                   # Modern Python packaging
│   ├── README.md                        # User guide
│   └── webwork/
│       ├── __init__.py                  # Main barrel export (40+ items)
│       ├── core/
│       │   ├── __init__.py             # Re-exports all submodules
│       │   ├── pg.py                   # Re-exports PG.py barrel
│       │   ├── pgml.py                 # Re-exports PGML.py barrel
│       │   ├── pgstandard.py           # Re-exports PGstandard.py barrel
│       │   └── pgcourse.py             # Re-exports PGcourse.py barrel
│       └── math/
│           ├── __init__.py             # Re-exports submodules
│           └── objects.py              # Re-exports MathObjects.py barrel
│
├── PG.py                                 # DEPRECATED (with warnings)
├── PGstandard.py                         # DEPRECATED (with warnings)
├── PGML.py                               # DEPRECATED (with warnings)
├── MathObjects.py                        # DEPRECATED (with warnings)
├── PGcourse.py                           # DEPRECATED (with warnings)
└── ... (other deprecated modules)
```

### Translator Updates

**Location:** `packages/pg_translator/pg_translator/pg_preprocessor_pygment.py`

**Changes:**
1. Line 179: Standalone mode generates `from webwork import *` instead of `from MathObjects import *`
2. Lines 3178-3215: Convert legacy barrel modules to webwork namespace:
   - Maps: MathObjects, PGstandard, PGML, PG, PGcourse, PGbasicmacros, PGanswermacros
   - If any of these are imported, generates single `from webwork import *`
   - Avoids duplicate imports using `webwork_import_added` flag

### Deprecation Strategy

Old modules emit deprecation warnings but still work:

```python
# In packages/PGstandard.py
import warnings

warnings.warn(
    "Importing from 'PGstandard' is deprecated. Use 'from webwork import *' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from pg_macros.PGstandard import *
```

This provides a graceful migration path without breaking existing code.

## Benefits

### For Users

- **Simple:** `from webwork import *` vs. remembering 5+ module names
- **Discoverable:** `pip install webwork-pg` is clear and professional
- **Organized:** Namespace prevents conflicts (e.g., other projects' "PGML" module)
- **Extensible:** `from webwork.math import *` for explicit imports

### For Developers

- **Professional:** Proper Python namespace package (PEP 420)
- **Scalable:** Easy to add more submodules (plotting, graphics, etc.)
- **Maintainable:** Clear structure and organization
- **Backwards Compatible:** Old imports still work with warnings

### For Contributors

- **Clear:** Understanding the import system is straightforward
- **Documented:** Architecture is explicit in code organization
- **Tested:** Translator and imports are integrated

## Future Enhancements

### Potential New Submodules

```python
from webwork.graphics import *      # Graphing utilities
from webwork.plotting import *      # Plotting functions
from webwork.ui import *            # User interface components
from webwork.evaluation import *    # Grading and evaluation
```

### Lazy Loading

```python
# Can be implemented later for faster imports
from webwork.graphics import plot_function  # Only loads graphics module
```

### Type Hints

```python
# Can be enhanced with full type annotations
def Context(name: str) -> ContextObject:
    ...
```

## Troubleshooting

### Module Not Found Errors

If you get `ModuleNotFoundError: No module named 'webwork'`:

1. **For development:** Add packages directory to PYTHONPATH:
   ```bash
   export PYTHONPATH=/path/to/pg/packages:$PYTHONPATH
   python myproblem.pyg
   ```

2. **For deployment:** Install the package:
   ```bash
   pip install webwork-pg
   python myproblem.pyg
   ```

### Deprecation Warnings

To suppress deprecation warnings (not recommended):

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from PGstandard import *  # Still works but silences warning
```

Better: migrate to new imports:

```python
from webwork import *  # No warnings, future-proof
```

## References

- **PEP 420:** Namespace Packages
- **PEP 427:** Wheel Binary Package Format
- **Modern Python Packaging:** https://packaging.python.org/
- **WeBWorK Legacy PG:** `/macros/` directory in Perl codebase
- **Translator:** `packages/pg_translator/`

## Summary

The webwork namespace package refactoring provides:

✓ Unified, discoverable API (`pip install webwork-pg`)
✓ Professional package structure (PEP 420 namespace)
✓ Backwards compatibility (deprecation warnings)
✓ Clear organization (core/, math/ submodules)
✓ Better IDE support (explicit __all__)
✓ Future-proof architecture (easy to extend)
✓ Third-party friendly (simple imports for users)

This is a **recommended** change for production use and third-party distribution.
