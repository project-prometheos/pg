"""Debug PGML pattern matching."""

import re

text = "What is the meaning of life? [_]{num_cmp(answer)}"

patterns = {
    "answer_blank": re.compile(r"\[(_+)\]\{([^}]+)\}(?:\{(\d+)\})?"),
    "italic": re.compile(r"_([^_\s][^_]*?[^_\s])_"),
}

print("Text:", repr(text))
print()

for name, pattern in patterns.items():
    print(f"{name}:")
    for match in pattern.finditer(text):
        print(
            f"  Match at {match.start()}-{match.end()}: {repr(match.group(0))}")
        print(f"    Groups: {match.groups()}")
