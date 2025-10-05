"""
Test PGbasicmacros functionality.
"""

import sys
import os

# Add packages to path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(repo_root, "packages", "pg_macros"))

from pg_macros.core import pg_core, pg_basic_macros


def test_display_constants():
    """Test display mode constants."""
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # HTML mode
    assert pg_basic_macros.PAR() == "<p>"
    assert pg_basic_macros.BR() == "<br/>"
    assert pg_basic_macros.BBOLD() == "<strong>"
    assert pg_basic_macros.EBOLD() == "</strong>"
    
    # TeX mode
    env.display_mode = "TeX"
    assert pg_basic_macros.PAR() == "\n\n"
    assert pg_basic_macros.BR() == "\\\\"
    assert pg_basic_macros.BBOLD() == "\\textbf{"
    assert pg_basic_macros.EBOLD() == "}"
    
    print("✓ Display constants work")


def test_ans_rule():
    """Test ans_rule() answer blank."""
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Create answer blank
    html = pg_basic_macros.ans_rule(30)
    
    assert 'type="text"' in html
    assert 'size="30"' in html
    assert 'name="AnSwEr0001"' in html
    
    # Check that answer name was recorded
    assert "AnSwEr0001" in env.answers_hash
    assert "AnSwEr0001" in env.answer_blank_queue
    
    print("✓ ans_rule() works")


def test_ans_box():
    """Test ans_box() textarea."""
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Create answer box
    html = pg_basic_macros.ans_box(10, 60)
    
    assert '<textarea' in html
    assert 'rows="10"' in html
    assert 'cols="60"' in html
    assert 'name="AnSwEr0001"' in html
    
    print("✓ ans_box() works")


def test_pop_up_list():
    """Test pop_up_list() dropdown."""
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Create dropdown with array
    options = ["Option 1", "Option 2", "Option 3"]
    html = pg_basic_macros.pop_up_list(options)
    
    assert '<select' in html
    assert 'name="AnSwEr0001"' in html
    assert 'Option 1' in html
    assert 'Option 2' in html
    assert 'Option 3' in html
    
    print("✓ pop_up_list() works")


def test_radio_buttons():
    """Test ans_radio_buttons()."""
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Create radio buttons
    html = pg_basic_macros.ans_radio_buttons("Yes", "No", "Maybe")
    
    assert 'type="radio"' in html
    assert 'name="AnSwEr0001"' in html
    assert 'Yes' in html
    assert 'No' in html
    assert 'Maybe' in html
    assert 'radio-buttons-container' in html
    
    print("✓ ans_radio_buttons() works")


def test_modes_function():
    """Test MODES() function."""
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    result = pg_basic_macros.MODES(
        HTML="<b>HTML text</b>",
        TeX="\\textbf{TeX text}",
        PTX="<strong>PTX text</strong>"
    )
    
    assert result == "<b>HTML text</b>"
    
    # Change to TeX mode
    env.display_mode = "TeX"
    result = pg_basic_macros.MODES(
        HTML="<b>HTML text</b>",
        TeX="\\textbf{TeX text}",
        PTX="<strong>PTX text</strong>"
    )
    
    assert result == "\\textbf{TeX text}"
    
    print("✓ MODES() works")


def test_image_function():
    """Test image() function."""
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # HTML mode
    html = pg_basic_macros.image("graph.png", width=400, height=300, alt="Graph")
    assert '<img' in html
    assert 'src="graph.png"' in html
    assert 'width="400"' in html
    assert 'height="300"' in html
    assert 'alt="Graph"' in html
    
    # TeX mode
    env.display_mode = "TeX"
    tex = pg_basic_macros.image("graph.png", tex_size=500)
    assert '\\includegraphics' in tex
    assert 'graph.png' in tex
    
    print("✓ image() works")


def test_named_ans_rule():
    """Test NAMED_ANS_RULE() with explicit name."""
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    html = pg_basic_macros.NAMED_ANS_RULE("myAnswer", 25, "default value")
    
    assert 'name="myAnswer"' in html
    assert 'size="25"' in html
    assert 'myAnswer' in env.answers_hash
    
    print("✓ NAMED_ANS_RULE() works")


def test_constants():
    """Test mathematical constants."""
    import math
    
    assert abs(pg_basic_macros.PI() - math.pi) < 0.0001
    assert abs(pg_basic_macros.E() - math.e) < 0.0001
    
    print("✓ Constants work")


if __name__ == "__main__":
    print("Testing PGbasicmacros Implementation...\n")
    
    test_display_constants()
    test_ans_rule()
    test_ans_box()
    test_pop_up_list()
    test_radio_buttons()
    test_modes_function()
    test_image_function()
    test_named_ans_rule()
    test_constants()
    
    print("\n✅ All tests passed!")
