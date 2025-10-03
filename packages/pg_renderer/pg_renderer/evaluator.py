"""Execute Perl-like PG setup code in Python."""

import re
import math
from typing import Dict, Any
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
    
    def _handle_formula(self, expr: str) -> str:
        """Handle Formula() and Compute() objects."""
        # Extract the formula string
        match = re.search(r'(?:Formula|Compute)\(["\'](.+?)["\']\)', expr)
        if match:
            return match.group(1)
        return expr
    
    def _strip_comments(self, code: str) -> str:
        """Remove Perl comments."""
        return re.sub(r'#.*$', '', code, flags=re.MULTILINE)

