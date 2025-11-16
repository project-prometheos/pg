#!/usr/bin/env python3
"""Debug PGML parsing and rendering."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))

from pg.pgml import PGMLParser
from pg.renderer import PGMLRenderer

# Simulate the PGML content after preprocessing
pgml_content = """Simplify [``\\frac{6}{4}``].

Answer = [_]{answer.cmp(
    studentsMustReduceFractions = 1,
    reduceFractions = 1,
    allowMixedNumbers = 0
)}{15}"""

print("=" * 70)
print("TESTING PGML PARSING AND RENDERING")
print("=" * 70)

print("\nPGML Content:")
print(pgml_content)

print("\n" + "=" * 70)
print("PARSING")
print("=" * 70)

# Parse PGML
doc = PGMLParser.parse_text(pgml_content)
print(f"\nParsed document: {type(doc)}")
print(f"Number of blocks: {len(doc.blocks) if hasattr(doc, 'blocks') else 'N/A'}")

# Walk through AST to find answer blanks
from pg.pgml.parser import AnswerBlank

def find_answer_blanks(node):
    if isinstance(node, AnswerBlank):
        yield node
    elif hasattr(node, 'blocks'):
        for block in node.blocks:
            yield from find_answer_blanks(block)
    elif hasattr(node, 'content'):
        if isinstance(node.content, list):
            for child in node.content:
                yield from find_answer_blanks(child)
    elif hasattr(node, 'items'):
        if isinstance(node.items, list):
            for item in node.items:
                yield from find_answer_blanks(item)

blanks = list(find_answer_blanks(doc))
print(f"\nFound {len(blanks)} answer blank(s)")
for i, blank in enumerate(blanks):
    print(f"  Blank {i+1}:")
    print(f"    Width: {blank.width}")
    print(f"    Evaluator code: {blank.evaluator_code}")

print("\n" + "=" * 70)
print("RENDERING")
print("=" * 70)

# Create a mock variable context
class Fraction:
    def __init__(self, num, denom):
        self.num = num
        self.denom = denom

    def __str__(self):
        return f"{self.num}/{self.denom}"

    def to_string(self):
        return str(self)

    def cmp(self, **kwargs):
        class Checker:
            pass
        return Checker()

variables = {
    'answer': Fraction(3, 2)
}

# Render PGML
renderer = PGMLRenderer(variables=variables)
html, answer_blanks = renderer.render(pgml_content)

print(f"\nRendered HTML (first 300 chars):")
print(html[:300])

print(f"\nAnswer blanks extracted: {len(answer_blanks)}")
for name, spec in answer_blanks.items():
    print(f"  {name}:")
    print(f"    Type: {type(spec)}")
    if isinstance(spec, dict):
        print(f"    Keys: {list(spec.keys())}")
        if 'options' in spec:
            print(f"    Options: {spec['options']}")
        if 'evaluator' in spec:
            print(f"    Evaluator: {type(spec['evaluator'])}")
    else:
        print(f"    Value: {spec}")

print("\n" + "=" * 70)
