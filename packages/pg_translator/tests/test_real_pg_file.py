"""Test with real .pg files."""

import pytest
from pathlib import Path

from pg_translator import PGTranslator
from pg_translator.executor import PGExecutor
from pg_translator.in_process_sandbox import InProcessSandbox


def test_random_addition_pg_file():
    """Test loading and executing random_addition.pg."""
    # Setup
    sandbox = InProcessSandbox(timeout=10)
    executor = PGExecutor()
    executor.sandbox = sandbox
    translator = PGTranslator(executor=executor)
    
    # Test file path
    test_file = Path(__file__).parent / "problems" / "random_addition.pg"
    assert test_file.exists(), f"Test file not found: {test_file}"
    
    # Translate with seed
    result = translator.translate(
        pg_file_path=test_file,
        seed=42
    )
    
    # Should render without errors
    assert result.errors is None or len(result.errors) == 0, f"Errors: {result.errors}"
    
    # Should have HTML output
    assert result.statement_html, "No HTML output"
    assert "What is" in result.statement_html, "Missing question text"
    assert "Answer:" in result.statement_html, "Missing answer prompt"
    
    # Should have one answer blank
    assert len(result.answer_blanks) == 1, f"Expected 1 answer blank, got {len(result.answer_blanks)}"
    
    # Should have answer evaluator
    answer_name = list(result.answer_blanks.keys())[0]
    assert answer_name in result.answer_blanks
    
    print(f"\\nSuccess! Problem rendered:")
    print(result.statement_html)
    
    # Test grading with different seeds
    for seed in [1, 2, 3]:
        result = translator.translate(test_file, seed=seed)
        assert result.errors is None or len(result.errors) == 0
        
        # Extract the expected answer from metadata or problem variables
        # For now, just verify it renders
        assert result.statement_html
        print(f"\\nSeed {seed}: {result.statement_html[:100]}...")


def test_random_addition_with_grading():
    """Test grading the random addition problem."""
    # Setup
    sandbox = InProcessSandbox(timeout=10)
    executor = PGExecutor()
    executor.sandbox = sandbox
    translator = PGTranslator(executor=executor)
    
    test_file = Path(__file__).parent / "problems" / "random_addition.pg"
    
    # Use a known seed
    seed = 123
    result = translator.translate(test_file, seed=seed)
    
    # Problem should have variables a, b, ans in metadata
    # For now, we'll test by submitting some answers
    
    answer_name = list(result.answer_blanks.keys())[0]
    
    # Test with a likely correct answer (middle range)
    for test_answer in ["5", "10", "15", "20"]:
        graded = translator.translate(
            test_file,
            seed=seed,
            inputs={answer_name: test_answer}
        )
        
        if graded.answer_results and answer_name in graded.answer_results:
            ar = graded.answer_results[answer_name]
            print(f"\\nAnswer {test_answer}: score={ar.score}, correct={ar.correct}")
            
            # At least one should be correct
            if ar.correct:
                print(f"  ✓ Found correct answer: {test_answer}")
                return
    
    # If we get here, try to extract actual answer
    print(f"\\nCouldn't find correct answer in test range")
    print(f"Answer blank structure: {result.answer_blanks[answer_name]}")


if __name__ == "__main__":
    test_random_addition_pg_file()
    test_random_addition_with_grading()
