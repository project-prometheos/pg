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
    
    # Fix PGML import - replace incorrect import with comment
    # The PGML function will be added to namespace below
    if 'from pg.pgml import PGML' in result.code:
        result.code = result.code.replace(
            'from pg.pgml import PGML',
            '# from pg.pgml import PGML  # Fixed: PGML added to namespace below'
        )

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
        from pg.macros.choice import (
            MultipleChoice,
            CheckboxMultipleChoice,
            TrueFalse,
            new_multiple_choice,
            new_checkbox_multiple_choice,
            new_true_false,
        )
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

    HAS_ANSWER_CMP = False
    try:
        from pg.answer import radio_cmp, checkbox_cmp, num_cmp, str_cmp, fun_cmp
        HAS_ANSWER_CMP = True
    except ImportError:
        print("Warning: pg.answer.cmp not found", file=sys.stderr)

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

    # Add PGML if available - use renderer that registers answer blanks
    try:
        from pg.renderer.pgml import PGMLRenderer
        from pg.macros.core.pg_core import get_environment, ANS
        
        def PGML(pgml_text: str) -> str:
            """Render PGML and register answer blanks."""
            # Create renderer with access to namespace variables
            renderer = PGMLRenderer(variables=namespace)
            
            # Render PGML to HTML and extract answer blanks
            rendered_html, answer_blanks = renderer.render(pgml_text)
            
            # Register answer blanks in environment
            env = get_environment()
            for ans_name, ans_spec in answer_blanks.items():
                if isinstance(ans_spec, dict) and 'evaluator' in ans_spec:
                    # PGML spec format - register the evaluator
                    env.register_answer(ans_name, ans_spec['evaluator'])
                elif hasattr(ans_spec, 'cmp') or hasattr(ans_spec, 'evaluate'):
                    # It's an evaluator object
                    env.register_answer(ans_name, ans_spec)
                else:
                    # Simple value - create a basic evaluator
                    env.register_answer(ans_name, ans_spec)
            
            return rendered_html
        
        namespace['PGML'] = PGML
    except (ImportError, AttributeError) as e:
        # Fallback: try standard PGML
        try:
            from pg.macros.core.pgml import PGML
            namespace['PGML'] = PGML
        except (ImportError, AttributeError):
            print(f"Warning: PGML not found: {e}", file=sys.stderr)

    # Add MathObjects if available (only add what exists)
    if HAS_PG_MATH:
        math_objects = {}
        # Try to import each object, skip if not available
        for name in ['Context', 'Compute', 'Formula', 'Real', 'Complex',
                     'Point', 'Vector', 'Matrix', 'Interval', 'Set', 'Union',
                     'List', 'String', 'Infinity', 'FormulaUpToConstant', 'norm']:
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
        namespace['CheckboxMultipleChoice'] = CheckboxMultipleChoice
        namespace['TrueFalse'] = TrueFalse
        namespace['new_multiple_choice'] = new_multiple_choice
        namespace['new_checkbox_multiple_choice'] = new_checkbox_multiple_choice
        namespace['new_true_false'] = new_true_false

    # Add answer checkers if available
    if HAS_ANSWER_CMP:
        namespace['radio_cmp'] = radio_cmp
        namespace['checkbox_cmp'] = checkbox_cmp
        namespace['num_cmp'] = num_cmp
        namespace['str_cmp'] = str_cmp
        namespace['fun_cmp'] = fun_cmp

    # Add popup if available
    if HAS_POPUP:
        namespace['PopUp'] = PopUp

    # Add multianswer if available
    if HAS_MULTIANSWER:
        namespace['MultiAnswer'] = MultiAnswer
    
    # Add AnswerFormatHelp (wrapper around helpLink)
    try:
        from pg.macros.core.pgml_utils import helpLink
        
        def AnswerFormatHelp(helptype: str, customstring: str = None) -> str:
            """Generate help link for answer formatting (deprecated, use helpLink)."""
            return helpLink(helptype, customstring) if customstring else helpLink(helptype)
        
        namespace['AnswerFormatHelp'] = AnswerFormatHelp
        namespace['helpLink'] = helpLink
    except (ImportError, AttributeError):
        # Fallback: simple stub
        def AnswerFormatHelp(helptype: str, customstring: str = None) -> str:
            return f'<a href="/help/{helptype}">Help</a>'
        namespace['AnswerFormatHelp'] = AnswerFormatHelp

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

            # First, get correct answers directly from environment's evaluators
            # This is similar to how Perl adapter uses WeBWorK::PG with processAnswers => 1
            correct_answers = {}
            # Extract correct answers directly from pg_env.answers_hash
            for ans_name, ans_entry in pg_env.answers_hash.items():
                try:
                    # Extract evaluator from answer entry
                    evaluator = ans_entry
                    if isinstance(ans_entry, dict):
                        evaluator = ans_entry.get('ans_eval', ans_entry.get('evaluator', ans_entry))
                    
                    # Get correct answer from evaluator
                    if evaluator:
                        # Check if this is a MultiAnswerEvaluator (has multianswer attribute)
                        multianswer_obj = None
                        if hasattr(evaluator, 'multianswer'):
                            multianswer_obj = evaluator.multianswer
                        elif hasattr(evaluator, 'correct_answers') and isinstance(evaluator.correct_answers, (list, tuple)):
                            multianswer_obj = evaluator
                        elif hasattr(evaluator, 'answers') and isinstance(evaluator.answers, (list, tuple)):
                            multianswer_obj = evaluator
                        
                        if multianswer_obj and hasattr(multianswer_obj, 'correct_answers'):
                            # For MultiAnswer, store the list of correct answers
                            answer_list = multianswer_obj.correct_answers
                            if answer_list:
                                # Convert each answer to string
                                answer_strs = []
                                for a in answer_list:
                                    if hasattr(a, 'to_string'):
                                        answer_strs.append(a.to_string())
                                    elif hasattr(a, '__str__'):
                                        answer_strs.append(str(a))
                                    else:
                                        answer_strs.append(str(a))
                                # Store as comma-separated string for display
                                correct_answers[ans_name] = ', '.join(answer_strs)
                        # Try correct_answer first
                        elif hasattr(evaluator, 'correct_answer'):
                            correct_answers[ans_name] = evaluator.correct_answer
                        # Try correct_value (for RealAnswerChecker, etc.)
                        elif hasattr(evaluator, 'correct_value'):
                            correct_val = evaluator.correct_value
                            # Convert to string if it's a MathValue
                            if hasattr(correct_val, 'to_string'):
                                correct_answers[ans_name] = correct_val.to_string()
                            elif hasattr(correct_val, '__str__'):
                                correct_answers[ans_name] = str(correct_val)
                            else:
                                correct_answers[ans_name] = correct_val
                        # Try PopUp/DropDown correct attribute
                        elif hasattr(evaluator, 'correct'):
                            correct_answers[ans_name] = str(evaluator.correct)
                        # Try MathObject methods (for direct Real/Formula evaluators)
                        elif hasattr(evaluator, 'to_string'):
                            correct_answers[ans_name] = evaluator.to_string()
                        elif hasattr(evaluator, 'string') and callable(evaluator.string):
                            correct_answers[ans_name] = evaluator.string()
                        elif hasattr(evaluator, 'value'):
                            # For Real numbers, get the numeric value
                            val = evaluator.value
                            if isinstance(val, float) and val.is_integer():
                                correct_answers[ans_name] = str(int(val))
                            else:
                                correct_answers[ans_name] = str(val)
                        # If evaluator is a string, it might be a numeric value
                        elif isinstance(evaluator, str):
                            # Try to parse as number
                            try:
                                val = float(evaluator)
                                if val.is_integer():
                                    correct_answers[ans_name] = str(int(val))
                                else:
                                    correct_answers[ans_name] = evaluator  # Keep original string
                            except ValueError:
                                correct_answers[ans_name] = evaluator  # Keep as string
                        elif hasattr(evaluator, 'answer'):
                            correct_answers[ans_name] = evaluator.answer
                        # Check if evaluator is a function (from PopUp.cmp())
                        elif callable(evaluator) and not isinstance(evaluator, type):
                            # Try to extract from function closure
                            try:
                                if hasattr(evaluator, '__closure__') and evaluator.__closure__:
                                    for cell in evaluator.__closure__:
                                        cell_val = cell.cell_contents
                                        # Check if it's a PopUp object
                                        if cell_val and hasattr(cell_val, 'correct'):
                                            correct_answers[ans_name] = str(cell_val.correct)
                                            break
                                        # Or check if it's the correct value directly (string)
                                        elif isinstance(cell_val, str) and cell_val:
                                            correct_answers[ans_name] = cell_val
                                            break
                            except Exception:
                                pass
                        # Also try accessing through ans_eval if it's a dict
                        elif isinstance(evaluator, dict) and 'ans_eval' in evaluator:
                            ans_eval = evaluator['ans_eval']
                            # Check for MultiAnswerEvaluator or MultiAnswer in ans_eval
                            multianswer_obj = None
                            if hasattr(ans_eval, 'multianswer'):
                                multianswer_obj = ans_eval.multianswer
                            elif hasattr(ans_eval, 'correct_answers') and isinstance(ans_eval.correct_answers, (list, tuple)):
                                multianswer_obj = ans_eval
                            
                            if multianswer_obj and hasattr(multianswer_obj, 'correct_answers'):
                                answer_list = multianswer_obj.correct_answers
                                if answer_list:
                                    answer_strs = []
                                    for a in answer_list:
                                        if hasattr(a, 'to_string'):
                                            answer_strs.append(a.to_string())
                                        else:
                                            answer_strs.append(str(a))
                                    correct_answers[ans_name] = ', '.join(answer_strs)
                            elif hasattr(ans_eval, 'correct_answer'):
                                correct_answers[ans_name] = ans_eval.correct_answer
                            elif hasattr(ans_eval, 'correct_value'):
                                correct_val = ans_eval.correct_value
                                if hasattr(correct_val, 'to_string'):
                                    correct_answers[ans_name] = correct_val.to_string()
                                else:
                                    correct_answers[ans_name] = str(correct_val)
                            elif hasattr(ans_eval, 'correct'):
                                correct_answers[ans_name] = str(ans_eval.correct)
                            elif hasattr(ans_eval, 'to_string'):
                                correct_answers[ans_name] = ans_eval.to_string()
                            elif hasattr(ans_eval, 'string') and callable(ans_eval.string):
                                correct_answers[ans_name] = ans_eval.string()
                            elif hasattr(ans_eval, 'value'):
                                val = ans_eval.value
                                if isinstance(val, float) and val.is_integer():
                                    correct_answers[ans_name] = str(int(val))
                                else:
                                    correct_answers[ans_name] = str(val)
                            elif hasattr(ans_eval, 'answer'):
                                correct_answers[ans_name] = ans_eval.answer
                except Exception:
                    pass

            # Get answers from PGEnvironment and evaluate them
            for name, ans_data in pg_env.answers_hash.items():
                # Extract evaluator from answer data
                # It might be stored as {"ans_eval": evaluator} or directly as evaluator
                evaluator = ans_data
                if isinstance(ans_data, dict):
                    evaluator = ans_data.get('ans_eval', ans_data.get('evaluator', ans_data))
                
                # Try to get the correct answer and evaluate it
                correct_value = None
                
                # If evaluator is a function (from PopUp.cmp()), try to get the correct value
                # The function might have a closure that contains the correct value
                if callable(evaluator) and not isinstance(evaluator, type):
                    # Try to extract from function closure
                    try:
                        if hasattr(evaluator, '__closure__') and evaluator.__closure__:
                            for cell in evaluator.__closure__:
                                cell_val = cell.cell_contents
                                # Check if it's a PopUp object
                                if cell_val and hasattr(cell_val, 'correct'):
                                    # Found PopUp object in closure
                                    evaluator = cell_val
                                    break
                                # Or check if it's the correct value directly (string)
                                elif isinstance(cell_val, str) and cell_val:
                                    # Might be the correct answer string
                                    correct_value = cell_val
                                    break
                    except Exception:
                        pass
                score = 0.0
                is_correct = False
                message = ''
                
                # First try to get from correct_answers dict (from translator)
                if name in correct_answers:
                    correct_value = correct_answers[name]
                # Also try alternative name format (AnSwEr0001 vs AnSwEr1)
                elif name.startswith('AnSwEr') and len(name) > 6:
                    try:
                        num = int(name[6:])
                        # Try AnSwEr1 format
                        alt_name = f"AnSwEr{num}"
                        if alt_name in correct_answers:
                            correct_value = correct_answers[alt_name]
                    except ValueError:
                        pass
                
                # If not found, try to get from evaluator directly
                if correct_value is None:
                    try:
                        # Check for MultiAnswerEvaluator first
                        multianswer_obj = None
                        if hasattr(evaluator, 'multianswer'):
                            multianswer_obj = evaluator.multianswer
                        elif hasattr(evaluator, 'correct_answers') and isinstance(evaluator.correct_answers, (list, tuple)):
                            multianswer_obj = evaluator
                        
                        if multianswer_obj and hasattr(multianswer_obj, 'correct_answers'):
                            # For MultiAnswer, get the list and convert to string
                            answer_list = multianswer_obj.correct_answers
                            if answer_list:
                                answer_strs = []
                                for a in answer_list:
                                    if hasattr(a, 'to_string'):
                                        answer_strs.append(a.to_string())
                                    else:
                                        answer_strs.append(str(a))
                                correct_value = ', '.join(answer_strs)
                        # Get correct answer from evaluator
                        # Evaluators should have correct_answer or correct_value attribute
                        # Or it might be a MathObject directly (Real, Formula, etc.)
                        elif hasattr(evaluator, 'correct_answer'):
                            correct_value = evaluator.correct_answer
                        elif hasattr(evaluator, 'correct_value'):
                            correct_val = evaluator.correct_value
                            if hasattr(correct_val, 'to_string'):
                                correct_value = correct_val.to_string()
                            else:
                                correct_value = str(correct_val)
                        # Try PopUp/DropDown correct attribute
                        elif hasattr(evaluator, 'correct'):
                            correct_value = str(evaluator.correct)
                        # Try MathObject methods (for direct Real/Formula evaluators)
                        elif hasattr(evaluator, 'to_string'):
                            correct_value = evaluator.to_string()
                        elif hasattr(evaluator, 'string') and callable(evaluator.string):
                            correct_value = evaluator.string()
                        elif hasattr(evaluator, 'value'):
                            # For Real numbers, get the numeric value
                            val = evaluator.value
                            if isinstance(val, float) and val.is_integer():
                                correct_value = str(int(val))
                            else:
                                correct_value = str(val)
                        # If evaluator is a string, it might be a numeric value
                        elif isinstance(evaluator, str):
                            # Try to parse as number
                            try:
                                val = float(evaluator)
                                if val.is_integer():
                                    correct_value = str(int(val))
                                else:
                                    correct_value = evaluator  # Keep original string
                            except ValueError:
                                correct_value = evaluator  # Keep as string
                        elif isinstance(evaluator, dict) and 'correct_answer' in evaluator:
                            correct_value = evaluator['correct_answer']
                        elif hasattr(evaluator, 'answer'):
                            correct_value = evaluator.answer
                        elif isinstance(evaluator, dict) and 'answer' in evaluator:
                            correct_value = evaluator['answer']
                        # Try accessing through ans_eval if it's a dict
                        elif isinstance(evaluator, dict) and 'ans_eval' in evaluator:
                            ans_eval = evaluator['ans_eval']
                            if hasattr(ans_eval, 'correct_answer'):
                                correct_value = ans_eval.correct_answer
                            elif hasattr(ans_eval, 'correct_value'):
                                correct_val = ans_eval.correct_value
                                if hasattr(correct_val, 'to_string'):
                                    correct_value = correct_val.to_string()
                                else:
                                    correct_value = str(correct_val)
                            elif hasattr(ans_eval, 'correct'):
                                correct_value = str(ans_eval.correct)
                            elif hasattr(ans_eval, 'to_string'):
                                correct_value = ans_eval.to_string()
                            elif hasattr(ans_eval, 'string') and callable(ans_eval.string):
                                correct_value = ans_eval.string()
                            elif hasattr(ans_eval, 'value'):
                                val = ans_eval.value
                                if isinstance(val, float) and val.is_integer():
                                    correct_value = str(int(val))
                                else:
                                    correct_value = str(val)
                            elif hasattr(ans_eval, 'answer'):
                                correct_value = ans_eval.answer
                    except Exception:
                        pass
                
                # Convert correct answer to string for evaluation
                if correct_value is not None:
                    if hasattr(correct_value, 'to_string'):
                        correct_str = correct_value.to_string()
                    elif hasattr(correct_value, '__str__'):
                        correct_str = str(correct_value)
                    else:
                        correct_str = str(correct_value)
                    
                    # Evaluate the correct answer against itself
                    if hasattr(evaluator, 'evaluate'):
                        result = evaluator.evaluate(correct_str)
                        if hasattr(result, 'score'):
                            score = float(result.score)
                            is_correct = score >= 1.0
                            message = getattr(result, 'answer_message', '') or ''
                        elif isinstance(result, dict):
                            score = float(result.get('score', 0.0))
                            is_correct = score >= 1.0
                            message = result.get('message', '') or ''
                    elif hasattr(evaluator, 'cmp'):
                        # Try using cmp() method
                        checker = evaluator.cmp()
                        if hasattr(checker, 'check'):
                            check_result = checker.check(correct_str)
                            if isinstance(check_result, dict):
                                score = float(check_result.get('score', 0.0))
                                is_correct = score >= 1.0
                                message = check_result.get('message', '') or ''
                
                answers.append({
                    'name': name,
                    'correct': is_correct,
                    'score': score,
                    'message': message,
                    'correct_value': str(correct_value) if correct_value is not None else None,
                    'type': type(evaluator).__name__ if evaluator else 'unknown',
                })
        except (RuntimeError, AttributeError, ImportError) as e:
            print(f"Warning: Could not get PGEnvironment: {e}", file=sys.stderr)
            # Fallback to legacy buffers
            if hasattr(pgcore, '_output_buffer'):
                output_text = ''.join(str(x) for x in pgcore._output_buffer)

            if hasattr(pgcore, '_answers'):
                # Try to get correct answers from translator first
                correct_answers = {}
                try:
                    from pg.translator.translator import PGTranslator
                    translator = PGTranslator()
                    result = translator.translate(content, seed=seed, inputs={})
                    if hasattr(result, 'answer_blanks'):
                        for blank_name, blank_info in result.answer_blanks.items():
                            if blank_info and isinstance(blank_info, dict):
                                evaluator = blank_info.get('evaluator')
                                if evaluator:
                                    if isinstance(evaluator, dict):
                                        ans_eval = evaluator.get('ans_eval', evaluator)
                                    else:
                                        ans_eval = evaluator
                                    if hasattr(ans_eval, 'correct_answer'):
                                        correct_answers[blank_name] = ans_eval.correct_answer
                                    elif hasattr(ans_eval, 'answer'):
                                        correct_answers[blank_name] = ans_eval.answer
                except Exception:
                    pass
                
                for name, evaluator in pgcore._answers.items():
                    # Try to evaluate the correct answer
                    correct_value = None
                    score = 0.0
                    is_correct = False
                    message = ''
                    
                    # Try to get from correct_answers dict first
                    if name in correct_answers:
                        correct_value = correct_answers[name]
                    else:
                        try:
                            if hasattr(evaluator, 'correct_answer'):
                                correct_value = evaluator.correct_answer
                            elif hasattr(evaluator, 'correct_value'):
                                correct_val = evaluator.correct_value
                                if hasattr(correct_val, 'to_string'):
                                    correct_value = correct_val.to_string()
                                else:
                                    correct_value = str(correct_val)
                            elif hasattr(evaluator, 'answer'):
                                correct_value = evaluator.answer
                        except Exception:
                            pass
                    
                    if correct_value is not None:
                        try:
                            correct_str = str(correct_value)
                            if hasattr(evaluator, 'evaluate'):
                                result = evaluator.evaluate(correct_str)
                                if hasattr(result, 'score'):
                                    score = float(result.score)
                                    is_correct = score >= 1.0
                                    message = getattr(result, 'answer_message', '') or ''
                        except Exception:
                            pass
                    
                    answers.append({
                        'name': name,
                        'correct': is_correct,
                        'score': score,
                        'message': message,
                        'correct_value': str(correct_value) if correct_value is not None else None,
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
