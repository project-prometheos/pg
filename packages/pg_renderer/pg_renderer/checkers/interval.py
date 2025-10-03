"""Interval answer checker using SymPy sets."""

from __future__ import annotations

import re
from typing import Tuple, Dict, Any, List

from sympy import Interval, Union, oo, sympify
from sympy.sets.sets import Set

from .base import AnswerChecker


class IntervalChecker(AnswerChecker):
    """Check interval answers like [a, b), (-inf, 2], or unions."""

    def check(
        self,
        student_answer: str,
        correct_answer: str,
        context: Dict[str, Any] | None = None,
    ) -> Tuple[bool, str]:
        context = context or {}

        try:
            student_set = self._parse_interval(student_answer)
            correct_set = self._parse_interval(correct_answer)
        except Exception as e:
            return False, f"Invalid interval: {e}"

        if self._sets_equal(student_set, correct_set):
            return True, "Correct!"
        return False, "Incorrect interval."

    def _parse_interval(self, s: str) -> Set:
        s = s.strip()
        # Normalize infinity symbols
        s = (
            s.replace('∞', 'inf')
            .replace('infinity', 'inf')
            .replace('−', '-')
        )

        # Split unions by 'U' or '∪'
        parts = re.split(r"\s*[U∪]\s*", s)
        intervals: List[Set] = []
        for part in parts:
            part = part.strip()
            m = re.match(r"^([\[(])\s*([^,]+)\s*,\s*([^\])]+)\s*([\])])$", part)
            if not m:
                raise ValueError(f"Cannot parse interval part: '{part}'")
            left_br, a_str, b_str, right_br = m.groups()
            a = self._parse_endpoint(a_str)
            b = self._parse_endpoint(b_str)
            if a is None or b is None:
                raise ValueError(f"Invalid endpoints in '{part}'")
            left_open = left_br == '('
            right_open = right_br == ')'
            intervals.append(Interval(a, b, left_open=left_open, right_open=right_open))

        if not intervals:
            raise ValueError("Empty interval")

        if len(intervals) == 1:
            return intervals[0]
        return Union(*intervals)

    def _parse_endpoint(self, s: str):
        s = s.strip().lower()
        if s in {"inf", "+inf", "+infty", "infty", "+oo", "oo"}:
            return oo
        if s in {"-inf", "-infty", "-oo"}:
            return -oo
        try:
            return sympify(s)
        except Exception:
            return None

    def _sets_equal(self, a: Set, b: Set) -> bool:
        # Try structural equality first
        if a == b:
            return True
        # Fallback: sample points in a reasonable range
        # Probe a grid around -10..10 and some endpoints
        import random

        def in_set(val, S: Set) -> bool:
            try:
                return bool(val in S)
            except Exception:
                return False

        random.seed(1234)
        samples = [i for i in range(-10, 11)]
        samples += [random.uniform(-10, 10) for _ in range(20)]
        for x in samples:
            if in_set(x, a) != in_set(x, b):
                return False
        return True

