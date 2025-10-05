from pg_renderer import PGMLRenderer

# Test LaTeX delimiter conversion
test_cases = [
    ('Inline: \\(x^2\\)', 'Inline: $x^2$'),
    ('Display: \\[y = mx + b\\]', 'Display: $$y = mx + b$$'),
    ('Mixed: \\(a\\) and \\[b\\]', 'Mixed: $a$ and $$b$$'),
    ('PGML inline: [`x^2`]', 'PGML inline: $x^2$'),
    ('PGML display: [``y=mx+b``]', 'PGML display: $$y=mx+b$$'),
]

renderer = PGMLRenderer({})

print("Testing LaTeX delimiter conversion:")
print("=" * 70)

for input_text, expected in test_cases:
    result, _ = renderer.render(input_text)
    # Normalize whitespace
    result = result.strip()
    expected = expected.strip()
    
    status = '✅' if result == expected else '❌'
    print(f"{status} Input:    {input_text}")
    print(f"   Expected: {expected}")
    print(f"   Got:      {result}")
    print()

print("=" * 70)
