"""Tests for choice macros."""

import pytest

from pg_macros import loadMacros


def test_multiple_choice_basic():
    """Test basic multiple choice."""
    macros = loadMacros("PGchoicemacros.pl")
    new_multiple_choice = macros["new_multiple_choice"]

    mc = new_multiple_choice()
    mc.qa(
        "What is 2 + 2?",
        "4",  # Correct
        "3",
        "5",
        "6",
    )

    assert mc.question == "What is 2 + 2?"
    assert mc.choices[0] == "4"
    assert mc.correct_index == 0
    assert mc.correct_ans() == "4"


def test_multiple_choice_print():
    """Test multiple choice HTML generation."""
    macros = loadMacros("PGchoicemacros.pl")
    new_multiple_choice = macros["new_multiple_choice"]

    mc = new_multiple_choice()
    mc.qa("Question?", "A", "B", "C")

    question_html = mc.print_q()
    assert "Question?" in question_html

    choices_html = mc.print_a()
    assert 'type="radio"' in choices_html
    assert "A" in choices_html
    assert "B" in choices_html


def test_multiple_choice_shuffle():
    """Test shuffling choices."""
    macros = loadMacros("PGchoicemacros.pl")
    new_multiple_choice = macros["new_multiple_choice"]

    mc = new_multiple_choice()
    mc.qa("Question?", "Correct", "Wrong1", "Wrong2", "Wrong3")

    # Shuffle with seed
    mc.shuffle(seed=42)

    # Correct answer should still be identifiable
    assert mc.correct_ans() == "Correct"
    # Correct index should have updated
    assert mc.choices[mc.correct_index] == "Correct"


def test_multiple_choice_evaluator():
    """Test multiple choice answer evaluator."""
    macros = loadMacros("PGchoicemacros.pl")
    new_multiple_choice = macros["new_multiple_choice"]

    mc = new_multiple_choice()
    mc.qa("Question?", "A", "B", "C")

    evaluator = mc.cmp()

    # Correct index (0)
    result = evaluator.evaluate("0")
    assert result.correct is True

    # Wrong index
    result = evaluator.evaluate("1")
    assert result.correct is False


def test_true_false_basic():
    """Test basic true/false."""
    macros = loadMacros("PGchoicemacros.pl")
    new_true_false = macros["new_true_false"]

    tf = new_true_false()
    tf.qa("2 + 2 = 4", True)

    assert tf.question == "2 + 2 = 4"
    assert tf.correct is True
    assert tf.correct_ans() == "T"


def test_true_false_string_input():
    """Test true/false with string input."""
    macros = loadMacros("PGchoicemacros.pl")
    new_true_false = macros["new_true_false"]

    tf = new_true_false()
    tf.qa("Statement", "T")
    assert tf.correct is True

    tf.qa("Statement", "F")
    assert tf.correct is False

    tf.qa("Statement", "true")
    assert tf.correct is True


def test_true_false_print():
    """Test true/false HTML generation."""
    macros = loadMacros("PGchoicemacros.pl")
    new_true_false = macros["new_true_false"]

    tf = new_true_false()
    tf.qa("Question?", True)

    question_html = tf.print_q()
    assert "Question?" in question_html

    choices_html = tf.print_a()
    assert "True" in choices_html
    assert "False" in choices_html
    assert 'type="radio"' in choices_html


def test_true_false_evaluator():
    """Test true/false answer evaluator."""
    macros = loadMacros("PGchoicemacros.pl")
    new_true_false = macros["new_true_false"]

    tf = new_true_false()
    tf.qa("Question?", True)

    evaluator = tf.cmp()

    result = evaluator.evaluate("T")
    assert result.correct is True

    result = evaluator.evaluate("true")
    assert result.correct is True

    result = evaluator.evaluate("F")
    assert result.correct is False
