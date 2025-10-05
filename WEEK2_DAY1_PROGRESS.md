# Week 2 Progress Report - Day 1

**Date**: October 5, 2025
**Status**: IN PROGRESS - Integration challenges identified

---

## PROGRESS SUMMARY

### ✅ Completed
1. Created `macro_sandbox.py` - Enhanced sandbox with macro loading support
2. Created test problems (`simple_numeric.pg`, `random_addition.pg`)
3. Created comprehensive integration test suite (`test_week2_integration.py`)
4. Fixed `macro_loader.py` imports (PGSandbox → Sandbox)

### ⚠️ In Progress
1. Answer registration - answers are called but not captured properly
2. Subprocess sandbox architecture mismatch with macro system

### ❌ Blockers
1. **Architecture Mismatch**: Current sandbox uses subprocess isolation, but macro system needs in-process execution for answer evaluator objects
2. **Serialization Issue**: Answer evaluators are Python objects that can't be easily serialized across process boundary

---

## CURRENT TEST RESULTS

**Test**: `test_simple_numeric_problem_renders`

**What Works**:
```
✅ Problem renders: "What is 2 + 2?"
✅ Answer blank generates: <input type="text" name="AnSwEr0001"...>
✅ BR() works (line break present)
✅ No execution errors
```

**What Doesn't Work**:
```
❌ answer_blanks dict is empty {}
❌ num_answers in metadata is 0
❌ Answers not captured for grading
```

**Root Cause**: 
- `ANS(num_cmp(4))` is called in subprocess
- Answer evaluator object created in subprocess
- Answer evaluators can't be serialized back to parent process
- Result: answers dict comes back empty

---

## ARCHITECTURAL DECISION NEEDED

### Option 1: Keep Subprocess Sandbox (Current)

**Pros**:
- Better isolation
- More secure
- Resource limits easier

**Cons**:
- Can't pass evaluator objects across process boundary
- Need to serialize/deserialize all evaluators
- Complex reconstruction logic needed
- May lose evaluator state

**Implementation**:
1. Serialize evaluator type + parameters in subprocess
2. Send back serialized data via JSON
3. Reconstruct evaluators in parent process
4. Map answer names to reconstructed evaluators

**Complexity**: HIGH
**Time**: 2-3 days

### Option 2: In-Process Sandbox (RestrictedPython or similar)

**Pros**:
- Evaluator objects stay in memory
- No serialization needed
- Simpler integration with macros
- Can use Week 1 macro implementations directly

**Cons**:
- Less isolation
- Need careful security
- Variable naming restrictions (if using RestrictedPython)

**Implementation**:
1. Create in-process sandbox with restricted exec()
2. Load macros into sandbox namespace
3. Execute problem code
4. Collect evaluator objects directly

**Complexity**: MEDIUM
**Time**: 1-2 days

### Option 3: Hybrid Approach

**Pros**:
- Use subprocess for untrusted code
- Use in-process for macro definitions
- Best of both worlds

**Cons**:
- Most complex
- Two execution environments
- Coordination overhead

**Complexity**: VERY HIGH
**Time**: 3-4 days

---

## RECOMMENDATION

**Go with Option 2: In-Process Sandbox**

### Rationale:
1. **Compatibility**: Week 1 macro implementations (pg_core.py, pg_basic_macros.py) expect in-process execution
2. **Simplicity**: No serialization gymnastics
3. **Time**: Faster to implement
4. **Precedence**: Perl PG uses Safe compartment (in-process with restrictions)

### Security Considerations:
- Use Python's `compile()` with restricted mode
- Whitelist safe builtins
- Disable dangerous operations (__import__, open, exec, eval)
- Time limits via timeout
- Memory limits via resource module (Unix) or monitoring (Windows)

### Implementation Plan:
```python
class InProcessSandbox:
    """In-process sandbox with restricted execution."""
    
    def __init__(self):
        self.namespace = {}
        self._setup_safe_builtins()
        self._load_macros()
    
    def _setup_safe_builtins(self):
        """Setup safe built-in functions."""
        safe_builtins = {
            'abs': abs,
            'min': min,
            'max': max,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            # Math functions
            'round': round,
            'pow': pow,
            # Safe True/False/None
            'True': True,
            'False': False,
            'None': None,
        }
        self.namespace['__builtins__'] = safe_builtins
    
    def _load_macros(self):
        """Load PG macro modules."""
        # Import and register all macro functions
        from pg_macros.core import pg_core, pg_basic_macros
        
        # Create PG environment
        env = pg_core.PGEnvironment({'problemSeed': 1234})
        pg_core.set_environment(env)
        
        # Register all functions in namespace
        self.namespace.update({
            'DOCUMENT': pg_core.DOCUMENT,
            'ENDDOCUMENT': pg_core.ENDDOCUMENT,
            'TEXT': pg_core.TEXT,
            'ANS': pg_core.ANS,
            'ans_rule': pg_basic_macros.ans_rule,
            # ... etc
        })
    
    def execute(self, code: str) -> dict:
        """Execute code in sandbox."""
        exec(code, self.namespace)
        # Collect results from PGEnvironment
        env = pg_core.get_environment()
        return {
            'text': ''.join(env.output_array),
            'answers': env.answers_hash,
            # ...
        }
```

---

## NEXT STEPS (Revised Plan)

### Immediate (Today):
1. ✅ Document current status (this file)
2. ⏭️ Create `in_process_sandbox.py` with safe execution
3. ⏭️ Integrate with Week 1 macro implementations
4. ⏭️ Update `PGExecutor` to use in-process sandbox
5. ⏭️ Re-run integration tests

### Tomorrow:
1. Answer evaluators (num_cmp, str_cmp, fun_cmp)
2. Complete integration tests
3. Test with real .pg files

### Day 3:
1. Bug fixes
2. Documentation
3. Performance testing

---

## LESSONS LEARNED

1. **Architecture First**: Should have verified sandbox architecture before starting integration
2. **Object Serialization**: Python objects (like evaluators) don't serialize well across processes
3. **Reference Implementation**: Perl PG uses in-process Safe compartment, not subprocess
4. **Test Early**: Integration tests revealed architectural mismatch quickly

---

## DECISION LOG

**Decision**: Switch to in-process sandbox for Week 2 implementation

**Made By**: Implementation analysis
**Date**: October 5, 2025
**Rationale**: 
- Enables direct use of Week 1 macro implementations
- Matches Perl PG architecture (Safe compartment)
- Simpler integration path
- Faster development

**Trade-offs Accepted**:
- Less process isolation (mitigated by restricted builtins)
- Need careful security review (planned for Week 4)
- May need subprocess sandbox later for untrusted code (can add as Option 3 later)

---

**Status**: Ready to implement in-process sandbox
**Next Action**: Create `in_process_sandbox.py`
**ETA for Day 1 Complete**: End of day (6-8 hours remaining)
