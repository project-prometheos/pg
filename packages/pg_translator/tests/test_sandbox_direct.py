"""Quick test of in-process sandbox."""

from pg_translator.in_process_sandbox import InProcessSandbox

sandbox = InProcessSandbox(timeout=10)
sandbox.load_macros('PG.pl', 'PGbasicmacros.pl')

code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")
TEXT("What is 2 + 2?")
TEXT(BR())
TEXT("Answer: ", ans_rule(20))
ANS(num_cmp(4))
ENDDOCUMENT()
"""

result = sandbox.execute(code, seed=1234)
print('Success:', result.success)
print('Output:', repr(result.output_text))
print('Errors:', result.errors)
print('Answers:', len(result.answers), 'evaluators')
for name, evaluator in result.answers.items():
    print(f'  {name}: {type(evaluator).__name__}')
print('Has _pg_environment:', hasattr(sandbox, '_pg_environment'))
