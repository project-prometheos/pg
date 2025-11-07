import sys
from pathlib import Path

for pkg in ['pg_translator', 'pg_macros', 'pg_math', 'pg_mathobjects', 
            'pg_parser', 'pg_answer', 'pg_pgml', 'pg_renderer']:
    sys.path.insert(0, str(Path(__file__).parent / "packages" / pkg))

from pg_translator.preprocessor import PGPreprocessor

problem_file = Path("tutorial/sample-problems/Complex/ComplexOperations.pg")
problem_code = problem_file.read_text()

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(problem_code)

lines = result.code.split('\n')
for i in range(40, min(55, len(lines))):
    print(f"{i+1:3d}: {lines[i]}")
