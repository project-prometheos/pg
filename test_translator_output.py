"""Test what pg_translator actually outputs."""

import sys
sys.path.insert(0, r'd:\pg\packages\pg_translator')
sys.path.insert(0, r'd:\pg\packages\pg_parser')
sys.path.insert(0, r'd:\pg\packages\pg_math')
sys.path.insert(0, r'd:\pg\packages\pg_pgml')
sys.path.insert(0, r'd:\pg\packages\pg_answer')
sys.path.insert(0, r'd:\pg\packages\pg_mathobjects')

from pg_translator import PGTranslator

pg_source = """
DOCUMENT();
loadMacros("PGstandard.pl", "MathObjects.pl", "PGML.pl");

$a = 3;
$b = 4;
$answer = Formula("x^2 + $a*x + $b");

BEGIN_PGML
Solve the equation \\( x^2 + [$a]x + [$b] = 0 \\).

Answer: [_]{$answer}{20}

The formula is [`x^2 + [$a]x`].

Display math: [``\\frac{[$a]}{[$b]}``]

END_PGML

ENDDOCUMENT();
"""

translator = PGTranslator()
result = translator.translate_source(pg_source, seed=42)

print("=" * 80)
print("STATEMENT HTML:")
print("=" * 80)
print(result.statement_html)
print("\n" + "=" * 80)
print("SOLUTION HTML:")
print("=" * 80)
print(result.solution_html)
print("\n" + "=" * 80)
print("ANSWER BLANKS:")
print("=" * 80)
for name, blank in result.answer_blanks.items():
    print(f"{name}: {blank}")
