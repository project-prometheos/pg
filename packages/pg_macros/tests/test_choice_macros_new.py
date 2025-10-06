"""Tests for choice macros."""

import pytest
from pg_macros import load_macros


def test_multiple_choice_basic():
    """Test basic multiple choice."""
    exports = load_macros("PGchoicemacros.pl")
    new_multiple_choice = exports["new_multiple_choice"]
    
    mc = new_multiple_choice()
    mc.qa("What is 2+2?", "4")
    mc.extra("3", "5", "6")
    
    q = mc.print_q()
    assert "2+2" in q
    
    a = mc.print_a()
    assert "radio" in a
    assert "4" in a
    assert "3" in a


def test_checkbox_multiple_choice():
    """Test checkbox multiple choice."""
    exports = load_macros("PGchoicemacros.pl")
    new_checkbox_multiple_choice = exports["new_checkbox_multiple_choice"]
    
    cmc = new_checkbox_multiple_choice()
    cmc.qa("Select all even numbers:", "2", "4", "6")
    cmc.extra("1", "3", "5")
    
    q = cmc.print_q()
    assert "even" in q
    
    a = cmc.print_a()
    assert "checkbox" in a
    assert "2" in a
    assert "4" in a


def test_true_false():
    """Test true/false question."""
    exports = load_macros("PGchoicemacros.pl")
    new_true_false = exports["new_true_false"]
    
    tf = new_true_false("The sky is blue.", True)
    
    q = tf.print_q()
    assert "sky" in q
    
    a = tf.print_a()
    assert "True" in a
    assert "False" in a
    
    assert tf.correct_ans() == "T"


def test_true_false_false():
    """Test true/false with false answer."""
    exports = load_macros("PGchoicemacros.pl")
    new_true_false = exports["new_true_false"]
    
    tf = new_true_false("2+2=5", False)
    assert tf.correct_ans() == "F"


def test_match_list():
    """Test matching question."""
    exports = load_macros("PGchoicemacros.pl")
    new_match_list = exports["new_match_list"]
    
    ml = new_match_list()
    ml.qa(
        "Capital of France?", "Paris",
        "Capital of Italy?", "Rome",
        "Capital of Spain?", "Madrid"
    )
    ml.extra("London", "Berlin")
    
    q = ml.print_q()
    assert "France" in q
    
    a = ml.print_a()
    assert "Paris" in a or "Rome" in a


def test_popup():
    """Test popup select list."""
    exports = load_macros("PGchoicemacros.pl")
    new_pop_up_select_list = exports["new_pop_up_select_list"]
    
    popup = new_pop_up_select_list(["Choice A", "Choice B", "Choice C"])
    popup.qa("Choice A")
    
    html = popup.print_q()
    assert "select" in html
    assert "Choice A" in html


def test_multiple_choice_make_last():
    """Test makeLast functionality."""
    exports = load_macros("PGchoicemacros.pl")
    new_multiple_choice = exports["new_multiple_choice"]
    
    mc = new_multiple_choice()
    mc.qa("Pick one:", "Correct")
    mc.extra("A", "B", "C", "None of the above")
    mc.makeLast("None of the above")
    
    # Should work without error
    q = mc.print_q()
    a = mc.print_a()
    assert "None of the above" in a


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


