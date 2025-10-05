"""Test PGML parsing directly."""

from pg_translator.pgml_parser import PGMLParser, PGMLRenderer

pgml_text = """
What is the meaning of life? [_]{num_cmp(answer)}
"""

context = {"answer": 42}

parser = PGMLParser()
doc = parser.parse(pgml_text, context=context)

print("Parsed document:")
for node in doc.nodes:
    print(f"  {node}")

renderer = PGMLRenderer(context=context)
html = renderer.render(doc)

print("\nRendered HTML:")
print(repr(html))
