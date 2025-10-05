#!/usr/bin/env python3
"""Debug what context PGML actually receives."""

import pg_translator.pgml_parser
from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.preprocessor import PGPreprocessor
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))


# Monkey-patch PGML to see what context it receives
original_pgml_parser = __import__(
    'pg_translator.pgml_parser', fromlist=['PGMLParser']).PGMLParser


class DebugPGMLParser(original_pgml_parser):
    def parse(self, text, context=None):
        print(f"\n[DEBUG] PGML.parse called with:")
        print(f"  Text: {text[:100]}...")
        print(f"  Context type: {type(context)}")
        print(
            f"  Context keys: {list(context.keys())[:20] if context else 'None'}")
        if context and 'vertexform' in context:
            print(f"  vertexform value: {context['vertexform']}")
        return super().parse(text, context)


# Replace in module
pg_translator.pgml_parser.PGMLParser = DebugPGMLParser

# Now run the test
pg_code = """
DOCUMENT()

h = 3
k = 5
vertexform = f"(x-{h})^2-{k}"

BEGIN_PGML
The value is [$vertexform].
END_PGML

ENDDOCUMENT()
"""

print("="*70)
print("DEBUGGING CONTEXT PASSING TO PGML")
print("="*70)

preprocessor = PGPreprocessor()
python_code = preprocessor.preprocess(pg_code).code

sandbox = InProcessSandbox()
exec_result = sandbox.execute(python_code, seed=1234)

print(f"\n" + "="*70)
print(f"Final output: {exec_result.output_text}")
print(f"Namespace has vertexform: {'vertexform' in sandbox.namespace}")
if 'vertexform' in sandbox.namespace:
    print(f"vertexform value: {sandbox.namespace['vertexform']}")
