#!/usr/bin/env python3
"""Debug script to test rendering of Algebra/AlgebraicFractionAnswer"""

from app.services.pg_translator_service import get_pg_translator_service
from app.db import ProblemDB
import sys
sys.path.insert(0, 'apps/backend')


# Get problem
db = ProblemDB.get_instance()
# Test failing problem
problem = db.get_by_id('Algebra/AlgebraicFractionAnswer')

print("=" * 80)
print("PROBLEM SOURCE:")
print("=" * 80)
print(problem['pg_source'])
print("=" * 80)

# Render it
translator = get_pg_translator_service()
result = translator.render_problem(problem['pg_source'], seed=0)

print("\nRENDER RESULT:")
print("=" * 80)
print(f"statement_html length: {len(result['statement_html'])}")
print(f"statement_html: {result['statement_html']}")
print(f"inputs: {result['inputs']}")
print(f"answers: {result['answers']}")
print(f"warnings: {result['warnings']}")
print(f"errors: {result['errors']}")
