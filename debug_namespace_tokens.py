"""Debug why :: is not being converted."""

from pygments.lexers import PerlLexer
from pygments.token import Token

code = "LimitedPowers::OnlyIntegers("

lexer = PerlLexer()
tokens = list(lexer.get_tokens_unprocessed(code))

print("Tokens:")
for i, (pos, ttype, text) in enumerate(tokens):
    print(f"  {i}: pos={pos:3d}, type={str(ttype):40s}, text='{text}'")

print("\nChecking for :: detection:")
for i in range(len(tokens)):
    if tokens[i][2] == ':':
        print(f"  Found ':' at index {i}")
        if i + 1 < len(tokens):
            print(f"    Next token: '{tokens[i+1][2]}'")
            if tokens[i+1][2] == ':':
                print(f"    -> Should convert to '.'")
