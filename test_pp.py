import sys
sys.path.insert(0, "apps/backend")
from app.db import ProblemDB
from pg_translator.preprocessor import PGPreprocessor

db = ProblemDB.get_instance()
problem = db.get_by_id("Algebra/AlgebraicFractionAnswer")
preprocessor = PGPreprocessor()
result = preprocessor.preprocess(problem["pg_source"])

print("Last 800 chars:")
print("="*80)
print(result.code[-800:])
print("="*80)
print("PGML() count:", result.code.count("PGML("))
