# PG Translator Quick Reference

**Version**: 1.0
*  *Date**: October 5, 2025
**  Status**: Production Ready

## Quick Start

### Install Dependencies
```bash
pnpm install
python -m pip install -e packages/pg_translator -e packages/pg_macros -e packages/pg_answer -e packages/pg_math
```

### Translate a Problem
```python
from pg_translator import PGTranslator

translator = PGTranslator()
result = translator.translate("path/to/problem.pg", seed=1234)

print(result.statement_html)  # Problem HTML
print(result.answer_blanks)   # Answer info
print(result.solution_html)   # Solution (if any)
```

## Supported Syntaxes

### Traditional PG

```perl
DOCUMENT();
loadMacros("PGstandard.pl", "PGbasicmacros.pl");
TEXT(beginproblem());

$a = random(2, 9, 1);
$b = random(2, 9, 1);
$answer = $a + $b;

BEGIN_TEXT
What is \($a + $b\)?
$PAR
Answer: \{ans_rule(10)\}
END_TEXT

ANS(num_cmp($answer));
ENDDOCUMENT();
```

### Modern PGML

```perl
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

$a = random(2, 9, 1);
$b = random(2, 9, 1);

BEGIN_PGML
What is [$a] + [$b]?

Answer: [_]{$a + $b}
END_PGML

ENDDOCUMENT();
```

## PGML Syntax Guide

### Variables
```perl
[$variable]           # Interpolate variable value
[$a + $b]            # Interpolate expression
```

### Answer Blanks
```perl
[_]{$answer}         # Default width (20)
[____]{$answer}{30}  # Custom width (30)
```

### Formatting
```perl
**bold text**        # Bold
*italic text*        # Italic (or _italic_)
- List item          # Unordered list
```

### Math
```perl
\(x^2 + y^2\)       # Inline math
\[\int_0^1 x dx\]   # Display math
[`x^2`]             # Inline (alternative)
[``x^2``]           # Display (alternative)
```

### Solutions and Hints
```perl
BEGIN_PGML_SOLUTION
The answer is [$answer].
END_PGML_SOLUTION

BEGIN_PGML_HINT
**Hint:** Try factoring first.
END_PGML_HINT
```

## Common Patterns

### Multiple Answer Blanks

**Traditional**:
```perl
BEGIN_TEXT
Sum: \{ans_rule(10)\}
Product: \{ans_rule(10)\}
END_TEXT
ANS(num_cmp($sum));
ANS(num_cmp($product));
```

**PGML**:
```perl
BEGIN_PGML
Sum: [_]{$sum}
Product: [_]{$product}
END_PGML
```

### Random Numbers

```perl
$a = random(1, 10, 1);        # Integer 1-10
$b = random(0.5, 2.5, 0.5);   # 0.5, 1.0, 1.5, 2.0, 2.5
```

### Formatted Text

**Traditional**:
```perl
$BBOLD Important: $EBOLD Some text $PAR
```

**PGML**:
```perl
**Important:** Some text

```

## API Reference

### PGTranslator

```python
class PGTranslator:
    def translate(
        self,
        pg_file_path: str | Path,
        seed: int,
        inputs: dict[str, str] | None = None,
        context: Context | None = None,
    ) -> ProblemResult
```

### ProblemResult

```python
@dataclass
class ProblemResult:
    statement_html: str           # Problem statement
    answer_blanks: dict[str, Any] # Answer info
    solution_html: str | None     # Solution (if any)
    hint_html: str | None         # Hint (if any)
    metadata: dict[str, Any]      # Problem metadata
    errors: list[str] | None      # Execution errors
```

## Testing

### Run Tests

```bash
# Traditional PG tests
python test_real_pg_files.py

# PGML tests
python test_pgml_comprehensive.py

# Specific test suite
cd packages/pg_translator
pytest tests/test_integration_simple.py -v
```

### Create Test Problem

```python
# test_my_problem.py
from pg_translator import PGTranslator

pg_code = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

BEGIN_PGML
Test problem here
END_PGML

ENDDOCUMENT();
"""

translator = PGTranslator()
# Save to temp file and translate...
```

## Troubleshooting

### Common Issues

**1. Empty statement_html**
- Check that DOCUMENT() and ENDDOCUMENT() are present
- Verify TEXT() calls in problem
- Check for preprocessing errors

**2. Answer blanks not working**
- Traditional: Ensure ANS() calls present
- PGML: Check evaluator syntax `[_]{$expr}`
- Verify answer evaluation functions loaded

**3. Math not rendering**
- LaTeX is preserved as-is for frontend
- Frontend needs KaTeX configured
- Check delimiters: `\(...\)` or `\[...\]`

**4. Variables not interpolating**
- Traditional: Use `$var` in BEGIN_TEXT
- PGML: Use `[$var]` in BEGIN_PGML
- Check variable is defined before text block

### Debug Mode

```python
from pg_translator.preprocessor import PGPreprocessor

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_code, use_sandbox_macros=True)
print(result.code)  # See generated Python code
```

## Performance Tips

1. **Cache Translator Instance**: Reuse `PGTranslator()` for multiple problems
2. **Batch Processing**: Process multiple problems in sequence
3. **Simple Syntax**: PGML is slightly faster than traditional

## Best Practices

### For Problem Authors

1. **Use PGML for new problems** - cleaner, more maintainable
2. **Keep answer checking simple** - use built-in evaluators
3. **Test with multiple seeds** - ensure randomization works
4. **Add solutions and hints** - improve student experience

### For Developers

1. **Always check result.errors** - handle execution failures
2. **Validate answer_blanks** - ensure expected answers present
3. **Test UTF-8 content** - international characters work
4. **Use seed for reproducibility** - same seed = same problem

## Migration Guide

### Converting Traditional to PGML

**Before**:
```perl
BEGIN_TEXT
Calculate \($a + $b\).
$PAR
Answer: \{ans_rule(20)\}
END_TEXT
ANS(num_cmp($answer));
```

**After**:
```perl
BEGIN_PGML
Calculate [$a + $b].

Answer: [_]{$answer}
END_PGML
```

### Key Changes

| Traditional | PGML | Notes |
|------------|------|-------|
| `$var` | `[$var]` | Variable syntax |
| `\{func()\}` | `[_]{$eval}` | Answer blanks |
| `$PAR` | Blank line | Paragraph break |
| `$BBOLD...$EBOLD` | `**...**` | Bold text |
| `ANS(...)` | Inline `{$eval}` | Answer checking |

## Additional Resources

- **Full Documentation**: `PG_TRANSLATOR_COMPLETE_SUMMARY.md`
- **PGML Guide**: `PG_TRANSLATOR_PGML_SUPPORT.md`
- **Test Results**: `PGML_TEST_RESULTS.md`
- **Original Plan**: `PG_TRANSLATOR_COMPLETION_PLAN.md`

## Support

For issues or questions:
1. Check test files for examples
2. Review documentation files
3. Run debug mode to see generated code
4. Check preprocessor output for transformation issues

---

**Last Updated**: October 5, 2025
**Version**: 1.0 Production Release
