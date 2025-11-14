#!/usr/bin/env python3
"""
Python Runtime Adapter - FULLY INTEGRATED with pg_macros + pg_math!
Executes PG snippets using the complete Python implementation.
"""
import sys
import json
import random as _random
from pathlib import Path
from typing import Any, Dict


def execute_pg_snippet(snippet_path: Path, seed: int) -> Dict[str, Any]:
    """Execute a PG snippet with full pg_macros + pg_math support."""

    # 1. Preprocess PG → Python
    from pg.translator.preprocessor import PGPreprocessor
    preprocessor = PGPreprocessor()
    content = snippet_path.read_text(encoding='utf-8')
    result = preprocessor.preprocess(content, use_sandbox_macros=False)

    # 2. Import all implemented packages
    import pg.macros.core as pgcore

    HAS_PG_MATH = False
    try:
        import pg.math as pg_math
        HAS_PG_MATH = True
    except ImportError:
        print("Warning: pg_math not found", file=sys.stderr)
        pg_math = None

    HAS_CHOICE = False
    try:
        from pg.macros.choice import MultipleChoice, new_multiple_choice
        HAS_CHOICE = True
    except ImportError:
        print("Warning: pg_macros.choice not found", file=sys.stderr)

    HAS_POPUP = False
    try:
        from pg.macros.parsers.parser_popup import PopUp
        HAS_POPUP = True
    except ImportError:
        print("Warning: parser_popup not found", file=sys.stderr)

    HAS_MULTIANSWER = False
    try:
        from pg.macros.parsers import MultiAnswer
        HAS_MULTIANSWER = True
    except ImportError:
        print("Warning: MultiAnswer not found", file=sys.stderr)

    # 3. Setup execution environment
    _random.seed(seed)

    # Create envir dict that DOCUMENT() will use
    envir = {
        'problemSeed': seed,
        'displayMode': 'HTML',
        'showPartialCorrectAnswers': 1,
        'recordSubmittedAnswers': 1,
        'ANSWER_PREFIX': 'AnSwEr',
        'QUIZ_PREFIX': 'QuIz',
    }

    HAS_PG_ENV = True  # Assume it will work (DOCUMENT() will create it)

    # 4. Build comprehensive namespace
    namespace = {
        # Environment dict for DOCUMENT() to use
        'envir': envir,

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

        # Random numbers - CRITICAL!
        'random': pgcore.random if hasattr(pgcore, 'random') else lambda a, b, s=1: _random.uniform(a, b),
        'non_zero_random': pgcore.non_zero_random if hasattr(pgcore, 'non_zero_random') else lambda a, b, s=1: _random.uniform(a, b),
        'list_random': pgcore.list_random if hasattr(pgcore, 'list_random') else _random.choice,

        # Helpers
        'image': pgcore.image if hasattr(pgcore, 'image') else lambda f, **kw: f'<img src="{f}">',
        'ans_rule': pgcore.ans_rule if hasattr(pgcore, 'ans_rule') else lambda w=20: f'<input size="{w}">',
        'BR': lambda: '<br/>',  # Line break function
        'PAR': lambda: '<p>',   # Paragraph function
        'HR': lambda: '<hr/>',  # Horizontal rule function
        'MODES': pgcore.MODES if hasattr(pgcore, 'MODES') else lambda **kw: kw.get('HTML', ''),

        # Formatting helpers
        'BBOLD': lambda: '<b>',
        'EBOLD': lambda: '</b>',
        'BITALIC': lambda: '<i>',
        'EITALIC': lambda: '</i>',

        # Solution/Hint
        'SOLUTION': pgcore.SOLUTION if hasattr(pgcore, 'SOLUTION') else lambda *args: '',
        'HINT': pgcore.HINT if hasattr(pgcore, 'HINT') else lambda *args: '',
        'BEGIN_SOLUTION': lambda: '',
        'END_SOLUTION': lambda: '',
        'BEGIN_HINT': lambda: '',
        'END_HINT': lambda: '',
    }

    # Add MathObjects if available (only add what exists)
    if HAS_PG_MATH:
        math_objects = {}
        # Try to import each object, skip if not available
        for name in ['Context', 'Compute', 'Formula', 'Real', 'Complex',
                     'Point', 'Vector', 'Matrix', 'Interval', 'Set', 'Union',
                     'List', 'String', 'Infinity', 'FormulaUpToConstant']:
            if hasattr(pg_math, name):
                math_objects[name] = getattr(pg_math, name)

        # Try Fraction separately (may need special import)
        try:
            from pg.math.fraction import Fraction
            math_objects['Fraction'] = Fraction
        except (ImportError, AttributeError):
            pass

        namespace.update(math_objects)

    # Add choice macros if available
    if HAS_CHOICE:
        namespace['MultipleChoice'] = MultipleChoice
        namespace['new_multiple_choice'] = new_multiple_choice

    # Add popup if available
    if HAS_POPUP:
        namespace['PopUp'] = PopUp

    # Add multianswer if available
    if HAS_MULTIANSWER:
        namespace['MultiAnswer'] = MultiAnswer

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
    answers = []

    if HAS_PG_ENV:
        try:
            # Get the environment that DOCUMENT() created
            from pg.macros.core.pg_core import get_environment
            pg_env = get_environment()

            # Get text from PGEnvironment
            output_text = ''.join(pg_env.output_array)

            # Get answers from PGEnvironment
            for name, evaluator in pg_env.answers_hash.items():
                answers.append({
                    'name': name,
                    'correct': False,
                    'score': 0.0,
                    'message': '',
                    'type': type(evaluator).__name__ if evaluator else 'unknown',
                })
        except (RuntimeError, AttributeError, ImportError) as e:
            print(f"Warning: Could not get PGEnvironment: {e}", file=sys.stderr)
            # Fallback to legacy buffers
            if hasattr(pgcore, '_output_buffer'):
                output_text = ''.join(str(x) for x in pgcore._output_buffer)

            if hasattr(pgcore, '_answers'):
                for name, evaluator in pgcore._answers.items():
                    answers.append({
                        'name': name,
                        'correct': False,
                        'score': 0.0,
                        'message': '',
                        'type': type(evaluator).__name__ if evaluator else 'unknown',
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
        for error in output['errors'][:5]:  # Limit to first 5
            print(f"    {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
