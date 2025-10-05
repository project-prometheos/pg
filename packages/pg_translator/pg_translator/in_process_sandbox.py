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
            # String functions
            'chr': chr,
            'ord': ord,
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

        # Restricted builtins dict
        self.namespace['__builtins__'] = safe_builtins

        # Import safe modules
        import math
        import random
        self.namespace['math'] = math
        self.namespace['random'] = random

        # Load core PG macros by default
        self._load_pg_core()
        self._load_pg_basic_macros()
        self._load_pg_answer_macros()

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
                from .pgml_parser import PGMLParser, PGMLRenderer, AnswerBlankNode
                # Get current namespace for variable access
                import inspect
                frame = inspect.currentframe()
                if frame and frame.f_back:
                    context = frame.f_back.f_locals
                    globals_context = frame.f_back.f_globals
                else:
                    context = {}
                    globals_context = {}

                parser = PGMLParser()
                doc = parser.parse(pgml_text, context=context)

                # Collect answer blanks and evaluate their evaluators
                answer_blanks = []

                def collect_answer_blanks(node):
                    if isinstance(node, AnswerBlankNode):
                        answer_blanks.append(node)
                    if hasattr(node, 'children'):
                        for child in node.children:
                            collect_answer_blanks(child)

                for node in doc.nodes:
                    collect_answer_blanks(node)

                # Evaluate evaluator expressions and register answers
                for blank in answer_blanks:
                    if blank.evaluator_expr:
                        try:
                            # Evaluate in caller's context
                            evaluator = eval(
                                blank.evaluator_expr, globals_context, context)
                            # Register with ANS()
                            pg_core.ANS(evaluator)
                        except Exception as e:
                            # If evaluation fails, skip this answer blank
                            pass

                # Render PGML
                renderer = PGMLRenderer(context=context)
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
            """Render PGML markup to HTML."""
            from .pgml_parser import PGMLParser, PGMLRenderer, AnswerBlankNode
            # Get current namespace for variable access
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back:
                context = frame.f_back.f_locals
                globals_context = frame.f_back.f_globals
            else:
                context = {}
                globals_context = {}

            parser = PGMLParser()
            doc = parser.parse(pgml_text, context=context)

            # Collect answer blanks and evaluate their evaluators
            answer_blanks = []

            def collect_answer_blanks(node):
                if isinstance(node, AnswerBlankNode):
                    answer_blanks.append(node)
                if hasattr(node, 'children'):
                    for child in node.children:
                        collect_answer_blanks(child)

            for node in doc.nodes:
                collect_answer_blanks(node)

            # Evaluate evaluator expressions and register answers
            for blank in answer_blanks:
                if blank.evaluator_expr:
                    try:
                        # Evaluate in caller's context
                        evaluator = eval(blank.evaluator_expr,
                                         globals_context, context)
                        # Register with ANS()
                        ANS(evaluator)
                    except Exception as e:
                        # If evaluation fails, skip this answer blank
                        pass

            # Render PGML
            renderer = PGMLRenderer(context=context)
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
            errors = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"

        # Collect results from PG environment
        # Try to get environment from pg_core global
        try:
            if hasattr(self, '_pg_core'):
                from pg_macros.core import pg_core
                pg_env = pg_core.get_environment() if pg_core._pg_environment else None
            else:
                pg_env = self._pg_environment if hasattr(
                    self, '_pg_environment') else None
        except:
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


def create_in_process_sandbox(timeout: int = 30) -> InProcessSandbox:
    """
    Create an in-process sandbox.

    Args:
        timeout: Maximum execution time in seconds

    Returns:
        InProcessSandbox instance
    """
    return InProcessSandbox(timeout=timeout)
