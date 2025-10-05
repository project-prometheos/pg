#!/usr/bin/env python3
"""Test tokenizing prob02 PGML."""

from pg_pgml.tokenizer import PGMLTokenizer
import sys
sys.path.insert(0, "packages/pg_pgml")

text = r'''
**Problem 2.** Bestäm alla lösningar till \(\cot(x)=\sqrt3\) i intervallet \([0,2\pi[\). Placera svaren i växande ordning:
\([\,\_\,] \le [\,\_\,]\).

[_]{$A} <= [_]{$B}
'''

print("Tokenizing...")
print("Text:", repr(text[:100]))

tokenizer = PGMLTokenizer(text)

try:
    tokens = tokenizer.tokenize()
    print(f"Got {len(tokens)} tokens")
    for i, tok in enumerate(tokens[:20]):
        print(
            f"  {i}: {tok.type} = {repr(tok.value[:50] if len(tok.value) > 50 else tok.value)}")
except KeyboardInterrupt:
    print(
        f"\nHANG! Stopped at pos={tokenizer.pos}, char={repr(text[tokenizer.pos:tokenizer.pos+20])}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
