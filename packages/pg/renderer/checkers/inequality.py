"""Inequality checker using SymPy relational evaluation with sampling."""

from __future__ import annotations

import random
from typing import Tuple, Dict, Any, Set as TSet

from sympy import sympify, Symbol
from sympy.logic.boolalg import Boolean

from .base import AnswerChecker


class InequalityChecker(AnswerChecker):
    """Check inequalities by sampling variable assignments."""

    def __init__(self, tolerance: float = 0.01, samples: int = 32):
        super().__init__(tolerance)
        self.samples = samples

    def check(self, student_answer: str, correct_answer: str, context: Dict[str, Any] | None = None) -> Tuple[bool, str]:
        context = context or {}
        try:
            s_expr = self._parse_rel(student_answer)
            c_expr = self._parse_rel(correct_answer)
        except Exception as e:
            return False, f"Invalid inequality: {e}"

        # Determine variables from context or expressions
        vars_: TSet[Symbol] = set()
        ctx_vars = context.get('variables') or []
        if ctx_vars:
            vars_ = {Symbol(v) for v in ctx_vars}
        else:
            vars_.update(getattr(s_expr, 'free_symbols', set()))
            vars_.update(getattr(c_expr, 'free_symbols', set()))
        if not vars_:
            # No variables; evaluate both to booleans
            try:
                return (bool(s_expr == c_expr), "Correct!" if s_expr == c_expr else "Incorrect.")
            except Exception as e:
                return False, f"Invalid inequality: {e}"

        # Samples and limits from options if provided
        options = context.get('options', {})
        samples = options.get('numPoints', self.samples)
        limits = options.get('limits', {}) or {}

        random.seed(4242)
        for _ in range(samples):
            bindings = {}
            for v in vars_:
                name = str(v)
                if name in limits:
                    lo, hi = limits[name]
                else:
                    lo, hi = -10, 10
                bindings[name] = random.uniform(lo, hi)
            try:
                s_val = bool(s_expr.subs(bindings))
                c_val = bool(c_expr.subs(bindings))
            except Exception:
                # If substitution fails, try next sample
                continue
            if s_val != c_val:
                return False, "Your inequality does not define the same set."
        return True, "Correct!"

    def _parse_rel(self, s: str) -> Boolean:
        s = s.replace('^', '**')
        expr = sympify(s)
        if not isinstance(expr, Boolean):
            raise ValueError("Not an inequality or boolean expression.")
        return expr
