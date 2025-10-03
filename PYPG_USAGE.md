# pypg - PG Problem Testing Tool

A command-line tool for testing WeBWorK PG problems with student answers.

## Installation

No installation needed! Just run `pypg.py` or use the `pypg.bat` wrapper on Windows.

## Usage

### Basic Syntax

```bash
python pypg.py <problem_file.pg> [answer1] [answer2] ... [options]
```

On Windows, you can use:
```cmd
pypg problem_file.pg answer1 answer2 ...
```

### Examples

#### 1. Render a problem without checking answers
```bash
python pypg.py tutorial/sample-problems/Algebra/ExpandedPolynomial.pg --render-only
```

#### 2. Test with a single answer
```bash
python pypg.py tutorial/sample-problems/Algebra/ExpandedPolynomial.pg "x^2-6x+4"
```

#### 3. Test with multiple answers (in order of appearance)
```bash
python pypg.py tutorial/sample-problems/Algebra/DomainRange.pg "x>=1" "y>=0" "[1,inf)" "[0,inf)"
```

#### 4. Use a different random seed
```bash
python pypg.py tutorial/sample-problems/Algebra/SimpleFactoring.pg "x-2,x-3" "2,3" --seed 456
```

#### 5. Show the solution after checking
```bash
python pypg.py tutorial/sample-problems/Algebra/ExpandedPolynomial.pg "x^2-6x+4" --show-solution
```

## Options

| Option | Description |
|--------|-------------|
| `--seed SEED` | Set random seed for problem generation (default: random) |
| `--show-solution` | Display the solution after checking answers |
| `--render-only` | Only render the problem, don't check answers |
| `-h, --help` | Show help message |

## Answer Format Guidelines

### Numbers
```bash
"3.14"
"42"
"-7.5"
```

### Formulas/Expressions
Use quotes to protect special characters:
```bash
"x^2+3x-4"
"2*sin(x)"
"(x+1)(x-2)"
```

### Intervals
```bash
"[0,5]"        # Closed interval
"(0,5)"        # Open interval
"[0,inf)"      # Half-open to infinity
"(-inf,inf)"   # All real numbers
```

### Inequalities
```bash
"x >= 3"
"x < -5"
"y <= 10"
```

### Points and Vectors
```bash
"(3,4)"           # Point
"<1,2,3>"         # Vector
"(0,0), (1,1)"    # Multiple points (list)
```

### Lists
Use commas to separate items:
```bash
"1,2,3"           # List of numbers
"x-1,x+1"         # List of expressions
```

## Output Format

### Successful Answer Check
```
================================================================================
Problem: ExpandedPolynomial.pg
Path: tutorial\sample-problems\Algebra\ExpandedPolynomial.pg
Seed: 123
================================================================================

[RENDERING]
[OK] Problem rendered successfully

[PROBLEM STATEMENT]
--------------------------------------------------------------------------------
The quadratic expression $(x-3)^2-5$ is written in vertex form.
Write the expression in expanded form $ax^2 + bx + c$.

[____]
--------------------------------------------------------------------------------

[EXPECTED ANSWERS]
  1. AnSwEr0001
     Correct: x^2 + -6 x + 4
     Type: formula

[CHECKING ANSWERS]

[ANSWER CHECK RESULTS]
--------------------------------------------------------------------------------

1. AnSwEr0001 [OK]
   Student: x^2-6x+4
   Correct: x^2 + -6 x + 4
   Type: formula
   Message: Correct!
--------------------------------------------------------------------------------

Score: 4/4

*** ALL ANSWERS CORRECT! ***
```

### Failed Answer Check
```
[ANSWER CHECK RESULTS]
--------------------------------------------------------------------------------

1. AnSwEr0001 [FAIL]
   Student: x^2+5x+1
   Correct: x^2 + -6 x + 4
   Type: formula
   Message: Your answer is not equivalent to the correct answer.
--------------------------------------------------------------------------------

Score: 0/1

*** 1 INCORRECT ***
```

## Exit Codes

- `0`: All answers correct
- `1`: One or more answers incorrect OR error occurred

This makes `pypg` useful in automated testing scripts!

## Tips

### 1. Test Multiple Seeds
Problems are randomized based on seed. Test with different seeds:
```bash
for seed in 1 2 3 4 5; do
    echo "Testing seed $seed"
    python pypg.py problem.pg "answer" --seed $seed
done
```

### 2. Use in CI/CD
Since `pypg` returns proper exit codes, you can use it in automated tests:
```bash
python pypg.py problem.pg "correct_answer" || echo "Test failed!"
```

### 3. Quick Problem Preview
Use `--render-only` to quickly see what a problem looks like:
```bash
python pypg.py problem.pg --render-only
```

### 4. Verify Answer Format
If you're unsure what format to use, render first to see the expected format:
```bash
python pypg.py problem.pg --render-only
# Shows: "Correct: x^2 + -6 x + 4"
# Then test with: python pypg.py problem.pg "x^2-6x+4"
```

## Troubleshooting

### Problem: "Cannot find file"
Make sure the path to the .pg file is correct relative to your current directory.

### Problem: "Failed to render"
The problem might have syntax errors or use unsupported features. Check the error message.

### Problem: Answers always marked wrong
Make sure you're using the correct format. Use `--render-only` first to see the expected answer format.

### Problem: Wrong number of answers
The tool will warn you if you provide more or fewer answers than the problem expects.

## Development

This tool uses the Python PG renderer stack:
- `pg_renderer`: Problem rendering
- `pg_answer`: Answer checking
- `pg_pgml`: PGML parsing
- `pg_math`: Mathematical objects

## Examples by Topic

### Algebra
```bash
# Polynomials
python pypg.py tutorial/sample-problems/Algebra/ExpandedPolynomial.pg "x^2-6x+4"
python pypg.py tutorial/sample-problems/Algebra/FactoredPolynomial.pg "4(2x+1)(x+3)"

# Inequalities
python pypg.py tutorial/sample-problems/Algebra/InequalityAnswer.pg "x>=-10/3"

# Domain/Range
python pypg.py tutorial/sample-problems/Algebra/DomainRange.pg "x>=1" "y>=0" "[1,inf)" "[0,inf)"

# Points
python pypg.py tutorial/sample-problems/Algebra/PointAnswers.pg "(1,0),(-1,0)" "(0,-1)"
```

### Calculus (when available)
```bash
python pypg.py problems/Calculus/derivatives.pg "2x"
python pypg.py problems/Calculus/integrals.pg "x^2/2 + C"
```

## See Also

- `ALGEBRA_TEST_RESULTS.md` - Test results for Algebra sample problems
- `BACKEND_STATUS.md` - Status of the Python PG port
- `packages/pg_renderer/` - Core rendering engine

---

**Author**: PG Python Port Team  
**Date**: October 3, 2025  
**Version**: 1.0

