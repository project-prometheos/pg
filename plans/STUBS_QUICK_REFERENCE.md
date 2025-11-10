# Stub Functions - Quick Reference

Quick lookup for all stub functions that need implementation.

## By Category

### Answer Checking (7 stubs)
| Function | Module | Status | Difficulty |
|----------|--------|--------|------------|
| `MultiAnswer` | `pg_macros.answers.multi_answer` | ⚠️ Stub | 🔴 High |
| `COMPOSITION_ANS` | `pg_macros.answers.answer_composition` | ⚠️ Stub | 🟡 Medium |
| `UNORDERED_ANS` | `pg_macros.answers.unordered_answer` | ⚠️ Stub | 🟡 Medium |
| `AnswerHints` | `pg_macros.answers.answer_hints` | ⚠️ Stub | 🟡 Medium |
| `CheckboxList` | `pg_macros.parsers.parser_checkbox_list` | ⚠️ Stub | 🟡 Medium |
| `NumberWithUnits.cmp()` | `pg_macros.parsers.parser_number_with_units` | ⚠️ Stub | 🟡 Medium |

### Math Parsers (6 stubs)
| Function | Module | Status | Difficulty |
|----------|--------|--------|------------|
| `LinearRelation` | `pg_macros.parsers.parser_linear_relation` | ⚠️ Stub | 🔴 High |
| `DifferenceQuotient` | `pg_macros.parsers.parser_difference_quotient` | ⚠️ Stub | 🔴 High |
| `specialRadical` | `pg_macros.parsers.parser_special_trig` | ⚠️ Stub | 🟡 Medium |
| `specialAngle` | `pg_macros.parsers.parser_special_trig` | ⚠️ Stub | 🟡 Medium |
| `ImplicitPlane.cmp()` | `pg_macros.parsers.parser_implicit_plane` | ⚠️ Stub | 🟡 Medium |
| `ParametricLine.cmp()` | `pg_macros.parsers.parser_parametric_line` | ⚠️ Stub | 🟡 Medium |

### Multiple Choice (5 stubs)
| Function | Module | Status | Difficulty |
|----------|--------|--------|------------|
| `PopUp` | `pg_macros.parsers.parser_popup` | ⚠️ Stub | 🟡 Medium |
| `DropDown` | `pg_macros.parsers.parser_popup` | ⚠️ Stub | 🟡 Medium |
| `DropDownTF` | `pg_macros.parsers.parser_popup` | ⚠️ Stub | 🟢 Low |
| `RadioButtons` | `pg_macros.parsers.parser_popup` | ⚠️ Stub | 🟡 Medium |
| `RadioMultiAnswer` | `pg_macros.parsers.parser_radio_multianswer` | ⚠️ Stub | 🟡 Medium |

### Statistics (4 stubs)
| Function | Module | Status | Difficulty |
|----------|--------|--------|------------|
| `linear_regression` | `pg_macros.math.statistics_utils` | ⚠️ Stub | 🟡 Medium |
| `stats_mean` | `pg_macros.math.statistics_utils` | ✅ Basic | 🟢 Low |
| `stats_sd` | `pg_macros.math.statistics_utils` | ✅ Basic | 🟢 Low |
| `stats_SX_SXX` | `pg_macros.math.statistics_utils` | ✅ Basic | 🟢 Low |

### Graphics (3 stubs)
| Function | Module | Status | Difficulty |
|----------|--------|--------|------------|
| `Graph3D` | `pg_macros.graph.live_graphics_3d` | ⚠️ Stub | 🔴 High |
| `VectorField3D` | `pg_macros.graph.vector_field_3d` | ⚠️ Stub | 🔴 High |
| `GraphTool` | `pg_macros.graph.parser_graphtool` | ⚠️ Stub | 🔴 High |

### Interactive Elements (3 stubs)
| Function | Module | Status | Difficulty |
|----------|--------|--------|------------|
| `DraggableProof` | `pg_macros.math.draggable_proof` | ⚠️ Stub | 🔴 High |
| `DraggableSubsets` | `pg_macros.math.draggable_subsets` | ⚠️ Stub | 🔴 High |
| `Scaffold/Section` | `pg_macros.ui.scaffold` | ⚠️ Stub | 🟡 Medium |

### Context & Grading (5 stubs)
| Function | Module | Status | Difficulty |
|----------|--------|--------|------------|
| `LimitedPowers` | `pg_macros.contexts.limited_powers` | ⚠️ Stub | 🟡 Medium |
| `parser_Assignment` | `pg_macros.parsers.parser_assignment` | ⚠️ Stub | 🟡 Medium |
| `parserFunction` | `pg_macros.parsers.parser_function` | ⚠️ Stub | 🟡 Medium |
| `install_problem_grader` | `pg_macros.core.pg_graders` | ⚠️ Stub | 🟡 Medium |
| `custom_problem_grader_fluid` | `pg_macros.core.pg_graders` | ⚠️ Stub | 🟡 Medium |

### Utilities (8 stubs)
| Function | Module | Status | Difficulty |
|----------|--------|--------|------------|
| `tag` | `pg_macros.core.pgml_utils` | ✅ Basic | 🟢 Low |
| `helpLink` | `pg_macros.core.pgml_utils` | ⚠️ Stub | 🟢 Low |
| `random_subset` | `pg_macros.core.fallback_utilities` | ✅ Basic | 🟢 Low |
| `new_match_list` | `pg_macros.core.fallback_utilities` | ⚠️ Stub | 🟡 Medium |
| `pop_up_list_print_q` | `pg_macros.core.fallback_utilities` | ⚠️ Stub | 🟢 Low |
| `splice` | `pg_macros.core.array_utilities` | ✅ Basic | 🟢 Low |
| `push` | `pg_macros.core.array_utilities` | ✅ Basic | 🟢 Low |
| `undef` | `pg_macros.core.fallback_utilities` | ✅ Basic | 🟢 Low |

---

## By Priority

### 🔴 Priority 1: Critical (Highest Impact, Highest Effort)
- `MultiAnswer` - Multiple answer validation
- `LinearRelation` - Linear equation checking
- `DifferenceQuotient` - Calculus expression validation

### 🟠 Priority 2: High Impact (Medium-High Effort)
- `PopUp` / `DropDown` - Multiple choice interfaces
- `RadioButtons` / `RadioMultiAnswer` - Radio button groups
- `Graph3D` / `VectorField3D` - 3D Graphics
- `DraggableProof` / `DraggableSubsets` - Interactive elements

### 🟡 Priority 3: Medium Impact (Medium Effort)
- `specialRadical` / `specialAngle` - Math form validation
- `COMPOSITION_ANS` / `UNORDERED_ANS` - Answer composition
- `LimitedPowers` - Power restrictions
- `install_problem_grader` - Custom graders

### 🟢 Priority 4: Lower Priority (Low Effort)
- `tag` / `helpLink` - HTML utilities
- `random_subset` - Array utilities
- `linear_regression` - Statistics
- `parser_Assignment` - Assignment checking

---

## Implementation Status

**Total Stubs**: 45+
**Fully Implemented**: 10
**Basic Implementation**: 15
**Needs Full Implementation**: 20+

---

## By Difficulty Level

### 🟢 Low Difficulty (Can be done in 1-2 days each)
- `tag`, `helpLink`, `pop_up_list_print_q`
- `random_subset`, `splice`, `push`, `undef`
- `DropDownTF`, `stats_mean`, `stats_sd`, `stats_SX_SXX`
- Total: ~10 functions

### 🟡 Medium Difficulty (Can be done in 3-5 days each)
- `MultiAnswer` (5-7 days)
- `LinearRelation` (5-7 days)
- `PopUp`, `DropDown`, `RadioButtons`, `RadioMultiAnswer` (4-6 days each)
- `specialRadical`, `specialAngle` (3-5 days each)
- `LimitedPowers`, `parser_Assignment` (3-5 days each)
- `COMPOSITION_ANS`, `UNORDERED_ANS` (3-4 days each)
- `CheckboxList`, `new_match_list` (3-4 days each)
- Total: ~18 functions, ~60-80 days

### 🔴 High Difficulty (Can be done in 5-10 days each)
- `DifferenceQuotient` (5-7 days)
- `Graph3D` (7-10 days)
- `VectorField3D` (7-10 days)
- `GraphTool` (10-15 days)
- `DraggableProof` (10-15 days)
- `DraggableSubsets` (10-15 days)
- `Scaffold/Section` (7-10 days)
- `parserFunction` (5-7 days)
- `install_problem_grader` / `custom_problem_grader_fluid` (5-7 days)
- `linear_regression` (5-7 days)
- Total: ~10 functions, ~80-120 days

---

## Estimated Timeline

| Phase | Functions | Estimated Time |
|-------|-----------|-----------------|
| Phase 12 | Priority 1 (3) | 15-21 days |
| Phase 13 | Priority 2a - Graphics (3) | 21-35 days |
| Phase 14 | Priority 2b - Interactive (3) | 30-45 days |
| Phase 15 | Priority 3 (18) | 60-80 days |
| Phase 16 | Priority 4 (10) | 15-20 days |
| **Total** | **47 functions** | **~140-200 days** |

---

## Quick Lookup by Module

### `pg_macros/answers/`
- [ ] `MultiAnswer` - Multi-answer checking
- [ ] `COMPOSITION_ANS` - Function composition
- [ ] `UNORDERED_ANS` - Unordered answer sets
- [ ] `AnswerHints` - Custom hints
- [ ] `CheckboxList` - Checkbox group answers

### `pg_macros/parsers/`
- [ ] `LinearRelation` - Linear equation parsing
- [ ] `DifferenceQuotient` - Calculus expressions
- [ ] `specialRadical` - Radical form checking
- [ ] `specialAngle` - Angle form checking
- [ ] `PopUp`, `DropDown`, `RadioButtons` - Choice interfaces
- [ ] `RadioMultiAnswer` - Multi-group radio buttons
- [ ] `parser_Assignment` - Assignment validation
- [ ] All `.cmp()` methods in number parsers

### `pg_macros/math/`
- [ ] `linear_regression` - Regression calculations
- [ ] `DraggableProof` - Proof dragging interface
- [ ] `DraggableSubsets` - Subset selection

### `pg_macros/graph/`
- [ ] `Graph3D` - 3D graphing
- [ ] `VectorField3D` - 3D vector fields
- [ ] `GraphTool` - Interactive graph tool

### `pg_macros/core/`
- [ ] `LimitedPowers` - Power restrictions
- [ ] `install_problem_grader` - Grader installation
- [ ] `custom_problem_grader_fluid` - Custom grading

### `pg_macros/ui/`
- [ ] `Scaffold/Section` - Problem structure

---

## Testing Checklist Template

For each implementation:

```
Function: _________
Module: ___________

Testing:
- [ ] Unit tests written
- [ ] Unit tests passing (100%)
- [ ] Integration tests passing
- [ ] Edge cases handled
- [ ] Perl equivalence verified
- [ ] Error messages are helpful
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Code review passed
- [ ] Zero regressions in suite
```

---

## Notes for Developers

1. **Perl Reference**: Check `/tutorial/` for Perl macro implementations
2. **Test First**: Write tests before implementation
3. **Incremental**: Implement in small, testable chunks
4. **Document**: Add docstrings and comments as you go
5. **Verify**: Compare output with Perl implementations
6. **Performance**: Interactive elements should respond in <100ms
7. **Accessibility**: Include ARIA labels and keyboard support

---

## Related Documents

- `COMPLETE_STUB_MIGRATION_PLAN.md` - Overall migration strategy
- `packages/pg_macros/pg_macros/**/*.py` - Implementation files
- `packages/pg_macros/tests/` - Test files
- `tutorial/` - Perl reference implementations

