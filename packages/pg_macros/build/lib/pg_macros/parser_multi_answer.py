"""MultiAnswer macro implementation (simplified parity)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, List

from pg_answer.answer_hash import AnswerResult
from pg_answer.evaluator import AnswerEvaluator
from pg_answer.evaluators.string import StringEvaluator

from .runtime.answers import queue_answer, register_named_answer


@dataclass
class MultiAnswer:
    """Group several related answers for joint evaluation."""

    evaluators: List[AnswerEvaluator] = field(default_factory=list)
    checker: Callable[[List[AnswerResult]], AnswerResult] | None = None
    named: List[str] = field(default_factory=list)

    def __init__(self, *evaluators: AnswerEvaluator):
        self.evaluators = list(evaluators)
        self.checker = None
        self.named = []

    def with_(self, **options: Any) -> 'MultiAnswer':
        checker = options.get('checker')
        if callable(checker):
            self.checker = checker
        return self

    def assign_to(self, *names: str) -> 'MultiAnswer':
        self.named.extend(names)
        return self

    def cmp(self) -> 'MultiAnswerEvaluator':
        return MultiAnswerEvaluator(self.evaluators, checker=self.checker)

    def install(self) -> None:
        if self.named:
            for label, evaluator in zip(self.named, self.evaluators):
                register_named_answer(label, evaluator)
        else:
            queue_answer(*self.evaluators)


class MultiAnswerEvaluator(AnswerEvaluator):
    """Evaluator that dispatches to multiple underlying evaluators."""

    answer_type = 'multi'

    def __init__(self, evaluators: Iterable[AnswerEvaluator], checker: Callable[[List[AnswerResult]], AnswerResult] | None = None, **options: Any):
        super().__init__(correct_answer='', **options)
        self.evaluators = list(evaluators)
        self.checker = checker

    def evaluate(self, student_answer: str) -> AnswerResult:
        values = self._split_student_answer(student_answer)
        results: List[AnswerResult] = []
        for evaluator, value in zip(self.evaluators, values):
            result = evaluator.evaluate(value)
            results.append(result)
        if self.checker:
            total = self.checker(results)
            return total
        score = sum(r.score for r in results) / max(1, len(results))
        combined = AnswerResult(
            score=score,
            correct=all(r.correct for r in results),
            student_answer=json.dumps([r.student_answer for r in results]),
            correct_answer=json.dumps([r.correct_answer for r in results]),
            type='multi',
            metadata={'component_results': [r.to_dict() for r in results]},
        )
        if any(r.messages for r in results):
            for message_list in (r.messages for r in results if r.messages):
                for msg in message_list:
                    combined.add_message(msg)
        return combined

    def _split_student_answer(self, answer: str) -> List[str]:
        if not answer:
            return [''] * len(self.evaluators)
        if answer.strip().startswith('['):
            try:
                parsed = json.loads(answer)
                return [str(item) for item in parsed]
            except json.JSONDecodeError:
                pass
        parts = [part.strip() for part in answer.split(',')]
        while len(parts) < len(self.evaluators):
            parts.append('')
        return parts


def multi_answer_cmp(*evaluators: AnswerEvaluator) -> MultiAnswerEvaluator:
    return MultiAnswer(*evaluators).cmp()


__exports__ = ['MultiAnswer', 'multi_answer_cmp']

__all__ = list(__exports__)
