#!/usr/bin/env python
"""
Implementation script to systematically fix sample problems.

This script provides an interactive workflow to:
1. Identify failing problems
2. Categorize by error type
3. Apply fixes batch by batch
4. Track progress

Usage:
    python implement_fixes.py --start          # Begin the workflow
    python implement_fixes.py --diagnose       # Run full diagnosis
    python implement_fixes.py --summary        # Show current status
    python implement_fixes.py --fix-batch 1    # Fix specific batch
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
import argparse

# Add packages to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "pg_translator"))
sys.path.insert(0, str(project_root / "packages" / "pg_macros"))
sys.path.insert(0, str(project_root / "packages" / "pg_math"))


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_section(title: str):
    """Print a formatted section."""
    print(f"\n{'-'*80}")
    print(f"  {title}")
    print(f"{'-'*80}\n")


def get_baseline_stats() -> Dict:
    """Get baseline statistics."""
    return {
        'total': 157,
        'baseline_pass': 58,
        'baseline_fail': 99,
        'baseline_date': '2025-11-09',
    }


def load_fix_log() -> List[Dict]:
    """Load the fix log if it exists."""
    fix_log_file = project_root / "FIXES_LOG.md"
    
    if fix_log_file.exists():
        # Parse markdown fix log
        content = fix_log_file.read_text()
        fixes = []
        
        # Simple parsing - in production would be more robust
        current_fix = {}
        for line in content.split('\n'):
            if line.startswith('# FIX:'):
                if current_fix:
                    fixes.append(current_fix)
                current_fix = {'name': line.replace('# FIX:', '').strip()}
            elif line.startswith('Date:'):
                current_fix['date'] = line.replace('Date:', '').strip()
            elif line.startswith('Status:'):
                current_fix['status'] = line.replace('Status:', '').strip()
        
        if current_fix:
            fixes.append(current_fix)
        
        return fixes
    
    return []


def show_welcome():
    """Show welcome message and overview."""
    print_header("SAMPLE PROBLEMS FIXING IMPLEMENTATION")
    
    stats = get_baseline_stats()
    
    print(f"""
This implementation guide will systematically fix the 157 WeBWorK tutorial 
sample problems for the Python implementation.

CURRENT STATUS (Baseline: {stats['baseline_date']})
  Total Problems:    {stats['total']}
  Passing:           {stats['baseline_pass']} ({100*stats['baseline_pass']/stats['total']:.1f}%)
  Failing:           {stats['baseline_fail']} ({100*stats['baseline_fail']/stats['total']:.1f}%)

TARGET
  Success Rate:      ≥95% (≥151/157 passing)

AVAILABLE DOCUMENTATION
  1. PLAN_FIX_SAMPLE_PROBLEMS.md
     → 6-phase strategic plan
  
  2. README_FIXES_WORKFLOW.md
     → Practical workflow with commands
  
  3. FIX_DOCUMENTATION_TEMPLATE.md
     → How to document each fix
  
  4. COMPLETE_GUIDE_FIX_SAMPLE_PROBLEMS.md
     → Complete overview and reference

AVAILABLE TOOLS
  • scripts/batch_diagnose_all.py    - Categorize all failures
  • scripts/diagnose_problem.py      - Deep dive on one problem
  • scripts/quick_test.py            - Fast individual test
  • scripts/track_progress.py        - Progress tracking

NEXT STEPS
  1. Run initial diagnosis to see what's failing
  2. Review error categories
  3. Pick highest-impact error type
  4. Fix problems in batches (5-10 per batch)
  5. Test and track progress
  6. Iterate until done

""")


def show_quick_start():
    """Show quick start commands."""
    print_section("QUICK START - Next 5 Minutes")
    
    print("""
Step 1: See all failures categorized by error type
  python scripts/batch_diagnose_all.py
  
  This will create:
    - problems_diagnostic_report.txt (detailed)
    - problems_diagnostic_summary.json (structured)
    - problems_by_error_type.txt (quick reference)

Step 2: Understand a specific problem
  python scripts/diagnose_problem.py \\
    "tutorial/sample-problems/Algebra/SimpleFactoring.pg"
  
  This shows the error, generated code, and suggestions

Step 3: Fix and test
  1. Edit the .pg file
  2. python scripts/quick_test.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"
  3. If passes, repeat for similar problems

Step 4: Track progress
  python scripts/track_progress.py --note "Fixed batch 1 - NameErrors"
  python scripts/track_progress.py --report

""")


def show_phase_1_strategy():
    """Show Phase 1 strategy."""
    print_section("PHASE 1: Quick Wins (SyntaxError & ImportError)")
    
    print("""
OBJECTIVE
  Fix the easiest 15-20 problems (~10-15% improvement)
  These are usually syntax issues, missing macros, or typos

PROCESS
  1. python scripts/batch_diagnose_all.py
  2. Look for: SyntaxError and ImportError problems
  3. For each problem:
     a. python scripts/diagnose_problem.py "tutorial/.../Problem.pg"
     b. Edit the .pg file to fix the issue
     c. python scripts/quick_test.py "tutorial/.../Problem.pg"
     d. If passes, move to next problem
  4. After fixing 5-10 problems:
     - python scripts/track_progress.py --note "Fixed [N] syntax issues"
     - python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering -v -s

EXPECTED IMPACT
  Before: 58/157 passing (36.9%)
  After:  ~73/157 passing (46.5%)
  
  This alone will be a significant improvement!

COMMON FIXES FOR SYNTAXERROR
  • Fix string escaping (LaTeX with backslashes)
    Before: $latex = "\\sqrt{x}";
    After:  $latex = r"\\sqrt{x}"; or similar
  
  • Fix parentheses/brackets
  • Correct operator differences between Perl and Python
  • Fix malformed function calls

""")


def show_phase_2_strategy():
    """Show Phase 2 strategy."""
    print_section("PHASE 2: NameError Fixes (Missing Macros & Undefined Variables)")
    
    print("""
OBJECTIVE
  Fix problems with undefined functions or variables
  Usually need to add macros to loadMacros() call
  
  Estimated: 30-40 problems

PROCESS
  1. From diagnostic report, get list of NameError problems
  2. For each, diagnose: python scripts/diagnose_problem.py "..."
  3. Look for the undefined function/variable in error message
  4. Find which macro provides it (usually in macro docs or other problems)
  5. Add macro to loadMacros() in the .pg file
  6. Test: python scripts/quick_test.py "..."

EXAMPLE FIX
  Error: NameError: name 'Formula' is not defined
  
  Original:
    loadMacros("PG.pl", "PGcourse.pl");
  
  Fixed:
    loadMacros("PG.pl", "PGbasicmacros.pl", "PGcourse.pl");
  
  Why: Formula() is defined in PGbasicmacros.pl

COMMON PATTERNS
  • Formula not defined    → Add "PGbasicmacros.pl"
  • random() not defined   → Add "PGrandom.pl"
  • List not defined       → Add "PGanswergroup.pl"
  • Dispatch issues        → Look for specialized macros

EXPECTED IMPACT
  Before: ~73/157 (46.5%)
  After:  ~108/157 (68.8%)
  
  This is the biggest improvement phase!

""")


def show_strategy_overview():
    """Show overall strategy."""
    print_header("FIX STRATEGY OVERVIEW")
    
    print("""
The fixing process has 5 phases, ordered by impact and difficulty:

PHASE 1: SyntaxError & ImportError
  ├─ Problems: ~15-20 (20% of failures)
  ├─ Difficulty: Easy (syntax fixes)
  ├─ Time: 1-2 hours
  └─ Impact: +15 problems passing
  
PHASE 2: NameError (Missing Macros)
  ├─ Problems: ~30-40 (40% of failures)
  ├─ Difficulty: Easy-Medium (macro loading)
  ├─ Time: 2-4 hours
  └─ Impact: +35 problems passing
  
PHASE 3: AttributeError (Method Issues)
  ├─ Problems: ~10-15 (15% of failures)
  ├─ Difficulty: Medium (object compatibility)
  ├─ Time: 2-3 hours
  └─ Impact: +12 problems passing
  
PHASE 4: TypeError (Type Mismatches)
  ├─ Problems: ~10-15 (15% of failures)
  ├─ Difficulty: Medium-Hard (algorithm changes)
  ├─ Time: 3-5 hours
  └─ Impact: +12 problems passing
  
PHASE 5: Complex/Stubborn Issues
  ├─ Problems: ~5-10 (remaining)
  ├─ Difficulty: Hard (need investigation)
  ├─ Time: 2-3 hours
  └─ Impact: +8 problems passing

TOTAL EFFORT: ~10-20 hours spread over 3-5 days
TOTAL IMPROVEMENT: 58 → 155+ (36.9% → 98.7%)

KEY INSIGHTS
  • 80% of problems likely have simple fixes (SyntaxError + NameError)
  • Batch fixing saves time (fix one, identify pattern, apply to similar)
  • Track progress to stay motivated
  • Document patterns for reference

""")


def show_workflow_checklist():
    """Show workflow checklist."""
    print_section("IMPLEMENTATION CHECKLIST")
    
    print("""
PRE-FIXING CHECKLIST
  ☐ Read COMPLETE_GUIDE_FIX_SAMPLE_PROBLEMS.md
  ☐ Understand the 5 phases
  ☐ Activate conda environment: conda activate pytorch-5090
  ☐ Navigate to: cd d:\\pg

INITIAL DIAGNOSIS (30 minutes)
  ☐ Run: python scripts/batch_diagnose_all.py
  ☐ Review: problems_diagnostic_report.txt
  ☐ Review: problems_by_error_type.txt
  ☐ Note: Number of each error type

PHASE 1: SyntaxError (1-2 hours)
  ☐ Identify SyntaxError problems from report
  ☐ Pick first problem
  ☐ Run: python scripts/diagnose_problem.py "tutorial/.../Problem.pg"
  ☐ Edit the .pg file
  ☐ Test: python scripts/quick_test.py "tutorial/.../Problem.pg"
  ☐ If passes: commit fix, move to next
  ☐ After 5-10 fixes: python scripts/track_progress.py --note "..."
  ☐ Re-run full batch test to confirm improvement

PHASE 2: NameError (2-4 hours)
  ☐ Get fresh diagnostics (patterns may have changed)
  ☐ Identify NameError problems
  ☐ Look for common patterns (e.g., all need same macro)
  ☐ Apply batch fixes to similar problems
  ☐ Test each batch
  ☐ Track progress after each batch

PHASE 3 & BEYOND: Continue with same process
  ☐ Each phase: diagnose → batch fix → test → track
  
FINAL VALIDATION
  ☐ Run full test suite: pytest test_tutorial_sample_problems.py -v
  ☐ Verify: ≥95% pass rate (≥151/157)
  ☐ Review: PROGRESS_FIXES.json shows steady improvement
  ☐ Commit: Final batch with summary message

""")


def main():
    parser = argparse.ArgumentParser(
        description="Implementation guide for fixing sample problems"
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Show welcome and quick start"
    )
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Run full diagnosis"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show current status summary"
    )
    parser.add_argument(
        "--phase-1",
        action="store_true",
        help="Show Phase 1 strategy"
    )
    parser.add_argument(
        "--phase-2",
        action="store_true",
        help="Show Phase 2 strategy"
    )
    parser.add_argument(
        "--strategy",
        action="store_true",
        help="Show complete strategy overview"
    )
    parser.add_argument(
        "--checklist",
        action="store_true",
        help="Show implementation checklist"
    )
    
    args = parser.parse_args()
    
    # Default: show welcome
    if not any([args.start, args.diagnose, args.summary, args.phase_1, 
                args.phase_2, args.strategy, args.checklist]):
        args.start = True
    
    if args.start:
        show_welcome()
        show_quick_start()
        print_section("TIP")
        print("""
To see the complete strategy, run:
  python implement_fixes.py --strategy

To see a specific phase, run:
  python implement_fixes.py --phase-1
  python implement_fixes.py --phase-2

To see the full checklist, run:
  python implement_fixes.py --checklist

When ready to start fixing, run:
  python scripts/batch_diagnose_all.py

Good luck! 🚀
""")
    
    if args.diagnose:
        print_section("RUNNING FULL DIAGNOSIS")
        print("This will take 30-60 seconds...\n")
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/batch_diagnose_all.py"],
            cwd=str(project_root)
        )
        sys.exit(result.returncode)
    
    if args.summary:
        print_header("CURRENT STATUS SUMMARY")
        
        stats = get_baseline_stats()
        print(f"Baseline ({stats['baseline_date']}):")
        print(f"  Passing:  {stats['baseline_pass']}/157 ({100*stats['baseline_pass']/157:.1f}%)")
        print(f"  Failing:  {stats['baseline_fail']}/157 ({100*stats['baseline_fail']/157:.1f}%)")
        
        # Try to load latest progress
        progress_file = project_root / "PROGRESS_FIXES.json"
        if progress_file.exists():
            try:
                progress = json.loads(progress_file.read_text())
                if progress:
                    latest = progress[-1]
                    print(f"\nLatest Checkpoint ({latest['timestamp'][:10]}):")
                    print(f"  Passing:  {latest['stats']['success']}/157 ({100*latest['stats']['success']/157:.1f}%)")
                    print(f"  Failing:  {latest['stats']['errors']}/157")
                    print(f"  Note: {latest.get('note', 'N/A')}")
            except:
                pass
        
        print("\nFor detailed status, see:")
        print("  - PROGRESS_FIXES.json (structured)")
        print("  - problems_diagnostic_report.txt (detailed)")
        print("  - problems_by_error_type.txt (quick reference)")
    
    if args.strategy:
        show_strategy_overview()
    
    if args.phase_1:
        show_phase_1_strategy()
    
    if args.phase_2:
        show_phase_2_strategy()
    
    if args.checklist:
        show_workflow_checklist()


if __name__ == '__main__':
    main()
