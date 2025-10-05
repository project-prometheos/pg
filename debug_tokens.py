"""Debug Pygments tokens for ->with(."""

from pygments.lexers import PerlLexer

code = "$multians = MultiAnswer($num, $den)->with("

lexer = PerlLexer()
tokens = list(lexer.get_tokens_unprocessed(code))

print("Tokens:")
for pos, ttype, text in tokens:
    print(f"  {pos:3d}: {str(ttype):40s} '{text}'")
