# AI Coding Agent Prompt: Fix Fraction Context Blessing Issue

## Problem Statement

We are working on a parity testing framework that compares Perl and Python implementations of WeBWorK/PG (Problem Generation) macros. The Perl adapter (`parity_lab/perl_ref/run_pg_snippet.pl`) executes PG snippets and serializes outputs to JSON for comparison with Python.

**Current Issue**: Fraction context snippets (`fraction_basic.pg`, `fraction_mixed.pg`) fail in the Perl adapter with the error:

```
Can't call method "operators" on unblessed reference at (eval 137) line 297.
```

This error occurs inside `context::Fraction::extending()` when it tries to call `$context->operators` on a context object that is not properly blessed as a `Parser::Context` object.

## Context and Background

### Architecture

1. **Perl Adapter** (`parity_lab/perl_ref/run_pg_snippet.pl`): Executes PG snippets in a controlled environment
2. **Python Adapter** (`parity_lab/py_port/run_pg_snippet.py`): Executes preprocessed Python versions of PG snippets
3. **Parity Tests**: Compare outputs from both adapters to ensure feature parity

### How Context Extensions Work

The fraction context is created through a chain of function calls:

1. `context::Fraction::Init()` is called when `contextFraction.pl` is loaded
2. `Init()` calls `context::Fraction::extending('Numeric')`
3. `extending()` calls `context::Extensions::create("Fraction", "Numeric")` to get a copy of the Numeric context
4. `extending()` then calls `context::Extensions::extend($context, ..., context => "Context")` to extend it
5. `extend()` should bless the context as `context::Fraction::Context` (a subclass of `Parser::Context`)

### The Error Location

The error occurs at line 297 in `macros/contexts/contextFraction.pl`:

```perl
sub extending {
    my ($from, %options) = @_;
    my $context = context::Extensions::create("Fraction", $from);
    # ... setup code ...
    my $operators = $context->operators;  # <-- LINE 297: ERROR HERE
    # ...
}
```

At this point, `$context` is not properly blessed, so calling `->operators` fails.

## Constraints

**CRITICAL**: We **CANNOT** edit library files or Perl reference files. These are off-limits:
- `lib/Parser/Context.pm`
- `lib/Value/Context.pm`
- `lib/Value/WeBWorK.pm`
- `macros/contexts/contextExtensions.pl`
- `macros/contexts/contextFraction.pl`

**ONLY** the Perl adapter (`parity_lab/perl_ref/run_pg_snippet.pl`) can be modified.

## What We've Tried

1. **Wrapper Functions**: Installed wrappers around `context::Extensions::create()`, `context::Extensions::extend()`, and `context::Fraction::extending()` to ensure contexts are blessed before returning. These wrappers check if the context is unblessed and bless it as `Parser::Context`.

2. **Post-Processing**: Added code to fix contexts in `%main::context` after `PG.pl` loads and `Init()` functions run.

3. **Early Installation**: Moved wrapper installation to before `PG.pl` loads, so they're in place when `Init()` is called.

4. **Class Pre-loading**: Ensured `context::Fraction::Context` class exists before `extending()` is called.

**Result**: None of these approaches have worked. The error persists, indicating the context is still unblessed when `->operators` is called.

## Root Cause Hypothesis

The issue appears to be that `context::Extensions::extend()` is called with `context => "Context"`, which should bless the context as `context::Fraction::Context`. However, something in the blessing chain is failing:

1. `Value::Context->copy()` calls `$self->new()` which should preserve the class
2. `Parser::Context->copy()` (in `WeBWorK.pm`) calls `Value::Context::copy()` directly
3. `context::Extensions::extend()` tries to bless the context, but the blessing may not be working correctly

The problem might be:
- The context returned by `create()` is already unblessed
- The `extend()` function's blessing logic has a bug
- There's a timing issue where the context is used before `extend()` completes

## What We Need

Please investigate and fix the fraction context blessing issue in the Perl adapter. The solution should:

1. **Work within constraints**: Only modify `parity_lab/perl_ref/run_pg_snippet.pl`
2. **Fix the root cause**: Ensure contexts are properly blessed when `context::Fraction::extending()` is called
3. **Be robust**: Handle edge cases and ensure it works for both `fraction_basic.pg` and `fraction_mixed.pg`
4. **Not break existing functionality**: Ensure other snippets (18/21 currently working) continue to work

## Test Cases

To verify the fix works:

```bash
cd /mnt/userdata/martin/GitHub/pg
eval $(perl -I ~/perl5/lib/perl5/ -Mlocal::lib 2>/dev/null)
export PERL5LIB="$HOME/perl5/lib/perl5:$PERL5LIB"

# Test fraction_basic
perl parity_lab/perl_ref/run_pg_snippet.pl \
    parity_lab/tests/snippets/fraction_basic.pg \
    42 /tmp/test_fraction_basic.json

# Test fraction_mixed  
perl parity_lab/perl_ref/run_pg_snippet.pl \
    parity_lab/tests/snippets/fraction_mixed.pg \
    42 /tmp/test_fraction_mixed.json

# Check results
python3 -c "
import json
for f in ['/tmp/test_fraction_basic.json', '/tmp/test_fraction_mixed.json']:
    with open(f) as file:
        data = json.load(file)
        print(f'{f}: {len(data.get(\"html\", \"\"))} chars, {len(data.get(\"errors\", []))} errors')
        if data.get('errors'):
            print(f'  Error: {data[\"errors\"][0][:200]}')
"
```

Success criteria:
- Both snippets produce HTML output (non-zero length)
- Both snippets have 0 errors
- The HTML contains fraction-related content

## Additional Context

### File Structure
- `parity_lab/perl_ref/run_pg_snippet.pl` - Perl adapter (ONLY file we can edit)
- `parity_lab/tests/snippets/fraction_basic.pg` - Test snippet
- `parity_lab/tests/snippets/fraction_mixed.pg` - Test snippet
- `macros/contexts/contextFraction.pl` - Fraction context implementation (read-only)
- `macros/contexts/contextExtensions.pl` - Context extension framework (read-only)
- `lib/Parser/Context.pm` - Parser context base class (read-only)
- `lib/Value/Context.pm` - Value context base class (read-only)

### Key Code Flow

1. Adapter loads `PG.pl` which calls `_contextFraction_init()`
2. `_contextFraction_init()` calls `context::Fraction::Init()`
3. `Init()` calls `context::Fraction::extending('Numeric')`
4. `extending()` calls `context::Extensions::create("Fraction", "Numeric")` → should return blessed context
5. `extending()` calls `$context->operators` → **FAILS HERE** (context not blessed)
6. `extending()` calls `context::Extensions::extend($context, ..., context => "Context")` → should bless as `context::Fraction::Context`

### Debugging Hints

- The error occurs at line 297 in `contextFraction.pl`, which is inside `extending()` before `extend()` is called
- This suggests `create()` is returning an unblessed context
- However, `create()` should call `Parser::Context->getCopy()` which should return a blessed context
- The wrapper around `create()` should catch unblessed contexts, but it's not working

Possible issues to investigate:
1. Is `create()` being called before the wrapper is installed?
2. Is the context being modified/unblessed after `create()` returns?
3. Is there a different code path that bypasses our wrappers?
4. Is the context being stored in `%main::context` and then retrieved later in an unblessed state?

## Expected Outcome

After the fix:
- `fraction_basic.pg` should execute successfully and produce HTML output
- `fraction_mixed.pg` should execute successfully and produce HTML output
- Both should have 0 errors in the JSON output
- This would bring parity from 18/21 (86%) to 20/21 (95%) snippets working

Please investigate the root cause and implement a fix in the Perl adapter that ensures contexts are properly blessed throughout the execution chain.

