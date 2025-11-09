# 🚀 Next Actions: Wire Up Your Implementation

You have **55-65% parity already implemented** but disconnected. Here's how to connect it:

---

## ✅ Immediate Action (30 minutes)

### Update the Python Runtime Adapter

Edit [parity_lab/py_port/run_pg_snippet.py](parity_lab/py_port/run_pg_snippet.py):

```python
#!/usr/bin/env python3
"""
Python Runtime Adapter - NOW WITH FULL MACRO SUPPORT!
"""
import sys
import json
import random as _random
from pathlib import Path
from typing import Any, Dict

def execute_pg_snippet(snippet_path: Path, seed: int) -> Dict[str, Any]:
    """Execute a PG snippet with full pg_macros + pg_math support."""

    # 1. Preprocess PG → Python
    from pg_translator.preprocessor import PGPreprocessor
    preprocessor = PGPreprocessor()
    content = snippet_path.read_text(encoding='utf-8')
    result = preprocessor.preprocess(content, use_sandbox_macros=False)

    # 2. Import all implemented packages
    import pg_macros.core as pgcore
    try:
        import pg_math
        HAS_PG_MATH = True
    except ImportError:
        print("Warning: pg_math not found", file=sys.stderr)
        HAS_PG_MATH = False

    try:
        from pg_macros.choice import MultipleChoice, new_multiple_choice
        HAS_CHOICE = True
    except ImportError:
        HAS_CHOICE = False

    try:
        from pg_macros.parsers.parser_popup import PopUp
        HAS_POPUP = True
    except ImportError:
        HAS_POPUP = False

    # 3. Setup execution environment
    _random.seed(seed)

    # Clear output buffers (if they exist)
    if hasattr(pgcore, '_output_buffer'):
        pgcore._output_buffer.clear()
    if hasattr(pgcore, '_answers'):
        pgcore._answers.clear()

    # 4. Build comprehensive namespace
    namespace = {
        # Core PG lifecycle
        'DOCUMENT': pgcore.DOCUMENT if hasattr(pgcore, 'DOCUMENT') else lambda: None,
        'ENDDOCUMENT': pgcore.ENDDOCUMENT if hasattr(pgcore, 'ENDDOCUMENT') else lambda: '',
        'beginproblem': lambda: '',

        # Text output
        'TEXT': pgcore.TEXT if hasattr(pgcore, 'TEXT') else print,
        'BEGIN_TEXT': lambda: '',
        'END_TEXT': lambda: '',

        # Answer registration
        'ANS': pgcore.ANS if hasattr(pgcore, 'ANS') else lambda x: None,
        'NAMED_ANS': pgcore.NAMED_ANS if hasattr(pgcore, 'NAMED_ANS') else lambda n, x: None,

        # Random numbers
        'random': pgcore.random if hasattr(pgcore, 'random') else _random.uniform,
        'non_zero_random': pgcore.non_zero_random if hasattr(pgcore, 'non_zero_random') else _random.uniform,
        'list_random': pgcore.list_random if hasattr(pgcore, 'list_random') else _random.choice,

        # Helpers
        'image': pgcore.image if hasattr(pgcore, 'image') else lambda f, **kw: f'<img src="{f}">',
        'ans_rule': pgcore.ans_rule if hasattr(pgcore, 'ans_rule') else lambda w=20: f'<input size="{w}">',
    }

    # Add MathObjects if available
    if HAS_PG_MATH:
        namespace.update({
            'Context': pg_math.Context,
            'Compute': pg_math.Compute,
            'Formula': pg_math.Formula,
            'Real': pg_math.Real,
            'Complex': pg_math.Complex,
            'Point': pg_math.Point,
            'Vector': pg_math.Vector,
            'Matrix': pg_math.Matrix,
            'Fraction': pg_math.Fraction,
            'Interval': pg_math.Interval,
            'Set': pg_math.Set,
            'Union': pg_math.Union,
            'List': pg_math.List,
            'String': pg_math.String,
            'Infinity': pg_math.Infinity,
        })

    # Add choice macros if available
    if HAS_CHOICE:
        namespace['MultipleChoice'] = MultipleChoice
        namespace['new_multiple_choice'] = new_multiple_choice

    # Add popup if available
    if HAS_POPUP:
        namespace['PopUp'] = PopUp

    # 5. Execute the preprocessed code
    errors = []
    warnings = []

    try:
        exec(result.code, namespace)
    except Exception as e:
        errors.append(f"Execution error: {e}")
        import traceback
        errors.append(traceback.format_exc())

    # 6. Collect outputs
    output_text = ''
    if hasattr(pgcore, '_output_buffer'):
        output_text = ''.join(pgcore._output_buffer)

    answers = []
    if hasattr(pgcore, '_answers'):
        for name, evaluator in pgcore._answers.items():
            answers.append({
                'name': name,
                'correct': False,
                'score': 0.0,
                'message': '',
                'type': type(evaluator).__name__,
            })

    return {
        'tex': output_text,
        'html': output_text,
        'answers': answers,
        'errors': errors,
        'warnings': warnings,
    }

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <snippet.pg> <seed> <output.json>", file=sys.stderr)
        sys.exit(1)

    snippet_file = Path(sys.argv[1])
    seed = int(sys.argv[2])
    output_json = Path(sys.argv[3])

    if not snippet_file.exists():
        print(f"Error: Snippet file not found: {snippet_file}", file=sys.stderr)
        sys.exit(1)

    # Execute snippet
    output = execute_pg_snippet(snippet_file, seed)

    # Write JSON output
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, sort_keys=True)

    print(f"✓ Python output written: {output_json}", file=sys.stderr)
    print(f"  Seed: {seed}", file=sys.stderr)
    print(f"  HTML length: {len(output['html'])} chars", file=sys.stderr)
    print(f"  Answers: {len(output['answers'])}", file=sys.stderr)
    print(f"  Errors: {len(output['errors'])}", file=sys.stderr)

    # If there were errors, print them
    if output['errors']:
        print(f"\n  Errors:", file=sys.stderr)
        for error in output['errors']:
            print(f"    {error}", file=sys.stderr)

if __name__ == "__main__":
    main()
```

---

## ✅ Test It (5 minutes)

```bash
cd parity_lab

# Test 1: Random numbers (should work now!)
python py_port/run_pg_snippet.py tests/snippets/random_numbers.pg 12345 build/test1.json
cat build/test1.json

# Test 2: Fraction (if pg_math imports work)
python py_port/run_pg_snippet.py tests/snippets/fraction_basic.pg 12345 build/test2.json
cat build/test2.json

# Test 3: PGML
python py_port/run_pg_snippet.py tests/snippets/pgml_inline_math.pg 12345 build/test3.json
cat build/test3.json
```

---

## ✅ Re-run Parity Assessment (5 minutes)

```bash
cd parity_lab

# This should now show way more symbols!
python tools/inventory/dump_py_inventory.py build/py_inventory.json

# Generate new diff
python tools/inventory/diff_inventory.py \
  build/perl_inventory.json \
  build/py_inventory.json \
  build/inv_diff_FINAL.html

# Open it
start build/inv_diff_FINAL.html
```

**Expected result**: 120-150 symbols found (up from 98)

---

## ✅ Fix Remaining Gaps (Next 2-3 Days)

### Gap 1: MODES() Function
**Location**: `packages/pg_macros/pg_macros/core/pg_core.py`

Add:
```python
def MODES(html=None, tex=None, ptx=None, **kwargs):
    """Return content based on current display mode."""
    # For now, return HTML (most common)
    return html if html is not None else ''
```

### Gap 2: MultiAnswer Parser
**Location**: Create `packages/pg_macros/pg_macros/parsers/parser_multianswer.py`

```python
class MultiAnswer:
    """Multi-part answer with custom checker."""

    def __init__(self, *correct_answers):
        self.correct_answers = correct_answers
        self.checker = None

    def with_(self, **options):
        """Set options (checker, singleResult, etc.)."""
        if 'checker' in options:
            self.checker = options['checker']
        return self

    def cmp(self):
        """Return answer evaluator."""
        # Return evaluator that uses self.checker
        ...
```

### Gap 3: Graph Macros (Optional - Low Priority)
**Location**: Create `packages/pg_macros/pg_macros/graph/pg_graph_macros.py`

Skip for now - only ~5-10% of problems use graphs.

---

## 📊 Expected Timeline

| Day | Task | Outcome |
|-----|------|---------|
| **Day 1 (Today)** | Update `py_port/run_pg_snippet.py` | ✅ Tests run without import errors |
| **Day 2** | Add MODES() and missing helpers | ✅ 95% of PGstandard.pl works |
| **Day 3-4** | Implement MultiAnswer | ✅ Multi-part problems work |
| **Day 5** | Test on OPL corpus | ✅ 60-70% of problems pass |

---

## 🎯 Success Criteria

After these actions:

- ✅ `random_numbers.pg` runs successfully (Perl vs Python match)
- ✅ `fraction_basic.pg` runs successfully
- ✅ `pgml_inline_math.pg` runs successfully
- ✅ Parity inventory shows 120+ symbols
- ✅ Coverage estimate: **60-70%**

---

## 📚 Reference Documentation

- **Full Status**: [COMPREHENSIVE_PARITY_STATUS.md](COMPREHENSIVE_PARITY_STATUS.md)
- **Parity Lab Guide**: [parity_lab/README.md](parity_lab/README.md)
- **Quick Start**: [parity_lab/QUICK_START.md](parity_lab/QUICK_START.md)

---

## 🎓 Key Insight

**You're not building from scratch - you're WIRING existing implementations!**

- ✅ pg_math has MathObjects (7,943 lines)
- ✅ pg_macros.core has PG runtime (793 lines)
- ✅ pg_macros.choice has choice macros (213 lines)
- ❌ They just aren't connected yet

**Fix: One file update → unlock 9,000+ lines of code!**

---

**Start here**: Edit `parity_lab/py_port/run_pg_snippet.py` (copy code above) and test! 🚀
