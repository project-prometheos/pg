# WeBWorK PG - Python Edition

Modern Python reimplementation of WeBWorK's PG (Problem Generation) language for authoring online homework problems.

## Quick Start

### Installation

```bash
pip install webwork-pg
```

### Create Your First Problem

Create a file named `my_problem.pyg`:

```python
from webwork import *

DOCUMENT()

# Problem setup
Context("Numeric")
a = random(2, 5)
answer = Compute(f"{a} * x + 1")

# Problem statement
BEGIN_PGML
Find the derivative of [``y = [$a]x + 1``]

[_]{answer}{20}
END_PGML

# Solution
SOLUTION(PGML('''
The derivative of a linear function [``y = [$a]x + 1``] is [``[$a]``].
'''))

ENDDOCUMENT()
```

### Run Your Problem

```bash
python my_problem.pyg
```

## Features

- **Full PG Compatibility**: Drop-in replacement for WeBWorK's Perl PG system
- **Clean Python API**: Pythonic syntax while maintaining PG semantics
- **MathObjects**: Intelligent mathematical objects (Context, Formula, Compute, etc.)
- **PGML Support**: Markup language for problem statements
- **Answer Checking**: Flexible answer comparison and grading
- **Random Number Generation**: Problem variation through seeded randomization

## Architecture

```
webwork/
├── core/          Core PG functionality
│   ├── pg.py      DOCUMENT(), TEXT(), ANS()
│   ├── pgml.py    PGML() markup language
│   ├── pgstandard.py   Standard macros
│   └── pgcourse.py     Course configuration
└── math/          Mathematical objects
    └── objects.py Context, Compute, Formula, etc.
```

## Key Concepts

### DOCUMENT Structure

Every PG problem must have this structure:

```python
from webwork import *

DOCUMENT()

# Problem setup and variables
# ...

# Problem statement
BEGIN_PGML
Problem text in PGML format
[_]{answer}
END_PGML

ENDDOCUMENT()
```

### Contexts

Configure the mathematical domain:

```python
Context("Numeric")        # Real numbers
Context("Complex")        # Complex numbers
Context("Vector")         # 2D/3D vectors
Context("Matrix")         # Matrices
Context("Interval")       # Intervals
```

### Mathematical Objects

Create and manipulate mathematical expressions:

```python
# Parse and evaluate expressions
x = Compute("2*x + 1")

# Create formulas with automatic differentiation
f = Formula("x^2 + 2*x")

# Create specific types
v = Vector(1, 2, 3)
m = Matrix([1, 2], [3, 4])
```

### Answer Checking

Compare student answers to expected answers:

```python
# Exact answer match
ANS(answer.cmp())

# With custom parameters
ANS(answer.cmp(
    tolType => 'relative',
    tol => 0.001,
))
```

## Compatibility with Perl PG

This package maintains **semantic compatibility** with WeBWorK's Perl PG system:

- All core macros are available
- Problem statement syntax is identical
- Answer checking logic is preserved
- MathObjects behavior matches Perl implementation

However, **Python semantics** take precedence:

```python
# Python list syntax
a = random(1, 5)
v = Vector(1, 2, 3)

# Python f-strings for interpolation
s = f"The answer is {answer}"

# Python comprehensions
values = [random(1, 10) for _ in range(5)]
```

## Third-Party Problem Libraries

Convert existing Perl PG problems to Python:

```bash
# Using the converter tool
pypg convert my_problem.pg my_problem.pyg

# Or use the Python API
from pg_translator import convert_pg_file

output_file, result = convert_pg_file("my_problem.pg")
```

## Development

Install in development mode:

```bash
pip install -e .
```

Run tests:

```bash
pytest tests/
```

## Documentation

- [PG Syntax Reference](https://webwork.maa.org/wiki/PG_Syntax)
- [Problem Authoring](https://webwork.maa.org/wiki/Creating_WeBWorK_problems)
- [MathObjects Reference](https://webwork.maa.org/wiki/MathObjects)

## License

GPL-2.0-or-later - Same as WeBWorK

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## Support

- Issues: [GitHub Issues](https://github.com/webwork/pg/issues)
- Discussions: [WeBWorK Community](https://webwork.maa.org/forums)
