"""
Pytest configuration for contract tests
"""
import pytest
from pathlib import Path


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "perl_required: marks tests that require Perl runtime"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture(scope="session")
def parity_lab_root():
    """Get parity lab root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def build_dir(parity_lab_root):
    """Get build directory, creating if needed."""
    build = parity_lab_root / "build"
    build.mkdir(parents=True, exist_ok=True)
    return build


@pytest.fixture(scope="session")
def snippets_dir(parity_lab_root):
    """Get snippets directory."""
    return parity_lab_root / "tests" / "snippets"


# Test utility functions

def normalize_html(html: str) -> str:
    """
    Normalize HTML for comparison.
    - Collapse whitespace runs
    - Trim leading/trailing whitespace
    - Decode common HTML entities
    """
    import re
    import html as html_module
    
    # Decode HTML entities
    html = html_module.unescape(html)
    
    # Collapse whitespace
    html = re.sub(r'\s+', ' ', html)
    
    # Trim
    html = html.strip()
    
    return html


def normalize_tex(tex: str) -> str:
    """
    Normalize TeX for comparison.
    - Collapse whitespace
    - Normalize line endings
    """
    import re
    
    # Normalize line endings
    tex = tex.replace('\r\n', '\n')
    
    # Collapse multiple spaces
    tex = re.sub(r' +', ' ', tex)
    
    # Trim
    tex = tex.strip()
    
    return tex


def compare_answers(perl_answers: list, py_answers: list, tolerance: float = 1e-9) -> tuple[bool, str]:
    """
    Compare answer lists from Perl and Python outputs.
    Returns (matches, error_message).
    """
    if len(perl_answers) != len(py_answers):
        return False, f"Answer count mismatch: Perl has {len(perl_answers)}, Python has {len(py_answers)}"
    
    for i, (perl_ans, py_ans) in enumerate(zip(perl_answers, py_answers)):
        # Compare answer names
        if perl_ans.get('name') != py_ans.get('name'):
            return False, f"Answer {i}: name mismatch - Perl: {perl_ans.get('name')}, Python: {py_ans.get('name')}"
        
        # Compare correct answers (with numeric tolerance)
        perl_correct = perl_ans.get('correct_value')
        py_correct = py_ans.get('correct_value')
        
        if isinstance(perl_correct, (int, float)) and isinstance(py_correct, (int, float)):
            if abs(perl_correct - py_correct) > tolerance:
                return False, f"Answer {i}: numeric value mismatch - Perl: {perl_correct}, Python: {py_correct}"
        elif perl_correct != py_correct:
            return False, f"Answer {i}: value mismatch - Perl: {perl_correct}, Python: {py_correct}"
    
    return True, ""


def assert_outputs_match(perl_output: dict, py_output: dict, normalize: bool = True, check_answers: bool = True):
    """
    Assert that Perl and Python outputs match.
    Raises AssertionError with detailed message if they don't match.
    """
    errors = []
    
    # Compare HTML output
    if 'html' in perl_output and 'html' in py_output:
        perl_html = normalize_html(perl_output['html']) if normalize else perl_output['html']
        py_html = normalize_html(py_output['html']) if normalize else py_output['html']
        
        if perl_html != py_html:
            errors.append(f"HTML mismatch:\nPerl: {perl_html[:200]}...\nPython: {py_html[:200]}...")
    
    # Compare TeX output
    if 'tex' in perl_output and 'tex' in py_output:
        perl_tex = normalize_tex(perl_output['tex']) if normalize else perl_output['tex']
        py_tex = normalize_tex(py_output['tex']) if normalize else py_output['tex']
        
        if perl_tex != py_tex:
            errors.append(f"TeX mismatch:\nPerl: {perl_tex[:200]}...\nPython: {py_tex[:200]}...")
    
    # Compare answers
    if check_answers and 'answers' in perl_output and 'answers' in py_output:
        matches, msg = compare_answers(perl_output['answers'], py_output['answers'])
        if not matches:
            errors.append(f"Answers mismatch: {msg}")
    
    # Compare error counts
    perl_errors = perl_output.get('errors', [])
    py_errors = py_output.get('errors', [])
    
    if len(perl_errors) != len(py_errors):
        errors.append(f"Error count mismatch: Perl has {len(perl_errors)}, Python has {len(py_errors)}")
    
    if errors:
        raise AssertionError("\n".join(errors))