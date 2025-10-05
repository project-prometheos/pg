# PG Problem Solver CLI Tool

## Overview

`pg_solve.py` is a command-line tool for interactively solving WeBWorK PG problems. It displays problem statements with readable math formatting (using Unicode symbols like π, θ, √, etc.) and allows you to input answers for checking.

## Installation

No installation needed - just run the Python script directly:

```bash
python pg_solve.py <problem_file> [options]
```

## Usage

### Basic Usage

Solve a problem interactively:

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob01.pg
```

This will:
1. Display the problem statement with formatted math
2. Prompt you to enter answers for each blank
3. Check your answers and display results

### Command-Line Options

#### `--seed SEED`
Specify a random seed for problem randomization:

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob01.pg --seed 1234
```

This is useful for:
- Getting the same problem variant consistently
- Testing specific problem instances
- Comparing results with others

#### `--solution`
Show the problem solution (if available):

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob01.pg --solution
```

Note: Solutions are only shown if the problem file includes a SOLUTION section.

#### `--hint`
Show problem hints (if available):

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob01.pg --hint
```

Note: Hints are only shown if the problem file includes a HINT section.

#### `--no-check`
Display the problem without prompting for answers:

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob01.pg --no-check
```

This is useful for:
- Previewing problem statements
- Batch viewing multiple problems
- Testing rendering without interaction

### Combining Options

You can combine multiple options:

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob01.pg --seed 5678 --solution --hint
```

## Math Formatting

The tool converts LaTeX math notation to readable terminal output using Unicode symbols and mathematical notation:

### Input (LaTeX)

```latex
\(\tan\!\left(\frac{23\pi}{6}\right)\)
```

### Output (Terminal)

```text
[ tan((23π)/(6)) ]
```

### Supported Conversions

#### Fractions
- `\frac{a}{b}` → `(a)/(b)`
- Nested fractions are fully supported

#### Greek Letters
- `\pi` → π
- `\theta` → θ
- `\alpha` → α, `\beta` → β, `\gamma` → γ, `\delta` → δ

#### Functions
- `\sin` → sin, `\cos` → cos, `\tan` → tan
- `\sqrt` → √

#### Operators
- `\cdot` → ·
- `\times` → ×
- `\div` → ÷
- `\pm` → ±

#### Relations
- `\leq` → ≤
- `\geq` → ≥
- `\neq` → ≠
- `\approx` → ≈

#### Special
- `\infty` → ∞

## Examples

### Example 1: Basic Problem Solving

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob01.pg
```

Output:
```
======================================================================
  PG PROBLEM SOLVER
======================================================================

Problem: ps1-prob01.pg
Seed: 45036

======================================================================
  PROBLEM
======================================================================

**Problem 1.** Beräkna [ tan(π/8) ]. Svaret får innehålla rötter
men inte trigonometriska funktioner.

This problem has 1 answer blank(s).

======================================================================
  ENTER YOUR ANSWERS
======================================================================

Answer 1: sqrt(2)-1

✅ All answers are correct!
```

### Example 2: Previewing with Specific Seed

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob05.pg --seed 1234 --no-check
```

Output:
```
======================================================================
  PG PROBLEM SOLVER
======================================================================

Problem: ps1-prob05.pg
Seed: 1234

======================================================================
  PROBLEM
======================================================================

**Problem 5.** Beräkna [ tan(π/8) ]. Svaret får innehålla rötter
men inte trigonometriska funktioner.

This problem has 1 answer blank(s).
```

### Example 3: Viewing with Solution and Hints

```bash
python pg_solve.py webwork_ps1_pg/ps1-prob01.pg --solution --hint
```

## Answer Checking

The tool integrates with the PG problem rendering backend to check answers:

- **Correct answers**: Shown with ✅
- **Incorrect answers**: Shown with ❌ (with error message if available)
- **Syntax errors**: Reported with helpful messages

## Implementation Details

### Backend Integration

The tool uses the FastAPI backend (`http://localhost:8000`) to:
1. Render problem statements
2. Check answer correctness
3. Extract hints and solutions

### Error Handling

- If the backend is not running, answer checking is disabled
- Rendering errors are reported with diagnostic information
- Invalid answer formats are caught and reported

## Technical Architecture

### Key Functions

1. **`strip_html(html_text)`**
   - Removes HTML tags
   - Unescapes LaTeX delimiters
   - Preserves problem structure

2. **`format_math(text)`**
   - Converts LaTeX to Unicode
   - Handles inline math `\(...\)` and `$...$`
   - Handles display math `\[...\]` and `$$...$$`

3. **`display_problem(problem_data, show_solution, show_hint)`**
   - Formats problem statement
   - Shows hints and solutions if requested
   - Lists answer blanks

4. **`get_user_answers(num_answers)`**
   - Interactive prompts for each answer
   - Ctrl+C to cancel

5. **`check_answers(problem_file, seed, answers)`**
   - Submits answers to backend
   - Displays results with formatting

## Future Enhancements

Potential improvements:
- [ ] Batch mode for multiple problems
- [ ] Save/load answer history
- [ ] Answer hints based on common mistakes
- [ ] Export results to CSV
- [ ] Support for multi-part problems with dependencies
- [ ] Graphical visualization of problem data

## See Also

- `PYPG_QUICK_START.md` - Guide to the Python PG system
- `README.md` - Main project documentation
- `apps/backend/README.md` - Backend API documentation
