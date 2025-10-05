"""Test method chaining with multi-line parameters."""

from pg_translator.pg_preprocessor_pygment import PGPreprocessor

test_code = """
$multians = MultiAnswer($num, $den)->with(
    allowBlankAnswers => 1,
    checker => sub {
        return [1, 1];
    }
);
"""

prep = PGPreprocessor()
result = prep.preprocess(test_code, use_sandbox_macros=False)

print("Input:")
print(test_code)
print("\nOutput:")
print(result.code)
