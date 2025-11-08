"""LinearRelation - Linear relations and inequalities.

Reference: macros/parsers/parserLinearRelation.pl
"""

from typing import Union, List, Any, Optional


class LinearRelation:
    """
    LinearRelation represents a linear (in)equality like 'x + y <= 5'.

    Can be created from:
    - A formula string: LinearRelation("x + y <= 5")
    - A vector, point, and sign: LinearRelation([1,1], [2,3], "<=")
    - A vector, constant, and sign: LinearRelation([1,1], 5, "<=")
    """

    def __init__(self, *args, **options):
        """
        Initialize a LinearRelation.

        Args can be:
        - Single string: formula like "x + y <= 5"
        - Three arguments: vector, point/constant, sign
        """
        self.options = {
            'standardForm': False,
            **options
        }

        if len(args) == 1 and isinstance(args[0], str):
            # Formula string
            self.formula = args[0]
            self._parse_formula(args[0])
        elif len(args) == 3:
            # vector, point/constant, sign
            vector, value, sign = args
            self.vector = vector if isinstance(vector, list) else list(vector)
            self.value = value
            self.sign = sign
            self.formula = self._build_formula()
        else:
            raise ValueError("Invalid arguments to LinearRelation")

    def _parse_formula(self, formula: str):
        """Parse a formula string to extract components."""
        # Simple parsing - find the relation operator
        for op in ['<=', '>=', '!=', '<', '>', '=']:
            if op in formula:
                parts = formula.split(op, 1)
                self.lhs = parts[0].strip()
                self.rhs = parts[1].strip()
                self.sign = op
                break
        else:
            # No operator found
            self.lhs = formula
            self.rhs = '0'
            self.sign = '='

    def _build_formula(self) -> str:
        """Build a formula string from components."""
        # Simple linear relation: a*x + b*y + ... sign constant
        terms = []
        var_names = ['x', 'y', 'z', 'w']  # Standard variable names

        for i, coef in enumerate(self.vector):
            if i < len(var_names):
                if coef == 1:
                    terms.append(var_names[i])
                elif coef == -1:
                    terms.append(f'-{var_names[i]}')
                elif coef != 0:
                    terms.append(f'{coef}*{var_names[i]}')

        lhs = ' + '.join(terms).replace('+ -', '- ')
        return f'{lhs} {self.sign} {self.value}'

    def check_at(self, point: Union[List[float], Any]) -> bool:
        """
        Check if a point satisfies the relation.

        Args:
            point: List of coordinates or Point/Vector object

        Returns:
            True if point satisfies the relation
        """
        # Convert to list if needed
        if hasattr(point, 'data'):
            point = point.data
        elif not isinstance(point, list):
            point = list(point)

        # Compute dot product if we have vector form
        if hasattr(self, 'vector'):
            dot_product = sum(v * p for v, p in zip(self.vector, point))

            # Compare with value using the sign
            if self.sign == '=':
                return abs(dot_product - self.value) < 1e-10
            elif self.sign == '<':
                return dot_product < self.value
            elif self.sign == '>':
                return dot_product > self.value
            elif self.sign == '<=':
                return dot_product <= self.value
            elif self.sign == '>=':
                return dot_product >= self.value
            elif self.sign == '!=':
                return abs(dot_product - self.value) >= 1e-10

        return False

    def cmp(self, **options):
        """Create an answer evaluator."""
        class LinearRelationEvaluator:
            def __init__(self, lr):
                self.lr = lr

            def evaluate(self, answer: str) -> dict:
                """Evaluate a student answer."""
                # Simple comparison - check if formulas match
                return {
                    'correct': str(answer).strip() == str(self.lr.formula).strip(),
                    'score': 1.0 if str(answer).strip() == str(self.lr.formula).strip() else 0.0,
                    'message': ''
                }

        return LinearRelationEvaluator(self)

    def reduce(self):
        """
        Reduce the linear relation to simplest form.

        Returns:
            Self for method chaining
        """
        # For now, just return self
        # Full implementation would simplify coefficients, etc.
        return self

    def __str__(self):
        """String representation."""
        return self.formula

    def __repr__(self):
        """Developer representation."""
        return f'LinearRelation("{self.formula}")'
