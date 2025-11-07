import sys
from pathlib import Path

for pkg in ['pg_translator', 'pg_macros', 'pg_math', 'pg_mathobjects', 
            'pg_parser', 'pg_answer', 'pg_pgml', 'pg_renderer']:
    sys.path.insert(0, str(Path(__file__).parent / "packages" / pkg))

from pg_translator.preprocessor import PGPreprocessor

problem_file = Path("tutorial/sample-problems/Misc/FormulaAnswer.pg")
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
    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)
    for i in range(start, end):
        marker = ">>>" if i == e.lineno - 1 else "   "
        print(f"{marker} {i+1:3d}: {lines[i]}")
    print(f"\nError: {e.msg}")
    print(f"Text: {e.text}")
    print(f"Offset: {e.offset}")
