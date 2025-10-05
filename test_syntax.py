import sys
sys.path.insert(0, "apps/backend")
from app.db import ProblemDB
from pg_translator.preprocessor import PGPreprocessor

db = ProblemDB.get_instance()
problem = db.get_by_id("Algebra/AlgebraicFractionAnswer")
preprocessor = PGPreprocessor()
result = preprocessor.preprocess(problem["pg_source"])

lines = result.code.split("\n")
print(f"Total lines: {len(lines)}")
print("Lines 65-72:")
for i in range(64, min(72, len(lines))):
    print(f"{i+1:3d}: {lines[i]}")
