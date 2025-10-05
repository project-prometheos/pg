"""Test PGML function directly."""

from pg_translator.pgml_parser import PGMLParser, PGMLRenderer

pgml_text = "Add: [$a] + [$b]"
context = {"a": 5, "b": 3}

parser = PGMLParser()
doc = parser.parse(pgml_text, context=context)

print("Parsed nodes:")
for node in doc.nodes:
    print(f"  {node}")

renderer = PGMLRenderer(context=context)
html = renderer.render(doc)

print("\nRendered HTML:")
print(repr(html))
