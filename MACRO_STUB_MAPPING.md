# Perl Macro to Python Module Mapping

This document maps stubbed functions in `in_process_sandbox.py` to their canonical Perl macro source files and the corresponding Python modules they should be moved to.

## Mapping Strategy

1. **Identify the Perl source**: Find which `.pl` file in `macros/` exports the function
2. **Convert filename to Python module**: Follow naming convention
   - `parserGraphTool.pl` → `packages/pg_macros/parser_graphtool.py`
   - `niceTables.pl` → `packages/pg_macros/nice_tables.py`
   - `draggableProof.pl` → `packages/pg_macros/draggable_proof.py`
   - `scaffold.pl` → `packages/pg_macros/scaffold.py`
3. **Move stub implementation**: Extract from sandbox, place in Python module
4. **Export from module**: Add to `__all__` list

## Current Stubs → Python Module Mapping

### Graph Tools
| Stub Function | Perl Source | Python Module | Status |
|--------------|-------------|---------------|--------|
| `GraphTool` | `macros/graph/parserGraphTool.pl` | `packages/pg_macros/parser_graphtool.py` | To migrate |

**Perl exports from parserGraphTool.pl:**
- `GraphTool` (main constructor)
- `with` (method for setting options)
- `cmp` (answer checking)
- `ans_rule` (generates HTML answer blank)
- Plus 25+ internal methods

**Current stub location:** `in_process_sandbox.py` lines 887-906, 1302-1313

---

### Table Layout
| Stub Function | Perl Source | Python Module | Status |
|--------------|-------------|---------------|--------|
| `LayoutTable` | `macros/ui/niceTables.pl` | `packages/pg_macros/nice_tables.py` | To migrate |
| `DataTable` | `macros/ui/niceTables.pl` | `packages/pg_macros/nice_tables.py` | To migrate |

**Perl exports from niceTables.pl:**
- `LayoutTable` (layout-oriented table)
- `DataTable` (data-oriented table with answer checking)
- `Row`, `Rows`, `Cols` (table structure helpers)
- Plus formatting utilities

**Current stub location:** `in_process_sandbox.py` lines 1950-1961

---

### Interactive Proof Tools
| Stub Function | Perl Source | Python Module | Status |
|--------------|-------------|---------------|--------|
| `DraggableProof` | `macros/math/draggableProof.pl` | `packages/pg_macros/draggable_proof.py` | To migrate |
| `DraggableSubsets` | (separate macro) | `packages/pg_macros/draggable_subsets.py` | To migrate |

**Perl exports from draggableProof.pl:**
- `DraggableProof` (constructor via `new`)
- `Print` (render method)
- `CorrectProof` (sets correct ordering)
- `cmp` (answer checking)

**Current stub location:** 
- `DraggableProof`: lines 909-915, 1534-1540
- `DraggableSubsets`: lines 917-919, 1541-1543

---

### Scaffolding (Not Currently Stubbed)
| Stub Function | Perl Source | Python Module | Status |
|--------------|-------------|---------------|--------|
| `Scaffold` | `macros/core/scaffold.pl` | `packages/pg_macros/scaffold.py` | Not yet stubbed |

**Perl exports from scaffold.pl:**
- `Scaffold` (via `new`)
- Section management: `Begin`, `End`, `start_section`, `end_section`
- Opening logic: `can_open`, `is_open`, `correct_or_first_incorrect`, etc.

**Action needed:** Create stub if any sample problems use it

---

## Python Module Structure

Each Python macro module should follow this pattern:

```python
# packages/pg_macros/parser_graphtool.py
"""
Python implementation of parserGraphTool.pl

Provides GraphTool for interactive graphing in problems.
"""

__all__ = ['GraphTool']

class GraphToolStub:
    """Stub implementation of GraphTool."""
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def with_params(self, **params):
        """Set parameters for the GraphTool."""
        self.kwargs.update(params)
        return self
    
    def __str__(self):
        return "[GraphTool]"


def GraphTool(*args, **kwargs):
    """
    Create a GraphTool object for interactive graphing.
    
    Stub implementation - returns a placeholder object.
    Full implementation would interface with JSXGraph.
    """
    return GraphToolStub(*args, **kwargs)
```

## Macro Loading Registry

The sandbox will use this mapping to load Python modules:

```python
# packages/pg_translator/pg_translator/macro_registry.py

PERL_TO_PYTHON_MODULES = {
    'parserGraphTool.pl': 'packages.pg_macros.parser_graphtool',
    'niceTables.pl': 'packages.pg_macros.nice_tables',
    'draggableProof.pl': 'packages.pg_macros.draggable_proof',
    'scaffold.pl': 'packages.pg_macros.scaffold',
    'PGcourse.pl': 'packages.pg_macros.pgcourse',
    # Add more as needed
}

def load_macro_module(pl_filename):
    """Import the Python module corresponding to a Perl macro file."""
    python_module = PERL_TO_PYTHON_MODULES.get(pl_filename)
    if python_module:
        try:
            return __import__(python_module, fromlist=['*'])
        except ImportError:
            return None
    return None
```

## Migration Checklist

- [ ] Create `packages/pg_macros/parser_graphtool.py` with `GraphTool` stub
- [ ] Create `packages/pg_macros/nice_tables.py` with `LayoutTable` and `DataTable` stubs
- [ ] Create `packages/pg_macros/draggable_proof.py` with `DraggableProof` stub
- [ ] Create `packages/pg_macros/draggable_subsets.py` with `DraggableSubsets` stub
- [ ] Create `packages/pg_macros/pgcourse.py` for course-specific helpers
- [ ] Implement `MacroRegistry` in sandbox to load these modules
- [ ] Add deprecation warnings to inline sandbox stubs
- [ ] Test with sample problems: GraphTool, LayoutTable, DraggableProof
- [ ] Document macro resolution order in developer docs

## Testing Strategy

For each migrated stub:
1. Run the corresponding sample problem (e.g., `TriangleGraphTool.pg`)
2. Verify it loads from the Python macro module (add debug logging)
3. Confirm problem renders without errors
4. Check that answer blanks appear correctly (even if checking is stubbed)

Sample test command:
```bash
python pg_solve.py tutorial/sample-problems/Geometry/TriangleGraphTool.pg --debug
```
