from pg_translator.preprocessor import PGPreprocessor

# The actual problem file
with open('tutorial/sample-problems/Algebra/AnswerBlankInExponent.pg', 'r', encoding='utf-8') as f:
    code = f.read()

# Patch preprocess to add logging
p = PGPreprocessor()
original_transform = p._transform_line

call_log = []

def logging_transform(line):
    result = original_transform(line)
    call_log.append({
        'input': line,
        'output': result,
        'has_newline': '\n' in result
    })
    return result

p._transform_line = logging_transform

result = p.preprocess(code)

# Find the calls related to the else block
print("Lines containing 'exp =' transformations:")
print("="*60)
for i, call in enumerate(call_log):
    if 'exp =' in call['input'] or 'exp =' in call['output']:
        print(f"\nCall #{i}:")
        print(f"  Input: {call['input']!r}")
        print(f"  Output: {call['output']!r}")
        if call['has_newline']:
            print(f"  ⚠️  HAS NEWLINE!")
