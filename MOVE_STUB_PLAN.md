# Summary: Moving Stubs from `in_process_sandbox.py` to Macro Modules

## Current State

**Problem**: Many function stubs are hardcoded directly in `in_process_sandbox.py` as fallbacks. This makes the codebase harder to maintain and doesn't align with WeBWorK's modular macro architecture.

**Current stub locations** (examples):
- `GraphTool` - lines 887-906, 1302-1313
- `LayoutTable` - lines 1950-1961  
- `DraggableProof` - lines 909-915, 1534-1540
- `DraggableSubsets` - lines 917-919, 1541-1543

## The Plan

### 1. **Leverage Existing Infrastructure**
The codebase already has:
- ✅ `packages/pg_macros/registry.py` - Maps `.pl` filenames → Python modules
- ✅ `MacroRegistry.load()` - Dynamically imports Python macro modules
- ✅ Sandbox's `load_macros()` - Accepts `.pl` filenames

### 2. **Map Stubs to Their Source Macros** (Already Done)
By analyzing `macros/*.pl` files, we identified:

| Stub Function | Perl Source | Target Python Module |
|--------------|-------------|---------------------|
| `GraphTool` | `macros/graph/parserGraphTool.pl` | `pg_macros/graph/parser_graphtool.py` |
| `LayoutTable` | `macros/ui/niceTables.pl` | `pg_macros/ui/nice_tables.py` |
| `DraggableProof` | `macros/math/draggableProof.pl` | `pg_macros/math/draggable_proof.py` |
| `DraggableSubsets` | (separate macro) | `pg_macros/ui/draggable_subsets.py` |

### 3. **Migration Steps**

#### Step A: Extend `registry.py` mapping
Add new entries to the `module_map` dict:
```python
module_map = {
    # ... existing ...
    "parserGraphTool.pl": "pg_macros.graph.parser_graphtool",
    "draggableProof.pl": "pg_macros.math.draggable_proof", 
    # niceTables.pl already exists ✓
}
```

#### Step B: Create Python macro modules
Move stubs from `in_process_sandbox.py` into proper modules:

**Example: `pg_macros/graph/parser_graphtool.py`**
```python
__all__ = ['GraphTool']

class GraphToolStub:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def with_params(self, **params):
        self.kwargs.update(params)
        return self
    
    def __str__(self):
        return "[GraphTool]"

def GraphTool(*args, **kwargs):
    return GraphToolStub(*args, **kwargs)
```

#### Step C: Update sandbox to use registry
Instead of inline stubs, the sandbox will:
1. Call `registry.load('parserGraphTool.pl')` when a problem uses it
2. Inject exported symbols into the execution namespace
3. Keep inline stubs ONLY as final fallback with deprecation warning

#### Step D: Test migration
Run sample problems that use these features:
- `TriangleGraphTool.pg` → tests `GraphTool`
- `LayoutTable.pg` → tests `LayoutTable`
- `DraggableProof.pg` → tests `DraggableProof`

### 4. **Key Design Decisions**

✅ **Keep `.pl` names in registry keys** - The preprocessor reads `loadMacros('parserGraphTool.pl')` and we map that string directly

✅ **Use Python naming in file paths** - Actual modules use underscores: `parser_graphtool.py`, not `parserGraphTool.py`

✅ **Preserve current stub behavior** - Initial migration just relocates code; we can add real functionality later

✅ **Maintain backward compatibility** - Inline stubs remain as last-resort fallback during transition

### 5. **Benefits**

- **Modular architecture** - Each macro's behavior lives where it belongs
- **Easier to enhance** - Add real functionality by extending the Python module
- **Better debugging** - Clear error messages when macros are missing
- **1:1 parity with Perl** - Matches WeBWorK's macro structure

### 6. **Migration Priority**

**Phase 1 (High Impact):**
- GraphTool (used in geometry problems)
- LayoutTable (used in table layouts)
- DraggableProof (used in proof problems)

**Phase 2 (As Needed):**
- Other specialized tools as encountered in sample problems
- Course-specific helpers in `PGcourse.pl`

## End Result

After migration:
```
PG problem: loadMacros('parserGraphTool.pl', 'niceTables.pl')
    ↓
Registry maps to Python modules
    ↓
Sandbox imports: pg_macros.graph.parser_graphtool
                pg_macros.ui.nice_tables
    ↓
Functions injected into namespace: GraphTool(), LayoutTable()
    ↓
Problem executes successfully ✓
```

## Implementation Checklist

- [ ] **Step 1**: Extend `packages/pg_macros/pg_macros/registry.py`
  - [ ] Add `"parserGraphTool.pl": "pg_macros.graph.parser_graphtool"`
  - [ ] Add `"draggableProof.pl": "pg_macros.math.draggable_proof"`
  - [ ] Verify `"niceTables.pl"` mapping already exists

- [ ] **Step 2**: Create/update Python macro modules
  - [ ] Create `packages/pg_macros/pg_macros/graph/` directory
  - [ ] Create `packages/pg_macros/pg_macros/graph/__init__.py`
  - [ ] Create `packages/pg_macros/pg_macros/graph/parser_graphtool.py` with `GraphTool` stub
  - [ ] Create `packages/pg_macros/pg_macros/math/draggable_proof.py` with `DraggableProof` stub
  - [ ] Check if `packages/pg_macros/pg_macros/ui/nice_tables.py` has `LayoutTable`; add if missing

- [ ] **Step 3**: Update sandbox loading mechanism
  - [ ] Modify `in_process_sandbox.py` to call `registry.load()` for macro files
  - [ ] Add deprecation warnings to inline stub fallbacks
  - [ ] Ensure exported symbols are properly injected into namespace

- [ ] **Step 4**: Testing
  - [ ] Run `python pg_solve.py tutorial/sample-problems/Geometry/TriangleGraphTool.pg`
  - [ ] Run `python pg_solve.py tutorial/sample-problems/ProblemTechniques/LayoutTable.pg`
  - [ ] Run `python pg_solve.py tutorial/sample-problems/Misc/DraggableProof.pg`
  - [ ] Verify problems render without errors
  - [ ] Check that stubs are loaded from Python modules (add debug logging)

- [ ] **Step 5**: Documentation
  - [ ] Update developer docs on macro resolution order
  - [ ] Document how to add new macro modules
  - [ ] Add migration guide for future stub relocations

## Notes

- The preprocessor already treats `loadMacros()` as a no-op in the generated Python code
- The sandbox's `load_macros()` method is the actual mechanism that loads Python modules
- Keep the existing inline stubs temporarily as fallbacks during migration
- Test incrementally: migrate one stub at a time, verify it works, then move to the next
