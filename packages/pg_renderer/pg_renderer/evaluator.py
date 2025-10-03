"""Execute Perl-like PG setup code in Python."""

import re
import math
from typing import Dict, Any
from pg_math import Formula as PGFormula
from .context import Context
from .random import PGRandom


class PGEvaluator:
    """Execute Perl-like PG setup code in Python."""
    
    def __init__(self, seed: int = 0):
        self.seed = seed
        self.random = PGRandom(seed)
        self.context = Context("Numeric")
        self.variables: Dict[str, Any] = {}
        
        # Built-in functions
        self.builtins = {
            'random': self.random.random,
            'non_zero_random': self.random.non_zero_random,
            'list_random': self.random.list_random,
            'pi': math.pi,
            'e': math.e,
        }
    
    def evaluate(self, setup_code: str) -> Dict[str, Any]:
        """
        Execute setup code and return variable bindings.

        This is a simplified Perl→Python translator.
        Only supports basic variable assignments and function calls.
        """

        # Clean up code
        setup_code = self._strip_comments(setup_code)

        # Handle do { } until () blocks by extracting and executing the inner code
        # For MVP, we'll just execute the assignments once (ignoring the until condition)
        setup_code = re.sub(r'do\s*\{([^}]+)\}\s*until\s*\([^)]+\);', r'\1', setup_code, flags=re.DOTALL)

        # Split into statements (handle multi-line assignments)
        statements = self._extract_statements(setup_code)

        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue

            # Handle Context() calls and Context()->variables->are()
            if 'Context(' in stmt or 'Context()' in stmt:
                self._handle_context(stmt)
                continue

            # Handle list assignment: ($var1, $var2) = (expr1, expr2);
            if stmt.startswith('(') and '=' in stmt and stmt.count('(') >= 2:
                # Find the = sign and split into left and right parts
                eq_pos = stmt.find('=')
                left_part = stmt[:eq_pos].strip()
                right_part = stmt[eq_pos+1:].strip().rstrip(';')

                # Parse left side: ($var1, $var2)
                if left_part.startswith('(') and left_part.endswith(')'):
                    var_names = [v.strip().lstrip('$') for v in left_part[1:-1].split(',')]
                else:
                    continue

                # Parse right side: (expr1, expr2) - handle nested parentheses
                if right_part.startswith('(') and right_part.endswith(')'):
                    expr_str = right_part[1:-1]
                    expressions = []
                    current_expr = ""
                    paren_count = 0
                    for char in expr_str:
                        if char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                        elif char == ',' and paren_count == 0:
                            expressions.append(current_expr.strip())
                            current_expr = ""
                            continue
                        current_expr += char
                    if current_expr:
                        expressions.append(current_expr.strip())
                else:
                    continue

                if len(var_names) == len(expressions):
                    try:
                        values = [self._eval_expression(expr) for expr in expressions]
                        for var_name, value in zip(var_names, values):
                            self.variables[var_name] = value
                    except Exception as e:
                        # Store expressions as strings if evaluation fails
                        for var_name, expr in zip(var_names, expressions):
                            self.variables[var_name] = expr
                continue

            # Handle variable assignments: $var = expr;
            if match := re.match(r'\$(\w+)\s*=\s*(.+)', stmt, re.DOTALL):
                var_name = match.group(1)
                expr = match.group(2).rstrip(';').strip()
                # Handle MultiAnswer(...) with optional ->with(...)
                if 'MultiAnswer(' in expr:
                    multi = self._handle_multianswer(expr)
                    if multi is not None:
                        self.variables[var_name] = multi
                        continue
                # Handle $var->cmp(...) in setup
                if '->cmp(' in expr:
                    spec = self._handle_cmp_expression(expr)
                    if spec is not None:
                        self.variables[var_name] = spec
                        continue
                try:
                    self.variables[var_name] = self._eval_expression(expr)
                except Exception as e:
                    # Store as string if evaluation fails
                    self.variables[var_name] = expr
                continue

        return self.variables

    def _extract_statements(self, code: str) -> list[str]:
        """
        Extract Perl statements from code, handling multi-line constructs.

        Statements are terminated by semicolons, but we need to be careful
        about semicolons inside strings and nested structures.
        """
        statements = []
        current = []
        depth = 0  # Track nesting depth of braces/parens
        in_string = False
        string_char = None
        i = 0

        while i < len(code):
            char = code[i]

            # Handle string literals
            if char in ('"', "'") and (i == 0 or code[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None

            # Track nesting depth (only when not in string)
            if not in_string:
                if char in ('{', '('):
                    depth += 1
                elif char in ('}', ')'):
                    depth -= 1
                # Statement terminator: semicolon at depth 0
                elif char == ';' and depth == 0:
                    current.append(char)
                    stmt = ''.join(current).strip()
                    if stmt and not stmt.startswith('#'):
                        statements.append(stmt)
                    current = []
                    i += 1
                    continue

            current.append(char)
            i += 1

        # Add any remaining content as a statement
        if current:
            stmt = ''.join(current).strip()
            if stmt and not stmt.startswith('#'):
                statements.append(stmt)

        return statements
    
    def _eval_expression(self, expr: str) -> Any:
        """Evaluate a Perl-like expression in Python."""
        
        # Replace Perl variables with Python dict lookups
        # $a → self.variables['a']
        expr_py = re.sub(r'\$(\w+)', r"self.variables['\1']", expr)
        
        # Replace Perl operators
        expr_py = expr_py.replace('^', '**')  # Power operator
        
        # Handle function calls
        # random(1, 5, 1) → self.random.random(1, 5, 1)
        # Use word boundaries to avoid partial replacements
        for func in ['non_zero_random', 'list_random', 'random']:
            expr_py = re.sub(rf'\b{func}\(', f'self.random.{func}(', expr_py)
        
        # Handle Formula() and Compute()
        if 'Formula(' in expr or 'Compute(' in expr:
            return self._handle_formula(expr)
        
        # Evaluate safely
        try:
            # Create safe namespace
            namespace = {
                'self': self,
                'math': math,
                'pi': math.pi,
                'e': math.e,
            }
            result = eval(expr_py, namespace)
            return result
        except Exception as e:
            raise ValueError(f"Failed to evaluate: {expr} → {expr_py}: {e}")
    
    def _handle_context(self, line: str):
        """Handle Context() declarations and Context()->variables->are()."""
        # Context('Name')
        match = re.search(r'Context\(["\'](\w+)["\']\)', line)
        if match:
            context_name = match.group(1)
            self.context = Context(context_name)
            return

        # Context()->variables->are(y => 'Real', z => 'Real')
        vars_match = re.search(r'Context\(\)\s*->\s*variables\s*->\s*are\s*\((.*?)\)', line, re.DOTALL)
        if vars_match:
            vars_str = vars_match.group(1)
            # Parse key => value pairs
            self.context.variables = {}
            for pair in re.finditer(r'(\w+)\s*=>\s*["\'](\w+)["\']', vars_str):
                var_name = pair.group(1)
                var_type = pair.group(2)
                self.context.variables[var_name] = var_type
    
    def _handle_formula(self, expr: str):
        """Handle Formula() and Compute() objects and return a Formula object.

        In Perl, Formula()/Compute() produce MathObject formulas with methods like ->cmp().
        Mirror that here by returning a pg_math.Formula instance rather than a string.
        """
        # Extract the formula string
        match = re.search(r'(?:Formula|Compute)\(["\'](.+?)["\']\)', expr)
        if match:
            formula_str = match.group(1)
            # Interpolate Perl variables in the formula string
            formula_str = self._interpolate_perl_variables(formula_str)
            try:
                # Pass context variables to Formula
                variables = list(self.context.variables.keys()) if self.context else []
                return PGFormula(formula_str, variables=variables, context=self.context)
            except Exception:
                # Fallback to raw string if we can't construct a Formula
                return formula_str
        return expr

    def _interpolate_perl_variables(self, text: str) -> str:
        """Replace $var with actual values from self.variables."""
        def replace_var(match):
            var_name = match.group(1)
            if var_name in self.variables:
                value = self.variables[var_name]
                # If it's a numeric value, use it directly
                if isinstance(value, (int, float)):
                    return str(value)
                # If it's a Formula, get its string representation
                if hasattr(value, 'to_string'):
                    return value.to_string()
                return str(value)
            # Keep the variable if not found
            return match.group(0)

        return re.sub(r'\$(\w+)', replace_var, text)

    def _handle_cmp_expression(self, expr: str):
        """Parse Perl-style cmp expressions into an answer spec dict.

        Supports:
        - $var->cmp(...)
        - Compute('...')->cmp(...)
        - Formula('...')->cmp(...)

        Returns dict or None if not parsed.
        """
        s = expr.strip()
        # Case 1: $var->cmp(...)
        m = re.match(r'^\$(\w+)\s*->\s*cmp\s*\((.*?)\)\s*(?:->.*)?$', s, flags=re.DOTALL)
        if m:
            base_name = m.group(1)
            options_str = m.group(2)
            base_val = self.variables.get(base_name)
            custom_checker_src, opts = self._extract_custom_checker(options_str)
            checker = 'standard'
            if opts.get('upToConstant', False):
                checker = 'up_to_additive_constant'
            if custom_checker_src is not None:
                checker = 'custom'

            if hasattr(base_val, 'to_string'):
                value_str = base_val.to_string()
                variables = getattr(base_val, 'variables', [])
            else:
                value_str = str(base_val) if base_val is not None else ''
                variables = []

            spec = {
                'correct_value': value_str,
                'type': 'formula',
                'checker': checker,
                'variables': variables,
                'options': opts,
            }
            if custom_checker_src is not None:
                spec['options']['custom_checker_src'] = custom_checker_src
            return spec

        # Case 2: Compute('...')->cmp(...) or Formula('...')->cmp(...)
        m2 = re.match(r"^(?:Compute|Formula)\(\s*['\"](.+?)['\"]\s*\)\s*->\s*cmp\s*\((.*?)\)\s*(?:->.*)?$", s, flags=re.DOTALL)
        if m2:
            expr_str = m2.group(1)
            options_str = m2.group(2)
            custom_checker_src, opts = self._extract_custom_checker(options_str)
            checker = 'standard'
            if opts.get('upToConstant', False):
                checker = 'up_to_additive_constant'
            if custom_checker_src is not None:
                checker = 'custom'
            return {
                'correct_value': expr_str,
                'type': 'formula',
                'checker': checker,
                'variables': [],
                'options': opts | ({'custom_checker_src': custom_checker_src} if custom_checker_src is not None else {}),
            }

        return None

    def _handle_multianswer(self, expr: str):
        """Parse MultiAnswer(arg1, arg2, ...)[->with(...)] into a group spec.

        Returns a dict with keys:
          - __multi__: True
          - answers: list of evaluated values (Formula or primitives)
          - checker: 'standard' or 'custom'
          - options: parsed options from ->with(...)
          - custom_checker_src: optional Perl sub body string
        """
        s = expr.strip()
        m = re.match(r'^MultiAnswer\s*\((.*?)\)\s*(?:->\s*with\s*\((.*)\)\s*)?$', s, flags=re.DOTALL)
        if not m:
            return None
        args_str = m.group(1)
        with_opts = m.group(2) or ''

        # Split args_str by commas not inside parentheses or quotes
        args = []
        current = ''
        depth = 0
        in_str = False
        str_ch = ''
        for ch in args_str:
            if in_str:
                current += ch
                if ch == str_ch:
                    in_str = False
                continue
            if ch in ('"', "'"):
                in_str = True
                str_ch = ch
                current += ch
                continue
            if ch == '(':
                depth += 1
                current += ch
                continue
            if ch == ')':
                depth -= 1
                current += ch
                continue
            if ch == ',' and depth == 0:
                if current.strip():
                    args.append(current.strip())
                current = ''
                continue
            current += ch
        if current.strip():
            args.append(current.strip())

        values = []
        for a in args:
            try:
                v = self._eval_expression(a)
            except Exception:
                v = a
            values.append(v)

        # Extract custom checker from with(...), if present
        custom_src, opts = self._extract_custom_checker(with_opts)
        checker = 'custom' if custom_src is not None else 'standard'

        return {
            '__multi__': True,
            'answers': values,
            'checker': checker,
            'options': opts,
            'custom_checker_src': custom_src,
        }

    def _parse_cmp_options(self, s: str) -> Dict[str, Any]:
        """Parse minimal Perl-style cmp options 'key => value'."""
        opts: Dict[str, Any] = {}
        parts = [p.strip() for p in s.split(',') if p.strip()]
        for part in parts:
            if '=>' not in part:
                continue
            key, val = [x.strip() for x in part.split('=>', 1)]
            key = key.strip("'\"")
            v = val.strip()
            if v in ('1', 'true', 'True'):
                opts[key] = True
            elif v in ('0', 'false', 'False'):
                opts[key] = False
            else:
                v_clean = v.strip("'\"")
                try:
                    opts[key] = int(v_clean)
                except ValueError:
                    try:
                        opts[key] = float(v_clean)
                    except ValueError:
                        opts[key] = v_clean
        return opts
    
    def _extract_custom_checker(self, s: str):
        """Extract checker => sub { ... } from cmp options string if present.

        Returns (custom_checker_src or None, options_dict_without_checker).
        """
        m = re.search(r"checker\s*=>\s*sub\s*\{", s, flags=re.DOTALL)
        if not m:
            return None, self._parse_cmp_options(s)
        start = m.end() - 1
        depth = 0
        i = start
        while i < len(s):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
            i += 1
        else:
            return None, self._parse_cmp_options(s)
        code = s[start + 1 : end]
        s_wo = s[: m.start()] + s[end + 1 :]
        return code.strip(), self._parse_cmp_options(s_wo)
    
    def _strip_comments(self, code: str) -> str:
        """Remove Perl comments."""
        return re.sub(r'#.*$', '', code, flags=re.MULTILINE)
