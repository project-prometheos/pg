# PG Macro Parity Lab

Comprehensive testing framework to verify 1:1 feature and API parity between Perl reference implementations and Python ports of the top 10 WeBWorK/PG macros.

## Overview

This parity lab implements a rigorous, measurable process to ensure Python ports achieve complete compatibility with Perl reference implementations.

### Target Macros

1. PGstandard.pl
2. PGcourse.pl
3. MathObjects.pl
4. PGchoicemacros.pl
5. PGML.pl
6. PGgraphmacros.pl
7. AnswerFormatHelp.pl
8. parserPopUp.pl
9. parserMultiAnswer.pl
10. contextFraction.pl

## Directory Structure

```
parity_lab/
├── perl_ref/           # Perl runtime adapters
│   └── run_pg_snippet.pl
├── py_port/            # Python runtime adapters
│   └── run_pg_snippet.py
├── tests/
│   ├── snippets/       # Micro PG test problems
│   ├── contract/       # Contract tests (pytest)
│   ├── perl/           # Perl tests
│   └── fuzz/           # Property-based tests
├── tools/
│   ├── inventory/      # Symbol extraction & diff
│   ├── render_diff/    # Output comparison
│   └── corpus/         # OPL problem selection
├── demo/               # Demo problems & scripts
│   ├── problems/
│   └── run_demo.sh
└── build/              # Generated artifacts
```

## Quick Start

### Prerequisites

```bash
# Python 3.12+
python --version

# Perl 5.20.3+
perl --version

# Install Python dependencies
pip install pytest pytest-cov hypothesis

# Install Perl dependencies (from repo root)
cpanm --installdeps .
```

### Phase 1: Inventory & Diff

Extract and compare API surfaces between Perl and Python implementations.

```bash
# Extract Perl symbols
python tools/inventory/dump_perl_inventory.py \
  ../macros/core \
  build/perl_inventory.json

# Extract Python symbols
python tools/inventory/dump_py_inventory.py \
  build/py_inventory.json

# Generate diff report
python tools/inventory/diff_inventory.py \
  build/perl_inventory.json \
  build/py_inventory.json \
  build/inv_diff.html

# View report
start build/inv_diff.html  # Windows
# open build/inv_diff.html  # macOS
# xdg-open build/inv_diff.html  # Linux
```

### Phase 2: Contract Testing

Run differential tests comparing Perl and Python runtime outputs.

```bash
# Run contract tests
pytest tests/contract -v

# With coverage
pytest tests/contract \
  --cov=pg_macros \
  --cov-report=html:build/reports/coverage \
  --cov-report=term-missing
```

### Phase 3: OPL Corpus Selection

Select real-world problems from the Open Problem Library.

```bash
# Clone OPL (if not already available)
git clone https://github.com/openwebwork/webwork-open-problem-library.git ../opl

# Select test corpus
python tools/corpus/select_opl_problems.py \
  ../opl \
  build/corpus.json \
  5000  # Max files to scan

# Review selection
python -m json.tool build/corpus.json | less
```

### Phase 4: Demo

Run canonical demonstration problems.

```bash
# Run demo suite
bash demo/run_demo.sh
```

## Testing Individual Snippets

```bash
# Test a single PG snippet
seed=12345
snippet=tests/snippets/fraction_basic.pg

# Run in Perl
perl perl_ref/run_pg_snippet.pl "$snippet" "$seed" build/perl_out.json

# Run in Python
python py_port/run_pg_snippet.py "$snippet" "$seed" build/py_out.json

# Compare
python tools/render_diff/diff_outputs.py \
  build/perl_out.json \
  build/py_out.json
```

## Success Criteria

- ✅ 100% API surface coverage (all exported functions/classes present)
- ✅ 100% contract test pass rate on ≥100 OPL problems
- ✅ Identical grading decisions (correct/incorrect, partial credit)
- ✅ Normalized rendering equivalence (TeX/HTML/PGML)
- ✅ Error message parity (exception types and messages)
- ✅ Zero regressions on OPL exemplar problems
- ✅ ≥95% Python code coverage in pg_macros package

## Normalization Rules

### Text Normalization
- Whitespace: collapse runs of spaces, trim leading/trailing
- HTML entities: `&lt;` ↔ `<`, `&nbsp;` ↔ ` ` (decode for comparison)
- Line endings: normalize `\r\n` → `\n`

### Numeric Normalization
- Floating point: tolerance of 1e-9 for comparisons
- Boolean coercion: Perl `1/0/undef` ↔ Python `True/False/None`

### Naming Conventions
- Perl: `camelCase` or `under_scores` (mixed)
- Python: `snake_case` for functions, `PascalCase` for classes
- Documented aliasing for compatibility

## Adding New Test Snippets

1. Create `.pg` file in `tests/snippets/`:

```perl
DOCUMENT();
loadMacros("PGstandard.pl", "MathObjects.pl");
TEXT(beginproblem());

Context("Numeric");
$ans = Compute("42");

BEGIN_TEXT
What is the answer? \{ans_rule(10)\}
END_TEXT

ANS($ans->cmp());
ENDDOCUMENT();
```

2. Add contract test in `tests/contract/`:

```python
def test_my_snippet():
    snippet = SNIPPETS / "my_snippet.pg"
    perl_out = run_perl_snippet(snippet, seed=12345)
    py_out = run_python_snippet(snippet, seed=12345)
    assert_outputs_match(perl_out, py_out)
```

## Triage & Issue Tracking

### Issue Labels
- `api-gap`: Missing function/class or incompatible signature
- `behavior-gap`: Incorrect output, grading, or side-effect
- `doc-gap`: Missing or incorrect documentation
- `perf-regression`: >2x slower than Perl
- `normalization-needed`: Intentional difference requiring normalization rule
- `test-gap`: Insufficient coverage

### Severity
- **Blocker**: Prevents any problem using the macro from working
- **Major**: Causes incorrect grading/rendering for common cases
- **Minor**: Edge case issue or cosmetic difference

## Development Workflow

1. **Discovery**: Run inventory diff or contract tests
2. **Log**: Create GitHub issue with evidence
3. **Fix**: Implement in Python port, add regression test
4. **Verify**: Re-run contract suite
5. **Close**: Update parity checklist, close issue

## Continuous Integration

The parity tests can be integrated into CI/CD:

```yaml
# .github/workflows/parity.yml
- name: Run inventory diff
  run: |
    python parity_lab/tools/inventory/dump_perl_inventory.py macros/core parity_lab/build/perl_inventory.json
    python parity_lab/tools/inventory/dump_py_inventory.py parity_lab/build/py_inventory.json
    python parity_lab/tools/inventory/diff_inventory.py parity_lab/build/perl_inventory.json parity_lab/build/py_inventory.json parity_lab/build/inv_diff.html

- name: Run contract tests
  run: pytest parity_lab/tests/contract -v --cov=pg_macros --cov-fail-under=95
```

## Troubleshooting

### Perl adapter fails
- Check Perl dependencies: `cpanm --installdeps .`
- Verify macro paths in `perl_ref/run_pg_snippet.pl`

### Python adapter incomplete
- The Python adapter is a stub - implementation is in progress
- Focus on API parity first via inventory diff

### Tests hang or timeout
- Reduce test corpus size
- Use pytest `-x` flag to stop on first failure

## References

- [Main Project README](../README.md)
- [CLAUDE.md](../CLAUDE.md) - Development guidelines
- [WeBWorK Documentation](https://webwork.maa.org/wiki/)
- [Open Problem Library](https://github.com/openwebwork/webwork-open-problem-library)

## License

Same as parent PG repository.
