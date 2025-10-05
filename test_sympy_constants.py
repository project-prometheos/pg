import sympy as sp

tests = [
    ('pi', 'lowercase'),
    ('Pi', 'uppercase (capital P)'),
    ('E', 'Euler constant uppercase'),
    ('e', 'Euler constant lowercase'),
]

print('Sympy constant support:')
for name, desc in tests:
    try:
        value = sp.sympify(name).evalf()
        print(f'  ✅ {desc:30s} {name} = {value}')
    except Exception as e:
        print(f'  ❌ {desc:30s} {name} - Error: {e}')

# Check if unicode pi can be preprocessed
print('\nUnicode π symbol:')
unicode_pi = 'π'
print(f'  Direct: {repr(unicode_pi)}')
replaced = unicode_pi.replace('π', 'pi')
print(f'  Replaced to "pi": {replaced}')
value = sp.sympify(replaced).evalf()
print(f'  Value: {value}')
