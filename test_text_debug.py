"""Debug TEXT accumulation."""

from pg_translator.in_process_sandbox import InProcessSandbox

code = """
DOCUMENT()
TEXT("Hello, world!")
ENDDOCUMENT()
"""

sandbox = InProcessSandbox(timeout=10)
result = sandbox.execute(code, seed=1234)

print("Success:", result.success)
print("Output text:", repr(result.output_text))
print("Errors:", result.errors)
