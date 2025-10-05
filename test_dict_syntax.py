from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor

test_cases = [
    # Simple dict
    "allcellcss = { padding => '3pt' }",

    # Function with dict
    "func(param => value, opts => { key => 'val' })",

    # Multiple keys in dict
    "hash = { key1 => 'a', key2 => 'b', key3 => 'c' }",

    # Function params only
    "func(key1 => 1, key2 => 2)",

    # Mixed
    "MultiAnswer(1, 2)->with(checker => sub { })",
]

processor = PGPreprocessor()

for test in test_cases:
    result = processor._transform_line(test)
    print(f"IN:  {test}")
    print(f"OUT: {result}")
    print()
