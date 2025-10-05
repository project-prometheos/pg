"""Compare preprocessor output."""

from pg_translator.preprocessor import PGPreprocessor as OrigPrep
from pg_translator.pg_preprocessor_pygment import PGPreprocessor as PygmentPrep

# Test code with variable interpolation
code = """
$h = 3;
$k = 5;
$formula = Compute("(x-$h)^2-$k");
"""

print("=" * 70)
print("ORIGINAL PREPROCESSOR")
print("=" * 70)
orig_prep = OrigPrep()
orig_result = orig_prep.preprocess(code, use_sandbox_macros=False)
print(orig_result.code)

print("\n" + "=" * 70)
print("PYGMENT PREPROCESSOR")
print("=" * 70)
pyg_prep = PygmentPrep()
pyg_result = pyg_prep.preprocess(code, use_sandbox_macros=False)
print(pyg_result.code)

print("\n" + "=" * 70)
print("COMPARISON")
print("=" * 70)
has_fstr_orig = ('f"' in orig_result.code) or ("f'" in orig_result.code)
has_fstr_pyg = ('f"' in pyg_result.code) or ("f'" in pyg_result.code)
has_dollar_h = '$h' in pyg_result.code
print(f"Original has f-string: {has_fstr_orig}")
print(f"Pygment has f-string: {has_fstr_pyg}")
print(f"Pygment has $h: {has_dollar_h}")
