"""Test sandbox execution with PGML answer blank."""

from pg_translator.in_process_sandbox import InProcessSandbox

code = """
DOCUMENT()
loadMacros("PG.pl")

answer = 42

pgml_block_0 = '''
What is the meaning of life? [_]{num_cmp(answer)}
'''
TEXT(PGML(pgml_block_0))

ENDDOCUMENT()
"""

sandbox = InProcessSandbox(timeout=10)
result = sandbox.execute(code, seed=1234)

print("Success:", result.success)
print("Output text:", repr(result.output_text))
print("Answers:", result.answers)
print("Errors:", result.errors if result.errors else "None")
