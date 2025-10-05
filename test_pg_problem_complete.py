"""
Test a complete "Hello World" PG problem.

This demonstrates the full problem lifecycle.
"""

import sys
import os

# Add packages to path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(repo_root, "packages", "pg_macros"))

from pg_macros.core import pg_core, pg_basic_macros


def test_hello_world_problem():
    """Test a complete Hello World problem."""
    print("\n=== Running Hello World Problem ===\n")
    
    # Simulate problem code
    envir = {
        "problemSeed": 12345,
        "displayMode": "HTML",
        "showPartialCorrectAnswers": 1,
    }
    
    # Initialize environment (normally done by DOCUMENT())
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Problem code
    pg_core.TEXT("Welcome to PG!")
    pg_core.TEXT(pg_basic_macros.PAR())
    pg_core.TEXT("What is 2 + 2?")
    pg_core.TEXT(pg_basic_macros.BR())
    pg_core.TEXT("Answer: ")
    pg_core.TEXT(pg_basic_macros.ans_rule(10))
    
    # Mock evaluator
    evaluator = {"type": "numeric", "correct": 4}
    pg_core.ANS(evaluator)
    
    # Get results
    text, header, post_header, answers, flags = pg_core.ENDDOCUMENT()
    
    # Validate
    print("Problem Text:")
    print("-" * 60)
    print(text)
    print("-" * 60)
    
    assert "Welcome to PG!" in text
    assert "What is 2 + 2?" in text
    assert '<input type="text"' in text
    assert 'name="AnSwEr0001"' in text
    
    assert "AnSwEr0001" in answers
    assert answers["AnSwEr0001"]["ans_eval"]["correct"] == 4
    
    print("\n✅ Hello World problem works!\n")


def test_problem_with_multiple_answers():
    """Test problem with multiple answer blanks."""
    print("\n=== Running Multi-Answer Problem ===\n")
    
    envir = {
        "problemSeed": 67890,
        "displayMode": "HTML",
    }
    
    # Initialize
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Problem code
    pg_core.TEXT("Solve these problems:")
    pg_core.TEXT(pg_basic_macros.PAR())
    
    pg_core.TEXT("1. What is 3 + 5? ")
    pg_core.TEXT(pg_basic_macros.ans_rule(10))
    pg_core.TEXT(pg_basic_macros.BR())
    
    pg_core.TEXT("2. What is 10 - 4? ")
    pg_core.TEXT(pg_basic_macros.ans_rule(10))
    pg_core.TEXT(pg_basic_macros.BR())
    
    pg_core.TEXT("3. Choose the correct answer: ")
    pg_core.TEXT(pg_basic_macros.pop_up_list(["Select...", "Yes", "No"]))
    
    # Register evaluators
    eval1 = {"type": "numeric", "correct": 8}
    eval2 = {"type": "numeric", "correct": 6}
    eval3 = {"type": "string", "correct": "Yes"}
    
    pg_core.ANS(eval1, eval2, eval3)
    
    # Get results
    text, header, post_header, answers, flags = pg_core.ENDDOCUMENT()
    
    print("Problem Text:")
    print("-" * 60)
    print(text)
    print("-" * 60)
    
    # Validate
    assert "Solve these problems" in text
    assert "AnSwEr0001" in answers
    assert "AnSwEr0002" in answers
    assert "AnSwEr0003" in answers
    
    assert answers["AnSwEr0001"]["ans_eval"]["correct"] == 8
    assert answers["AnSwEr0002"]["ans_eval"]["correct"] == 6
    assert answers["AnSwEr0003"]["ans_eval"]["correct"] == "Yes"
    
    assert len(answers) == 3
    assert flags["ANSWER_ENTRY_ORDER"] == ["AnSwEr0001", "AnSwEr0002", "AnSwEr0003"]
    
    print("\n✅ Multi-answer problem works!\n")


def test_problem_with_named_answers():
    """Test problem with explicitly named answers."""
    print("\n=== Running Named Answer Problem ===\n")
    
    envir = {"problemSeed": 111, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Problem code with named answers
    pg_core.TEXT("Enter your answers:")
    pg_core.TEXT(pg_basic_macros.PAR())
    
    pg_core.TEXT("Part A: ")
    pg_core.TEXT(pg_basic_macros.NAMED_ANS_RULE("partA", 15))
    pg_core.TEXT(pg_basic_macros.BR())
    
    pg_core.TEXT("Part B: ")
    pg_core.TEXT(pg_basic_macros.NAMED_ANS_RULE("partB", 15))
    
    # Register named evaluators
    evalA = {"type": "numeric", "correct": 42}
    evalB = {"type": "string", "correct": "hello"}
    
    pg_core.NAMED_ANS("partA", evalA)
    pg_core.NAMED_ANS("partB", evalB)
    
    # Get results
    text, header, post_header, answers, flags = pg_core.ENDDOCUMENT()
    
    print("Problem Text:")
    print("-" * 60)
    print(text)
    print("-" * 60)
    
    # Validate
    assert 'name="partA"' in text
    assert 'name="partB"' in text
    
    assert "partA" in answers
    assert "partB" in answers
    
    assert answers["partA"]["ans_eval"]["correct"] == 42
    assert answers["partB"]["ans_eval"]["correct"] == "hello"
    
    print("\n✅ Named answer problem works!\n")


def test_problem_with_solution_hint():
    """Test problem with solution and hint."""
    print("\n=== Running Problem with Solution/Hint ===\n")
    
    envir = {"problemSeed": 222, "displayMode": "HTML"}
    env = pg_core.PGEnvironment(envir)
    pg_core.set_environment(env)
    
    # Problem code
    pg_core.TEXT("What is 5 × 5?")
    pg_core.TEXT(pg_basic_macros.BR())
    pg_core.TEXT("Answer: ")
    pg_core.TEXT(pg_basic_macros.ans_rule(10))
    
    pg_core.ANS({"type": "numeric", "correct": 25})
    
    # Add solution and hint
    pg_core.SOLUTION("Multiply 5 by 5 to get 25.")
    pg_core.HINT("Remember that multiplication is repeated addition.")
    pg_core.COMMENT("This problem tests basic multiplication.")
    
    # Get results
    text, header, post_header, answers, flags = pg_core.ENDDOCUMENT()
    
    # Validate flags
    assert flags["solutionExists"] == 1
    assert flags["hintExists"] == 1
    assert flags["comment"] == "This problem tests basic multiplication."
    
    print("Flags:")
    print(f"  solutionExists: {flags['solutionExists']}")
    print(f"  hintExists: {flags['hintExists']}")
    print(f"  comment: {flags['comment']}")
    
    print("\n✅ Solution/Hint problem works!\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTING COMPLETE PG PROBLEMS")
    print("=" * 60)
    
    test_hello_world_problem()
    test_problem_with_multiple_answers()
    test_problem_with_named_answers()
    test_problem_with_solution_hint()
    
    print("\n" + "=" * 60)
    print("✅ ALL END-TO-END TESTS PASSED!")
    print("=" * 60 + "\n")
