"""
In-Process Sandbox for PG Code Execution.

Provides safe in-process execution with:
- Restricted builtins (no eval, exec, __import__, open, etc.)
- Macro function integration
- Direct access to evaluator objects (no serialization)
- Timeout protection

This matches the Perl PG Safe compartment architecture.
"""

from __future__ import annotations

import signal
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable

from pg_parser import Context


@dataclass
class ExecutionResult:
    """Result from in-process execution."""

    success: bool
    """Whether execution succeeded"""

    output_text: str
    """Accumulated problem text"""

    answers: dict[str, Any]
    """Answer evaluators by name"""

    solution_text: str | None = None
    """Solution text if any"""

    hint_text: str | None = None
    """Hint text if any"""

    errors: str = ""
    """Error messages"""

    variables: dict[str, Any] = field(default_factory=dict)
    """Problem variables"""


class TimeoutError(Exception):
    """Execution timeout exceeded."""
    pass


class InProcessSandbox:
    """
    Safe in-process code execution sandbox.

    Executes PG code in a restricted namespace with:
    - Limited builtins (no dangerous functions)
    - Macro functions available
    - PGEnvironment integration
    - Timeout protection (Unix only)
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize sandbox.

        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
        self.namespace: dict[str, Any] = {}
        self._pg_environment = None
        self._setup_safe_namespace()

    def _setup_safe_namespace(self) -> None:
        """Setup namespace with safe builtins only."""
        # Safe built-in functions
        safe_builtins = {
            # Type constructors
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'tuple': tuple,
            'dict': dict,
            'set': set,
            # Math functions
            'abs': abs,
            'round': round,
            'pow': pow,
            'min': min,
            'max': max,
            'sum': sum,
            # Utilities
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'reversed': reversed,
            'all': all,
            'any': any,
            # String functions
            'chr': chr,
            'ord': ord,
            # Type checking
            'isinstance': isinstance,
            'issubclass': issubclass,
            'type': type,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            # Constants
            'True': True,
            'False': False,
            'None': None,
            # Exceptions (needed for try/except)
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'IndexError': IndexError,
            'AttributeError': AttributeError,
            'ZeroDivisionError': ZeroDivisionError,
        }

        # Allow controlled __import__ for specific modules
        import builtins
        original_import = builtins.__import__

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            """Allow importing only safe modules."""
            # Allow pg_mathobjects and its submodules
            if name.startswith('pg_mathobjects'):
                return original_import(name, globals, locals, fromlist, level)
            # Allow math and random (already in namespace but allow re-import)
            if name in ('math', 'random'):
                return original_import(name, globals, locals, fromlist, level)
            # Block everything else
            raise ImportError(f"Import of '{name}' is not allowed in sandbox")

        safe_builtins['__import__'] = safe_import

        # Restricted builtins dict
        self.namespace['__builtins__'] = safe_builtins

        # Import safe modules
        import math
        import random
        self.namespace['math'] = math
        self.namespace['random'] = random

        # Add common mathematical constants
        self.namespace['pi'] = math.pi
        self.namespace['e'] = math.e

        # Load MathObjects
        self._load_mathobjects()

        # Load core PG macros by default
        self._load_pg_core()
        self._load_pg_basic_macros()
        self._load_pg_answer_macros()

        # Load additional context macros (stubs)
        self._load_context_macros()

    def _load_mathobjects(self) -> None:
        """Load MathObjects framework into namespace."""
        try:
            # Import MathObjects
            from pg_mathobjects import Context, Formula, Real, Compute
            from pg_mathobjects.formula_up_to_constant import FormulaUpToConstant

            # Make available in namespace
            self.namespace['Context'] = Context
            self.namespace['Formula'] = Formula
            self.namespace['Real'] = Real
            self.namespace['Compute'] = Compute
            self.namespace['FormulaUpToConstant'] = FormulaUpToConstant

        except ImportError:
            # Fallback: provide minimal stubs
            def Context(name=None):
                """Stub Context function."""
                return None

            def Formula(expr):
                """Stub Formula function - returns string."""
                return str(expr)

            def Real(value):
                """Stub Real function - returns float."""
                return float(value)

            def Compute(expr):
                """Stub Compute function - tries to eval."""
                try:
                    return eval(str(expr))
                except:
                    return str(expr)

            self.namespace['Context'] = Context
            self.namespace['Formula'] = Formula
            self.namespace['Real'] = Real
            self.namespace['Compute'] = Compute

    def load_macros(self, *macro_names: str) -> None:
        """
        Load PG macro modules into namespace.

        Args:
            *macro_names: Macro names (e.g., "PG.pl", "PGbasicmacros.pl")
        """
        for macro_name in macro_names:
            if macro_name in ("PG.pl", "pg_core"):
                self._load_pg_core()
            elif macro_name in ("PGbasicmacros.pl", "pg_basic_macros"):
                self._load_pg_basic_macros()
            elif macro_name in ("PGanswermacros.pl", "pg_answer_macros"):
                self._load_pg_answer_macros()

    def _load_pg_core(self) -> None:
        """Load PG core macros."""
        try:
            from pg_macros.core import pg_core

            # Define PGML function (not in pg_core)
            def PGML(pgml_text):
                """Render PGML markup to HTML."""
                from pg_pgml import PGMLParser, HTMLRenderer
                from pg_pgml.parser import AnswerBlank

                # Get current namespace for variable access
                context = self.namespace

                # Parse PGML text using the proper tokenizer/parser
                doc = PGMLParser.parse_text(pgml_text)

                # Collect answer blanks from the document tree
                answer_blanks = []
                visited = set()  # Track visited nodes to prevent infinite loops

                def collect_answer_blanks(node, depth=0):
                    """Recursively collect AnswerBlank nodes."""
                    if depth > 50:  # Prevent stack overflow
                        return

                    # Prevent revisiting the same node
                    node_id = id(node)
                    if node_id in visited:
                        return
                    visited.add(node_id)

                    if isinstance(node, AnswerBlank):
                        answer_blanks.append(node)
                        return  # Don't recurse into AnswerBlank itself

                    # Check for children in various node types
                    if hasattr(node, 'blocks') and node.blocks:
                        for child in node.blocks:
                            collect_answer_blanks(child, depth + 1)
                    if hasattr(node, 'content') and isinstance(node.content, list):
                        for child in node.content:
                            collect_answer_blanks(child, depth + 1)
                    if hasattr(node, 'items') and node.items:
                        for item in node.items:
                            collect_answer_blanks(item, depth + 1)

                # Start collection from document root
                collect_answer_blanks(doc)

                # Evaluate evaluator expressions and register answers
                for blank in answer_blanks:
                    if blank.evaluator_code:
                        try:
                            # Remove Perl $ sigil before evaluation
                            eval_expr = blank.evaluator_code.lstrip('$')
                            # Evaluate in current namespace
                            evaluator = eval(eval_expr, {}, context)
                            # Register with ANS()
                            pg_core.ANS(evaluator)
                        except Exception:
                            # If evaluation fails, skip this answer blank
                            pass

                # Render PGML to HTML using proper renderer
                renderer = HTMLRenderer(context=context)
                return renderer.render(doc)

            # Register core functions
            self.namespace.update({
                'DOCUMENT': pg_core.DOCUMENT,
                'ENDDOCUMENT': pg_core.ENDDOCUMENT,
                'TEXT': pg_core.TEXT,
                'BEGIN_TEXT': pg_core.BEGIN_TEXT,
                'END_TEXT': pg_core.END_TEXT,
                'ANS': pg_core.ANS,
                'NAMED_ANS': pg_core.NAMED_ANS,
                'NEW_ANS_NAME': pg_core.NEW_ANS_NAME,
                'SOLUTION': pg_core.SOLUTION,
                'HINT': pg_core.HINT,
                'COMMENT': pg_core.COMMENT,
                'PGML': PGML,
                'random': pg_core.random,
                'non_zero_random': pg_core.non_zero_random,
                'list_random': pg_core.list_random,
                'loadMacros': pg_core.loadMacros,
                'PGEnvironment': pg_core.PGEnvironment,
                'set_environment': pg_core.set_environment,
                'get_environment': pg_core.get_environment,
            })

            # Store reference for initialization
            self._pg_core = pg_core

        except ImportError:
            # Fallback: provide stub implementations
            self._load_pg_core_stubs()

    def _load_pg_core_stubs(self) -> None:
        """Load stub implementations if pg_core not available."""
        # Simple stub environment
        class StubEnvironment:
            def __init__(self, envir):
                self.data = envir  # Store namespace for PGML variable access
                self.output_array = []
                self.answers_hash = {}
                self.solution_array = []
                self.hint_array = []
                self._answer_counter = 0

            def append_text(self, text):
                self.output_array.append(str(text))

            def new_ans_name(self):
                self._answer_counter += 1
                return f"AnSwEr{self._answer_counter:04d}"

        _env = StubEnvironment(self.namespace)

        def DOCUMENT(): pass
        def ENDDOCUMENT(): pass
        def TEXT(*args): _env.append_text(''.join(str(a) for a in args))
        def BEGIN_TEXT(): return ''
        def END_TEXT(): return ''

        def ANS(*evaluators):
            for ev in evaluators:
                name = _env.new_ans_name()
                _env.answers_hash[name] = ev

        def NAMED_ANS(name, evaluator):
            _env.answers_hash[name] = evaluator

        def NEW_ANS_NAME(): return _env.new_ans_name()
        def SOLUTION(*args): _env.solution_array.extend(str(a) for a in args)
        def HINT(*args): _env.hint_array.extend(str(a) for a in args)
        def COMMENT(*args): pass

        # PGML rendering function
        def PGML(pgml_text):
            """Render PGML markup to HTML (fallback mode without pg_core)."""
            from pg_pgml import PGMLParser, HTMLRenderer
            from pg_pgml.parser import AnswerBlank

            # Get current namespace for variable access
            context = self.namespace

            # Parse PGML text using the proper tokenizer/parser
            doc = PGMLParser.parse_text(pgml_text)

            # Collect answer blanks from the document tree
            answer_blanks = []
            visited = set()  # Track visited nodes to prevent infinite loops

            def collect_answer_blanks(node, depth=0):
                """Recursively collect AnswerBlank nodes."""
                if depth > 50:  # Prevent stack overflow
                    return

                # Prevent revisiting the same node
                node_id = id(node)
                if node_id in visited:
                    return
                visited.add(node_id)

                if isinstance(node, AnswerBlank):
                    answer_blanks.append(node)
                    return  # Don't recurse into AnswerBlank itself

                # Check for children in various node types
                if hasattr(node, 'blocks') and node.blocks:
                    for child in node.blocks:
                        collect_answer_blanks(child, depth + 1)
                if hasattr(node, 'content') and isinstance(node.content, list):
                    for child in node.content:
                        collect_answer_blanks(child, depth + 1)
                if hasattr(node, 'items') and node.items:
                    for item in node.items:
                        collect_answer_blanks(item, depth + 1)

            # Start collection from document root
            collect_answer_blanks(doc)

            # Evaluate evaluator expressions and register answers
            for blank in answer_blanks:
                if blank.evaluator_code:
                    try:
                        # Remove Perl $ sigil before evaluation
                        eval_expr = blank.evaluator_code.lstrip('$')
                        # Evaluate in current namespace
                        evaluator = eval(eval_expr, {}, context)
                        # Register with ANS()
                        ANS(evaluator)
                    except Exception:
                        # If evaluation fails, skip this answer blank
                        pass

            # Render PGML to HTML using proper renderer
            renderer = HTMLRenderer(context=context)
            return renderer.render(doc)

        # Random functions (don't shadow random module)
        import random as _random_module

        def pg_random(a=0, b=1, step=None):
            if step:
                return a + _random_module.randint(0, int((b-a)/step)) * step
            return a + _random_module.random() * (b - a)

        def non_zero_random(a, b, step=None):
            while True:
                v = pg_random(a, b, step)
                if v != 0:
                    return v

        def list_random(*items):
            return _random_module.choice(items)

        def loadMacros(*args): pass
        def get_environment(): return _env
        def set_environment(env): pass

        self.namespace.update({
            'DOCUMENT': DOCUMENT,
            'ENDDOCUMENT': ENDDOCUMENT,
            'TEXT': TEXT,
            'PGML': PGML,
            'BEGIN_TEXT': BEGIN_TEXT,
            'END_TEXT': END_TEXT,
            'ANS': ANS,
            'NAMED_ANS': NAMED_ANS,
            'NEW_ANS_NAME': NEW_ANS_NAME,
            'SOLUTION': SOLUTION,
            'HINT': HINT,
            'COMMENT': COMMENT,
            'random': pg_random,
            'non_zero_random': non_zero_random,
            'list_random': list_random,
            'loadMacros': loadMacros,
            'get_environment': get_environment,
            'set_environment': set_environment,
            # Add a dummy macro loader to suppress warnings
            # Macros are pre-loaded, so this just prevents the warning
            '_macro_loader': type('DummyLoader', (), {'load_macro': lambda self, x: None})(),
        })

        self._stub_env = _env

    def _load_pg_basic_macros(self) -> None:
        """Load PG basic macros."""
        try:
            from pg_macros.core import pg_basic_macros

            # Register basic macro functions
            self.namespace.update({
                'ans_rule': pg_basic_macros.ans_rule,
                'ans_box': pg_basic_macros.ans_box,
                'ans_radio_buttons': pg_basic_macros.ans_radio_buttons,
                'pop_up_list': pg_basic_macros.pop_up_list,
                'NAMED_ANS_RULE': pg_basic_macros.NAMED_ANS_RULE,
                'NAMED_ANS_BOX': pg_basic_macros.NAMED_ANS_BOX,
                'NAMED_ANS_RADIO_BUTTONS': pg_basic_macros.NAMED_ANS_RADIO_BUTTONS,
                'NAMED_POP_UP_LIST': pg_basic_macros.NAMED_POP_UP_LIST,
                'beginproblem': pg_basic_macros.beginproblem,
                'PAR': pg_basic_macros.PAR,
                'BR': pg_basic_macros.BR,
                'BBOLD': pg_basic_macros.BBOLD,
                'EBOLD': pg_basic_macros.EBOLD,
                'BITALIC': pg_basic_macros.BITALIC,
                'EITALIC': pg_basic_macros.EITALIC,
                'BCENTER': pg_basic_macros.BCENTER,
                'ECENTER': pg_basic_macros.ECENTER,
                'BUL': pg_basic_macros.BUL,
                'EUL': pg_basic_macros.EUL,
                'MODES': pg_basic_macros.MODES,
                'image': pg_basic_macros.image,
                'PI': pg_basic_macros.PI,
                'E': pg_basic_macros.E,
            })

        except ImportError:
            # Fallback: provide stub implementations
            self._load_pg_basic_macros_stubs()

    def _load_pg_basic_macros_stubs(self) -> None:
        """Load stub implementations for basic macros."""
        def ans_rule(width=20):
            env = self.namespace.get(
                'get_environment', lambda: self._stub_env)()
            name = env.new_ans_name()
            return f'<input type="text" name="{name}" size="{width}"/>'

        def ans_box(rows=5, cols=20):
            env = self.namespace.get(
                'get_environment', lambda: self._stub_env)()
            name = env.new_ans_name()
            return f'<textarea name="{name}" rows="{rows}" cols="{cols}"></textarea>'

        def beginproblem(): return ""
        def PAR(): return '<p>'
        def BR(): return '<br/>'
        def BBOLD(): return '<strong>'
        def EBOLD(): return '</strong>'
        def BITALIC(): return '<em>'
        def EITALIC(): return '</em>'
        def BCENTER(): return '<div style="text-align:center;">'
        def ECENTER(): return '</div>'
        def BUL(): return '<u>'
        def EUL(): return '</u>'
        def MODES(**kwargs): return kwargs.get('HTML', '')
        def image(filename, **opts): return f'<img src="{filename}"/>'

        import math
        def PI(): return math.pi
        def E(): return math.e

        self.namespace.update({
            'ans_rule': ans_rule,
            'ans_box': ans_box,
            'beginproblem': beginproblem,
            'PAR': PAR,
            'BR': BR,
            'BBOLD': BBOLD,
            'EBOLD': EBOLD,
            'BITALIC': BITALIC,
            'EITALIC': EITALIC,
            'BCENTER': BCENTER,
            'ECENTER': ECENTER,
            'BUL': BUL,
            'EUL': EUL,
            'MODES': MODES,
            'image': image,
            'PI': PI,
            'E': E,
        })

    def _load_pg_answer_macros(self) -> None:
        """Load PG answer checker macros."""
        try:
            from pg_answer.evaluators import NumericEvaluator, StringEvaluator, FormulaEvaluator

            def num_cmp(correct, **options):
                return NumericEvaluator(correct_answer=correct, **options)

            def str_cmp(correct, **options):
                return StringEvaluator(correct_answer=correct, **options)

            def fun_cmp(correct, **options):
                return FormulaEvaluator(correct_answer=correct, **options)

            self.namespace.update({
                'num_cmp': num_cmp,
                'str_cmp': str_cmp,
                'fun_cmp': fun_cmp,
            })

        except ImportError:
            # Fallback: simple stub evaluators
            class StubEvaluator:
                def __init__(self, correct_answer, **options):
                    self.correct_answer = correct_answer
                    self.options = options

                def evaluate(self, student_answer):
                    from pg_answer import AnswerResult
                    try:
                        is_correct = float(student_answer) == float(
                            self.correct_answer)
                        return AnswerResult(
                            is_correct=is_correct,
                            score=1.0 if is_correct else 0.0,
                            student_answer=student_answer,
                            correct_answer=str(self.correct_answer)
                        )
                    except:
                        return AnswerResult(
                            is_correct=False,
                            score=0.0,
                            student_answer=student_answer,
                            correct_answer=str(self.correct_answer),
                            message="Invalid answer format"
                        )

            def num_cmp(correct, **options):
                return StubEvaluator(correct, **options)

            def str_cmp(correct, **options):
                return StubEvaluator(correct, **options)

            def fun_cmp(correct, **options):
                return StubEvaluator(correct, **options)

            self.namespace.update({
                'num_cmp': num_cmp,
                'str_cmp': str_cmp,
                'fun_cmp': fun_cmp,
            })

    def initialize_environment(self, seed: int, context: Context | None = None) -> None:
        """
        Initialize PG environment for problem execution.

        Args:
            seed: Random seed
            context: Mathematical context
        """
        # IMPORTANT: Clear namespace and reinitialize for each problem
        # This prevents variable pollution between problems
        self.namespace.clear()
        self._setup_safe_namespace()

        # IMPORTANT: Reset Context to prevent variable pollution
        # Context is a global singleton that persists between problems
        try:
            from pg_mathobjects import Context
            # Force creation of fresh Numeric context
            Context('Numeric')
        except ImportError:
            pass  # pg_mathobjects not available

        # Set random seed
        import random as _random_module
        _random_module.seed(seed)

        # Also set seed on the random module in namespace if it's the real module
        if 'random' in self.namespace and hasattr(self.namespace['random'], 'seed'):
            self.namespace['random'].seed(seed)

        # Set up envir dict that DOCUMENT() will use
        self.namespace['envir'] = {
            'problemSeed': seed,
            'displayMode': 'HTML',
            'showPartialCorrectAnswers': 1,
            'inputs_ref': {},
        }

        # Don't initialize PGEnvironment here - DOCUMENT() will do it
        # Just clear any previous environment
        self._pg_environment = None

        # Also clear pg_core's global environment if we're using it
        if hasattr(self, '_pg_core') and hasattr(self._pg_core, '_pg_environment'):
            self._pg_core._pg_environment = None

    @contextmanager
    def _timeout_context(self):
        """Context manager for timeout protection (Unix only)."""
        if sys.platform == 'win32':
            # Windows doesn't support signal.alarm
            # Use simple time tracking instead
            start_time = time.time()
            yield
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                raise TimeoutError(
                    f"Execution exceeded {self.timeout} seconds")
        else:
            # Unix: use signal.alarm
            def timeout_handler(signum, frame):
                raise TimeoutError(
                    f"Execution exceeded {self.timeout} seconds")

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout)
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

    def execute(self, code: str, seed: int, context: Context | None = None) -> ExecutionResult:
        """
        Execute PG code in sandbox.

        Args:
            code: Python code to execute
            seed: Random seed
            context: Mathematical context

        Returns:
            ExecutionResult with all problem data
        """
        # Initialize environment
        self.initialize_environment(seed, context)

        errors = ""

        try:
            with self._timeout_context():
                # Compile code with restricted mode
                compiled = compile(code, '<problem>', 'exec')

                # Execute in namespace
                exec(compiled, self.namespace)

        except TimeoutError as e:
            errors = str(e)
        except Exception as e:
            import traceback
            errors = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"        # Collect results from PG environment
        # Try to get environment from pg_core global
        try:
            if hasattr(self, '_pg_core'):
                # Use the SAME pg_core instance that was loaded in namespace
                pg_env = self._pg_core.get_environment() if self._pg_core._pg_environment else None
            elif hasattr(self, '_stub_env'):
                # Use stub environment if pg_core not available
                pg_env = self._stub_env
            else:
                pg_env = self._pg_environment if hasattr(
                    self, '_pg_environment') else None
        except Exception as ex:
            pg_env = None

        if pg_env:
            output_text = ''.join(pg_env.output_array)
            answers = dict(pg_env.answers_hash)
            solution_text = ''.join(getattr(pg_env, 'solution_array', [])) if hasattr(
                pg_env, 'solution_array') else None
            hint_text = ''.join(getattr(pg_env, 'hint_array', [])) if hasattr(
                pg_env, 'hint_array') else None
        else:
            output_text = ""
            answers = {}
            solution_text = None
            hint_text = None

        # Collect problem variables
        variables = {}
        for key, value in self.namespace.items():
            if not key.startswith('_') and key not in ('__builtins__',):
                # Only include simple types
                if isinstance(value, (int, float, str, bool, list, tuple, dict)):
                    variables[key] = value

        return ExecutionResult(
            success=not errors,
            output_text=output_text,
            answers=answers,
            solution_text=solution_text if solution_text else None,
            hint_text=hint_text if hint_text else None,
            errors=errors,
            variables=variables
        )

    def _load_context_macros(self) -> None:
        """Load context-related macro stubs (LimitedPowers, etc.)."""
        # Stub class for LimitedPowers
        class LimitedPowersStub:
            """Stub for LimitedPowers macro package."""
            @staticmethod
            def OnlyIntegers(**kwargs):
                """Stub for LimitedPowers::OnlyIntegers - accepts but ignores parameters."""
                # In real PG, this restricts allowed powers in polynomial contexts
                # For now, we just accept the call and do nothing
                pass

            @staticmethod
            def OnlyPositiveIntegers(**kwargs):
                """Stub for LimitedPowers::OnlyPositiveIntegers."""
                pass

        # Stub class for MultiAnswer
        class MultiAnswerStub:
            """Stub for MultiAnswer - used for checking multiple related answer blanks together."""

            def __init__(self, *args, **kwargs):
                self.answers = args
                self.options = kwargs

            def with_params(self, **kwargs):
                """Method for setting options (works around 'with' keyword)."""
                self.options.update(kwargs)
                return self

        # Add .with() method using setattr to work around Python keyword
        setattr(MultiAnswerStub, 'with', MultiAnswerStub.with_params)

        # Stub for AnswerHints - provides custom hints for specific incorrect answers
        def AnswerHintsStub(*args, **kwargs):
            """Stub for AnswerHints macro - returns a filter function."""
            # In real PG, this creates a filter that shows hints for specific wrong answers
            # For now, just return a dummy filter
            def filter_func(answer_hash):
                return answer_hash
            return filter_func

        # Stub for parser package
        class ParserStub:
            """Stub for parser package."""
            class Assignment:
                """Stub for parser::Assignment."""
                @staticmethod
                def Allow():
                    """Stub for parser::Assignment->Allow."""
                    pass

        # Stub for helpLink - provides links to help documentation
        def helpLinkStub(topic):
            """Stub for helpLink - returns a help link."""
            return f'<a href="/help/{topic}" target="_blank">Help</a>'

        # Stub for LayoutTable - creates formatted table layouts
        def LayoutTableStub(rows, **kwargs):
            """Stub for LayoutTable - returns a simple table representation."""
            # In real PG, this creates nicely formatted tables
            # For now, just return a simple string representation
            return f"[Table with {len(rows)} rows]"

        self.namespace['LimitedPowers'] = LimitedPowersStub
        self.namespace['MultiAnswer'] = MultiAnswerStub
        self.namespace['AnswerHints'] = AnswerHintsStub
        self.namespace['parser'] = ParserStub
        self.namespace['helpLink'] = helpLinkStub
        self.namespace['LayoutTable'] = LayoutTableStub


def create_in_process_sandbox(timeout: int = 30) -> InProcessSandbox:
    """
    Create an in-process sandbox.

    Args:
        timeout: Maximum execution time in seconds

    Returns:
        InProcessSandbox instance
    """
    return InProcessSandbox(timeout=timeout)
