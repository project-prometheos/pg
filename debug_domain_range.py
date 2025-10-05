"""Debug the DomainRange problem to see what code is generated."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'pg_translator'))

from pg_translator.pg_preprocessor_pygment import PGPreprocessor

pg_src = Path('tutorial/sample-problems/Algebra/DomainRange.pg').read_text()

preprocessor = PGPreprocessor()
result = preprocessor.preprocess(pg_src, use_sandbox_macros=False)

print("="*60)
print("PREPROCESSED CODE:")
print("="*60)
print(result.code)
print("="*60)
