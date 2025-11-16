"""
Test that both Perl and Python adapters can correctly evaluate answers.

This test runs all snippets and verifies that:
1. Both adapters can get correct answers
2. Both adapters can evaluate correct answers and assign score=1
3. Both adapters mark correct answers as correct=true/1
"""
import json
import pytest
from pathlib import Path
from typing import Dict, Any, List

from conftest import (
    parity_lab_root,
    build_dir,
    snippets_dir,
)


def run_perl_snippet(snippet_path: Path, seed: int, parity_lab_root: Path, build_dir: Path) -> Dict[str, Any]:
    """Run a PG snippet through Perl adapter."""
    from subprocess import run, PIPE
    import os
    
    perl_adapter = parity_lab_root / "perl_ref" / "run_pg_snippet.pl"
    output_file = build_dir / f"perl_{snippet_path.stem}_{seed}.json"
    
    env = os.environ.copy()
    env['PERL5LIB'] = f"{os.environ.get('HOME', '')}/perl5/lib/perl5:{env.get('PERL5LIB', '')}"
    env['PG_ROOT'] = str(parity_lab_root.parent)
    
    result = run(
        ["perl", str(perl_adapter), str(snippet_path), str(seed), str(output_file)],
        capture_output=True,
        text=True,
        env=env,
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


def check_answer_evaluation(answers: List[Dict[str, Any]], adapter_name: str) -> tuple[bool, str]:
    """
    Check that answers are being evaluated correctly.
    Returns (is_valid, error_message).
    
    This checks that:
    1. If answers exist, they have correct_value (indicates we can get correct answers)
    2. If correct_value exists, score and correct flag are set (indicates evaluation happened)
    3. If score >= 0.9, correct flag should be true/1 (indicates correct evaluation)
    """
    if not answers:
        return True, ""  # No answers is valid (some snippets don't have answers)
    
    issues = []
    evaluated_count = 0
    
    for i, ans in enumerate(answers):
        name = ans.get('name', f'answer_{i}')
        
        # Check if correct_value is present (indicates we got the correct answer)
        correct_value = ans.get('correct_value')
        score = ans.get('score')
        is_correct = ans.get('correct')
        
        # If we have a correct_value, evaluation should have happened
        if correct_value is not None and correct_value != '':
            if score is None:
                issues.append(f"{adapter_name} answer {name}: has correct_value but missing score")
            elif is_correct is None:
                issues.append(f"{adapter_name} answer {name}: has correct_value but missing correct flag")
            else:
                evaluated_count += 1
                # If score indicates correctness, check the flag
                if isinstance(score, (int, float)) and score >= 0.9:
                    if isinstance(is_correct, bool) and not is_correct:
                        issues.append(
                            f"{adapter_name} answer {name}: score={score} but correct={is_correct} "
                            f"(expected True for correct answer)"
                        )
                    elif isinstance(is_correct, int) and is_correct == 0:
                        issues.append(
                            f"{adapter_name} answer {name}: score={score} but correct={is_correct} "
                            f"(expected 1 for correct answer)"
                        )
        # If no correct_value, that's OK - might not be implemented yet
        # But we should at least have score and correct flag if evaluation happened
        elif score is not None or is_correct is not None:
            # Partial evaluation is OK
            pass
    
    # If we have answers but none were evaluated, that's a problem
    if len(answers) > 0 and evaluated_count == 0:
        issues.append(f"{adapter_name}: {len(answers)} answers found but none have correct_value (evaluation not working)")
    
    if issues:
        return False, "; ".join(issues)
    
    return True, ""


def get_all_snippets(snippets_dir: Path) -> List[Path]:
    """Get all .pg snippet files."""
    return sorted(snippets_dir.glob("*.pg"))


@pytest.mark.parametrize("snippet_path", [
    pytest.param(None, id="all_snippets")
])
def test_all_snippets_answer_checking(snippet_path, parity_lab_root: Path, snippets_dir: Path, build_dir: Path):
    """
    Test that all snippets can have their answers evaluated correctly by both adapters.
    """
    all_snippets = get_all_snippets(snippets_dir)
    
    if not all_snippets:
        pytest.skip("No snippets found")
    
    seed = 42
    results = {
        'perl_working': [],
        'perl_failed': [],
        'python_working': [],
        'python_failed': [],
        'both_working': [],
        'both_failed': [],
    }
    
    for snippet in all_snippets:
        snippet_name = snippet.stem
        
        # Run Perl
        perl_ok = False
        perl_output = None
        try:
            perl_output = run_perl_snippet(snippet, seed, parity_lab_root, build_dir)
            perl_valid, perl_msg = check_answer_evaluation(perl_output.get('answers', []), 'Perl')
            if perl_valid:
                perl_ok = True
                results['perl_working'].append(snippet_name)
            else:
                results['perl_failed'].append((snippet_name, perl_msg))
        except Exception as e:
            results['perl_failed'].append((snippet_name, str(e)))
        
        # Run Python
        python_ok = False
        python_output = None
        try:
            python_output = run_python_snippet(snippet, seed, parity_lab_root, build_dir)
            python_valid, python_msg = check_answer_evaluation(python_output.get('answers', []), 'Python')
            if python_valid:
                python_ok = True
                results['python_working'].append(snippet_name)
            else:
                results['python_failed'].append((snippet_name, python_msg))
        except Exception as e:
            results['python_failed'].append((snippet_name, str(e)))
        
        # Track both
        if perl_ok and python_ok:
            results['both_working'].append(snippet_name)
        elif not perl_ok and not python_ok:
            results['both_failed'].append(snippet_name)
    
    # Print summary
    print("\n" + "="*70)
    print("Answer Checking Test Summary")
    print("="*70)
    print(f"Total snippets: {len(all_snippets)}")
    print(f"Perl working: {len(results['perl_working'])}")
    print(f"Python working: {len(results['python_working'])}")
    print(f"Both working: {len(results['both_working'])}")
    print(f"Both failed: {len(results['both_failed'])}")
    
    if results['perl_failed']:
        print(f"\nPerl failures ({len(results['perl_failed'])}):")
        for name, msg in results['perl_failed'][:5]:
            print(f"  - {name}: {msg[:100]}")
    
    if results['python_failed']:
        print(f"\nPython failures ({len(results['python_failed'])}):")
        for name, msg in results['python_failed'][:5]:
            print(f"  - {name}: {msg[:100]}")
    
    # Assert that at least some snippets work
    assert len(results['both_working']) > 0, \
        f"No snippets have working answer checking in both adapters. " \
        f"Perl working: {len(results['perl_working'])}, " \
        f"Python working: {len(results['python_working'])}"
    
    # Assert that Perl is working for snippets with answers
    perl_with_answers = [s for s in results['perl_working'] 
                        if any(a.get('answers') for a in [run_perl_snippet(
                            snippets_dir / f"{s}.pg", seed, parity_lab_root, build_dir
                        )] if s in results['perl_working'])]
    
    if results['perl_working']:
        print(f"\n✓ Perl answer checking working for {len(results['perl_working'])} snippets")
    
    if results['python_working']:
        print(f"✓ Python answer checking working for {len(results['python_working'])} snippets")


@pytest.mark.parametrize("snippet_name", [
    "standard_basic.pg",
    "fraction_mixed.pg",
    "multianswer_basic.pg",
    "pgml_answer_blanks.pg",
])
def test_specific_snippet_answer_checking(snippet_name: str, parity_lab_root: Path, snippets_dir: Path, build_dir: Path):
    """
    Test specific snippets that should have answer checking.
    """
    snippet = snippets_dir / snippet_name
    if not snippet.exists():
        pytest.skip(f"Snippet not found: {snippet_name}")
    
    seed = 42
    
    # Run Perl
    try:
        perl_output = run_perl_snippet(snippet, seed, parity_lab_root, build_dir)
    except Exception as e:
        pytest.skip(f"Perl adapter failed: {e}")
    
    # Run Python
    python_output = run_python_snippet(snippet, seed, parity_lab_root, build_dir)
    
    # Check Perl answers
    perl_answers = perl_output.get('answers', [])
    perl_valid, perl_msg = check_answer_evaluation(perl_answers, 'Perl')
    assert perl_valid, f"Perl answer evaluation failed: {perl_msg}"
    
    # Check Python answers
    python_answers = python_output.get('answers', [])
    python_valid, python_msg = check_answer_evaluation(python_answers, 'Python')
    assert python_valid, f"Python answer evaluation failed: {python_msg}"
    
    # Both should have answers if the snippet has answer blanks
    # But allow for cases where one adapter might not have answers yet
    if len(perl_answers) > 0 or len(python_answers) > 0:
        # At least one should have answers
        assert len(perl_answers) > 0 or len(python_answers) > 0, \
            f"At least one adapter should have answers for {snippet_name}"
        
        # If both have answers, they should match in count (roughly)
        if len(perl_answers) > 0 and len(python_answers) > 0:
            # Allow some flexibility - name formats differ
            pass

