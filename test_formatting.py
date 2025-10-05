#!/usr/bin/env python3
"""Test the formatting improvements for pg_solve.py"""

import re


def strip_html(html_text):
    """Remove HTML tags for terminal display."""
    import re
    # Unescape LaTeX delimiters that were escaped for HTML
    html_text = html_text.replace('\\\\(', '\\(')
    html_text = html_text.replace('\\\\)', '\\)')
    html_text = html_text.replace('\\\\[', '\\[')
    html_text = html_text.replace('\\\\]', '\\]')

    # Clean up LaTeX placeholder notation for answer blanks BEFORE removing HTML tags
    # Convert [\,\_\,] or similar patterns to just ___ for readability
    # These are visual placeholders in the problem text, not actual answer blanks
    # Match just the bracket pattern, not the surrounding \( \)
    # Use [^\].]* to ensure we don't match across sentences (periods)
    html_text = re.sub(r'\[[^\].]*\\_[^\].]*\]', '___', html_text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_text)
    # Decode common HTML entities
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ')
    # Clean up multiple spaces and newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def format_math(text):
    """Convert LaTeX math delimiters for terminal display."""
    import re

    def clean_latex(latex_str):
        """Clean up LaTeX for terminal display with mathematical notation."""
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

        # Convert fractions
        while 'frac{' in latex_str or r'\frac{' in latex_str:
            match = re.search(
                r'\\?frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', latex_str)
            if match:
                num = match.group(1).strip()
                den = match.group(2).strip()
                replacement = f'({num})/({den})'
                latex_str = latex_str[:match.start()] + \
                    replacement + latex_str[match.end():]
            else:
                latex_str = latex_str.replace(r'\frac', 'frac')
                break

        # Convert Greek letters
        latex_str = latex_str.replace(r'\pi', 'π')
        latex_str = latex_str.replace(r'\theta', 'θ')

        # Convert trig functions
        latex_str = latex_str.replace(r'\sin', 'sin')
        latex_str = latex_str.replace(r'\cos', 'cos')
        latex_str = latex_str.replace(r'\tan', 'tan')

        # Convert sqrt
        latex_str = latex_str.replace(r'\sqrt', '√')

        # Convert operators
        latex_str = latex_str.replace(r'\leq', '≤')
        latex_str = latex_str.replace(r'\le', '≤')

        # Handle interval notation: [a,b[ → [a,b)  (half-open intervals)
        # Only convert the closing bracket if preceded by a comma (to avoid breaking other bracket uses)
        latex_str = re.sub(r'([0-9π]),\s*([0-9π]+)\[', r'\1, \2)', latex_str)

        # Clean up extra spaces
        latex_str = re.sub(r'\s+', ' ', latex_str).strip()
        return latex_str

    # Inline math: \(...\)
    text = re.sub(r'\\\((.+?)\\\)',
                  lambda m: f'[ {clean_latex(m.group(1))} ]', text)
    # Inline math: $...$
    text = re.sub(
        r'(?<!\$)\$(?!\$)([^$]+)\$', lambda m: f'[ {clean_latex(m.group(1))} ]', text)

    # Clean up interval notation: [0,2π[ → [0, 2π)
    text = re.sub(r'\[([^[\]]+)\[', r'[\1)', text)

    return text


# Test cases
test_cases = [
    {
        'input': r'Bestäm alla lösningar till \(\tan(x)=1/\sqrt3\) i \([0,2\pi[\). Växande ordning: \([\,\_\,] \le [\,\_\,]\).',
        'description': 'Problem 17 text with placeholders'
    },
    {
        'input': r'Beräkna \(\tan\!\left(\frac{23\pi}{6}\right)\)',
        'description': 'Fraction with trig function'
    },
    {
        'input': r'Interval \([0,2\pi[\) notation',
        'description': 'Half-open interval'
    }
]

print("="*70)
print("Testing Format Improvements")
print("="*70)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['description']}")
    print(f"Input:  {test['input']}")

    # Process
    stripped = strip_html(test['input'])
    formatted = format_math(stripped)

    print(f"Output: {formatted}")
    print("-"*70)
