# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the WeBWorK Problem Generator (PG) repository - an open-source online homework system for math and sciences courses. The project is undergoing a modernization effort, with both a legacy Perl codebase and a new monorepo architecture.

**Key Components:**

1. **Legacy PG System (Perl)** - The mature, production-ready problem generation engine
   - Lives in `lib/`, `macros/`, and related directories
   - Uses MathObjects (Value.pm, Parser.pm) for mathematical computation
   - Extensive macro library for problem authoring

2. **Modern Monorepo (Python/TypeScript)** - New architecture being scaffolded
   - `apps/backend`: FastAPI service exposing problem generation APIs
   - `apps/web`: React + Vite frontend for rendering problems
   - `packages/problemkit`: Framework-agnostic Python problem authoring core
   - `packages/schemas` & `packages/ui`: Shared TypeScript packages

## Development Commands

### Monorepo (Nx + pnpm)

```bash
# Install dependencies
pnpm install

# Development (runs both backend and frontend)
pnpm dev

# Run specific app
pnpm exec nx run backend:dev
pnpm exec nx run web:dev

# Build all packages
pnpm build

# Lint/test
pnpm lint
pnpm test
pnpm exec nx run web:test
pnpm exec nx run backend:test

# Format check
pnpm format
```

### Python Backend

```bash
# Install Python dependencies (requires Python 3.12)
python -m pip install -e packages/problemkit -e apps/backend[dev]

# Run backend tests
pnpm exec nx run backend:test
```

### Legacy Perl System

```bash
# Install Perl dependencies
cpanm --installdeps .

# Run all tests
prove -lr t/

# Run specific test
prove -lv t/macros/pgaux.t

# Format Perl code
bin/run-perltidy.pl <file>
```

## Architecture

### Legacy PG Architecture

**Core Parser/Value System:**
- `lib/Parser.pm`: Expression parser that converts strings to parse trees
- `lib/Value.pm`: MathObjects system - intelligent mathematical objects with built-in answer checking
- `lib/Parser/`, `lib/Value/`: Subcomponents for different object types (Complex, Matrix, Vector, etc.)

**Problem Environment:**
- `lib/WeBWorK/PG/Translator.pm`: Translates .pg problem files into renderable output
- `lib/WeBWorK/PG/Environment.pm`: Sets up problem execution context
- `lib/WeBWorK/PG/ImageGenerator.pm`: Handles LaTeX image generation
- `lib/PGcore.pm`: Core PG functionality and utilities

**Macro System:**
The `macros/` directory contains reusable problem authoring components organized by category:
- `macros/core/`: Core PG macros (PGstandard.pl, PGML.pl, etc.)
- `macros/contexts/`: Context definitions for different math domains
- `macros/parsers/`: Parser-related macros
- `macros/math/`: Mathematical utilities
- `macros/graph/`: Graphing and visualization
- `macros/ui/`: User interface elements
- `macros/answers/`: Answer checking and evaluation

### Modern Monorepo Architecture

**Backend (FastAPI):**
- `apps/backend/app/main.py`: Application entry point
- `apps/backend/app/routers/`: API endpoints (problems, solutions, checks, health)
- `apps/backend/app/services/`: Business logic
- `apps/backend/app/schemas/`: Pydantic models for API contracts

**Problemkit (Python):**
Core problem authoring framework:
- `packages/problemkit/problemkit/models.py`: ProblemInstance and InputSpec models
- `packages/problemkit/problemkit/decorators.py`: @problem decorator for authoring
- `packages/problemkit/problemkit/registry.py`: Problem registration system
- `packages/problemkit/problemkit/rng.py`: Random number generation
- `packages/problemkit/problemkit/samples/`: Example problems (see calculus.py)

**Frontend (React):**
- `apps/web/src/pages/`: Page components
- `apps/web/src/components/`: Reusable UI components
- `apps/web/src/services/`: API client and data fetching
- Uses KaTeX for math rendering and MathLive for math input

## Code Quality Tools

**Pre-commit hooks** (`.pre-commit-config.yaml`):
- Python: black, ruff, mypy
- JavaScript/TypeScript: eslint, prettier
- General: YAML validation, trailing whitespace

**Run pre-commit manually:**
```bash
pre-commit run --all-files
```

## Testing Philosophy

From `t/README.md`:
- Follow Test Driven Development - write tests for bugs before fixing
- Unit tests (`.t` files) test individual modules and functions
- Integration tests (`.pg` files) test problem rendering
- Use `Test2::V0` for Perl tests
- Mock services when possible for faster, isolated tests

**Writing Perl Unit Tests:**
```perl
use Test2::V0;
use lib 't/lib';
use Test::PG;

loadMacros("MathObjects.pl");
Context("Numeric");
my $f = Compute("x^2");
is check_score($f->eval(x=>2), '4'), 1, 'description';
```

## Key Conventions

**Version:** PG 2.20 (see VERSION file)

**Perl Standards:**
- Use `.perltidyrc` for formatting
- Runtime requires Perl 5.20.3+
- Dependencies managed via cpanfile

**Python Standards:**
- Python 3.12+ required
- Line length: 100 characters (ruff/black)
- Type hints required (mypy strict mode in problemkit)
- Use pydantic for data models

**TypeScript Standards:**
- ESLint with Prettier for formatting
- React hooks rules enforced
- Vite for building and dev server

**Git Workflow:**
- Main branch: `main`
- Follow conventional commits for clarity
- Pre-commit hooks must pass

## Problem Authoring

**Legacy (Perl):** Problems use macros from `macros/` directory loaded via `loadMacros()`

**Modern (Python):** Use `@problem` decorator:
```python
from problemkit.decorators import problem
from problemkit.models import ProblemInstance, InputSpec

@problem(id="unique.id", vars=["x"], tags=["tag1"])
def my_problem(*, seed: int, rng: RNG) -> ProblemInstance:
    return ProblemInstance(
        statement_tex="Problem statement",
        inputs=[InputSpec(name="ans", type="math")],
        answers={"ans": "solution"},
        solution_tex="Solution explanation"
    )
```

## Repository Structure Notes

- `conf/`: Configuration files
- `doc/`: POD documentation for MathObjects
- `tutorial/`: WeBWorK tutorials
- `assets/`: Static assets
- `bin/`: Utility scripts (perltidy, PGML conversion)
- `docker/`: Docker configuration
- `htdocs/`: Legacy web assets
