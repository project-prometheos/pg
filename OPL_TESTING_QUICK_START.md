# OPL Testing Quick Start Guide

## Setup

The OPL (Open Problem Library) is already cloned at `d:\pg\opl`. If it's not there, clone it with:

```bash
git clone https://github.com/openwebwork/webwork-open-problem-library.git opl
```

## Running Tests

### Basic Test (50 problems)
```bash
python test_opl_problems.py --limit 50
```

### Verbose Output (show each problem)
```bash
python test_opl_problems.py --limit 100 --verbose
```

### Save Results to JSON
```bash
python test_opl_problems.py --limit 200 --save-results results.json
```

### Test Specific Category
```bash
python test_opl_problems.py --category "Contrib/Hope" --verbose
```

### Full Debug Mode
```bash
python test_opl_problems.py --limit 50 --debug --verbose
```

## Understanding Results

### Success Rate
- **5-6%** on first 200 problems
- **12%** on first 50 problems
- Success depends on which problems are selected

### Error Types

**Syntax Errors (54-55%)**
- Perl-specific syntax not convertible to Python
- Examples: hash assignment in function calls, module method calls
- Requires preprocessor enhancements

**Name Errors (34-35%)**
- Missing macro implementations
- Examples: `Parser`, context modules, scaffolding macros
- Requires porting more PG macros

**Other Errors (5-6%)**
- Runtime errors, attribute errors, import errors

## Analyzing Failures

### View Specific Error
```python
import json
with open('results.json') as f:
    data = json.load(f)
    for result in data['results']:
        if result['error_type'] == 'syntax_error':
            print(f"{result['path']}: {result['error']}")
            break
```

### Count Error Types
```python
import json
from collections import Counter
with open('results.json') as f:
    data = json.load(f)
    error_types = Counter(r['error_type'] for r in data['results'])
    for error_type, count in error_types.most_common():
        print(f"{error_type}: {count}")
```

## Common Issues to Investigate

1. **Parser::* module calls** (Name Error)
   - Examples: `Parser::Number::NoDecimals`
   - Solution: Implement Parser configuration methods

2. **Context hash assignments** (Syntax Error)
   - Example: `Context()->{format}{number} = "%.6f#"`
   - Solution: Preprocess to separate assignments

3. **Missing contexts** (Name Error)
   - Examples: `contextFraction.pl`, `contextUnits.pl`
   - Solution: Implement context macros

4. **Scaffolding macros** (Name Error)
   - Example: `scaffold.pl` functionality
   - Solution: Port scaffolding system

## Performance

- 50 problems: ~15-20 seconds
- 200 problems: ~60-80 seconds
- 1000 problems: ~5-10 minutes

## Tips for Debugging Individual Problems

```bash
# Test a specific problem
python pg_solve.py "opl/Contrib/AgnesScott/Calculus/BoxMinAreaScafford.pg" --no-check

# This will show:
# - Preprocessing output
# - Execution errors
# - Problem statement (if successful)
```

## Next Steps for Improvement

1. **Most impactful:** Implement missing Parser configuration methods
2. **High impact:** Support context hash assignment syntax
3. **Medium impact:** Implement fraction context
4. **Ongoing:** Add more macro implementations based on error frequency

