"""Test sandbox execution directly."""

from pg_translator.in_process_sandbox import InProcessSandbox

code = """
DOCUMENT()
loadMacros("PG.pl")

a = 5
b = 3

pgml_block_0 = '''
Add: [$a] + [$b]
'''
TEXT(PGML(pgml_block_0))

ENDDOCUMENT()
"""

sandbox = InProcessSandbox(timeout=10)
result = sandbox.execute(code, seed=1234)

print("Success:", result.success)
print("Output text:", repr(result.output_text))
print("Errors:", result.errors if result.errors else "None")
