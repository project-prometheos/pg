#!/usr/bin/env python
"""
pypg - Command-line tool for testing PG problems with answers.

Usage:
    pypg <problem_file.pg> [answer1] [answer2] ... [--seed SEED]
    
Examples:
    pypg tutorial/sample-problems/Algebra/ExpandedPolynomial.pg "x^2-6x+4"
    pypg tutorial/sample-problems/Algebra/SimpleFactoring.pg "x-2,x-3" "2,3" --seed 123
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'pg_renderer'))

from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker


def print_separator(char='=', length=80):
    """Print a separator line."""
    print(char * length)


def print_problem_header(problem_file: Path, seed: int):
    """Print problem information header."""
    print_separator()
    print(f"Problem: {problem_file.name}")
    print(f"Path: {problem_file}")
    print(f"Seed: {seed}")
    print_separator()


def print_rendered_problem(result: Dict[str, Any]):
    """Print the rendered problem statement."""
    print("\n[PROBLEM STATEMENT]")
    print("-" * 80)
    
    # Clean up HTML for terminal display
    html = result['statement_html']
    # Remove answer blank placeholders for cleaner display
    import re
    html = re.sub(r'___ANSWER_BLANK_\w+___', '[____]', html)
    # Remove excessive whitespace
    html = re.sub(r'\n\s*\n', '\n\n', html)
    
    print(html)
    print("-" * 80)


def print_answer_blanks(result: Dict[str, Any]):
    """Print expected answer information."""
    print("\n[EXPECTED ANSWERS]")
    if not result['answers']:
        print("  (No answers required)")
        return
    
    for i, (answer_id, answer_data) in enumerate(result['answers'].items(), 1):
        print(f"  {i}. {answer_id}")
        print(f"     Correct: {answer_data['correct_value']}")
        print(f"     Type: {answer_data['type']}")


def check_answers(
    result: Dict[str, Any],
    student_answers: List[str],
    checker: AnswerChecker
) -> Dict[str, Any]:
    """Check student answers against correct answers."""
    answer_ids = list(result['answers'].keys())
    
    if len(student_answers) > len(answer_ids):
        print(f"\n[WARNING] You provided {len(student_answers)} answers but problem has {len(answer_ids)} blanks")
        student_answers = student_answers[:len(answer_ids)]
    elif len(student_answers) < len(answer_ids):
        print(f"\n[WARNING] You provided {len(student_answers)} answers but problem has {len(answer_ids)} blanks")
    
    results = {}
    for i, answer_id in enumerate(answer_ids):
        if i < len(student_answers):
            student_answer = student_answers[i]
            correct_data = result['answers'][answer_id]
            
            is_correct, message = checker.check(
                student_answer,
                correct_data['correct_value'],
                correct_data['type'],
                {}
            )
            
            results[answer_id] = {
                'student': student_answer,
                'correct': is_correct,
                'message': message,
                'correct_answer': correct_data['correct_value'],
                'type': correct_data['type']
            }
        else:
            results[answer_id] = {
                'student': '(not provided)',
                'correct': False,
                'message': 'No answer provided',
                'correct_answer': result['answers'][answer_id]['correct_value'],
                'type': result['answers'][answer_id]['type']
            }
    
    return results


def print_answer_results(results: Dict[str, Any]):
    """Print answer checking results with color-coded output."""
    print("\n[ANSWER CHECK RESULTS]")
    print_separator('-')
    
    all_correct = all(r['correct'] for r in results.values())
    num_correct = sum(1 for r in results.values() if r['correct'])
    total = len(results)
    
    for i, (answer_id, result) in enumerate(results.items(), 1):
        status = "[OK]" if result['correct'] else "[FAIL]"
        print(f"\n{i}. {answer_id} {status}")
        print(f"   Student: {result['student']}")
        print(f"   Correct: {result['correct_answer']}")
        print(f"   Type: {result['type']}")
        print(f"   Message: {result['message']}")
    
    print_separator('-')
    print(f"\nScore: {num_correct}/{total}")
    
    if all_correct:
        print("\n*** ALL ANSWERS CORRECT! ***")
    else:
        print(f"\n*** {total - num_correct} INCORRECT ***")


def print_solution(result: Dict[str, Any]):
    """Print the solution if available."""
    if result.get('solution_html'):
        print("\n[SOLUTION]")
        print("-" * 80)
        print(result['solution_html'])
        print("-" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test PG problems with answer strings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pypg tutorial/sample-problems/Algebra/ExpandedPolynomial.pg "x^2-6x+4"
  pypg tutorial/sample-problems/Algebra/SimpleFactoring.pg "x-2,x-3" "2,3" --seed 123
  pypg tutorial/sample-problems/Algebra/DomainRange.pg "x>=1" "y>=0" "[1,inf)" "[0,inf)"
        """
    )
    
    parser.add_argument(
        'problem_file',
        type=str,
        help='Path to the .pg problem file'
    )
    
    parser.add_argument(
        'answers',
        nargs='*',
        help='Student answers in order of appearance (use quotes for complex expressions)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for problem generation (default: random, range: 1-999999)'
    )
    
    parser.add_argument(
        '--show-solution',
        action='store_true',
        help='Show the solution after checking answers'
    )
    
    parser.add_argument(
        '--render-only',
        action='store_true',
        help='Only render the problem, don\'t check answers'
    )
    
    args = parser.parse_args()
    
    # Generate random seed if not provided
    if args.seed is None:
        import random
        args.seed = random.randint(1, 999999)
    
    # Validate problem file
    problem_file = Path(args.problem_file)
    if not problem_file.exists():
        print(f"[ERROR] Problem file not found: {problem_file}")
        return 1
    
    # Read problem source
    try:
        with open(problem_file, 'r', encoding='utf-8') as f:
            pg_source = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read problem file: {e}")
        return 1
    
    # Print header
    print_problem_header(problem_file, args.seed)
    
    # Render problem
    print("\n[RENDERING]")
    renderer = PGRenderer()
    try:
        result = renderer.render(pg_source, seed=args.seed)
    except Exception as e:
        print(f"[ERROR] Failed to render problem: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Check for render errors
    if result.get('errors'):
        print("[RENDER ERRORS]")
        for error in result['errors']:
            print(f"  {error}")
        return 1
    
    print("[OK] Problem rendered successfully")
    
    # Print rendered problem
    print_rendered_problem(result)
    
    # Print expected answers
    print_answer_blanks(result)
    
    # If render-only mode, stop here
    if args.render_only:
        if args.show_solution:
            print_solution(result)
        return 0
    
    # Check if answers were provided
    if not args.answers:
        print("\n[INFO] No answers provided. Use --render-only to just render the problem.")
        print("[INFO] To check answers, provide them as arguments after the problem file.")
        return 0
    
    # Check answers
    print("\n[CHECKING ANSWERS]")
    checker = AnswerChecker(tolerance=0.01)
    check_results = check_answers(result, args.answers, checker)
    
    # Print results
    print_answer_results(check_results)
    
    # Show solution if requested
    if args.show_solution:
        print_solution(result)
    
    # Return exit code based on correctness
    all_correct = all(r['correct'] for r in check_results.values())
    return 0 if all_correct else 1


if __name__ == '__main__':
    sys.exit(main())

