import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.math.compute import Compute
from pg.math.geometric import Point
from pg.math.collections import List
import re

# Test parsing individual Point elements
elem_str = "((1, 0))"
print(f"Element string: {elem_str}")

# Try Compute
cleaned_elem = elem_str.strip()
if cleaned_elem.startswith('((') and cleaned_elem.endswith('))'):
    cleaned_elem = cleaned_elem[1:-1].strip()
    print(f"After removing outer parens: {cleaned_elem}")

parsed = Compute(cleaned_elem)
print(f"Compute result type: {type(parsed).__name__}")
print(f"Compute result: {parsed}")
print(f"Is Point? {isinstance(parsed, Point)}")

# Try regex extraction
match = re.match(r'\(([^,]+),\s*([^)]+)\)', cleaned_elem)
if match:
    x_str, y_str = match.groups()
    print(f"Extracted: x={x_str}, y={y_str}")
    x = Compute(x_str.strip())
    y = Compute(y_str.strip())
    print(f"x type: {type(x).__name__}, y type: {type(y).__name__}")
    point = Point(x, y)
    print(f"Created Point: {point}")
    print(f"Point type: {type(point).__name__}")
    
    # Test creating a List
    elements = [point]
    student_list = List(elements)
    print(f"Created List: {student_list}")
    print(f"List type: {type(student_list).__name__}")
    print(f"List elements: {student_list.elements}")
    print(f"First element type: {type(student_list.elements[0]).__name__}")

