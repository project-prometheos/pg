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
        
        # Process line by line
        for line in setup_code.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle Context() calls
            if 'Context(' in line:
                self._handle_context(line)
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
        for func in ['random', 'non_zero_random', 'list_random']:
            expr_py = expr_py.replace(f'{func}(', f'self.random.{func}(')
        
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

