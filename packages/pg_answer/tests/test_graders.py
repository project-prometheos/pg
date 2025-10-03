"""Tests for problem graders."""

import pytest

from pg_answer.answer_hash import AnswerResult
from pg_answer.graders import (
    AverageGrader,
    CustomGrader,
    FirstAnswerGrader,
    MinimumGrader,
    StandardGrader,
)


def test_standard_grader_all_correct():
    """Test standard grader with all correct answers."""
    answers = [
        AnswerResult(score=1.0, correct=True),
        AnswerResult(score=1.0, correct=True),
        AnswerResult(score=1.0, correct=True),
    ]

    grader = StandardGrader()
    score = grader.grade(answers)

    assert score == 1.0


def test_standard_grader_one_wrong():
    """Test standard grader with one wrong answer."""
    answers = [
        AnswerResult(score=1.0, correct=True),
        AnswerResult(score=0.0, correct=False),
        AnswerResult(score=1.0, correct=True),
    ]

    grader = StandardGrader()
    score = grader.grade(answers)

    assert score == 0.0


def test_standard_grader_empty():
    """Test standard grader with no answers."""
    grader = StandardGrader()
    score = grader.grade([])

    assert score == 0.0


def test_average_grader_unweighted():
    """Test average grader with equal weights."""
    answers = [
        AnswerResult(score=1.0),
        AnswerResult(score=0.5),
        AnswerResult(score=0.0),
    ]

    grader = AverageGrader()
    score = grader.grade(answers)

    assert score == 0.5  # (1.0 + 0.5 + 0.0) / 3


def test_average_grader_weighted():
    """Test average grader with custom weights."""
    answers = [
        AnswerResult(score=1.0),  # 50% weight
        AnswerResult(score=0.0),  # 30% weight
        AnswerResult(score=1.0),  # 20% weight
    ]

    grader = AverageGrader(weights=[0.5, 0.3, 0.2])
    score = grader.grade(answers)

    assert score == 0.7  # 1.0*0.5 + 0.0*0.3 + 1.0*0.2


def test_average_grader_weight_validation():
    """Test average grader validates weights sum to 1.0."""
    answers = [AnswerResult(score=1.0), AnswerResult(score=0.5)]

    grader = AverageGrader(weights=[0.4, 0.4])  # Sum = 0.8, not 1.0

    with pytest.raises(ValueError, match="sum to 1.0"):
        grader.grade(answers)


def test_average_grader_weight_count_mismatch():
    """Test average grader validates weight count."""
    answers = [AnswerResult(score=1.0), AnswerResult(score=0.5)]

    grader = AverageGrader(weights=[0.5, 0.3, 0.2])  # 3 weights, 2 answers

    with pytest.raises(ValueError, match="must match"):
        grader.grade(answers)


def test_first_answer_grader():
    """Test first answer grader."""
    answers = [
        AnswerResult(score=0.5),
        AnswerResult(score=1.0),
        AnswerResult(score=0.0),
    ]

    grader = FirstAnswerGrader()
    score = grader.grade(answers)

    assert score == 0.5  # Score of first answer


def test_minimum_grader():
    """Test minimum grader."""
    answers = [
        AnswerResult(score=1.0),
        AnswerResult(score=0.3),
        AnswerResult(score=0.8),
    ]

    grader = MinimumGrader()
    score = grader.grade(answers)

    assert score == 0.3  # Minimum score


def test_custom_grader():
    """Test custom grader with user function."""

    def my_grading(answers):
        # Custom logic: average of first two answers only
        if len(answers) < 2:
            return 0.0
        return (answers[0].score + answers[1].score) / 2

    answers = [
        AnswerResult(score=1.0),
        AnswerResult(score=0.6),
        AnswerResult(score=0.0),  # Ignored
    ]

    grader = CustomGrader(my_grading)
    score = grader.grade(answers)

    assert score == 0.8  # (1.0 + 0.6) / 2
