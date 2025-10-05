#!/usr/bin/env python3
"""Debug why answers aren't being extracted from PGML."""

import sys
sys.path.insert(0, 'packages/pg_translator')
sys.path.insert(0, 'packages/pg_macros')
sys.path.insert(0, 'packages/pg_math')
sys.path.insert(0, 'packages/pg_pgml')

from pg_math import Compute, Context
from pg_pgml import PGMLParser, HTMLRenderer

# Set up context
Context('Fraction-NoDecimals')
answer = Compute('3/2')

# Create a simple PGML with evaluator
pgml_text = '''
Simplify.

Answer = [_]{answer.cmp(
    studentsMustReduceFractions  = 1,
    reduceFractions  = 1,
    allowMixedNumbers  = 0
)}{15}
'''

# Parse and render
doc = PGMLParser.parse_text(pgml_text)
print(f"Parsed document: {doc}")
print(f"\nAnswer blank info:")
for block in doc.blocks:
    for elem in block.content:
        if hasattr(elem, 'evaluator_code'):
            print(f"  evaluator_code: {repr(elem.evaluator_code)}")

# Create context dict
context = {
    'answer': answer,
}

# Track registered answers
registered_answers = {}

# Render with answer registration
renderer = HTMLRenderer(context=context)
renderer._register_answer = lambda name, ev: registered_answers.update({name: ev})

html = renderer.render(doc)

print(f"\nRendered HTML length: {len(html)}")
print(f"Registered answers: {registered_answers}")
print(f"\nHTML snippet:")
print(html[:300])
