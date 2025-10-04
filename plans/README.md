# PG PYTHON PORT - IMPLEMENTATION PLANS

**Date**: 2025-10-04
**Goal**: Achieve 1:1 feature parity with Perl PG implementation

---

## OVERVIEW

These plans detail the implementation roadmap for achieving complete feature parity between the Perl PG system and the Python port. Based on the comprehensive code review (see `../REVIEW_20251004.md`), we need to port approximately **15,850 lines of code** across 4 major subsystems.

---

## IMPLEMENTATION PLANS

### 1. [Macro System Implementation](01_MACRO_SYSTEM_IMPLEMENTATION.md)
**Effort**: 8-12 weeks (1 dev) | 4-6 weeks (2 devs)
**Priority**: CRITICAL
**Gap**: ~13,500 LOC (90% missing)

**Key Components**:
- Macro loading infrastructure (unrestricted_load, PG_macro_file_eval)
- PG.pl port (2,441 lines → 1,800 Python)
- PGbasicmacros.pl port (3,200 lines → 2,200 Python)
- PGML.pl parser (2,100 lines → 1,500 Python)
- PGauxiliaryFunctions.pl (1,800 lines → 1,200 Python)
- Graph and UI macros (basic support)

**Phases**:
1. Macro loading infrastructure (Week 1-2)
2. Core macro ports (Week 3-6)
3. Auxiliary macros (Week 7-8)
4. Specialized macros (Week 9-10)
5. Graph/UI macros (Week 11-12)

**Deliverables**:
- ✅ Macro loader with caching
- ✅ Core PG functions (TEXT, ANS, loadMacros)
- ✅ PGML parser with 80%+ syntax coverage
- ✅ 500+ problems render correctly (80% OPL coverage)

---

### 2. [Translator Features Implementation](02_TRANSLATOR_FEATURES_IMPLEMENTATION.md)
**Effort**: 2-3 weeks (1 dev)
**Priority**: CRITICAL
**Gap**: ~1,109 LOC

**Key Components**:
- Macro loading system (unrestricted_load, PG_macro_file_eval)
- Error handling (PG_errorMessage with stack traces)
- Answer processing (checkbox/radio button support)
- Problem grading (std_grader, avg_grader with partial credit)
- Post-processing hooks (content modification)

**Phases**:
1. Macro loading infrastructure (Week 1, Days 1-3)
2. Error handling system (Week 1, Days 4-5)
3. Answer processing enhancements (Week 2, Days 1-3)
4. Problem grading system (Week 2, Days 4-5)
5. Post-processing hooks (Week 3, Days 1-3)

**Deliverables**:
- ✅ Macro loading for .py macros
- ✅ Formatted error messages with file names
- ✅ Checkbox/radio button processing
- ✅ Grader plugin system
- ✅ Post-processing hooks for content modification

---

### 3. [Formula Enhancements Implementation](03_FORMULA_ENHANCEMENTS_IMPLEMENTATION.md)
**Effort**: 2 weeks (1 dev)
**Priority**: HIGH
**Gap**: ~456 LOC

**Key Components**:
- Advanced test point generation with granularity
- Adaptive parameter system (C*f(x) → student answer)
- Test value caching and optimization
- Domain checking with undefined points
- Enhanced differentiation with chain rule
- Python function generation with caching

**Phases**:
1. Test point system enhancements (Week 1, Days 1-2)
2. Adaptive parameters (Week 1, Days 3-5)
3. Domain checking (Week 2, Days 1-2)
4. Differentiation enhancements (Week 2, Days 3-4)
5. Python function generation (Week 2, Day 5)

**Deliverables**:
- ✅ Random point generation with distribution control
- ✅ Adaptive parameter solving (linear and multi-parameter)
- ✅ Undefined point tracking (UNDEF sentinel)
- ✅ Enhanced derivative calculation
- ✅ Fast Python function generation with SymPy lambdify

---

### 4. [Answer System Implementation](04_ANSWER_SYSTEM_IMPLEMENTATION.md)
**Effort**: 2-3 weeks (1 dev)
**Priority**: HIGH
**Gap**: ~850 LOC

**Key Components**:
- Answer filter chain architecture (pre/post filters)
- Value::cmp() for all MathValue types
- MultiAnswer coordination system
- Enhanced evaluators (units, fractions)
- Standard filter library

**Phases**:
1. Answer filter architecture (Week 1, Days 1-3)
2. Value::cmp() for all types (Week 1, Days 4-5 + Week 2, Days 1-2)
3. MultiAnswer system (Week 2, Days 3-5)
4. Enhanced evaluators (Week 3, Days 1-3)

**Deliverables**:
- ✅ Filter chain with pre/post processing
- ✅ cmp() method on all MathValue types
- ✅ MultiAnswer for coordinated answer blanks
- ✅ Units and fraction support
- ✅ Standard filter library (case, whitespace, units, etc.)

---

## TIMELINE SUMMARY

### Sequential Execution (1 Developer)
| Plan | Duration | Dependencies |
|------|----------|--------------|
| Translator Features | 2-3 weeks | None (can start immediately) |
| Formula Enhancements | 2 weeks | None (parallel with Translator) |
| Answer System | 2-3 weeks | Formula enhancements |
| Macro System | 8-12 weeks | Translator features |
| **TOTAL** | **14-20 weeks** | 3.5-5 months |

### Parallel Execution (3 Developers)
- **Developer 1**: Macro System (12 weeks)
- **Developer 2**: Translator Features (3 weeks) → Answer System (3 weeks) → Support Macros (6 weeks)
- **Developer 3**: Formula Enhancements (2 weeks) → Testing/Integration (10 weeks)
- **TOTAL**: **12 weeks** (3 months)

---

## CRITICAL PATH

The **Macro System** is on the critical path due to its size (13,500 LOC). Other systems can be developed in parallel:

```
Week 1-3:  Translator Features + Formula Enhancements (parallel)
Week 4-6:  Answer System + Macro Loading (parallel)
Week 7-12: Macro Ports (PG, PGbasic, PGML, etc.)
```

---

## DEPENDENCIES

```
Macro System
  ├─ Requires: Translator macro loading
  └─ Blocks: Most problem rendering

Translator Features
  ├─ Requires: None
  └─ Enables: Macro loading, error handling

Formula Enhancements
  ├─ Requires: None
  └─ Enables: Accurate answer checking

Answer System
  ├─ Requires: Formula (for adaptive params)
  └─ Enables: Sophisticated answer checking
```

---

## SUCCESS METRICS

### Phase 1 Success (Week 6)
- ✅ Translator features complete
- ✅ Formula enhancements working
- ✅ Answer system functional
- ✅ 50+ basic problems render

### Phase 2 Success (Week 12)
- ✅ Core macros ported (PG, PGbasic, PGML)
- ✅ 200+ problems render
- ✅ PGML syntax 80%+ supported

### Phase 3 Success (Week 20)
- ✅ All 4 plans complete
- ✅ 500+ problems render (80% OPL coverage)
- ✅ Full test suite passing
- ✅ Performance targets met:
  - Macro loading: <100ms/file
  - Problem render: <500ms average
  - Test coverage: >90%

---

## RISK MITIGATION

### Risk 1: Perl→Python Translation Complexity
**Mitigation**:
- Start with Python versions of critical macros
- Create Perl bridge for complex legacy code
- Use AST tools to semi-automate translation

### Risk 2: Macro Interdependencies
**Mitigation**:
- Map full dependency graph before starting
- Load macros in topological order
- Comprehensive integration testing

### Risk 3: Performance Degradation
**Mitigation**:
- Profile early and often
- Cache aggressively (functions, test points, macros)
- Benchmark against Perl for critical paths

### Risk 4: Feature Scope Creep
**Mitigation**:
- Stick to 1:1 parity goal
- Defer enhancements to post-parity phase
- Regular stakeholder check-ins

---

## RESOURCE REQUIREMENTS

### Development Team
- **Minimum**: 1 senior developer (20 weeks)
- **Recommended**: 3 developers (12 weeks)
  - 1 on macros (full-time)
  - 1 on translator/answer (part-time → macros)
  - 1 on formula/testing (part-time → integration)

### Infrastructure
- Python 3.12+
- SymPy for formula operations
- lxml for DOM manipulation
- pytest for testing
- CI/CD pipeline for continuous testing

---

## NEXT STEPS

1. **Immediate** (Week 1):
   - Start Translator Features (Days 1-3: Macro loading)
   - Start Formula Enhancements (Days 1-2: Test points)
   - Set up project tracking (sprints, milestones)

2. **Short-term** (Weeks 2-6):
   - Complete Translator and Formula plans
   - Begin Answer System
   - Start PG.pl port

3. **Medium-term** (Weeks 7-12):
   - Complete Answer System
   - Finish core macro ports
   - Achieve 200+ problem rendering

4. **Long-term** (Weeks 13-20):
   - Complete specialized macros
   - Achieve 500+ problem rendering
   - Full test suite parity

---

## CONTACT & QUESTIONS

For questions about these plans:
- See comprehensive review: `../REVIEW_20251004.md`
- Check implementation files: `01_*.md` through `04_*.md`
- Review progress tracking: (TBD - project board)

---

**Generated**: 2025-10-04
**Status**: Ready for implementation
**Version**: 1.0
