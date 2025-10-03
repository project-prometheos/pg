#!/usr/bin/env python
"""
Simple test script for webwork_ps1_pg problems.

This script manually defines the correct answers for each problem
and tests them using pypg.py.
"""

import subprocess
import sys
from pathlib import Path


# Manually extracted correct answers for each problem
CORRECT_ANSWERS = {
    "ps1-prob01.pg": ["-sqrt(3)/3"],
    "ps1-prob02.pg": ["pi/6", "7*pi/6"],  # Two answers in increasing order
    "ps1-prob03.pg": ["pi/6", "11*pi/6"],  # Two answers in increasing order
    "ps1-prob04.pg": ["pi/4", "5*pi/4"],   # Two answers in increasing order
    "ps1-prob05.pg": ["pi/3", "5*pi/3"],   # Two answers in increasing order
    "ps1-prob06.pg": ["pi/6", "7*pi/6"],   # Two answers in increasing order
    "ps1-prob07.pg": ["pi/4", "7*pi/4"],   # Two answers in increasing order
    "ps1-prob08.pg": ["pi/3", "4*pi/3"],   # Two answers in increasing order
    "ps1-prob09.pg": ["pi/2", "3*pi/2"],   # Two answers in increasing order
    "ps1-prob10.pg": ["sqrt(89)", "atan2(8,5)"],  # C and phi
    "ps1-prob11.pg": ["sqrt(13)", "atan2(3,2)"],  # C and phi
    "ps1-prob12.pg": ["2*sin(x + pi/6)"],  # Function form
    "ps1-prob13.pg": ["3*sin(x + pi/4)"],  # Function form
    "ps1-prob14.pg": ["sqrt(5)*sin(x + atan2(2,1))"],  # Function form
    "ps1-prob15.pg": ["sqrt(10)*sin(x + atan2(3,1))"],  # Function form
    "ps1-prob16.pg": ["4*sin(x + pi/3)"],  # Function form
    "ps1-prob17.pg": ["sqrt(17)*sin(x + atan2(4,1))"],  # Function form
    "ps1-prob18.pg": ["sqrt(26)*sin(x + atan2(5,1))"],  # Function form
    "ps1-prob19.pg": ["sqrt(29)*sin(x + atan2(5,2))"],  # Function form
    "ps1-prob20.pg": ["sqrt(34)*sin(x + atan2(5,3))"],  # Function form
    "ps1-prob21.pg": ["3*ln(27) + 64*ln(5)"],  # Logarithmic expression
    "ps1-prob22.pg": ["2*ln(8) + 32*ln(3)"],   # Logarithmic expression
    "ps1-prob23.pg": ["4*ln(16) + 16*ln(7)"],  # Logarithmic expression
    "ps1-prob24.pg": ["5*ln(32) + 8*ln(9)"],   # Logarithmic expression
    "ps1-prob25.pg": ["pi"],  # arccos(-1)
}


def test_problem(pg_file: Path, correct_answers: list) -> dict:
    """Test a single problem with correct answers."""
    print(f"\n{'='*60}")
    print(f"Testing: {pg_file.name}")
    print(f"Correct answers: {correct_answers}")
    print(f"{'='*60}")
    
    # Run pypg.py with the correct answers
    cmd = [
        'python', 'pypg.py', 
        str(pg_file),
        '--',  # Separate positional args from flags
        *correct_answers,
        '--seed', '123'
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        output = result.stdout
        error = result.stderr
        
        print(output)
        
        # Parse the output to determine success/failure
        if "*** ALL ANSWERS CORRECT! ***" in output:
            status = "PASS"
            message = "All answers correct"
            score = 1.0
        elif "***" in output and "INCORRECT" in output:
            status = "FAIL"
            message = "Some answers incorrect"
            # Extract score from output
            import re
            score_match = re.search(r'Score: (\d+)/(\d+)', output)
            if score_match:
                correct_count = int(score_match.group(1))
                total_count = int(score_match.group(2))
                score = correct_count / total_count if total_count > 0 else 0
            else:
                score = 0
        else:
            status = "ERROR"
            message = f"Unexpected output or error: {error}"
            score = 0
        
        print(f"\nStatus: {status}")
        print(f"Message: {message}")
        print(f"Score: {score}")
        
        return {
            'file': pg_file.name,
            'status': status,
            'message': message,
            'correct_answers': correct_answers,
            'score': score,
            'output': output,
            'error': error
        }
        
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out after 30 seconds")
        return {
            'file': pg_file.name,
            'status': 'TIMEOUT',
            'message': 'Command timed out after 30 seconds',
            'correct_answers': correct_answers,
            'score': 0
        }
    except Exception as e:
        print(f"ERROR: Command failed: {e}")
        return {
            'file': pg_file.name,
            'status': 'ERROR',
            'message': f'Command failed: {e}',
            'correct_answers': correct_answers,
            'score': 0
        }


def main():
    """Main function to run the tests."""
    print("WebWork PS1 Problem Tester (Simple Version)")
    print("=" * 60)
    
    webwork_dir = Path("webwork_ps1_pg")
    
    if not webwork_dir.exists():
        print(f"Error: Directory {webwork_dir} not found!")
        return
    
    # Get all PG files
    pg_files = sorted(webwork_dir.glob("ps1-prob*.pg"))
    
    if not pg_files:
        print(f"No PG files found in {webwork_dir}")
        return
    
    print(f"Found {len(pg_files)} PG files to test")
    
    results = []
    
    # Test each file
    for pg_file in pg_files:
        if pg_file.name in CORRECT_ANSWERS:
            correct_answers = CORRECT_ANSWERS[pg_file.name]
            result = test_problem(pg_file, correct_answers)
            results.append(result)
        else:
            print(f"\nSkipping {pg_file.name} - no correct answers defined")
            results.append({
                'file': pg_file.name,
                'status': 'SKIP',
                'message': 'No correct answers defined',
                'correct_answers': [],
                'score': 0
            })
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] in ['ERROR', 'TIMEOUT'])
    skipped = sum(1 for r in results if r['status'] == 'SKIP')
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    if total_tests > skipped:
        print(f"Success rate: {passed/(total_tests-skipped)*100:.1f}%")
    
    # Show failed/error cases
    if failed > 0 or errors > 0:
        print(f"\n{'='*80}")
        print("FAILED/ERROR CASES")
        print(f"{'='*80}")
        
        for result in results:
            if result['status'] in ['FAIL', 'ERROR', 'TIMEOUT']:
                print(f"\n{result['file']}: {result['status']}")
                print(f"  Message: {result['message']}")
                print(f"  Correct answers: {result['correct_answers']}")
                if result['status'] == 'FAIL':
                    print(f"  Score: {result['score']}")
    
    # Exit with appropriate code
    failed_count = sum(1 for r in results if r['status'] in ['FAIL', 'ERROR', 'TIMEOUT'])
    if failed_count > 0:
        print(f"\nExiting with code 1 due to {failed_count} failures/errors")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
