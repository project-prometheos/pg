# PG Solve CLI Tool - Visual Demo

## Enhanced Math Formatting

The tool now displays mathematical expressions using proper fraction notation and Unicode symbols.

### Example 1: Trigonometric Expression with Fraction

**Original LaTeX:**
```latex
\tan\!\left(\frac{23\pi}{6}\right)
```

**CLI Output:**
```
tan((23π)/(6))
```

### Example 2: Nested Fraction

**Original LaTeX:**
```latex
\frac{\frac{a}{b}}{c}
```

**CLI Output:**
```
((a)/(b))/(c)
```

### Example 3: Square Root Expression

**Original LaTeX:**
```latex
\cos(x)=-1/\sqrt{3}
```

**CLI Output:**
```
cos(x)=-1/√3
```

### Example 4: Interval Notation

**Original LaTeX:**
```latex
\left[-\frac{\pi}{2},\frac{\pi}{2}\right]
```

**CLI Output:**
```
[-(π)/(2),(π)/(2)]
```

## Full Problem Examples

### Example 1: Trigonometry Problem

```
======================================================================
  PG PROBLEM SOLVER
======================================================================

Problem: ps1-prob01.pg
Seed: 1234

======================================================================
  PROBLEM
======================================================================

**Problem 1.** Beräkna [ tan((23π)/(6)) ]. Svaret får innehålla 
rötter men inte trigonometriska funktioner.

This problem has 1 answer blank(s).
```

### Example 2: Equation with Square Root

```
======================================================================
  PG PROBLEM SOLVER
======================================================================

Problem: ps1-prob06.pg
Seed: 85161

======================================================================
  PROBLEM
======================================================================

**Problem 6.** Hur många lösningar har [ cos(x)=-1/√3 ] i 
intervallet [ [-(π)/(2),(π)/(2)] ]?

This problem has 1 answer blank(s).
```

## Mathematical Notation Features

### Fractions
- Proper fraction format: `(numerator)/(denominator)`
- Nested fractions fully supported
- Parentheses for clarity

### Greek Letters
| LaTeX | Display |
|-------|---------|
| `\pi` | π |
| `\theta` | θ |
| `\alpha` | α |
| `\beta` | β |
| `\gamma` | γ |
| `\delta` | δ |

### Mathematical Symbols
| LaTeX | Display | Meaning |
|-------|---------|---------|
| `\sqrt` | √ | Square root |
| `\cdot` | · | Multiplication |
| `\times` | × | Times |
| `\div` | ÷ | Division |
| `\pm` | ± | Plus-minus |
| `\leq` | ≤ | Less than or equal |
| `\geq` | ≥ | Greater than or equal |
| `\neq` | ≠ | Not equal |
| `\approx` | ≈ | Approximately |
| `\infty` | ∞ | Infinity |

## Comparison: Before and After

### Before Enhancement
```
**Problem 1.** Beräkna [ tan(frac{23π}{6}) ].
```
- Fractions shown as LaTeX commands
- Less readable for quick comprehension

### After Enhancement
```
**Problem 1.** Beräkna [ tan((23π)/(6)) ].
```
- Fractions shown with proper notation
- More natural mathematical appearance
- Easier to read and understand

## Implementation Details

The formatting is achieved through a two-step process:

1. **LaTeX Parsing**: Regex-based extraction of mathematical expressions
2. **Symbol Conversion**: 
   - Fraction conversion: `\frac{a}{b}` → `(a)/(b)`
   - Unicode substitution for Greek letters and operators
   - Removal of LaTeX commands (e.g., `\left`, `\right`, `\!`)

### Fraction Handling
The tool uses a recursive regex pattern that can handle nested braces:
```python
r'\\?frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
```

This pattern:
- Matches `\frac{...}{...}` or `frac{...}{...}`
- Handles nested braces within numerator and denominator
- Processes innermost fractions first for nested expressions

## Usage Tips

### For Students
- Use the CLI to practice problems without needing a web browser
- Copy-paste the formatted expressions into your notes
- The Unicode symbols work in most modern terminals and text editors

### For Instructors
- Use `--seed` to generate specific problem variants
- Use `--no-check` to preview problems quickly
- Combine with `--solution` for answer keys

### For Developers
- The formatting logic is in `format_math()` function
- Easy to extend with additional LaTeX commands
- Unicode fallbacks for terminals that don't support symbols
