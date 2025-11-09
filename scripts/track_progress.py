#!/usr/bin/env python
"""
Track progress on fixing sample problems.

Maintains a progress file and shows improvement over time.

Usage:
    python track_progress.py
    python track_progress.py --note "Fixed Priority 1 NameErrors"
    python track_progress.py --report  # Show full history
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import argparse
import subprocess

# Add packages to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_answer"))
sys.path.insert(0, str(project_root / "packages" / "pg_parser"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))

from pg_translator import PGTranslator


def run_tests() -> dict:
    """Run the batch test and parse results."""
    
    # Run pytest batch rendering test
    try:
        cmd = [
            sys.executable,
            "-m", "pytest",
            "packages/pg_translator/tests/test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering",
            "-v", "-s"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=600
        )
        
        output = result.stdout + result.stderr
        
        # Parse output for counts
        stats = {
            'success': 0,
            'warnings': 0,
            'errors': 0,
        }
        
        # Look for the summary in output
        for line in output.split('\n'):
            if '[OK] Success:' in line:
                stats['success'] = int(line.split(':')[1].strip())
            elif '[WARN] Warnings:' in line:
                stats['warnings'] = int(line.split(':')[1].strip())
            elif '[FAIL] Errors:' in line:
                stats['errors'] = int(line.split(':')[1].strip())
        
        total = stats['success'] + stats['warnings'] + stats['errors']
        if total == 0:
            # Fallback: count PASSED/FAILED in output
            stats['success'] = output.count(' PASSED')
            stats['errors'] = output.count(' FAILED')
        
        return stats
    
    except Exception as e:
        print(f"Error running tests: {e}")
        return None


def load_progress() -> list:
    """Load progress history."""
    progress_file = project_root / "PROGRESS_FIXES.json"
    
    if progress_file.exists():
        try:
            return json.loads(progress_file.read_text())
        except:
            return []
    
    return []


def save_progress(history: list):
    """Save progress history."""
    progress_file = project_root / "PROGRESS_FIXES.json"
    progress_file.write_text(json.dumps(history, indent=2))


def get_baseline() -> dict:
    """Get baseline statistics."""
    return {
        'total': 157,
        'baseline_success': 58,
        'baseline_errors': 99,
        'baseline_date': '2025-11-09',
    }


def main():
    parser = argparse.ArgumentParser(description="Track progress on fixing sample problems")
    parser.add_argument(
        "--note",
        help="Add a note about this checkpoint"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Show full progress history"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Don't run tests, just show last result"
    )
    
    args = parser.parse_args()
    
    baseline = get_baseline()
    history = load_progress()
    
    if args.report:
        # Show full history
        print("\n" + "="*80)
        print("PROGRESS HISTORY")
        print("="*80)
        
        if not history:
            print("No progress recorded yet")
        else:
            print(f"\n{'Date':<19} {'Success':>8} {'Errors':>8} {'Rate':>8} {'Note':<40}")
            print("-"*80)
            
            for entry in history:
                date = entry['timestamp'][:10]
                success = entry['stats']['success']
                errors = entry['stats']['errors']
                rate = f"{100*success/(success+errors):.1f}%" if (success+errors) > 0 else "N/A"
                note = entry.get('note', '')[:40]
                
                print(f"{date}  {success:>8}  {errors:>8}  {rate:>8}  {note}")
        
        # Calculate improvement
        if len(history) > 0:
            baseline_success = baseline['baseline_success']
            current_success = history[-1]['stats']['success']
            improvement = current_success - baseline_success
            
            print("\n" + "-"*80)
            print(f"Baseline (2025-11-09): {baseline_success} passing")
            print(f"Current:               {current_success} passing")
            print(f"Improvement:           +{improvement} ({100*improvement/baseline['total']:.1f}%)")
    
    else:
        # Run test and record checkpoint
        if args.quick:
            # Just show last result
            if history:
                last = history[-1]
                stats = last['stats']
                total = baseline['total']
                success_rate = 100 * stats['success'] / total if total > 0 else 0
                
                print(f"\n📊 Last Checkpoint: {last['timestamp']}")
                print(f"   Passing: {stats['success']}/{total} ({success_rate:.1f}%)")
                print(f"   Errors:  {stats['errors']}")
                print(f"   Warnings: {stats['warnings']}")
                if last.get('note'):
                    print(f"   Note: {last['note']}")
            else:
                print("No checkpoint recorded yet")
        
        else:
            print("\n🧪 Running tests...")
            stats = run_tests()
            
            if stats:
                total = baseline['total']
                success_rate = 100 * stats['success'] / total if total > 0 else 0
                
                # Record checkpoint
                checkpoint = {
                    'timestamp': datetime.now().isoformat(),
                    'stats': stats,
                    'note': args.note or '',
                }
                history.append(checkpoint)
                save_progress(history)
                
                # Show results
                print(f"\n✅ Checkpoint recorded\n")
                print(f"📊 Current Results:")
                print(f"   Passing:  {stats['success']}/{total} ({success_rate:.1f}%)")
                print(f"   Errors:   {stats['errors']}")
                print(f"   Warnings: {stats['warnings']}")
                
                # Show improvement
                baseline_success = baseline['baseline_success']
                improvement = stats['success'] - baseline_success
                
                print(f"\n📈 Progress:")
                print(f"   Baseline: {baseline_success} (2025-11-09)")
                print(f"   Current:  {stats['success']}")
                print(f"   Gain:     +{improvement} ({100*improvement/total:.1f}%)")
                
                if args.note:
                    print(f"\n📝 Note: {args.note}")
                
                print(f"\n💾 History saved to: PROGRESS_FIXES.json")
            
            else:
                print("❌ Failed to run tests")
                sys.exit(1)


if __name__ == '__main__':
    main()
