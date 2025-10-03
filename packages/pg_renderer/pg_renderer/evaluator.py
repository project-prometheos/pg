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
        
        # Process line by line
        for line in setup_code.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle Context() calls
            if 'Context(' in line:
                self._handle_context(line)
                continue
            
            # Handle list assignment: ($var1, $var2) = (expr1, expr2);
            if line.startswith('(') and '=' in line and line.count('(') >= 2:
                # Find the = sign and split into left and right parts
                eq_pos = line.find('=')
                left_part = line[:eq_pos].strip()
                right_part = line[eq_pos+1:].strip().rstrip(';')
                
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
            if match := re.match(r'\$(\w+)\s*=\s*(.+?);', line):
                var_name = match.group(1)
                expr = match.group(2)
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
        """Handle Context() declarations."""
        match = re.search(r'Context\(["\'](\w+)["\']\)', line)
        if match:
            context_name = match.group(1)
            self.context = Context(context_name)
    
    def _handle_formula(self, expr: str):
        """Handle Formula() and Compute() objects and return a Formula object.

        In Perl, Formula()/Compute() produce MathObject formulas with methods like ->cmp().
        Mirror that here by returning a pg_math.Formula instance rather than a string.
        """
        # Extract the formula string
        match = re.search(r'(?:Formula|Compute)\(["\'](.+?)["\']\)', expr)
        if match:
            formula_str = match.group(1)
            try:
                return PGFormula(formula_str, context=self.context)
            except Exception:
                # Fallback to raw string if we can't construct a Formula
                return formula_str
        return expr

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
            opts = self._parse_cmp_options(options_str)
            checker = 'standard'
            if opts.get('upToConstant', False):
                checker = 'up_to_additive_constant'

            if hasattr(base_val, 'to_string'):
                value_str = base_val.to_string()
                variables = getattr(base_val, 'variables', [])
            else:
                value_str = str(base_val) if base_val is not None else ''
                variables = []

            return {
                'correct_value': value_str,
                'type': 'formula',
                'checker': checker,
                'variables': variables,
                'options': opts,
            }

        # Case 2: Compute('...')->cmp(...) or Formula('...')->cmp(...)
        m2 = re.match(r"^(?:Compute|Formula)\(\s*['\"](.+?)['\"]\s*\)\s*->\s*cmp\s*\((.*?)\)\s*(?:->.*)?$", s, flags=re.DOTALL)
        if m2:
            expr_str = m2.group(1)
            options_str = m2.group(2)
            opts = self._parse_cmp_options(options_str)
            checker = 'standard'
            if opts.get('upToConstant', False):
                checker = 'up_to_additive_constant'
            return {
                'correct_value': expr_str,
                'type': 'formula',
                'checker': checker,
                'variables': [],
                'options': opts,
            }

        return None

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
    
    def _strip_comments(self, code: str) -> str:
        """Remove Perl comments."""
        return re.sub(r'#.*$', '', code, flags=re.MULTILINE)
