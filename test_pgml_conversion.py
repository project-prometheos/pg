#!/usr/bin/env python
"""Test PGML conversion for PS1 Problem 02"""
import re

# This is what comes from the database for PS1/Problem-02
pgml_input = r"""**Problem 2.** Bestäm alla lösningar till \(\cot(x)=\sqrt3\) i intervallet \([0,2\pi[\). Placera svaren i växande ordning:
\([\,\_\,] \le [\,\_\,]\).

[_]{$A} <= [_]{$B}"""


def _pgml_to_markdown(pgml_text: str) -> str:
    """
    Convert PGML to Markdown with math delimiters.

    PGML uses \(...\) for inline math and \[...\] for display math.
    We convert these to $ ... $ and $$ ... $$ for markdown/KaTeX rendering.
    """
    # Convert PGML inline math \(...\) to $ ... $
    pgml_text = re.sub(r'\\\((.*?)\\\)', r'$\1$', pgml_text, flags=re.DOTALL)

    # Convert PGML display math \[...\] to $$ ... $$
    pgml_text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', pgml_text, flags=re.DOTALL)

    # Convert backtick math [` ... `] to $ ... $
    pgml_text = re.sub(r'\[`([^`]+)`\]', r'$\1$', pgml_text)

    # Convert code-fenced math [``` ... ```] to display math
    pgml_text = re.sub(r'\[```(.*?)```\]', r'$$\1$$',
                       pgml_text, flags=re.DOTALL)

    # Convert answer blanks [_]{...} to [____]
    pgml_text = re.sub(r'\[_\]\{[^}]+\}', r'[____]', pgml_text)

    return pgml_text


print("=" * 80)
print("ORIGINAL PGML:")
print("=" * 80)
print(pgml_input)
print()

converted = _pgml_to_markdown(pgml_input)
print("=" * 80)
print("CONVERTED MARKDOWN:")
print("=" * 80)
print(converted)
print()

print("=" * 80)
print("VERIFICATION:")
print("=" * 80)
print("✓ Inline math \\(...\\) converted to $...$:",
      "$\\cot(x)=\\sqrt3$" in converted)
print("✓ Inline math for interval:", "$[0,2\\pi[$" in converted)
print("✓ Answer blanks converted:", "[____]" in converted)
print("✗ Raw PGML still present:", "\\(" in converted or "\\[" in converted)
