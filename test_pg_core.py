"""
Test basic PG core functionality.
"""

import sys
import os

# Add packages to path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(repo_root, "packages", "pg_macros"))

# Now import
from pg_macros.core import pg_core


def test_environment_creation():
    """Test creating PG environment."""
    envir = {
        "problemSeed": 123,
        "displayMode": "HTML",
        "showPartialCorrectAnswers": 1,
    }
    
    env = pg_core.PGEnvironment(envir)
    
    assert env.problem_seed == 123
    assert env.display_mode == "HTML"
    assert env.flags["showPartialCorrectAnswers"] == 1
    assert len(env.output_array) == 0
    assert len(env.answers_hash) == 0
    
    print("✓ Environment creation works")


def test_document_lifecycle():
    """Test DOCUMENT() and ENDDOCUMENT()."""
    # Set up environment
    envir = {"problemSeed": 123, "displayMode": "HTML"}
    
    # Create environment manually (DOCUMENT would do this)
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Add some text
    pg_core.TEXT("Hello", "World")
    pg_core.TEXT("Problem text here")
    
    # Get result
    text = env.get_text()
    
    assert "Hello World" in text or "Hello  World" in text  # Account for spacing
    assert "Problem text here" in text
    
    print("✓ Document lifecycle works")


def test_text_accumulation():
    """Test TEXT() accumulation."""
    envir = {"problemSeed": 123}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    pg_core.TEXT("First line")
    pg_core.TEXT("Second line")
    pg_core.HEADER_TEXT("<script>alert('test')</script>")
    
    assert "First line" in env.get_text()
    assert "Second line" in env.get_text()
    assert "alert('test')" in env.get_header()
    
    print("✓ Text accumulation works")


def test_answer_registration():
    """Test ANS() and answer registration."""
    envir = {"problemSeed": 123}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Mock evaluator
    evaluator1 = {"type": "numeric", "correct": 42}
    evaluator2 = {"type": "numeric", "correct": 17}
    
    # Register answers implicitly
    pg_core.ANS(evaluator1, evaluator2)
    
    # Check registration
    assert len(env.answers_hash) == 2
    assert len(env.answer_entry_order) == 2
    
    print("✓ Answer registration works")


def test_named_answers():
    """Test NAMED_ANS()."""
    envir = {"problemSeed": 123}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    evaluator = {"type": "numeric", "correct": 42}
    pg_core.NAMED_ANS("answer1", evaluator)
    
    assert "answer1" in env.answers_hash
    assert env.answers_hash["answer1"]["ans_eval"] == evaluator
    
    print("✓ Named answers work")


def test_answer_name_generation():
    """Test NEW_ANS_NAME()."""
    envir = {"problemSeed": 123, "ANSWER_PREFIX": "AnSwEr"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    name1 = pg_core.NEW_ANS_NAME()
    name2 = pg_core.NEW_ANS_NAME()
    name3 = pg_core.NEW_ANS_NAME()
    
    assert name1 == "AnSwEr0001"
    assert name2 == "AnSwEr0002"
    assert name3 == "AnSwEr0003"
    
    print("✓ Answer name generation works")


def test_random_functions():
    """Test random number functions."""
    envir = {"problemSeed": 123}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Test random
    r1 = pg_core.random(1, 10)
    assert 1 <= r1 <= 10
    
    # Test non_zero_random
    r2 = pg_core.non_zero_random(-5, 5, 1)
    assert -5 <= r2 <= 5
    assert r2 != 0
    
    # Test list_random
    r3 = pg_core.list_random("a", "b", "c", "d")
    assert r3 in ["a", "b", "c", "d"]
    
    print("✓ Random functions work")


def test_utility_functions():
    """Test utility functions."""
    assert pg_core.not_null("text") == True
    assert pg_core.not_null("") == False
    assert pg_core.not_null(None) == False
    assert pg_core.not_null(0) == False
    assert pg_core.not_null(42) == True
    assert pg_core.not_null([1, 2]) == True
    assert pg_core.not_null([]) == False
    
    print("✓ Utility functions work")


def test_persistent_data():
    """Test persistent data storage."""
    envir = {"problemSeed": 123}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Store data
    pg_core.persistent_data("counter", 42)
    
    # Retrieve data
    value = pg_core.persistent_data("counter")
    assert value == 42
    
    # Update data
    pg_core.persistent_data("counter", 43)
    value = pg_core.persistent_data("counter")
    assert value == 43
    
    print("✓ Persistent data works")


def test_solution_hint_flags():
    """Test solution and hint flags."""
    envir = {"problemSeed": 123}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    assert env.flags["solutionExists"] == 0
    assert env.flags["hintExists"] == 0
    
    pg_core.SOLUTION("Solution text")
    assert env.flags["solutionExists"] == 1
    
    pg_core.HINT("Hint text")
    assert env.flags["hintExists"] == 1
    
    pg_core.COMMENT("Comment text")
    assert env.flags["comment"] == "Comment text"
    
    print("✓ Solution/Hint flags work")


if __name__ == "__main__":
    print("Testing PG Core Implementation...\n")
    
    test_environment_creation()
    test_document_lifecycle()
    test_text_accumulation()
    test_answer_registration()
    test_named_answers()
    test_answer_name_generation()
    test_random_functions()
    test_utility_functions()
    test_persistent_data()
    test_solution_hint_flags()
    
    print("\n✅ All tests passed!")
