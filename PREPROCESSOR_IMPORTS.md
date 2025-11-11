# Preprocessor-Based Macro Import System

## Overview

The PG translator uses a **preprocessor-based approach** to convert Perl `loadMacros()` calls into Python `import` statements at compile time. This is simpler, more Pythonic, and eliminates runtime complexity.

## How It Works

### 1. PG Problem Files (Perl Syntax)

Problems use standard Perl `loadMacros()` calls:

```perl
## In a .pg file:
DOCUMENT();

loadMacros("PGstandard.pl", "PGML.pl", "PGcourse.pl");

Context()->variables->are(x => 'Real', y => 'Real');
$a = random(20, 40);
```

### 2. Preprocessor Conversion

The preprocessor ([pg_preprocessor_pygment.py](packages/pg_translator/pg_translator/pg_preprocessor_pygment.py)) automatically converts `loadMacros()` to Python imports:

```python
## Converted Python code:
DOCUMENT()

# Loaded macros: PGstandard.pl, PGML.pl, PGcourse.pl
from pg_macros.core.pg_core import BEGIN_TEXT, END_TEXT, random, non_zero_random, ANS, TEXT, DOCUMENT
from pg_macros.core.pgml import PGML

Context().variables.are(x='Real', y='Real')
a = random(20, 40)
```

The `loadMacros()` call is replaced with Python imports based on the **Macro Registry**.

### 3. Macro Registry

The registry ([packages/pg_macros/pg_macros/registry.py](packages/pg_macros/pg_macros/registry.py)) maps Perl macro names to Python modules:

```python
OPTIONAL_MACROS = {
    "pg_core": {
        "module": "pg_macros.core.pg_core",
        "aliases": ["PG.pl", "PGstandard.pl"],
        "functions": ["BEGIN_TEXT", "END_TEXT", "random", "ANS", ...],
    },
    "PGML": {
        "module": "pg_macros.core.pgml",
        "aliases": ["PGML.pl"],
        "functions": ["PGML"],
    },
    # ... 30+ more macros
}
```

## Architecture

```
┌─────────────────┐
│ Problem.pg      │
│ (Perl syntax)   │
│                 │
│ loadMacros(     │
│   "PG.pl",      │
│   "PGML.pl"     │
│ )               │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ PGPreprocessor                  │
│                                 │
│ _transform_load_macros()        │
│   ├─ Parse macro names          │
│   ├─ Look up in registry        │
│   ├─ Get module + functions     │
│   └─ Generate imports           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Converted Python Code           │
│                                 │
│ from pg_macros.core.pg_core    │
│   import BEGIN_TEXT, random...  │
│ from pg_macros.core.pgml       │
│   import PGML                   │
│                                 │
│ DOCUMENT()                      │
│ a = random(20, 40)              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│ InProcessSandbox│
│ Executes code   │
│ (all macros     │
│  pre-loaded)    │
└─────────────────┘
```

## Benefits vs. Dynamic Loading

| Aspect | Preprocessor Imports | Dynamic Loading (Old) |
|--------|---------------------|----------------------|
| **Complexity** | ✅ Simple (~70 lines) | ❌ Complex (~800 lines) |
| **Performance** | ✅ Compile-time (no overhead) | ⚠️ Runtime overhead |
| **Pythonic** | ✅ Standard Python imports | ❌ Custom loading mechanism |
| **IDE Support** | ✅ Autocomplete, type hints | ❌ No IDE support |
| **Debugging** | ✅ Clear import statements | ⚠️ Hidden runtime loading |
| **Namespace Issues** | ✅ Imports overwrite naturally | ❌ Complex preservation logic |
| **Maintenance** | ✅ Minimal code | ❌ MacroLoader, registry, etc. |

## Implementation Details

### Preprocessor Method

**Location:** `packages/pg_translator/pg_translator/pg_preprocessor_pygment.py:3074`

```python
def _transform_load_macros(self, macro_list_str: str) -> Tuple[List[str], str]:
    """
    Transform loadMacros() call to Python imports using the macro registry.
    """
    from pg_macros.registry import get_macro_info

    # Parse macro names
    macros = re.findall(r'"([^"]+)"|\'([^\']+)\'', macro_list_str)
    flattened = [a or b for a, b in macros]

    # Collect imports by module (deduplicate)
    imports_by_module: dict[str, set[str]] = {}

    for macro in flattened:
        info = get_macro_info(macro)
        if info and info.get("module"):
            module = info["module"]
            functions = info.get("functions", [])

            if functions:
                # Add specific function imports
                imports_by_module[module] = imports_by_module.get(module, set())
                imports_by_module[module].update(functions)

    # Generate import statements
    import_lines = []
    for module in sorted(imports_by_module.keys()):
        functions = imports_by_module[module]
        func_list = ", ".join(sorted(functions))
        import_lines.append(f"from {module} import {func_list}")

    return import_lines, comment
```

### Integration Points

1. **Preprocessing** (lines 171-181): Extract `loadMacros()` calls
2. **Conversion** (line 3074): Transform to imports
3. **Insertion** (lines 334-355): Insert imports after `DOCUMENT()`

### Registry Structure

**Location:** `packages/pg_macros/pg_macros/registry.py`

Each macro definition includes:
- `module`: Python module path
- `aliases`: Perl names that map to this module
- `functions`: Specific functions to import
- `category`: Grouping (core, graphics, parsers, etc.)
- `description`: Human-readable description

## Supported Macros

The registry currently defines **30+ macros**:

### Core Macros
- `PG.pl` / `PGstandard.pl` → `pg_macros.core.pg_core`
- `PGbasicmacros.pl` → `pg_macros.core.pg_basic_macros`
- `PGanswermacros.pl` → `pg_macros.answers.pg_answer_macros`
- `PGML.pl` → `pg_macros.core.pgml`
- `PGcourse.pl` → (empty - configuration only)

### Parser Macros
- `parserPopUp.pl` → `pg_macros.parsers.parser_popup`
- `parserRadioButtons.pl` → `pg_macros.parsers.parser_radio_buttons`
- `parserCheckboxes.pl` → `pg_macros.parsers.parser_checkboxes`
- `parserMultiAnswer.pl` → `pg_macros.parsers.parser_multi_answer`

### Graphics Macros
- `PGgraphmacros.pl` → `pg_macros.graph.pg_graph_macros`
- `parserGraphTool.pl` → `pg_macros.graph.parser_graphtool`
- `VectorField3D.pl` → `pg_macros.graph.vector_field_3d`

### Context Macros
- `contextFraction.pl` → `pg_macros.contexts.context_fraction`
- `contextLimitedPolynomial.pl` → `pg_macros.contexts.context_limited_polynomial`

### Interactive Macros
- `draggableProof.pl` → `pg_macros.math.draggable_proof`
- `draggableSubsets.pl` → `pg_macros.ui.draggable_subsets`

See [registry.py](packages/pg_macros/pg_macros/registry.py) for the complete list.

## Adding New Macros

To add a new macro to the system:

### 1. Port the Perl Macro to Python

Create the Python module (e.g., `packages/pg_macros/pg_macros/ui/my_macro.py`):

```python
def my_function():
    """My awesome function."""
    pass

def another_function():
    """Another function."""
    pass
```

### 2. Register in Registry

Add to `packages/pg_macros/pg_macros/registry.py`:

```python
OPTIONAL_MACROS = {
    # ... existing macros ...

    "myMacro": {
        "module": "pg_macros.ui.my_macro",
        "aliases": ["myMacro.pl"],
        "category": "ui",
        "functions": ["my_function", "another_function"],
        "description": "My awesome macro",
    },
}
```

### 3. That's It!

No changes needed to:
- Preprocessor (uses registry automatically)
- Sandbox (loads all macros statically)
- Executor (unchanged)

Problems can now use:
```perl
loadMacros("myMacro.pl");
my_function();  # Works!
```

## Code Changes Summary

### Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `pg_preprocessor_pygment.py` | Enhanced `_transform_load_macros()` | ~70 modified |
| `in_process_sandbox.py` | Removed dynamic loading | ~200 removed |
| `translator.py` | Removed MacroLoader | ~8 removed |
| `macro_registry.py` | Moved to pg_macros | Moved |

### Files Deleted

- `macro_loader.py` (~422 lines)
- `test_dynamic_loading.py` (~185 lines)

**Total:** ~800 lines removed, ~70 lines modified - **major simplification!**

## Testing

### Render Test

```bash
python pypg.py tutorial/sample-problems/Algebra/Logarithms.pg --render-only
```

**Result:** ✅ Problem renders successfully

### Full Test

```bash
python pypg.py tutorial/sample-problems/Algebra/Logarithms.pg "21*ln(x)+28*ln(y)-40*ln(z)"
```

**Result:** ✅ Problem executes and checks answers

## Comparison with Perl Reference

### Perl Approach

```perl
# In PG.pl:
sub loadMacros {
    my @files = @_;
    foreach my $file (@files) {
        my $filePath = findMacroFile($file);
        compile_file($filePath);  # Eval in Safe compartment
    }
}
```

- **Runtime:** Loads files during problem execution
- **Dynamic:** Can load conditionally
- **Compartmentalized:** Each problem in Safe compartment

### Python Approach

```python
# Preprocessor converts at compile time:
loadMacros("PG.pl")
# →
from pg_macros.core.pg_core import BEGIN_TEXT, END_TEXT, ...
```

- **Compile-time:** Converts to imports before execution
- **Static:** Imports happen at module load
- **Standard Python:** Uses normal import mechanism

### Trade-offs

| Feature | Perl | Python | Impact |
|---------|------|--------|--------|
| **Conditional loading** | ✅ Supported | ❌ Not supported | Rare in practice |
| **Compile-time optimization** | ❌ Runtime | ✅ Compile-time | Better performance |
| **IDE support** | ❌ No | ✅ Yes | Better DX |
| **Simplicity** | ⚠️ Complex | ✅ Simple | Easier maintenance |

The Python approach sacrifices theoretical runtime flexibility (rare) for practical benefits (simplicity, performance, tooling).

## Migration from Old System

If you were using the old dynamic loading system:

### Before (Dynamic Loading)

```python
from pg_translator.in_process_sandbox import InProcessSandbox

# Old: use_dynamic_loading parameter
sandbox = InProcessSandbox(timeout=30, use_dynamic_loading=True)
```

### After (Preprocessor Imports)

```python
from pg_translator.in_process_sandbox import InProcessSandbox

# New: no dynamic loading parameter needed
sandbox = InProcessSandbox(timeout=30)
```

All problems work the same - the conversion is automatic!

## Future Enhancements

Potential improvements:

1. **Selective Imports:** Only import functions actually used in the problem
2. **Import Optimization:** Merge imports from same module
3. **Circular Dependency Detection:** Warn about problematic imports
4. **Custom Search Paths:** Support user-defined macro locations

## Summary

The preprocessor-based macro import system:

✅ **Simpler** - 800 lines removed
✅ **Pythonic** - Standard imports
✅ **Faster** - Compile-time conversion
✅ **Maintainable** - Just add to registry
✅ **Reliable** - No namespace issues
✅ **Compatible** - Problems unchanged

This approach achieves the same goal as dynamic loading (making macros available) with **10% of the complexity**.
