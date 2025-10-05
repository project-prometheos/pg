# Strategic Thinking: Implementation Approach
## 1:1 100% Parity Achievement Strategy

**Date**: October 5, 2025  
**Author**: Analysis of Perl codebase vs Python port

---

## KEY INSIGHT: The Real Blocker

After comprehensive review of:
- 4 implementation plans (01-04)
- Perl reference code (133,164 lines)
- Python port status (~7,200 lines, 5.4%)
- Dependency graph

**The critical finding: The MACRO SYSTEM is the architectural keystone.**

Without it, nothing else works. You can't even run:
```python
TEXT("Hello World");
```

---

## THE ARCHITECTURE REALITY

### What We Thought (Wrong)

```
Parser → Formula → Answer System → Problems Work
```

### What Actually Is (Correct)

```
Macro System (PG.pl)
    ↓
Translator (loads & executes macros)
    ↓
    ├─→ PGML (uses macros)
    ├─→ Answer System (uses macros)
    ├─→ Context System (uses macros)
    └─→ Formula (uses context)
         ↓
    Parser (supporting role)
```

**The macro system is the foundation, not a layer on top.**

---

## WHY MACRO SYSTEM FIRST?

### 1. Every PG Problem Uses Macros

**Minimal problem**:
```perl
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");

BEGIN_PGML
What is 2+2?

[_____]{4}
END_PGML

ENDDOCUMENT();
```

This requires:
- `DOCUMENT()` - from PG.pl
- `loadMacros()` - from PG.pl
- `BEGIN_PGML`/`END_PGML` - from PGML.pl (loaded via loadMacros)
- `[_____]{4}` - answer blank with evaluator (from PGbasicmacros.pl)
- `ENDDOCUMENT()` - from PG.pl

**Without macros: NOTHING RENDERS.**

### 2. Macros Define the Environment

Macros provide:
- Problem output functions (TEXT, SOLUTION, HINT)
- Answer registration (ANS, NAMED_ANS)
- Answer blank generation (ans_rule, etc.)
- Mathematical context setup
- Display mode handling
- Evaluation environment

**The translator needs these to function.**

### 3. Macro Loading is Complex

From Translator.pm:
```perl
sub unrestricted_load {
    my $self = shift;
    my $macro_file = shift;
    
    # Save permission mask
    my $stored_mask = $self->{safe_compartment}->mask();
    
    # Set unrestricted (empty mask)
    $self->{safe_compartment}->mask(0);
    
    # Load file
    my $errors = $self->rdo($macro_file);
    
    # Call init function if exists
    my $name = get_name($macro_file);
    my $init = "_${name}_init";
    if (defined &{$init}) {
        &{$init}();
    }
    
    # Restore mask
    $self->{safe_compartment}->mask($stored_mask);
    
    return $errors;
}
```

**This is non-trivial**: permission management, init functions, safe execution.

### 4. Current Python Status

**macro_loader.py**:
- Has skeleton structure
- Missing actual execution
- Missing permission management
- Missing init function calling
- Missing namespace integration

**Result**: Can't load any macros, can't run any problems.

---

## THE DEPENDENCY TRAP

### What Happens If We Skip Macros?

**Scenario**: "Let's finish Formula first, then do macros"

**Problem**: Formula needs Context, which needs macros.

```python
# Formula.py needs:
from pg_math import Context  # ← Context needs to be set up by macros

# In problems:
Context("Fraction")  # ← This is a macro-loaded context

$ans = Compute("x^2")  # ← Compute() is a macro function
```

**Every advanced feature depends on macros being loaded and initialized.**

### The Cascade Effect

```
Skip Macros
    ↓
Can't test real problems
    ↓
Can't verify Formula changes
    ↓
Can't test Answer System
    ↓
Can't test PGML
    ↓
Can't verify anything works
```

**Without macros, we're building in a vacuum.**

---

## WHAT THE PLANS TELL US

### Plan 01: Macro System (8-12 weeks)

**Most detailed plan** because it's most critical:
- PG.pl port: 1,800 lines needed
- PGbasicmacros.pl: 2,200 lines needed
- PGML.pl completion: 1,500 lines needed
- Macro loader: 400 lines needed
- Plus auxiliary functions, choice macros, etc.

**Total: ~6,000 lines to write**

### Plan 02: Translator Features (2-3 weeks)

**Depends on Plan 01** completion:
- unrestricted_load() needs to execute macros
- PG_errorMessage() needs file mapping from macros
- Grading needs answer system from macros

### Plan 03: Formula Enhancements (2 weeks)

**Already 65% done**, but:
- Adaptive parameters need full context system
- Testing needs real problems (needs macros)
- Integration needs answer system (needs macros)

### Plan 04: Answer System (2-3 weeks)

**Depends on Plan 01**:
- Filter chains need macro functions
- cmp() methods need context (from macros)
- MultiAnswer needs environment (from macros)

---

## THE RIGHT APPROACH

### Phase 1A: Core Macro System (Weeks 1-4)

**Goal**: Get TEXT(), ANS(), loadMacros() working

**Implementation Order**:

1. **Week 1: Macro Loader**
   - Complete `unrestricted_load()`
   - Implement permission masking
   - Add init function calling
   - Test with simple Python macros

2. **Week 2: PG.pl Core**
   - Port TEXT(), BEGIN_TEXT/END_TEXT
   - Port ANS(), NAMED_ANS()
   - Port DOCUMENT(), ENDDOCUMENT()
   - Port basic environment functions

3. **Week 3: PGbasicmacros.pl Essentials**
   - ans_rule(), ans_radio_buttons(), pop_up_list()
   - Display constants (PAR, BR, etc.)
   - MODES()
   - Basic image()

4. **Week 4: Integration & Testing**
   - loadMacros() works end-to-end
   - Simple problems render
   - Error handling
   - Documentation

**Deliverable**: 10 simple problems render and grade

### Phase 1B: PGML Basics (Weeks 5-6)

**Goal**: BEGIN_PGML/END_PGML work

**Depends on**: Phase 1A complete (needs macros loaded)

1. **Week 5: PGML Macro Integration**
   - PGML.pl as loadable macro
   - BEGIN_PGML/END_PGML functions
   - Integration with answer blanks

2. **Week 6: Essential PGML Features**
   - Tables
   - Headings  
   - Answer blanks with evaluators
   - Solution sections

**Deliverable**: 20 PGML problems render

### Phase 1C: Answer System Basics (Weeks 7-8)

**Goal**: Answer checking works reliably

**Depends on**: Phases 1A & 1B complete

1. **Week 7: Filter Chains**
   - Pre/post filter infrastructure
   - Standard filters
   - Integration with evaluators

2. **Week 8: cmp() Methods**
   - Add cmp() to all MathValue types
   - Basic MultiAnswer
   - Grading system

**Deliverable**: 50 problems with diverse answer types

### Phase 2: Expansion (Weeks 9-16)

**Build on solid foundation**:
- More macros (auxiliary, choice, graph)
- Formula enhancements
- Context system
- Advanced PGML

---

## WHY THIS APPROACH WINS

### 1. Testability

After Phase 1A:
- ✅ Can test with real problems
- ✅ Can verify each change works
- ✅ Can catch regressions
- ✅ Can measure progress (N problems render)

### 2. Incremental Value

Each week delivers:
- Week 1: Macro loading works
- Week 2: TEXT() and ANS() work
- Week 3: Input fields work
- Week 4: Simple problems work
- Week 5-6: PGML problems work
- Week 7-8: Answer checking works
- **Result**: Continuous progress, not big-bang**

### 3. Risk Mitigation

**If we hit a blocker**:
- Have working foundation
- Can pivot to workarounds
- Don't lose all progress

**If we do Formula first and hit macro blocker**:
- All Formula work untestable
- Might need to rework
- Lost time

### 4. Team Coordination

With macros done first:
- Multiple developers can work in parallel
- Clear interfaces between components
- Less merge conflicts
- Independent testing

---

## THE NUMBERS

### Current Plan Estimates

| Plan | Est. Time | Depends On |
|------|-----------|------------|
| 01 - Macros | 8-12 wks | Nothing |
| 02 - Translator | 2-3 wks | Plan 01 |
| 03 - Formula | 2 wks | Plan 01 |
| 04 - Answer | 2-3 wks | Plan 01 |

**Serial (as written)**: 14-20 weeks

**Parallel (after Plan 01)**: 8-12 weeks + max(2-3 wks) = 11-15 weeks

**Time saved by doing 01 first: Can parallelize 02-04**

### Realistic Timeline

**1 Developer**:
- Phase 1A (Macros): 4 weeks
- Phase 1B (PGML): 2 weeks
- Phase 1C (Answer): 2 weeks
- Phase 2 (Expansion): 8 weeks
- **Total: 16 weeks (4 months)**

**2 Developers**:
- Phase 1A: 2 weeks (pair on critical parts)
- Phase 1B-C: 2 weeks (parallel)
- Phase 2: 4 weeks (parallel)
- **Total: 8 weeks (2 months)**

---

## CRITICAL SUCCESS FACTORS

### 1. Stay Focused on Macros

**Don't get distracted by**:
- "Formula needs just one more feature..."
- "Let's refactor the parser first..."
- "We should redesign the context system..."

**Stay focused until macros work.**

### 2. Test with Real Problems

**Every feature should be tested with**:
- Actual PG problem files
- From the OPL if possible
- Not just unit tests

**Metric**: Number of OPL problems that render correctly

### 3. One Macro File at a Time

**Don't try to port all macros at once**:
- Port PG.pl completely first
- Then PGbasicmacros.pl
- Then PGML.pl
- etc.

**Each macro file should be 100% complete before moving on.**

### 4. Prioritize by Usage

**Port macros in order of usage frequency**:
1. PG.pl - used by 100% of problems
2. PGbasicmacros.pl - used by 95%
3. PGML.pl - used by 80%
4. PGauxiliaryFunctions.pl - used by 70%
5. etc.

**Don't port obscure macros until core is done.**

---

## RECOMMENDATION TO CODING AGENT

### Immediate Next Steps

1. **Read Plans 01-04 carefully**
   - Understand the full scope
   - Note the dependencies
   - See the detailed specs

2. **Start with Plan 01, Phase 1**
   - Implement MacroLoader.unrestricted_load()
   - Get init function calling working
   - Test with simple Python macro

3. **Then PG.pl core functions**
   - TEXT()
   - BEGIN_TEXT/END_TEXT
   - ANS()
   - DOCUMENT/ENDDOCUMENT

4. **Test continuously**
   - Create test problems
   - Verify each function works
   - Document what works

### What NOT To Do

❌ **Don't** jump to Formula enhancements  
❌ **Don't** refactor existing code extensively  
❌ **Don't** try to do everything at once  
❌ **Don't** skip testing with real problems  
❌ **Don't** implement features without macro support  

### Success Metrics

**Week 1**: Macro loader loads Python macros and calls init functions  
**Week 2**: TEXT() and ANS() work in test problems  
**Week 3**: ans_rule() generates input fields  
**Week 4**: 10 simple problems render correctly  

---

## CONCLUSION

The path to 100% parity is clear:

1. **Macros First** - Nothing works without them
2. **Test Continuously** - Use real problems as validation
3. **Incremental Progress** - Deliver value each week
4. **Stay Focused** - Don't get distracted by "nice to haves"

**The plans (01-04) provide the detailed roadmap.**  
**This document provides the strategic thinking.**  
**Now: Execute.**

---

**Key Message**: 

> The macro system is not "just another component" - it's the foundation that everything else is built on. Port it first, port it completely, and the rest will follow naturally.

---

**Next Action**: Implement Plan 01, Phase 1, Week 1 (Macro Loader)
