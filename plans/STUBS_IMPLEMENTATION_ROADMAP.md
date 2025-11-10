# Stub Functions Implementation Roadmap

This document outlines all stub functions and classes that have been migrated to proper macro modules but still need complete implementations. These are organized by category and priority.

## Overview

- **Total Stubs Identified**: 80+
- **Status**: Migrated to modules with basic placeholder implementations
- **Current State**: Functional for basic use cases, need enhanced functionality
- **Next Phase**: Implementation of full Perl-equivalent behavior

---

## Priority 1: Critical Answer Checking (HIGH PRIORITY)

### 1. MultiAnswer (`pg_macros/answers/multi_answer.py`)

**Current**: Basic stub with default checking logic
**Needs**: 
- Enhanced custom checker support
- Proper score aggregation across multiple answers
- Support for dependent answer validation
- Better error handling and messaging

**Usage Example**:
```perl
$ma = MultiAnswer($ans1, $ans2, $ans3)->with_params(
    singleResult => 1,
    checker => sub {
        my ($correct, $student, $self) = @_;
        # Validate relationships between answers
    }
);
```

**Implementation Tasks**:
- [ ] Implement full `singleResult` parameter support
- [ ] Add support for `allowBlankAnswers` parameter
- [ ] Implement answer value access patterns
- [ ] Add custom score mixing strategies
- [ ] Support for partial credit across answer groups

---

## Priority 2: Parser Classes (HIGH PRIORITY)

### 2. LinearRelation (`pg_macros/parsers/parser_linear_relation.py`)

**Current**: Stub with `cmp()` and `reduce()` methods
**Needs**:
- Parse linear relationship strings (e.g., "2x + 3y = 5")
- Validate student answers match correct linear form
- Handle coefficient variations and simplification

**Implementation Tasks**:
- [ ] Parse linear expression strings
- [ ] Normalize coefficients and terms
- [ ] Compare linear forms (including equivalent forms)
- [ ] Generate appropriate error messages
- [ ] Support for systems of linear equations

### 3. DifferenceQuotient (`pg_macros/parsers/parser_difference_quotient.py`)

**Current**: Stub with formula storage
**Needs**:
- Validate difference quotient expressions
- Check for correct step size (h or delta)
- Evaluate at specified points
- Compare multiple forms of the same expression

**Implementation Tasks**:
- [ ] Parse difference quotient format
- [ ] Validate step parameter handling
- [ ] Compare algebraic equivalence
- [ ] Support for various notations (h, Δx, dx, etc.)
- [ ] Generate pedagogical feedback

### 4. PopUp/DropDown (`pg_macros/parsers/parser_popup.py`)

**Current**: Stub classes with basic structure
**Needs**:
- Generate HTML for select elements
- Store display labels vs values
- Handle multiple selections

**Implementation Tasks**:
- [ ] Generate proper HTML select/option elements
- [ ] Support for optgroup organization
- [ ] CSS styling integration
- [ ] Accessibility attributes (ARIA labels, etc.)
- [ ] Support for keyboard navigation hints

### 5. RadioButtons (`pg_macros/parsers/parser_popup.py`)

**Current**: Stub class with basic structure
**Needs**:
- Generate HTML radio button groups
- Handle exclusive selection
- Group radio buttons logically

**Implementation Tasks**:
- [ ] Generate proper HTML radio input elements
- [ ] Group labels and inputs correctly
- [ ] Support for custom CSS classes
- [ ] Accessibility improvements (ARIA roles)
- [ ] Support for horizontal/vertical layouts

### 6. RadioMultiAnswer (`pg_macros/parsers/parser_radio_multianswer.py`)

**Current**: Stub class for multiple radio groups
**Needs**:
- Manage multiple radio button groups
- Validate combinations across groups
- Store and check relationships

**Implementation Tasks**:
- [ ] Track multiple independent radio groups
- [ ] Support cross-group validation logic
- [ ] Generate coordinated HTML
- [ ] Handle group naming and labeling
- [ ] Implement custom scoring across groups

---

## Priority 3: Special Math Parsers

### 7. specialRadical (`pg_macros/parsers/parser_special_trig.py`)

**Current**: Delegates to Compute, needs special handling
**Needs**:
- Parse radical expressions in simplified form
- Validate for proper radical simplification
- Compare radicals that differ only in form

**Implementation Tasks**:
- [ ] Parse √ expressions
- [ ] Validate simplification rules
- [ ] Compare equivalent radical forms
- [ ] Handle nested radicals
- [ ] Support for rationalization

### 8. specialAngle (`pg_macros/parsers/parser_special_trig.py`)

**Current**: Delegates to Compute, needs angle-specific handling
**Needs**:
- Parse angles (degrees, radians, fractions of π)
- Validate coterminal angles
- Compare angle equivalence

**Implementation Tasks**:
- [ ] Parse angle notation (rad, deg, π multiples)
- [ ] Normalize angle representations
- [ ] Check coterminal equivalence
- [ ] Support for angle ranges
- [ ] Handle unit conversions

---

## Priority 4: Statistics Functions

### 9. stats_mean, stats_sd, stats_SX_SXX (`pg_macros/math/statistics_utils.py`)

**Current**: Basic statistical calculations
**Needs**:
- Verify calculations against Perl implementations
- Add more statistical functions
- Handle edge cases and weighted data

**Implementation Tasks**:
- [ ] Verify mean calculation accuracy
- [ ] Verify SD calculation (sample vs population)
- [ ] Add `stats_median()` function
- [ ] Add `stats_quartiles()` function
- [ ] Add support for weighted statistics
- [ ] Add confidence interval calculations

### 10. linear_regression (`pg_macros/math/statistics_utils.py`)

**Current**: Stub returning (1, 0)
**Needs**:
- Implement proper least-squares regression
- Calculate R² and correlation
- Generate regression diagnostics

**Implementation Tasks**:
- [ ] Implement least-squares algorithm
- [ ] Calculate slope and intercept accurately
- [ ] Compute R-squared value
- [ ] Calculate correlation coefficient
- [ ] Add residual analysis
- [ ] Support for weighted regression

---

## Priority 5: Fallback Utilities

### 11. random_subset (`pg_macros/core/fallback_utilities.py`)

**Current**: Returns first N items from list
**Needs**:
- True random subset selection
- Weighted random selection
- Proper shuffling

**Implementation Tasks**:
- [ ] Implement Fisher-Yates shuffle for true randomness
- [ ] Add weighted selection support
- [ ] Support for selection without replacement
- [ ] Performance optimization for large sets

### 12. new_match_list (`pg_macros/core/fallback_utilities.py`)

**Current**: Returns stub object
**Needs**:
- Create proper matching problem infrastructure
- Support question/answer pairing
- Generate HTML for matching interface

**Implementation Tasks**:
- [ ] Implement matching list structure
- [ ] Add question and answer storage
- [ ] Generate HTML matching interface
- [ ] Add scoring logic for matches
- [ ] Support for drag-and-drop matching

### 13. splice (`pg_macros/core/array_utilities.py`)

**Current**: Basic array manipulation
**Needs**:
- Verify full Perl splice behavior
- Handle all edge cases
- Optimize for large arrays

**Implementation Tasks**:
- [ ] Verify matches Perl splice() exactly
- [ ] Test edge cases (negative indices, etc.)
- [ ] Add performance optimizations
- [ ] Support for list context return values

---

## Priority 6: Graphics Functions

### 14. Graph3D (`pg_macros/graph/live_graphics_3d.py`)

**Current**: Stub 3D graph class
**Needs**:
- Full 3D rendering capability
- Surface plotting
- Parameter editing

**Implementation Tasks**:
- [ ] Implement 3D coordinate system
- [ ] Add surface plotting algorithms
- [ ] Support multiple surface representations
- [ ] Add color mapping for values
- [ ] Implement rotation/zoom functionality
- [ ] Export to common 3D formats

### 15. VectorField3D (`pg_macros/graph/vector_field_3d.py`)

**Current**: Stub vector field class
**Needs**:
- Render 3D vector fields
- Scale vector representations
- Interactive exploration

**Implementation Tasks**:
- [ ] Parse vector field definitions
- [ ] Implement vector rendering at grid points
- [ ] Add vector scaling/normalization
- [ ] Support for color-coded magnitude
- [ ] Interactive parameter adjustment

---

## Priority 7: Interactive Elements

### 16. DraggableProof (`pg_macros/math/draggable_proof.py`)

**Current**: Basic stub implementation
**Needs**:
- Generate drag-and-drop proof interface
- Validate step ordering
- Track proof progression

**Implementation Tasks**:
- [ ] Implement drag target zones
- [ ] Add proof step validation
- [ ] Generate HTML/CSS for interface
- [ ] Add JavaScript drag handlers
- [ ] Implement hint system
- [ ] Track step attempts and feedback

### 17. DraggableSubsets (`pg_macros/math/draggable_subsets.py`)

**Current**: Stub implementation
**Needs**:
- Create draggable subset selection interface
- Validate subset answers
- Generate visual feedback

**Implementation Tasks**:
- [ ] Implement draggable item containers
- [ ] Add set membership validation
- [ ] Generate drop zones for subsets
- [ ] Add visual highlighting
- [ ] Implement undo/reset functionality

### 18. GraphTool (`pg_macros/graph/parser_graphtool.py`)

**Current**: Basic stub
**Needs**:
- Full interactive graphing interface
- Support for all graph element types
- Answer validation

**Implementation Tasks**:
- [ ] Implement drawing canvas
- [ ] Add tools for points, lines, curves
- [ ] Support for multiple objects
- [ ] Answer validation against correct graph
- [ ] Accessibility improvements
- [ ] Export/import graph definitions

---

## Priority 8: Core Utilities

### 19. tag (`pg_macros/core/pgml_utils.py`)

**Current**: Basic HTML tag generation
**Needs**:
- Comprehensive HTML tag support
- Attribute handling
- Self-closing tags

**Implementation Tasks**:
- [ ] Support all HTML tags
- [ ] Proper attribute escaping
- [ ] Self-closing tag handling
- [ ] CSS class support
- [ ] Data attribute support

### 20. helpLink (`pg_macros/core/pgml_utils.py`)

**Current**: Stub returning help link
**Needs**:
- Map topics to help documentation
- Generate proper links
- Support offline mode

**Implementation Tasks**:
- [ ] Create topic-to-URL mapping
- [ ] Support external documentation links
- [ ] Add embedded help content
- [ ] Implement search functionality
- [ ] Support for multiple documentation versions

### 21. LimitedPowers (`pg_macros/contexts/limited_powers.py`)

**Current**: Stub class with OnlyIntegers, OnlyPositiveIntegers
**Needs**:
- Restrict allowed polynomial powers
- Validate expressions
- Generate error messages

**Implementation Tasks**:
- [ ] Parse polynomial expressions
- [ ] Validate power constraints
- [ ] Generate helpful error messages
- [ ] Support for fractional/negative powers
- [ ] Integration with Context system

### 22. parserFunction (`pg_macros/parsers/parser_function.py`)

**Current**: Stub function
**Needs**:
- Define custom functions in context
- Parse function definitions
- Validate function answers

**Implementation Tasks**:
- [ ] Implement function definition parsing
- [ ] Add to Context object
- [ ] Support for multi-variable functions
- [ ] Domain restrictions
- [ ] Function composition support

### 23. install_problem_grader (`pg_macros/core/pg_graders.py`)

**Current**: Stub that does nothing
**Needs**:
- Register custom grading functions
- Handle grading workflow
- Compute scores

**Implementation Tasks**:
- [ ] Implement grader registration
- [ ] Hook into answer checking pipeline
- [ ] Support multiple answer evaluation
- [ ] Aggregate scores properly
- [ ] Generate feedback messages

### 24. custom_problem_grader_fluid (`pg_macros/core/pg_graders.py`)

**Current**: Returns stub grader function
**Needs**:
- Implement flexible grading logic
- Handle partial credit
- Support for custom scoring

**Implementation Tasks**:
- [ ] Implement flexible scoring rules
- [ ] Support weighted answers
- [ ] Add partial credit logic
- [ ] Generate score explanations
- [ ] Support for extra credit

---

## Priority 9: Parser Utilities

### 25. parser_Assignment (`pg_macros/parsers/parser_assignment.py`)

**Current**: Stub with Allow() method
**Needs**:
- Parse assignment expressions (e.g., "x = 5")
- Validate variable assignments
- Check for correct operations

**Implementation Tasks**:
- [ ] Parse assignment syntax
- [ ] Validate variable restrictions
- [ ] Compare assignment equivalence
- [ ] Support for multiple variables
- [ ] Handle functional equations

### 26. CheckboxList (`pg_macros/parsers/parser_checkbox_list.py`)

**Current**: Stub implementation
**Needs**:
- Generate checkbox group interface
- Validate selected combinations
- Score partial credit

**Implementation Tasks**:
- [ ] Generate HTML checkboxes
- [ ] Group labels with controls
- [ ] Add validation logic
- [ ] Support for "check all that apply" scoring
- [ ] Accessibility improvements

---

## Implementation Priority Matrix

| Priority | Functions | Est. Effort | Impact |
|----------|-----------|------------|--------|
| P1 - Critical | MultiAnswer, LinearRelation, DifferenceQuotient | High | Very High |
| P2 - High | PopUp, RadioButtons, RadioMultiAnswer | High | High |
| P3 - Medium | specialRadical, specialAngle | Medium | Medium |
| P4 - Medium | Statistics functions | Medium | High |
| P5 - Lower | Fallback utilities | Low | Low |
| P6 - Lower | 3D Graphics | High | Medium |
| P7 - Lower | Interactive elements | High | Medium |
| P8 - Medium | Core utilities | Medium | High |
| P9 - Lower | Parser utilities | Medium | Medium |

---

## Testing Requirements

Each implementation must include:

1. **Unit Tests**: Comprehensive test coverage for each function
2. **Integration Tests**: Tests with actual PG problems
3. **Edge Cases**: Boundary conditions and error handling
4. **Perl Equivalence**: Verification against original Perl implementations
5. **Performance Tests**: Ensure reasonable execution times

---

## Documentation Requirements

Each implementation must include:

1. **Docstrings**: Complete Python docstrings with examples
2. **Comments**: Inline comments for complex logic
3. **Perl Source References**: Links to original Perl implementations
4. **Usage Examples**: Real-world usage patterns
5. **Error Messages**: Helpful, pedagogical error messages

---

## Validation Checklist

Before marking as complete, each implementation should:

- [ ] Pass all unit tests
- [ ] Pass all integration tests
- [ ] Maintain backward compatibility
- [ ] Have zero regressions in integration suite
- [ ] Include proper documentation
- [ ] Have proper error handling
- [ ] Follow code style guidelines
- [ ] Have performance acceptable for interactive use

---

## Next Steps

1. **Phase 12**: Implement Priority 1 functions (MultiAnswer, LinearRelation, DifferenceQuotient)
2. **Phase 13**: Implement Priority 2 functions (PopUp, RadioButtons, etc.)
3. **Phase 14**: Implement Priority 3-4 functions (Math parsers, Statistics)
4. **Phase 15**: Implement Priority 5-9 functions (remaining utilities)
5. **Phase 16**: Performance optimization and final polish

**Total Estimated Effort**: 40-60 development days for full implementation

---

## Notes

- All implementations should preserve existing APIs (don't break backward compatibility)
- New features should be added alongside stubs, not replacing them
- Performance should be prioritized for interactive elements (Graphics, DraggableElements)
- Documentation should include Perl source code references for developers
- Consider creating adapter patterns for Perl ↔ Python differences

