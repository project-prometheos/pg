import sys
sys.path.insert(0, "apps/backend")
from app.db import ProblemDB
from pg_translator.preprocessor import PGPreprocessor

db = ProblemDB.get_instance()
problem = db.get_by_id("Algebra/AlgebraicFractionAnswer")
preprocessor = PGPreprocessor()
result = preprocessor.preprocess(problem["pg_source"])

lines = result.code.split("\n")
print(f"Lines 50-70:")
for i in range(49, min(70, len(lines))):
    print(f"{i+1:3d}: {lines[i]}")
