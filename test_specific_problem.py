import sys
from pathlib import Path

for pkg in ['pg_translator', 'pg_macros', 'pg_math', 'pg_mathobjects', 
            'pg_parser', 'pg_answer', 'pg_pgml', 'pg_renderer']:
    sys.path.insert(0, str(Path(__file__).parent / "packages" / pkg))

from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.macro_loader import MacroLoader
from pg_translator.preprocessor import PGPreprocessor
from pg_parser import Context

problem_path = sys.argv[1] if len(sys.argv) > 1 else "tutorial/sample-problems/ProblemTechniques/SimplePopUp.pg"
problem_file = Path(problem_path)
problem_code = problem_file.read_text()

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(problem_code)

print("Attempting to compile...")
try:
    compile(result.code, '<problem>', 'exec')
    print("SUCCESS: Code compiles!")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}:")
    lines = result.code.split('\n')
    start = max(0, e.lineno - 5)
    end = min(len(lines), e.lineno + 3)
    for i in range(start, end):
        marker = ">>>" if i == e.lineno - 1 else "   "
        print(f"{marker} {i+1:3d}: {lines[i]}")
    print(f"\nError: {e.msg}")
