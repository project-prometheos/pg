"""
Tests for grading system.
"""

import pytest
from pg_answer import AnswerResult
from pg_translator.grading import (
    std_problem_grader,
    avg_problem_grader,
    process_checkbox_radio_input,
    stringify_answers,
)


def test_process_checkbox_radio_single():
    """Test checkbox/radio processing with single selection."""
    # Radio button (single checked)
    response = [("yes", "CHECKED"), ("no", "")]
    result = process_checkbox_radio_input(response)
    assert result == "yes"


def test_process_checkbox_radio_multiple():
    """Test checkbox processing with multiple selections."""
    # Checkbox (multiple checked)
    response = [("a", "CHECKED"), ("b", ""), ("c", "CHECKED")]
    result = process_checkbox_radio_input(response)
    assert result == ["a", "c"]


def test_process_checkbox_radio_none():
    """Test processing with no selection."""
    response = [("a", ""), ("b", "")]
    result = process_checkbox_radio_input(response)
    assert result == ""


def test_std_grader_all_correct():
    """Test standard grader with all correct answers."""
    answers = {
        "ans1": AnswerResult(score=1, correct=True, student_answer="42", correct_answer="42"),
        "ans2": AnswerResult(score=1, correct=True, student_answer="7", correct_answer="7"),
    }

    state = {
        "recorded_score": 0,
        "num_of_correct_ans": 0,
        "num_of_incorrect_ans": 0,
    }

    result, new_state = std_problem_grader(answers, state, answers_submitted=True)

    assert result["score"] == 1
    assert new_state["recorded_score"] == 1
    assert new_state["num_of_correct_ans"] == 1
    assert new_state["num_of_incorrect_ans"] == 0


def test_std_grader_partial_wrong():
    """Test standard grader with some wrong answers."""
    answers = {
        "ans1": AnswerResult(score=1, correct=True, student_answer="42", correct_answer="42"),
        "ans2": AnswerResult(score=0, correct=False, student_answer="8", correct_answer="7"),
    }

    state = {
        "recorded_score": 0,
        "num_of_correct_ans": 0,
        "num_of_incorrect_ans": 0,
    }

    result, new_state = std_problem_grader(answers, state, answers_submitted=True)

    # All-or-nothing: should be 0
    assert result["score"] == 0
    assert new_state["recorded_score"] == 0
    assert new_state["num_of_incorrect_ans"] == 1


def test_std_grader_not_submitted():
    """Test standard grader when answers not submitted."""
    answers = {
        "ans1": AnswerResult(score=1, correct=True, student_answer="42", correct_answer="42"),
    }

    state = {"recorded_score": 0}

    result, new_state = std_problem_grader(answers, state, answers_submitted=False)

    # Should not grade
    assert result["score"] == 0
    assert new_state["recorded_score"] == 0


def test_avg_grader_partial_credit():
    """Test average grader with partial credit."""
    answers = {
        "ans1": AnswerResult(score=1, correct=True, student_answer="42", correct_answer="42"),
        "ans2": AnswerResult(score=0.5, correct=False, student_answer="6", correct_answer="7"),
        "ans3": AnswerResult(score=0, correct=False, student_answer="0", correct_answer="10"),
    }

    state = {
        "recorded_score": 0,
        "num_of_correct_ans": 0,
        "num_of_incorrect_ans": 0,
    }

    result, new_state = avg_problem_grader(answers, state, answers_submitted=True)

    # Average: (1 + 0.5 + 0) / 3 = 0.5
    assert result["score"] == 0.5
    assert new_state["recorded_score"] == 0.5
    assert new_state["num_of_incorrect_ans"] == 1


def test_avg_grader_with_weights():
    """Test average grader with weighted answers."""
    # Create answer with weight
    ans1 = AnswerResult(score=1, correct=True, student_answer="42", correct_answer="42")
    ans1.weight = 2  # Double weight

    ans2 = AnswerResult(score=0, correct=False, student_answer="0", correct_answer="7")
    ans2.weight = 1

    answers = {"ans1": ans1, "ans2": ans2}

    state = {"recorded_score": 0}

    result, new_state = avg_problem_grader(answers, state, answers_submitted=True)

    # Weighted average: (2*1 + 1*0) / (2+1) = 2/3
    assert abs(result["score"] - (2/3)) < 0.001


def test_avg_grader_credit_from():
    """Test average grader with credit_from (optional answers)."""
    # Main answer correct
    ans1 = AnswerResult(score=1, correct=True, student_answer="42", correct_answer="42")
    ans1.credit_from = "ans2"  # Gives credit to ans2

    # Optional answer (blank)
    ans2 = AnswerResult(score=0, correct=False, student_answer="", correct_answer="10")

    answers = {"ans1": ans1, "ans2": ans2}

    state = {"recorded_score": 0}

    result, new_state = avg_problem_grader(answers, state, answers_submitted=True)

    # ans2 should get credit because it's blank and ans1 is correct
    assert result["score"] == 1


def test_stringify_answers():
    """Test answer stringification."""
    from pg_math import Real

    answers = {
        "ans1": AnswerResult(
            score=1,
            correct=True,
            student_answer=Real(42.5),
            correct_answer=Real(42.5)
        )
    }

    stringify_answers(answers)

    # Should be converted to strings
    assert isinstance(answers["ans1"].student_answer, str)
    assert isinstance(answers["ans1"].correct_answer, str)
