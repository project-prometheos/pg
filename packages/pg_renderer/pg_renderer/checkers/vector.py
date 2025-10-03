"""Vector and point answer checkers."""

from __future__ import annotations

import re
from typing import Tuple, Dict, Any, List

from sympy import sympify

from .base import AnswerChecker


def _parse_components(s: str) -> List[float]:
    parts = [p.strip() for p in s.split(',') if p.strip()]
    vals: List[float] = []
    for p in parts:
        try:
            vals.append(float(sympify(p)))
        except Exception:
            raise ValueError(f"Invalid component: {p}")
    return vals


class VectorChecker(AnswerChecker):
    """Check vectors like <1, 2, 3>."""

    def check(self, student_answer: str, correct_answer: str, context: Dict[str, Any] | None = None) -> Tuple[bool, str]:
        try:
            s = student_answer.strip()
            c = correct_answer.strip()
            if not (s.startswith('<') and s.endswith('>') and c.startswith('<') and c.endswith('>')):
                return False, "Invalid vector format. Use <a, b, c>."
            s_vals = _parse_components(s[1:-1])
            c_vals = _parse_components(c[1:-1])
        except Exception as e:
            return False, f"Invalid vector: {e}"

        if len(s_vals) != len(c_vals):
            return False, "Vector dimensions do not match."
        for sv, cv in zip(s_vals, c_vals):
            if abs(sv - cv) > self.tolerance:
                return False, "Incorrect vector."
        return True, "Correct!"


class PointChecker(AnswerChecker):
    """Check points like (1, 2) by numeric tolerance."""

    def check(self, student_answer: str, correct_answer: str, context: Dict[str, Any] | None = None) -> Tuple[bool, str]:
        try:
            s = student_answer.strip()
            c = correct_answer.strip()
            if not (s.startswith('(') and s.endswith(')') and c.startswith('(') and c.endswith(')')):
                return False, "Invalid point format. Use (a, b[, c])."
            s_vals = _parse_components(s[1:-1])
            c_vals = _parse_components(c[1:-1])
        except Exception as e:
            return False, f"Invalid point: {e}"

        if len(s_vals) != len(c_vals):
            return False, "Point dimensions do not match."
        for sv, cv in zip(s_vals, c_vals):
            if abs(sv - cv) > self.tolerance:
                return False, "Incorrect point."
        return True, "Correct!"

