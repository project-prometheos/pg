from pg_translator.preprocessor import PGPreprocessor

# Actual Perl from AnswerBlankInExponent.pg lines 44-47
perl_code = r'''if ($displayMode eq 'TeX') {
    $exp =
        "\( \displaystyle $expression = ("
        . ans_rule(4) . ")^{"
        . ans_rule(4) . "}\)";
}'''

print("Input Perl code:")
for i, line in enumerate(perl_code.split('\n'), 1):
    print(f'{i:3}: {repr(line)}')
print("\n" + "="*60 + "\n")

p = PGPreprocessor()
result = p.preprocess(perl_code)

print("Preprocessed Python code:")
lines = result.code.split('\n')
for i, line in enumerate(lines, 1):
    print(f'{i:3}: {repr(line)}')
