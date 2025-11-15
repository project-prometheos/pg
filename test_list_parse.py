import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.math.compute import Compute
from pg.math.collections import List
from pg.math.geometric import Point

# Test what Compute returns for list input
student_answer = "((1, 0)), ((-1, 0))"
print(f"Student answer: {student_answer}")

# Try Compute
try:
    parsed = Compute(student_answer)
    print(f"Compute result type: {type(parsed).__name__}")
    print(f"Compute result: {parsed}")
    print(f"Is List? {isinstance(parsed, List)}")
except Exception as e:
    print(f"Compute error: {e}")

# Try manual parsing
print("\nManual parsing:")
cleaned = student_answer.strip()
print(f"Cleaned: {cleaned}")

# Split by comma (handling nested parentheses)
elements = []
current = ""
depth = 0
for char in cleaned:
    if char in '([{':
        depth += 1
        current += char
    elif char in ')]}':
        depth -= 1
        current += char
    elif char == ',' and depth == 0:
        if current.strip():
            print(f"  Parsing element: {current.strip()}")
            try:
                elem_parsed = Compute(current.strip())
                print(f"    -> {type(elem_parsed).__name__}: {elem_parsed}")
                elements.append(elem_parsed)
            except Exception as e:
                print(f"    -> Error: {e}")
        current = ""
    else:
        current += char
if current.strip():
    print(f"  Parsing element: {current.strip()}")
    try:
        elem_parsed = Compute(current.strip())
        print(f"    -> {type(elem_parsed).__name__}: {elem_parsed}")
        elements.append(elem_parsed)
    except Exception as e:
        print(f"    -> Error: {e}")

print(f"\nElements: {elements}")
if elements:
    student_list = List(elements)
    print(f"Created List: {student_list}")
    print(f"List type: {type(student_list).__name__}")
    print(f"List elements: {student_list.elements}")

