import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.math.compute import Compute
from pg.math.collections import List

# Test what Compute returns
student_answer = "((1, 0)), ((-1, 0))"
print(f"Student answer: {student_answer}")

parsed = Compute(student_answer)
print(f"Compute result type: {type(parsed).__name__}")
print(f"Compute result: {parsed}")
print(f"Is List? {isinstance(parsed, List)}")
print(f"Is Python list? {isinstance(parsed, list)}")
print(f"Is tuple? {isinstance(parsed, tuple)}")

# Check if it has to_python method
if hasattr(parsed, 'to_python'):
    print(f"to_python(): {parsed.to_python()}")

