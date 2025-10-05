"""Debug the preprocessor issue."""

from pg_translator.pg_preprocessor_pygment import PGPreprocessor

# Simple test
code = """
$h = 3;
$k = 5;
$formula = Compute("(x-$h)^2-$k");
"""

prep = PGPreprocessor()
result = prep.preprocess(code, use_sandbox_macros=False)

print("Input:")
print(code)
print("\nPreprocessed code:")
print(result.code)
print("\nText blocks:")
for i, (block_type, content) in enumerate(result.text_blocks):
    print(f"\n--- Text block {i} ({block_type}) ---")
    print(content)
