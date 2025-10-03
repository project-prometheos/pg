#!/usr/bin/env python
"""
Test script for webwork_ps1_pg problems with correct answers.

This script:
1. Parses each PG file to extract the correct answers
2. Runs pypg.py with the correct answers
3. Reports success/failure for each problem
4. Provides a summary of results
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add packages to path for direct access
sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'pg_renderer'))

from pg_renderer import PGRenderer
from pg_renderer.parser import PGParser


class WebWorkPS1Tester:
    """Test all webwork_ps1_pg problems with correct answers."""
    
    def __init__(self):
        self.webwork_dir = Path("webwork_ps1_pg")
        self.results: List[Dict[str, Any]] = []
        self.renderer = PGRenderer()
        self.parser = PGParser()
        
    def extract_correct_answers(self, pg_file: Path) -> List[str]:
        """Extract correct answers from a PG file."""
        try:
            with open(pg_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the problem
            problem = self.parser.parse(content)
            
            # Render to get answer information
            rendered = self.renderer.render(content, seed=123)
            
            # Extract correct answers from the answers dict
            correct_answers = []
            for answer_id, answer_data in rendered['answers'].items():
                correct_value = answer_data.get('correct_value', '')
                correct_answers.append(str(correct_value))
            
            return correct_answers
            
        except Exception as e:
            print(f"Error extracting answers from {pg_file.name}: {e}")
            return []
    
    def test_problem(self, pg_file: Path) -> Dict[str, Any]:
        """Test a single problem with its correct answers."""
        print(f"\n{'='*60}")
        print(f"Testing: {pg_file.name}")
        print(f"{'='*60}")
        
        # Extract correct answers
        correct_answers = self.extract_correct_answers(pg_file)
        
        if not correct_answers:
            return {
                'file': pg_file.name,
                'status': 'ERROR',
                'message': 'Could not extract correct answers',
                'correct_answers': [],
                'student_answers': [],
                'score': 0
            }
        
        print(f"Extracted correct answers: {correct_answers}")
        
        # Run pypg.py with the correct answers
        cmd = [
            'python', 'pypg.py', 
            str(pg_file),
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
            
            # Parse the output to determine success/failure
            if "*** ALL ANSWERS CORRECT! ***" in output:
                status = "PASS"
                message = "All answers correct"
                score = 1.0
            elif "***" in output and "INCORRECT" in output:
                status = "FAIL"
                message = "Some answers incorrect"
                # Extract score from output
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
            
            print(f"Status: {status}")
            print(f"Message: {message}")
            print(f"Score: {score}")
            
            return {
                'file': pg_file.name,
                'status': status,
                'message': message,
                'correct_answers': correct_answers,
                'student_answers': correct_answers,  # We used correct answers as input
                'score': score,
                'output': output,
                'error': error
            }
            
        except subprocess.TimeoutExpired:
            return {
                'file': pg_file.name,
                'status': 'TIMEOUT',
                'message': 'Command timed out after 30 seconds',
                'correct_answers': correct_answers,
                'student_answers': [],
                'score': 0
            }
        except Exception as e:
            return {
                'file': pg_file.name,
                'status': 'ERROR',
                'message': f'Command failed: {e}',
                'correct_answers': correct_answers,
                'student_answers': [],
                'score': 0
            }
    
    def run_all_tests(self) -> None:
        """Run tests on all PG files in webwork_ps1_pg directory."""
        if not self.webwork_dir.exists():
            print(f"Error: Directory {self.webwork_dir} not found!")
            return
        
        # Get all PG files
        pg_files = sorted(self.webwork_dir.glob("ps1-prob*.pg"))
        
        if not pg_files:
            print(f"No PG files found in {self.webwork_dir}")
            return
        
        print(f"Found {len(pg_files)} PG files to test")
        
        # Test each file
        for pg_file in pg_files:
            result = self.test_problem(pg_file)
            self.results.append(result)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print a summary of all test results."""
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.results if r['status'] in ['ERROR', 'TIMEOUT'])
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"Success rate: {passed/total_tests*100:.1f}%")
        
        # Show failed/error cases
        if failed > 0 or errors > 0:
            print(f"\n{'='*80}")
            print("FAILED/ERROR CASES")
            print(f"{'='*80}")
            
            for result in self.results:
                if result['status'] in ['FAIL', 'ERROR', 'TIMEOUT']:
                    print(f"\n{result['file']}: {result['status']}")
                    print(f"  Message: {result['message']}")
                    print(f"  Correct answers: {result['correct_answers']}")
                    if result['status'] == 'FAIL':
                        print(f"  Score: {result['score']}")
        
        # Show problems that couldn't extract answers
        no_answers = [r for r in self.results if not r['correct_answers']]
        if no_answers:
            print(f"\n{'='*80}")
            print("PROBLEMS WITH NO EXTRACTED ANSWERS")
            print(f"{'='*80}")
            for result in no_answers:
                print(f"  {result['file']}: {result['message']}")
    
    def save_detailed_results(self, filename: str = "webwork_ps1_test_results.txt") -> None:
        """Save detailed results to a file."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("WebWork PS1 Test Results\n")
            f.write("=" * 50 + "\n\n")
            
            for result in self.results:
                f.write(f"File: {result['file']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Message: {result['message']}\n")
                f.write(f"Correct answers: {result['correct_answers']}\n")
                f.write(f"Score: {result['score']}\n")
                if 'output' in result and result['output']:
                    f.write(f"Output:\n{result['output']}\n")
                if 'error' in result and result['error']:
                    f.write(f"Error:\n{result['error']}\n")
                f.write("-" * 50 + "\n\n")
        
        print(f"\nDetailed results saved to: {filename}")


def main():
    """Main function to run the tests."""
    print("WebWork PS1 Problem Tester")
    print("=" * 50)
    
    tester = WebWorkPS1Tester()
    tester.run_all_tests()
    tester.save_detailed_results()
    
    # Exit with appropriate code
    failed_count = sum(1 for r in tester.results if r['status'] in ['FAIL', 'ERROR', 'TIMEOUT'])
    if failed_count > 0:
        print(f"\nExiting with code 1 due to {failed_count} failures/errors")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
