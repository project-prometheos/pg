import sys
from pathlib import Path
import inspect
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/Multianswer.pg", seed=1234)

# Get the MultiAnswer object
multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']

print(f"Checker function:")
print(f"  Type: {type(multi_eval.checker)}")
print(f"  Callable: {callable(multi_eval.checker)}")

# Try to inspect the source
try:
    source = inspect.getsource(multi_eval.checker)
    print(f"\nSource code:")
    print(source)
except Exception as e:
    print(f"\nCouldn't get source: {e}")

# Try to get the code object
if hasattr(multi_eval.checker, '__code__'):
    code = multi_eval.checker.__code__
    print(f"\nCode object info:")
    print(f"  co_argcount: {code.co_argcount}")
    print(f"  co_varnames: {code.co_varnames}")
    print(f"  co_names: {code.co_names}")
    print(f"  co_filename: {code.co_filename}")
    print(f"  co_firstlineno: {code.co_firstlineno}")

# Try to disassemble
print(f"\nDisassembly:")
try:
    import dis
    dis.dis(multi_eval.checker)
except Exception as e:
    print(f"  Error: {e}")

