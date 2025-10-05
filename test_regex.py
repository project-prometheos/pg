"""Test PGML regex for answer blanks."""

import re

pattern = re.compile(r"\[(_+)\]\{([^}]+)\}(?:\{(\d+)\})?")

text1 = "[_]{num_cmp(answer)}"
text2 = "[_]{$ans}"
text3 = "[___]{num_cmp(42)}{20}"

for text in [text1, text2, text3]:
    match = pattern.search(text)
    if match:
        print(f"'{text}' -> groups: {match.groups()}")
    else:
        print(f"'{text}' -> NO MATCH")
