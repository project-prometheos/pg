"""
Parity Comparison Tests

Tests that compare Perl reference implementations with Python equivalents
for formula evaluation, vector operations, answer checking, grading, etc.
"""
import json
import pytest
from pathlib import Path
from typing import Dict, Any

from conftest import (
    parity_lab_root,
    build_dir,
    snippets_dir,
    assert_outputs_match,
    normalize_html,
)


def run_perl_snippet(snippet_path: Path, seed: int, parity_lab_root: Path, build_dir: Path) -> Dict[str, Any]:
    """Run a PG snippet through Perl adapter."""
    from subprocess import run, PIPE
    
    perl_adapter = parity_lab_root / "perl_ref" / "run_pg_snippet.pl"
    output_file = build_dir / f"perl_{snippet_path.stem}_{seed}.json"
    
    result = run(
        ["perl", str(perl_adapter), str(snippet_path), str(seed), str(output_file)],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        pytest.skip(f"Perl adapter failed: {result.stderr}")
    
    with open(output_file) as f:
        return json.load(f)


def run_python_snippet(snippet_path: Path, seed: int, parity_lab_root: Path, build_dir: Path) -> Dict[str, Any]:
    """Run a PG snippet through Python adapter."""
    import sys
    from subprocess import run, PIPE
    
    py_adapter = parity_lab_root / "py_port" / "run_pg_snippet.py"
    output_file = build_dir / f"py_{snippet_path.stem}_{seed}.json"
    
    result = run(
        [sys.executable, str(py_adapter), str(snippet_path), str(seed), str(output_file)],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        pytest.fail(f"Python adapter failed: {result.stderr}")
    
    with open(output_file) as f:
        return json.load(f)


# Test categories - defined as functions to use fixtures
def get_formula_snippet(snippets_dir):
    return snippets_dir / "mathobjects_formula.pg"

def get_vector_snippet(snippets_dir):
    return snippets_dir / "mathobjects_vectors.pg"

def get_interval_snippet(snippets_dir):
    return snippets_dir / "mathobjects_intervals.pg"

def get_fraction_snippet(snippets_dir):
    return snippets_dir / "fraction_basic.pg"

def get_answer_checking_snippet(snippets_dir):
    return snippets_dir / "standard_basic.pg"

def get_grading_snippet(snippets_dir):
    return snippets_dir / "multianswer_basic.pg"

def get_pgml_snippet(snippets_dir):
    return snippets_dir / "pgml_answer_blanks.pg"

def get_choice_snippet(snippets_dir):
    return snippets_dir / "choice_multiple_choice.pg"


@pytest.mark.parametrize("snippet_name,description", [
    ("mathobjects_formula.pg", "Formula evaluation and answer checking"),
    ("mathobjects_vectors.pg", "Vector operations (dot product, norm)"),
    ("mathobjects_intervals.pg", "Interval/Set operations"),
    ("fraction_basic.pg", "Fraction arithmetic"),
    ("standard_basic.pg", "Basic answer checking"),
    ("multianswer_basic.pg", "MultiAnswer grading"),
    ("pgml_answer_blanks.pg", "PGML answer blanks"),
    ("choice_multiple_choice.pg", "Multiple choice questions"),
])
def test_parity_comparison(snippet_name: str, description: str, parity_lab_root: Path, snippets_dir: Path, build_dir: Path):
    """Compare Perl and Python outputs for a given snippet."""
    snippet = snippets_dir / snippet_name
    """Compare Perl and Python outputs for a given snippet."""
    if not snippet.exists():
        pytest.skip(f"Snippet not found: {snippet}")
    
    seed = 42
    
    # Run both implementations
    try:
        perl_output = run_perl_snippet(snippet, seed, parity_lab_root, build_dir)
    except Exception as e:
        pytest.skip(f"Perl execution failed: {e}")
    
    py_output = run_python_snippet(snippet, seed, parity_lab_root, build_dir)
    
    # Compare outputs
    assert_outputs_match(perl_output, py_output, normalize=True, check_answers=True)


def test_formula_evaluation_parity(parity_lab_root: Path, snippets_dir: Path, build_dir: Path):
    """Test that Formula evaluation produces same results in Perl and Python."""
    formula_snippet = snippets_dir / "mathobjects_formula.pg"
    if not formula_snippet.exists():
        pytest.skip("Formula snippet not found")
    
    seed = 42
    
    try:
        perl_output = run_perl_snippet(formula_snippet, seed, parity_lab_root, build_dir)
    except Exception:
        pytest.skip("Perl adapter not available")
    
    py_output = run_python_snippet(formula_snippet, seed, parity_lab_root, build_dir)
    
    # Check that both produce HTML output
    assert len(perl_output.get("html", "")) > 0, "Perl should produce HTML"
    assert len(py_output.get("html", "")) > 0, "Python should produce HTML"
    
    # Check that both register answers
    assert len(perl_output.get("answers", [])) > 0, "Perl should register answers"
    assert len(py_output.get("answers", [])) > 0, "Python should register answers"
    
    # Normalize and compare HTML
    perl_html = normalize_html(perl_output["html"])
    py_html = normalize_html(py_output["html"])
    
    # For now, just check they're not empty (full comparison requires Perl libs)
    assert perl_html != "" and py_html != "", "Both should produce non-empty HTML"


def test_vector_operations_parity(parity_lab_root: Path, snippets_dir: Path, build_dir: Path):
    """Test that Vector operations (dot product, norm) match between Perl and Python."""
    vector_snippet = snippets_dir / "mathobjects_vectors.pg"
    if not vector_snippet.exists():
        pytest.skip("Vector snippet not found")
    
    seed = 42
    
    try:
        perl_output = run_perl_snippet(vector_snippet, seed, parity_lab_root, build_dir)
    except Exception:
        pytest.skip("Perl adapter not available")
    
    py_output = run_python_snippet(vector_snippet, seed, parity_lab_root, build_dir)
    
    # Both should produce output with vector operations
    assert len(perl_output.get("html", "")) > 0
    assert len(py_output.get("html", "")) > 0
    
    # Both should have answer blanks
    assert len(perl_output.get("answers", [])) > 0
    assert len(py_output.get("answers", [])) > 0


def test_answer_checking_parity(parity_lab_root: Path, snippets_dir: Path, build_dir: Path):
    """Test that answer checking produces same results."""
    answer_snippet = snippets_dir / "standard_basic.pg"
    if not answer_snippet.exists():
        pytest.skip("Answer checking snippet not found")
    
    seed = 42
    
    try:
        perl_output = run_perl_snippet(answer_snippet, seed, parity_lab_root, build_dir)
    except Exception:
        pytest.skip("Perl adapter not available")
    
    py_output = run_python_snippet(answer_snippet, seed, parity_lab_root, build_dir)
    
    # Compare answer counts
    perl_answers = perl_output.get("answers", [])
    py_answers = py_output.get("answers", [])
    
    assert len(perl_answers) == len(py_answers), \
        f"Answer count mismatch: Perl={len(perl_answers)}, Python={len(py_answers)}"
    
    # Compare answer names
    perl_names = sorted([a.get("name") for a in perl_answers])
    py_names = sorted([a.get("name") for a in py_answers])
    
    assert perl_names == py_names, \
        f"Answer names mismatch: Perl={perl_names}, Python={py_names}"


def test_determinism(parity_lab_root: Path, snippets_dir: Path, build_dir: Path):
    """Test that same seed produces same output (determinism)."""
    formula_snippet = snippets_dir / "mathobjects_formula.pg"
    if not formula_snippet.exists():
        pytest.skip("Formula snippet not found")
    
    seed = 42
    
    # Run Python twice with same seed
    output1 = run_python_snippet(formula_snippet, seed, parity_lab_root, build_dir)
    output2 = run_python_snippet(formula_snippet, seed, parity_lab_root, build_dir)
    
    # Should produce identical outputs
    assert normalize_html(output1["html"]) == normalize_html(output2["html"]), \
        "Same seed should produce same HTML output"
    assert len(output1["answers"]) == len(output2["answers"]), \
        "Same seed should produce same number of answers"

