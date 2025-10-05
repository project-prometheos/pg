#!/usr/bin/env python3
"""Debug the interval notation issue"""

import re

# Simulate the full processing pipeline


def clean_latex(latex_str):
    """Clean up LaTeX for terminal display with mathematical notation."""
    print(f"  clean_latex input: {repr(latex_str)}")

    # Remove \! (thin space) and \displaystyle
    latex_str = latex_str.replace(r'\!', '')
    latex_str = latex_str.replace(r'\displaystyle', '')

    # Convert \left( and \right) to just ( and )
    latex_str = latex_str.replace(r'\left(', '(')
    latex_str = latex_str.replace(r'\right)', ')')
    latex_str = latex_str.replace(r'\left[', '[')
    latex_str = latex_str.replace(r'\right]', ']')
    latex_str = latex_str.replace(r'\left\{', '{')
    latex_str = latex_str.replace(r'\right\}', '}')

    print(f"  After left/right: {repr(latex_str)}")

    # Handle interval notation: [a,b[ → [a,b)  (half-open intervals)
    latex_str = re.sub(r'([0-9π]),\s*([0-9π]+)\[', r'\1, \2)', latex_str)

    print(f"  After interval: {repr(latex_str)}")

    return latex_str


def format_math(text):
    """Convert LaTeX math delimiters for terminal display."""
    print(f"format_math input: {repr(text)}")

    # Inline math: \(...\)
    def process_inline(match):
        content = match.group(1)
        print(f"Processing inline math: {repr(content)}")
        cleaned = clean_latex(content)
        result = f'[ {cleaned} ]'
        print(f"Inline result: {repr(result)}")
        return result

    text = re.sub(r'\\\((.+?)\\\)', process_inline, text)

    print(f"format_math output: {repr(text)}")
    return text


# Test
test_input = r'i \([0,2\pi[\).'
print("="*70)
print("FULL TRACE")
print("="*70)
print(f"Input: {repr(test_input)}")
print()

# Step 1: Replace pi
text = test_input.replace(r'\pi', 'π')
print(f"After \\pi → π: {repr(text)}")
print()

# Step 2: Format math
result = format_math(text)
print()
print(f"Final result: {result}")
