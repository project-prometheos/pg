# Quick Start Guide - Using the Macro System

This guide shows how to use the newly implemented Python PG macro system.

## Installation

The macro system is already installed in `packages/pg_macros`. No additional setup needed.

## Basic Usage

### 1. Import the Macros

```python
import sys
sys.path.insert(0, 'packages/pg_macros')

from pg_macros.core import pg_core, pg_basic_macros
```

### 2. Create a Problem Environment

```python
# Set up environment (normally done by translator)
envir = {
    "problemSeed": 123,
    "displayMode": "HTML",  # or "TeX" or "PTX"
    "showPartialCorrectAnswers": 1,
}

env = pg_core.PGEnvironment(envir)
pg_core.set_environment(env)
```

### 3. Write Problem Code

```python
# Problem text
pg_core.TEXT("What is 2 + 2?")
pg_core.TEXT(pg_basic_macros.BR())
pg_core.TEXT("Answer: ")
pg_core.TEXT(pg_basic_macros.ans_rule(10))

# Register answer evaluator
evaluator = {"type": "numeric", "correct": 4}
pg_core.ANS(evaluator)

# Optional: Add solution/hint
pg_core.SOLUTION("Add 2 and 2 to get 4.")
pg_core.HINT("Try adding the numbers.")
```

### 4. Get Results

```python
# Finalize problem
text, header, post_header, answers, flags = pg_core.ENDDOCUMENT()

print("Problem HTML:")
print(text)

print("\nAnswers:")
for name, answer in answers.items():
    print(f"  {name}: {answer}")

print("\nFlags:")
print(f"  Solution exists: {flags['solutionExists']}")
print(f"  Hint exists: {flags['hintExists']}")
```

## Complete Examples

### Example 1: Simple Problem

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'packages/pg_macros')

from pg_macros.core import pg_core, pg_basic_macros

# Setup
envir = {"problemSeed": 123, "displayMode": "HTML"}
env = pg_core.PGEnvironment(envir)
pg_core.set_environment(env)

# Problem
pg_core.TEXT("Compute 5 + 7:")
pg_core.TEXT(pg_basic_macros.BR())
pg_core.TEXT(pg_basic_macros.ans_rule(20))

pg_core.ANS({"type": "numeric", "correct": 12})

# Get result
text, _, _, answers, _ = pg_core.ENDDOCUMENT()
print(text)
```

### Example 2: Multi-Answer Problem

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'packages/pg_macros')

from pg_macros.core import pg_core, pg_basic_macros

# Setup
envir = {"problemSeed": 456, "displayMode": "HTML"}
env = pg_core.PGEnvironment(envir)
pg_core.set_environment(env)

# Problem
pg_core.TEXT("Fill in the answers:")
pg_core.TEXT(pg_basic_macros.PAR())

pg_core.TEXT("1. 3 × 4 = ")
pg_core.TEXT(pg_basic_macros.ans_rule(10))
pg_core.TEXT(pg_basic_macros.BR())

pg_core.TEXT("2. 15 ÷ 3 = ")
pg_core.TEXT(pg_basic_macros.ans_rule(10))
pg_core.TEXT(pg_basic_macros.BR())

pg_core.TEXT("3. Is 7 > 5? ")
pg_core.TEXT(pg_basic_macros.ans_radio_buttons("Yes", "No"))

# Register evaluators
pg_core.ANS(
    {"type": "numeric", "correct": 12},
    {"type": "numeric", "correct": 5},
    {"type": "string", "correct": "Yes"}
)

# Get result
text, _, _, answers, _ = pg_core.ENDDOCUMENT()
print(text)
print(f"\n{len(answers)} answers registered")
```

### Example 3: Named Answers

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'packages/pg_macros')

from pg_macros.core import pg_core, pg_basic_macros

# Setup
envir = {"problemSeed": 789, "displayMode": "HTML"}
env = pg_core.PGEnvironment(envir)
pg_core.set_environment(env)

# Problem with named answers
pg_core.TEXT("Enter your answers below:")
pg_core.TEXT(pg_basic_macros.PAR())

pg_core.TEXT("Part (a): ")
pg_core.TEXT(pg_basic_macros.NAMED_ANS_RULE("partA", 15))
pg_core.TEXT(pg_basic_macros.BR())

pg_core.TEXT("Part (b): ")
pg_core.TEXT(pg_basic_macros.NAMED_ANS_RULE("partB", 15))

# Register named evaluators
pg_core.NAMED_ANS("partA", {"type": "numeric", "correct": 42})
pg_core.NAMED_ANS("partB", {"type": "string", "correct": "hello"})

# Get result
text, _, _, answers, _ = pg_core.ENDDOCUMENT()
print(text)
```

### Example 4: Dropdown and Radio Buttons

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'packages/pg_macros')

from pg_macros.core import pg_core, pg_basic_macros

# Setup
envir = {"problemSeed": 111, "displayMode": "HTML"}
env = pg_core.PGEnvironment(envir)
pg_core.set_environment(env)

# Problem
pg_core.TEXT("Select the correct answer:")
pg_core.TEXT(pg_basic_macros.PAR())

pg_core.TEXT("Question 1: What color is the sky?")
pg_core.TEXT(pg_basic_macros.BR())
pg_core.TEXT(pg_basic_macros.pop_up_list(["?", "Blue", "Green", "Red"]))
pg_core.TEXT(pg_basic_macros.PAR())

pg_core.TEXT("Question 2: Is 2+2=4?")
pg_core.TEXT(pg_basic_macros.BR())
pg_core.TEXT(pg_basic_macros.ans_radio_buttons("True", "False"))

# Register evaluators
pg_core.ANS(
    {"type": "string", "correct": "Blue"},
    {"type": "string", "correct": "True"}
)

# Get result
text, _, _, answers, _ = pg_core.ENDDOCUMENT()
print(text)
```

## Display Modes

The macro system supports three output modes:

### HTML Mode (Default)
```python
env.display_mode = "HTML"
# Produces: <p>, <br/>, <strong>, <input>, etc.
```

### TeX Mode (LaTeX)
```python
env.display_mode = "TeX"
# Produces: \par, \\, \textbf{}, \underline{}, etc.
```

### PTX Mode (PreTeXt)
```python
env.display_mode = "PTX"
# Produces: <p>, <br/>, <strong>, <var>, etc.
```

## Available Functions

### Core Functions (from pg_core)
- `DOCUMENT()`, `ENDDOCUMENT()`
- `TEXT(*args)`, `HEADER_TEXT(*args)`
- `ANS(*evaluators)`, `NAMED_ANS(name, evaluator)`
- `NEW_ANS_NAME()`, `RECORD_ANS_NAME(name)`
- `SOLUTION(*args)`, `HINT(*args)`, `COMMENT(*args)`
- `random(low, high, step)`, `non_zero_random()`
- `list_random(*items)`
- `persistent_data(label, value)`
- `install_problem_grader(grader)`
- `not_null(value)`, `DEBUG_MESSAGE()`, `WARN_MESSAGE()`

### Basic Macros (from pg_basic_macros)
- `ans_rule(width)`, `ans_box(rows, cols)`
- `ans_radio_buttons(*options)`
- `pop_up_list(*options)`
- `NAMED_ANS_RULE(name, width)`
- `NAMED_ANS_BOX(name, rows, cols)`
- `PAR()`, `BR()`, `BRBR()`
- `BBOLD()`, `EBOLD()`, `BITALIC()`, `EITALIC()`
- `BUL()`, `EUL()`, `BCENTER()`, `ECENTER()`
- `HR()`, `NBSP()`, `LQ()`, `RQ()`
- `MODES(HTML=..., TeX=..., PTX=...)`
- `image(filename, **options)`
- `PI()`, `E()`

## Running Tests

```bash
# Run individual test suites
cd /home/runner/work/pg/pg

# Core functions
PYTHONPATH=packages/pg_macros python3 tests/macro_system/test_pg_core.py

# Basic macros
PYTHONPATH=packages/pg_macros python3 tests/macro_system/test_pg_basic_macros.py

# Complete problems
PYTHONPATH=packages/pg_macros python3 tests/macro_system/test_pg_problem_complete.py
```

## Next Steps

After mastering the basics:

1. **Study the test files** in `tests/macro_system/` for more examples
2. **Read the implementation** in `packages/pg_macros/pg_macros/core/`
3. **Integrate with translator** when ready for full problem rendering
4. **Implement answer evaluators** for real answer checking

## Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'pg_macros'
```
**Solution:** Set PYTHONPATH or add to sys.path:
```python
import sys
sys.path.insert(0, 'packages/pg_macros')
```

### Environment Not Initialized
```
RuntimeError: PG environment not initialized
```
**Solution:** Create and set environment before calling macros:
```python
env = pg_core.PGEnvironment(envir)
pg_core.set_environment(env)
```

### Answer Name Mismatch
**Issue:** Answer blank and evaluator don't match
**Solution:** Make sure to call ANS() after creating all answer blanks, and in the same order.

## Support

For questions or issues:
1. Check the test files in `tests/macro_system/`
2. Review `MACRO_SYSTEM_WEEK1_COMPLETE.md` for architecture details
3. See the original Perl files in `macros/` for reference
