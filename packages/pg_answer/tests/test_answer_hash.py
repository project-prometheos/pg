"""Tests for AnswerResult data class."""

import pytest

from pg_answer.answer_hash import AnswerResult


def test_answer_result_creation():
    """Test creating AnswerResult."""
    result = AnswerResult(
        score=1.0,
        correct=True,
        student_answer="42",
        correct_answer="42",
        type="numeric",
    )

    assert result.score == 1.0
    assert result.correct is True
    assert result.student_answer == "42"
    assert result.type == "numeric"


def test_answer_result_score_clamping():
    """Test score is clamped to [0, 1]."""
    result1 = AnswerResult(score=1.5)
    assert result1.score == 1.0

    result2 = AnswerResult(score=-0.5)
    assert result2.score == 0.0


def test_answer_result_correct_sync():
    """Test correct flag syncs with score."""
    # Score 1.0 -> correct True
    result1 = AnswerResult(score=1.0)
    assert result1.correct is True

    # Score 0.0 -> correct False
    result2 = AnswerResult(score=0.0)
    assert result2.correct is False


def test_add_message():
    """Test adding feedback messages."""
    result = AnswerResult()
    result.add_message("First message")
    result.add_message("Second message")

    assert len(result.messages) == 2
    assert "First message" in result.messages

    # Don't add duplicates
    result.add_message("First message")
    assert len(result.messages) == 2


def test_set_error():
    """Test setting error state."""
    result = AnswerResult(score=1.0, correct=True)
    result.set_error("Parse error")

    assert result.error_flag is True
    assert result.error_message == "Parse error"
    assert result.score == 0.0
    assert result.correct is False


def test_is_correct():
    """Test is_correct method with custom threshold."""
    result = AnswerResult(score=0.8)

    assert result.is_correct(threshold=0.7) is True
    assert result.is_correct(threshold=0.9) is False
    assert result.is_correct() is False  # Default threshold 1.0


def test_is_partial_credit():
    """Test partial credit detection."""
    assert AnswerResult(score=0.5).is_partial_credit() is True
    assert AnswerResult(score=0.0).is_partial_credit() is False
    assert AnswerResult(score=1.0).is_partial_credit() is False


def test_is_blank():
    """Test blank answer detection."""
    assert AnswerResult(original_student_answer="").is_blank() is True
    assert AnswerResult(original_student_answer="  ").is_blank() is True
    assert AnswerResult(original_student_answer="42").is_blank() is False


def test_to_dict():
    """Test serialization to dictionary."""
    result = AnswerResult(
        score=1.0,
        student_answer="42",
        correct_answer="42",
        type="numeric",
    )

    data = result.to_dict()

    assert isinstance(data, dict)
    assert data["score"] == 1.0
    assert data["student_answer"] == "42"
    assert data["type"] == "numeric"


def test_from_dict():
    """Test deserialization from dictionary."""
    data = {
        "score": 0.5,
        "correct": False,
        "student_answer": "40",
        "correct_answer": "42",
        "type": "numeric",
    }

    result = AnswerResult.from_dict(data)

    assert result.score == 0.5
    assert result.correct is False
    assert result.student_answer == "40"


def test_correct_answer_factory():
    """Test correct answer factory method."""
    result = AnswerResult.correct_answer("42", "42", "numeric")

    assert result.score == 1.0
    assert result.correct is True
    assert result.answer_message == "Correct!"


def test_incorrect_answer_factory():
    """Test incorrect answer factory method."""
    result = AnswerResult.incorrect_answer("40", "42", "numeric")

    assert result.score == 0.0
    assert result.correct is False
    assert result.answer_message == "Incorrect."


def test_error_answer_factory():
    """Test error answer factory method."""
    result = AnswerResult.error_answer("abc", "Not a number", "numeric")

    assert result.error_flag is True
    assert result.error_message == "Not a number"
    assert result.score == 0.0


def test_partial_credit_factory():
    """Test partial credit factory method."""
    result = AnswerResult.partial_credit_answer(0.7, "approx", "exact", "numeric")

    assert result.score == 0.7
    assert result.correct is False  # Not fully correct
    assert "70%" in result.answer_message
