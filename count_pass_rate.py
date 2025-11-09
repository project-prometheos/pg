"""Count passing and failing sample problems"""
import os
import subprocess
from pathlib import Path

sample_dir = Path("tutorial/sample-problems")
passed = 0
failed = 0
errors = {}

# Get all .pg files
pg_files = sorted(sample_dir.rglob("*.pg"))
print(f"Total sample problems: {len(pg_files)}\n")

for pg_file in pg_files:
    # Convert to pypg
    result = subprocess.run(
        ["python", "tools/fix_sample_problem.py", "--convert", pg_file.stem],
        capture_output=True,
        text=True
    )
    
    if "[OK]" in result.stdout:
        # Get the .pypg file
        pypg_file = pg_file.with_suffix(".pypg")
        if pypg_file.exists():
            # Try to compile it
            try:
                with open(pypg_file) as f:
                    code = f.read()
                compile(code, str(pypg_file), 'exec')
                passed += 1
            except SyntaxError as e:
                failed += 1
                error_key = f"{e.__class__.__name__}: {str(e).split('(')[0]}"
                if error_key not in errors:
                    errors[error_key] = []
                errors[error_key].append(pg_file.stem)
        else:
            failed += 1
    else:
        failed += 1

print(f"Passed: {passed}/{len(pg_files)} ({100*passed//len(pg_files)}%)")
print(f"Failed: {failed}/{len(pg_files)} ({100*failed//len(pg_files)}%)")

if errors:
    print(f"\nTop error types:")
    for error_type, problems in sorted(errors.items(), key=lambda x: -len(x[1]))[:5]:
        print(f"  {error_type}: {len(problems)} problems")
        if len(problems) <= 3:
            print(f"    {', '.join(problems)}")
