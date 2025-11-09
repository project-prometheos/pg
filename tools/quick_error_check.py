#!/usr/bin/env python3
"""Quick script to analyze multiple problems and summarize errors."""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

problems = [
    "NoSolution",
    "GraphToolCustomChecker", 
    "StringOrOtherType",
    "TableOfValues",
    "LinearApprox",
    "PrimesInFormulas",
    "LineSegmentGraphTool",
    "QuadrilateralGraphTool",
    "TriangleGraphTool",
    "GraphShading"
]

print("="* 80)
print("QUICK ERROR ANALYSIS - Top 10 Failing Problems")
print("=" * 80)
print()

for problem in problems:
    print(f"\n{'─' * 80}")
    print(f"Problem: {problem}")
    print(f"{'─' * 80}")
    
    cmd = [
        sys.executable,
        "-m", "pytest",
        str(project_root / "packages" / "pg_translator" / "tests" / "test_tutorial_sample_problems.py"),
        f"::test_tutorial_problem_renders[{problem}]",
        "--tb=short", "-v"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract just the error line
    for line in result.stdout.split('\n'):
        if 'SyntaxError:' in line or 'NameError:' in line or 'TypeError:' in line or 'AttributeError:' in line:
            print(f"ERROR: {line.strip()}")
            break
        if 'File "<problem>", line' in line:
            print(f"  {line.strip()}")
    
    print()

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
