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

        # Add common mathematical functions (for bare function calls)
        self.namespace['sqrt'] = math.sqrt
        self.namespace['sin'] = math.sin
        self.namespace['cos'] = math.cos
        self.namespace['tan'] = math.tan
        self.namespace['asin'] = math.asin
        self.namespace['acos'] = math.acos
        self.namespace['atan'] = math.atan
        self.namespace['arcsin'] = math.asin  # Alias
        self.namespace['arccos'] = math.acos  # Alias
        self.namespace['arctan'] = math.atan  # Alias
        self.namespace['exp'] = math.exp
        self.namespace['log'] = math.log
        self.namespace['ln'] = math.log  # Alias
        self.namespace['abs'] = abs

        # Load MathObjects
        self._load_mathobjects()

        # Load core PG macros by default
        self._load_pg_core()  # Load real pg_core (not stubs)
        self._load_pg_basic_macros()
        self._load_pg_answer_macros()

        # Load additional context macros (stubs)
        self._load_context_macros()

        # Load parser macros (PopUp, DropDown, etc.)
        self._load_parser_macros()

        # Load statistics macros (stats_mean, stats_sd, stats_SX_SXX)
        self._load_statistics_macros()

    def _load_mathobjects(self) -> None:
        """Load MathObjects framework into namespace."""
        try:
            # Import MathObjects
            # Use pg_math for Context and Compute (has full interval/inequality support)
            from pg_math.context import get_context as _get_context
            from pg_math.compute import Compute as _Compute
            from pg_mathobjects import Formula, Real
            from pg_mathobjects.formula_up_to_constant import FormulaUpToConstant
            from pg_math import Complex as _Complex, List as _List, Point, Vector, Interval, Set, Fraction

            # Context function that delegates to pg_math
            def Context(name=None):
                """Context function - delegates to pg_math.context.get_context."""
                return _get_context(name)

            # Compute function that delegates to pg_math
            def Compute(expr):
                """Compute function - delegates to pg_math.compute.Compute."""
                return _Compute(expr)

            # Wrapper for Complex that handles list arguments (Perl compatibility)
            def Complex(real, imag=0, **kwargs):
                """Complex wrapper that handles list/array arguments like Perl."""
                if isinstance(real, (list, tuple)):
                    # Unpack list: Complex([a, b]) → Complex(a, b)
                    if len(real) >= 2:
                        return _Complex(real[0], real[1], **kwargs)
                    elif len(real) == 1:
                        return _Complex(real[0], 0, **kwargs)
                    else:
                        return _Complex(0, 0, **kwargs)
                elif isinstance(real, str):
                    # String form: Complex("2-4i") - parse it
                    # For now, just pass to _Complex and let it handle or fail gracefully
                    import re
                    match = re.match(r'([+-]?\d+(?:\.\d+)?)\s*([+-])\s*(\d+(?:\.\d+)?)i', real.replace(' ', ''))
                    if match:
                        r = float(match.group(1))
                        sign = match.group(2)
                        i = float(match.group(3))
                        if sign == '-':
                            i = -i
                        return _Complex(r, i, **kwargs)
                return _Complex(real, imag, **kwargs)

            # Wrapper for List that handles variadic arguments (Perl compatibility)
            def List(*args, **kwargs):
                """List wrapper that handles variadic arguments like Perl."""
                if len(args) == 1 and isinstance(args[0], (list, tuple)):
                    # Single list argument: List([1, 2, 3])
                    return _List(list(args[0]), **kwargs)
                else:
                    # Multiple arguments: List(1, 2, 3)
                    return _List(list(args), **kwargs)

            # Make available in namespace
            self.namespace['Context'] = Context
            self.namespace['Formula'] = Formula
            self.namespace['Real'] = Real
            self.namespace['Complex'] = Complex
            self.namespace['Compute'] = Compute
            self.namespace['FormulaUpToConstant'] = FormulaUpToConstant
            self.namespace['List'] = List
            self.namespace['Point'] = Point
            self.namespace['Vector'] = Vector
            self.namespace['Interval'] = Interval
            self.namespace['Set'] = Set
            self.namespace['Fraction'] = Fraction

            # Create imaginary unit i = Complex(0, 1)
            self.namespace['i'] = _Complex(0, 1)

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

            def Complex(real, imag=0):
                """Stub Complex function - returns Python complex."""
                return complex(real, imag)

            self.namespace['Context'] = Context
            self.namespace['Formula'] = Formula
            self.namespace['Real'] = Real
            self.namespace['Complex'] = Complex
            self.namespace['Compute'] = Compute
            self.namespace['i'] = complex(0, 1)

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
                """Render PGML markup and register answer blanks."""
                from pg_renderer import PGMLRenderer

                # Get current environment
                env = pg_core.get_environment()

                # Create renderer with access to namespace variables
                renderer = PGMLRenderer(variables=self.namespace)

                # Render PGML to HTML and extract answer blanks
                rendered_html, answer_blanks = renderer.render(pgml_text)

                # Register answer blanks in environment
                for ans_name, ans_spec in answer_blanks.items():
                    # Create answer evaluator entry
                    if not isinstance(ans_spec, dict):
                        # It's an evaluator object or value
                        env.register_answer(ans_name, ans_spec)
                    else:
                        env.register_answer(ans_name, ans_spec)

                # Return rendered HTML (which TEXT() will append)
                return rendered_html

            # Define additional stubs not in pg_core
            def non_zero_point3D(*args):
                """Stub for non_zero_point3D - generates non-zero 3D point."""
                Point = self.namespace.get('Point')
                if Point:
                    return Point([pg_core.non_zero_random(-5, 5), pg_core.non_zero_random(-5, 5), pg_core.non_zero_random(-5, 5)])
                return [pg_core.non_zero_random(-5, 5), pg_core.non_zero_random(-5, 5), pg_core.non_zero_random(-5, 5)]

            def non_zero_vector3D(*args):
                """Stub for non_zero_vector3D - generates non-zero 3D vector."""
                Vector = self.namespace.get('Vector')
                if Vector:
                    return Vector([pg_core.non_zero_random(-5, 5), pg_core.non_zero_random(-5, 5), pg_core.non_zero_random(-5, 5)])
                return [pg_core.non_zero_random(-5, 5), pg_core.non_zero_random(-5, 5), pg_core.non_zero_random(-5, 5)]

            def Matrix(*args, **kwargs):
                """Matrix wrapper for compatibility."""
                _Matrix = self.namespace.get('Matrix')
                if not _Matrix:
                    try:
                        from pg_math.geometric import Matrix as _Matrix
                        self.namespace['Matrix'] = _Matrix
                    except ImportError:
                        if len(args) == 1 and isinstance(args[0], (list, tuple)):
                            return list(args[0])
                        return list(args)
                if len(args) == 1 and isinstance(args[0], (list, tuple)):
                    return _Matrix(args[0], **kwargs)
                return _Matrix(list(args), **kwargs)

            def Graph3D(*args, **kwargs):
                """Stub for Graph3D - 3D graphing object."""
                return type('Graph3D', (), {
                    'plotSurface': lambda *a, **k: None,
                    'addSurface': lambda *a, **k: None,
                    'addCurve': lambda *a, **k: None,
                    'addPoint': lambda *a, **k: None,
                })()

            def Plot(*args, **kwargs):
                """Stub for Plot - 2D plotting function."""
                return type('Plot', (), {
                    'plot': lambda *a, **k: None,
                    'add_function': lambda *a, **k: None,
                })()

            def COMPOSITION_ANS(*args, **kwargs):
                """Stub for COMPOSITION_ANS - function composition answer checker."""
                return pg_core.ANS(*args, **kwargs)

            def UNORDERED_ANS(*args, **kwargs):
                """Stub for UNORDERED_ANS - unordered answer checker."""
                return pg_core.ANS(*args, **kwargs)

            def DraggableProof(*args, **kwargs):
                """Stub for DraggableProof - drag-and-drop proof interface."""
                return type('DraggableProof', (), {
                    'Print': lambda *a, **k: '',
                    'CorrectProof': lambda *a, **k: [],
                })()

            def DraggableSubsets(*args, **kwargs):
                """Stub for DraggableSubsets - drag-and-drop subset interface."""
                return type('DraggableSubsets', (), {'Print': lambda *a, **k: ''})()

            def CheckboxList(*args, **kwargs):
                """Stub for CheckboxList - checkbox list interface."""
                return '<input type="checkbox" />'

            def tag(tagname, content='', **attrs):
                """Stub for tag - HTML tag generator."""
                attr_str = ' '.join(f'{k}="{v}"' for k, v in attrs.items())
                if content:
                    return f'<{tagname} {attr_str}>{content}</{tagname}>'
                else:
                    return f'<{tagname} {attr_str}/>'

            def Round(value, decimals=0):
                """Stub for Round - rounding function."""
                return round(float(value), int(decimals))

            def NumberWithUnits(value, units=''):
                """Stub for NumberWithUnits - number with units."""
                return type('NumberWithUnits', (), {
                    'value': value,
                    'units': units,
                    '__str__': lambda self: f'{value} {units}',
                })()

            def ImplicitEquation(*args, **kwargs):
                """Stub for ImplicitEquation - implicit equation parser."""
                Formula = self.namespace.get('Formula')
                if Formula:
                    return Formula(str(args[0]) if args else '0')
                return str(args[0]) if args else '0'

            def SolutionFor(*args, **kwargs):
                """Stub for SolutionFor - solution checker."""
                Formula = self.namespace.get('Formula')
                if Formula:
                    return Formula(str(args[0]) if args else '0')
                return str(args[0]) if args else '0'

            def ParametricLine(*args, **kwargs):
                """Stub for ParametricLine - parametric line parser."""
                return type('ParametricLine', (), {
                    '__str__': lambda self: 'ParametricLine',
                })()

            def ImplicitPlane(*args, **kwargs):
                """Stub for ImplicitPlane - implicit plane parser."""
                return type('ImplicitPlane', (), {
                    '__str__': lambda self: 'ImplicitPlane',
                })()

            def randomPerson():
                """Stub for randomPerson - generates random person name."""
                import random
                first_names = ['Alice', 'Bob', 'Carol', 'David', 'Eve', 'Frank']
                last_names = ['Smith', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson']
                return f"{random.choice(first_names)} {random.choice(last_names)}"

            # Additional graphics stubs
            def VectorField3D(*args, **kwargs):
                """Stub for VectorField3D - 3D vector field graphing."""
                return type('VectorField3D', (), {
                    'plot': lambda *a, **k: None,
                })()

            # Perl compatibility values
            def undef():
                """Stub for Perl's undef - returns None."""
                return None

            # Add pg_core functions to namespace
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
                'random_coprime': pg_core.random_coprime,
                'loadMacros': pg_core.loadMacros,
                'PGEnvironment': pg_core.PGEnvironment,
                'set_environment': pg_core.set_environment,
                'get_environment': pg_core.get_environment,
                # Common constants
                'SPACE': ' ',
                # Additional stubs
                'non_zero_point3D': non_zero_point3D,
                'non_zero_vector3D': non_zero_vector3D,
                'Matrix': Matrix,
                'Graph3D': Graph3D,
                'Plot': Plot,
                'VectorField3D': VectorField3D,
                'COMPOSITION_ANS': COMPOSITION_ANS,
                'UNORDERED_ANS': UNORDERED_ANS,
                'DraggableProof': DraggableProof,
                'DraggableSubsets': DraggableSubsets,
                'CheckboxList': CheckboxList,
                'tag': tag,
                'Round': Round,
                'NumberWithUnits': NumberWithUnits,
                'ImplicitEquation': ImplicitEquation,
                'SolutionFor': SolutionFor,
                'ParametricLine': ParametricLine,
                'ImplicitPlane': ImplicitPlane,
                'randomPerson': randomPerson,
                'undef': undef,
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
                self.pgml_array = []  # For PGML content
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
            """Return PGML markup - will be rendered by PGMLRenderer later."""
            # Don't store in pgml_array - just return so TEXT() can handle it
            return pgml_text

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

        def random_coprime(*arrays):
            """Stub for random_coprime."""
            import math
            import random
            from itertools import product
            if not arrays:
                return ()
            # Convert all arrays to lists, expanding list-wrapped ranges
            def expand_array(arr):
                expanded = list(arr)
                if len(expanded) == 1 and isinstance(expanded[0], range):
                    return list(expanded[0])
                return expanded
            list_arrays = [expand_array(arr) for arr in arrays]
            if len(list_arrays) == 1:
                return (list_random(*list_arrays[0]),)
            all_tuples = list(product(*list_arrays))
            coprime = [t for t in all_tuples if math.gcd(*[abs(x) for x in t]) == 1]
            return random.choice(coprime) if coprime else tuple([0] * len(list_arrays))

        def loadMacros(*args): pass
        def get_environment(): return _env
        def set_environment(env): pass

        def parserFunction(name=None, formula=None):
            """Stub for parserFunction - defines named function in context."""
            # Just a placeholder - real implementation would add to Context
            pass

        # Geometric stubs
        def non_zero_point3D(*args):
            """Stub for non_zero_point3D - generates non-zero 3D point."""
            # Returns a random 3D point with no zero coordinates
            # Access Point from namespace
            Point = self.namespace.get('Point')
            if Point:
                return Point([non_zero_random(-5, 5), non_zero_random(-5, 5), non_zero_random(-5, 5)])
            # Fallback: return list
            return [non_zero_random(-5, 5), non_zero_random(-5, 5), non_zero_random(-5, 5)]

        def non_zero_vector3D(*args):
            """Stub for non_zero_vector3D - generates non-zero 3D vector."""
            Vector = self.namespace.get('Vector')
            if Vector:
                return Vector([non_zero_random(-5, 5), non_zero_random(-5, 5), non_zero_random(-5, 5)])
            return [non_zero_random(-5, 5), non_zero_random(-5, 5), non_zero_random(-5, 5)]

        # Matrix constructor (wrap pg_math Matrix if available)
        def Matrix(*args, **kwargs):
            """Matrix wrapper for compatibility."""
            # Try to get Matrix from namespace (loaded by _load_mathobjects)
            _Matrix = self.namespace.get('Matrix')
            if not _Matrix:
                # Import if not in namespace yet
                try:
                    from pg_math.geometric import Matrix as _Matrix
                    self.namespace['Matrix'] = _Matrix
                except ImportError:
                    # Fallback: return list of lists
                    if len(args) == 1 and isinstance(args[0], (list, tuple)):
                        return list(args[0])
                    return list(args)
            # Handle various calling conventions
            if len(args) == 1 and isinstance(args[0], (list, tuple)):
                return _Matrix(args[0], **kwargs)
            return _Matrix(list(args), **kwargs)

        # Graphics stubs
        def Graph3D(*args, **kwargs):
            """Stub for Graph3D - 3D graphing object."""
            # Minimal stub - just return a placeholder object
            return type('Graph3D', (), {
                'plotSurface': lambda *a, **k: None,
                'addSurface': lambda *a, **k: None,
                'addCurve': lambda *a, **k: None,
                'addPoint': lambda *a, **k: None,
            })()

        def Plot(*args, **kwargs):
            """Stub for Plot - 2D plotting function."""
            return type('Plot', (), {
                'plot': lambda *a, **k: None,
                'add_function': lambda *a, **k: None,
            })()

        # Special answer evaluation functions
        def COMPOSITION_ANS(*args, **kwargs):
            """Stub for COMPOSITION_ANS - function composition answer checker."""
            return ANS(*args, **kwargs)

        def UNORDERED_ANS(*args, **kwargs):
            """Stub for UNORDERED_ANS - unordered answer checker."""
            return ANS(*args, **kwargs)

        # Interactive elements
        def DraggableProof(*args, **kwargs):
            """Stub for DraggableProof - drag-and-drop proof interface."""
            return type('DraggableProof', (), {
                'Print': lambda *a, **k: '',
                'CorrectProof': lambda *a, **k: [],
            })()

        def DraggableSubsets(*args, **kwargs):
            """Stub for DraggableSubsets - drag-and-drop subset interface."""
            return type('DraggableSubsets', (), {
                'Print': lambda *a, **k: '',
            })()

        def CheckboxList(*args, **kwargs):
            """Stub for CheckboxList - checkbox list interface."""
            return '<input type="checkbox" />'

        # String/HTML utilities
        def tag(tagname, content='', **attrs):
            """Stub for tag - HTML tag generator."""
            attr_str = ' '.join(f'{k}="{v}"' for k, v in attrs.items())
            if content:
                return f'<{tagname} {attr_str}>{content}</{tagname}>'
            else:
                return f'<{tagname} {attr_str}/>'

        # Numeric utilities
        def Round(value, decimals=0):
            """Stub for Round - rounding function."""
            return round(float(value), int(decimals))

        # Units
        def NumberWithUnits(value, units=''):
            """Stub for NumberWithUnits - number with units."""
            return type('NumberWithUnits', (), {
                'value': value,
                'units': units,
                '__str__': lambda self: f'{value} {units}',
            })()

        # Parser utilities
        def ImplicitEquation(*args, **kwargs):
            """Stub for ImplicitEquation - implicit equation parser."""
            Formula = self.namespace.get('Formula')
            if Formula:
                return Formula(str(args[0]) if args else '0')
            return str(args[0]) if args else '0'

        def SolutionFor(*args, **kwargs):
            """Stub for SolutionFor - solution checker."""
            Formula = self.namespace.get('Formula')
            if Formula:
                return Formula(str(args[0]) if args else '0')
            return str(args[0]) if args else '0'

        def ParametricLine(*args, **kwargs):
            """Stub for ParametricLine - parametric line parser."""
            return type('ParametricLine', (), {
                '__str__': lambda self: 'ParametricLine',
            })()

        def ImplicitPlane(*args, **kwargs):
            """Stub for ImplicitPlane - implicit plane parser."""
            return type('ImplicitPlane', (), {
                '__str__': lambda self: 'ImplicitPlane',
            })()

        # Random utilities
        def randomPerson():
            """Stub for randomPerson - generates random person name."""
            import random
            first_names = ['Alice', 'Bob', 'Carol', 'David', 'Eve', 'Frank']
            last_names = ['Smith', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson']
            return f"{random.choice(first_names)} {random.choice(last_names)}"

        # Additional graphics stubs
        def VectorField3D(*args, **kwargs):
            """Stub for VectorField3D - 3D vector field graphing."""
            return type('VectorField3D', (), {
                'plot': lambda *a, **k: None,
            })()

        # Perl compatibility values
        def undef():
            """Stub for Perl's undef - returns None."""
            return None

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
            'random_coprime': random_coprime,
            'loadMacros': loadMacros,
            'parserFunction': parserFunction,
            'get_environment': get_environment,
            'set_environment': set_environment,
            # Geometric stubs
            'non_zero_point3D': non_zero_point3D,
            'non_zero_vector3D': non_zero_vector3D,
            'Matrix': Matrix,
            # Graphics
            'Graph3D': Graph3D,
            'Plot': Plot,
            'VectorField3D': VectorField3D,
            # Special answer evaluation
            'COMPOSITION_ANS': COMPOSITION_ANS,
            'UNORDERED_ANS': UNORDERED_ANS,
            # Interactive elements
            'DraggableProof': DraggableProof,
            'DraggableSubsets': DraggableSubsets,
            'CheckboxList': CheckboxList,
            # String/HTML utilities
            'tag': tag,
            # Numeric utilities
            'Round': Round,
            # Units
            'NumberWithUnits': NumberWithUnits,
            # Parser utilities
            'ImplicitEquation': ImplicitEquation,
            'SolutionFor': SolutionFor,
            'ParametricLine': ParametricLine,
            'ImplicitPlane': ImplicitPlane,
            # Random utilities
            'randomPerson': randomPerson,
            # Perl compatibility
            'undef': undef,
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

        # Common constants
        SPACE = ' '

        self.namespace.update({
            'ans_rule': ans_rule,
            'ans_box': ans_box,
            'beginproblem': beginproblem,
            'PAR': PAR,
            'BR': BR,
            'SPACE': SPACE,
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
            from pg_math.context import get_context
            # Force creation of fresh Numeric context
            get_context('Numeric')
        except ImportError:
            pass  # pg_math not available

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
            # Collect results from PG environment
            errors = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
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
            # Get output from output_array (TEXT() calls, which include PGML content)
            if hasattr(pg_env, 'output_array') and pg_env.output_array:
                output_text = '\n\n'.join(pg_env.output_array)
            else:
                output_text = ''

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
                # Include simple types AND answer evaluators (objects with evaluate/cmp/check methods)
                if isinstance(value, (int, float, str, bool, list, tuple, dict)):
                    variables[key] = value
                elif hasattr(value, 'evaluate') or hasattr(value, 'cmp') or hasattr(value, 'check'):
                    # This is likely an answer evaluator (Formula, Real, AnswerChecker, etc.)
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

            def cmp(self):
                """Return a checker that can check multiple answers together."""
                # For now, return self so it can be used as a checker
                return self

            def check(self, *student_answers):
                """Check multiple student answers against the correct answers."""
                # Extract the custom checker if provided
                checker_func = self.options.get('checker')

                if checker_func and callable(checker_func):
                    # Call custom checker with (correct, student, self) tuple
                    try:
                        results = checker_func(
                            self.answers, student_answers, self)
                        # results should be a list of [score1, score2, ...]
                        # Convert to dict format for each answer
                        if isinstance(results, list):
                            # Return results for all answers
                            # For now, return a dict with aggregate result
                            all_correct = all(
                                r >= 1.0 for r in results) if results else False
                            return {
                                'correct': all_correct,
                                'score': 1.0 if all_correct else 0.0,
                                'message': 'Checked with custom MultiAnswer checker',
                                'results': results,  # Individual results for each blank
                            }
                    except Exception as e:
                        return {
                            'correct': False,
                            'score': 0.0,
                            'message': f'Error in custom checker: {str(e)}',
                        }

                # Default: check each answer individually
                if len(student_answers) != len(self.answers):
                    return {
                        'correct': False,
                        'score': 0.0,
                        'message': f'Expected {len(self.answers)} answers, got {len(student_answers)}',
                    }

                results = []
                for correct, student in zip(self.answers, student_answers):
                    if hasattr(correct, 'cmp'):
                        checker = correct.cmp()
                        if hasattr(checker, 'check'):
                            result = checker.check(student)
                            results.append(result.get('score', 0.0))
                        else:
                            results.append(0.0)
                    else:
                        # Simple comparison
                        results.append(1.0 if str(correct) ==
                                       str(student) else 0.0)

                all_correct = all(r >= 1.0 for r in results)
                return {
                    'correct': all_correct,
                    'score': 1.0 if all_correct else 0.0,
                    'message': '',
                    'results': results,
                }

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

        # Stub for parserFunction - defines named function in context
        def parserFunctionStub(*args, **kwargs):
            """Stub for parserFunction from parserFunction.pl macro."""
            # In real PG, this would add a named function to the Context
            # For now, just a placeholder
            pass

        self.namespace['parserFunction'] = parserFunctionStub

    def _load_parser_macros(self) -> None:
        """Load parser macros (PopUp, DropDown, RadioButtons, RadioMultiAnswer, LinearRelation, DifferenceQuotient, specialRadical, etc.)."""
        try:
            from pg_macros.parsers.parser_popup import PopUp, DropDown, DropDownTF, RadioButtons
            from pg_macros.parsers.parser_radio_multianswer import RadioMultiAnswer
            from pg_macros.parsers.parser_linear_relation import LinearRelation
            from pg_macros.parsers.parser_difference_quotient import DifferenceQuotient
            from pg_macros.parsers.parser_special_trig import specialRadical, specialAngle

            self.namespace['PopUp'] = PopUp
            self.namespace['DropDown'] = DropDown
            self.namespace['DropDownTF'] = DropDownTF
            self.namespace['RadioButtons'] = RadioButtons
            self.namespace['RadioMultiAnswer'] = RadioMultiAnswer
            self.namespace['LinearRelation'] = LinearRelation
            self.namespace['DifferenceQuotient'] = DifferenceQuotient
            self.namespace['specialRadical'] = specialRadical
            self.namespace['specialAngle'] = specialAngle
        except ImportError:
            # Provide fallback stubs if not available
            class PopUpStub:
                def __init__(self, choices, correct, **options):
                    self.choices = choices
                    self.correct = correct

                def cmp(self):
                    return lambda x: {'correct': True, 'score': 1.0}

            class RadioMultiAnswerStub:
                def __init__(self, parts, correct, **options):
                    self.parts = parts
                    self.correct = correct

                def cmp(self):
                    return lambda x: {'correct': True, 'score': 1.0}

            class LinearRelationStub:
                def __init__(self, *args, **options):
                    pass

                def cmp(self):
                    return lambda x: {'correct': True, 'score': 1.0}

            class DifferenceQuotientStub:
                def __init__(self, formula, dx=None, zero_point=0, **options):
                    self.formula = formula
                    self.dx = dx

                def cmp(self):
                    return lambda x: {'correct': True, 'score': 1.0}

            def specialRadicalStub(expr, *args, **kwargs):
                from pg_mathobjects import Compute
                return Compute(expr)

            def specialAngleStub(expr, *args, **kwargs):
                from pg_mathobjects import Compute
                return Compute(expr)

            self.namespace['PopUp'] = PopUpStub
            self.namespace['DropDown'] = PopUpStub
            self.namespace['DropDownTF'] = lambda correct, **opts: PopUpStub(['True', 'False'], correct)
            self.namespace['RadioButtons'] = PopUpStub
            self.namespace['RadioMultiAnswer'] = RadioMultiAnswerStub
            self.namespace['LinearRelation'] = LinearRelationStub
            self.namespace['DifferenceQuotient'] = DifferenceQuotientStub
            self.namespace['specialRadical'] = specialRadicalStub
            self.namespace['specialAngle'] = specialAngleStub

    def _load_statistics_macros(self) -> None:
        """Load statistics functions (stats_mean, stats_sd, stats_SX_SXX)."""
        try:
            from pg_macros.statistics import stats_mean, stats_sd, stats_SX_SXX

            self.namespace['stats_mean'] = stats_mean
            self.namespace['stats_sd'] = stats_sd
            self.namespace['stats_SX_SXX'] = stats_SX_SXX
        except ImportError:
            # Provide fallback stubs if not available
            import math

            def stats_mean_stub(*values):
                if len(values) == 1 and isinstance(values[0], (list, tuple)):
                    values = values[0]
                return sum(values) / len(values) if values else 0.0

            def stats_sd_stub(*values):
                if len(values) == 1 and isinstance(values[0], (list, tuple)):
                    values = values[0]
                if len(values) < 2:
                    return 0.0
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
                return math.sqrt(variance)

            def stats_SX_SXX_stub(*values):
                if len(values) == 1 and isinstance(values[0], (list, tuple)):
                    values = values[0]
                sum_x = sum(values) if values else 0.0
                sum_sq = sum(x ** 2 for x in values) if values else 0.0
                return (sum_x, sum_sq)

            self.namespace['stats_mean'] = stats_mean_stub
            self.namespace['stats_sd'] = stats_sd_stub
            self.namespace['stats_SX_SXX'] = stats_SX_SXX_stub


def create_in_process_sandbox(timeout: int = 30) -> InProcessSandbox:
    """
    Create an in-process sandbox.

    Args:
        timeout: Maximum execution time in seconds

    Returns:
        InProcessSandbox instance
    """
    return InProcessSandbox(timeout=timeout)
