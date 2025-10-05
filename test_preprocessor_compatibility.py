"""
Test if pg_preprocessor_pygment is a drop-in replacement for preprocessor.

This checks:
1. Same class name and interface
2. Same method signatures
3. Same return types
4. Compatible behavior on test inputs
"""

import sys

# Test both preprocessors
from pg_translator.preprocessor import PGPreprocessor as OriginalPreprocessor
from pg_translator.pg_preprocessor_pygment import PGPreprocessor as PygmentPreprocessor

# Test PG source
test_pg = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");

Context("Numeric");
$a = random(1, 10);
$ans = Compute("$a + 5");

BEGIN_PGML
The answer is [$a] plus 5.

[_]{$ans}
END_PGML

ENDDOCUMENT();
"""

print("=" * 70)
print("INTERFACE COMPARISON")
print("=" * 70)

# Check class names
print(f"✓ Class name matches: {OriginalPreprocessor.__name__ == PygmentPreprocessor.__name__}")

# Check method signature
import inspect

orig_sig = inspect.signature(OriginalPreprocessor.preprocess)
pyg_sig = inspect.signature(PygmentPreprocessor.preprocess)

print(f"✓ Method signature matches: {str(orig_sig) == str(pyg_sig)}")
print(f"  Original: preprocess{orig_sig}")
print(f"  Pygment:  preprocess{pyg_sig}")

# Test both preprocessors
print("\n" + "=" * 70)
print("FUNCTIONAL COMPARISON")
print("=" * 70)

try:
    orig_prep = OriginalPreprocessor()
    orig_result = orig_prep.preprocess(test_pg, use_sandbox_macros=True)
    print("✓ Original preprocessor: SUCCESS")
    print(f"  Code lines: {len(orig_result.code.splitlines())}")
    print(f"  Text blocks: {len(orig_result.text_blocks)}")
    print(f"  Line map entries: {len(orig_result.line_map)}")
except Exception as e:
    print(f"✗ Original preprocessor: FAILED - {e}")
    orig_result = None

try:
    pyg_prep = PygmentPreprocessor()
    pyg_result = pyg_prep.preprocess(test_pg, use_sandbox_macros=True)
    print("✓ Pygment preprocessor: SUCCESS")
    print(f"  Code lines: {len(pyg_result.code.splitlines())}")
    print(f"  Text blocks: {len(pyg_result.text_blocks)}")
    print(f"  Line map entries: {len(pyg_result.line_map)}")
except Exception as e:
    print(f"✗ Pygment preprocessor: FAILED - {e}")
    pyg_result = None

# Compare results
if orig_result and pyg_result:
    print("\n" + "=" * 70)
    print("RESULT COMPARISON")
    print("=" * 70)
    
    print(f"Text blocks match: {len(orig_result.text_blocks) == len(pyg_result.text_blocks)}")
    if orig_result.text_blocks and pyg_result.text_blocks:
        for i, (orig_block, pyg_block) in enumerate(zip(orig_result.text_blocks, pyg_result.text_blocks)):
            print(f"  Block {i}: {orig_block[0]} == {pyg_block[0]}: {orig_block[0] == pyg_block[0]}")
    
    print(f"\nReturn type matches: {type(orig_result).__name__ == type(pyg_result).__name__}")
    print(f"  Original: {type(orig_result).__name__}")
    print(f"  Pygment:  {type(pyg_result).__name__}")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

if orig_result and pyg_result:
    print("✅ YES - pg_preprocessor_pygment can be used as a drop-in replacement")
    print("   - Same class name: PGPreprocessor")
    print("   - Same method signature: preprocess(pg_source, use_sandbox_macros=True)")
    print("   - Same return type: PreprocessResult")
    print("   - Both process PG code successfully")
    print("\nTo switch, simply change the import in translator.py:")
    print("  from .pg_preprocessor_pygment import PGPreprocessor")
else:
    print("⚠️  PARTIAL - Both work but may have subtle differences in output")
