import sys
from pathlib import Path

# Add all necessary paths
for pkg in ['pg_translator', 'pg_macros', 'pg_math', 'pg_mathobjects', 
            'pg_parser', 'pg_answer', 'pg_pgml', 'pg_renderer']:
    sys.path.insert(0, str(Path(__file__).parent / "packages" / pkg))

from pg_translator.preprocessor import PGPreprocessor

problem_file = Path("tutorial/sample-problems/Misc/FormulaAnswer.pg")
problem_code = problem_file.read_text()

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(problem_code)

print("PREPROCESSED CODE:")
print("=" * 80)
for i, line in enumerate(result.code.split('\n'), 1):
    print(f"{i:3d}: {line}")
print("=" * 80)
