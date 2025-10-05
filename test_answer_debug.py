#!/usr/bin/env python3
"""Debug answer extraction."""

from pg_translator import PGTranslator
from pathlib import Path
import sys
sys.path.insert(0, "packages/pg_translator")

t = PGTranslator()
r = t.translate("webwork_ps1_pg/ps1-prob01.pg", seed=1234)
print("answer_blanks:", r.answer_blanks)
print("statement_html:",
      r.statement_html[:300] if r.statement_html else "NONE")
