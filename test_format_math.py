#!/usr/bin/env python3
"""Test the format_math function."""
import sys
import re

def format_math(text):
    """Convert LaTeX math delimiters for terminal display."""
    import re

    def simplify_parens(expr):
        """Remove unnecessary parentheses around single terms in fractions."""
        # Pattern: (single_term)/(other) or (other)/(single_term)
        # Single term = number, variable, or number+greek_letter (like 23π)
        # Not a function call (no inner parens) or operation (no +/-/*)

        # Match fractions like (23π)/(6) or (x)/(2)
        def is_simple_term(s):
            """Check if string is a simple term without operators or function calls."""
            s = s.strip()
            # Has operators or function calls - keep parens
            if any(op in s for op in ['+', '-', '*', '/', ' ']):
                return False
            if '(' in s or ')' in s:
                return False
            return True

        # Remove parens from simple numerators: (simple)/(any) → simple/(any)
        expr = re.sub(
            r'\(([^()]+)\)/\(', lambda m: f'{m.group(1)}/(' if is_simple_term(m.group(1)) else m.group(0), expr)
        # Remove parens from simple denominators: (any)/(simple) → (any)/simple
        expr = re.sub(r'\)/\(([^()]+)\)', lambda m: f')/{m.group(1)}' if is_simple_term(
            m.group(1)) else m.group(0), expr)
        # Remove parens from both if both simple: (simple)/(simple) → simple/simple
        expr = re.sub(r'\(([^()]+)\)/\(([^()]+)\)',
                      lambda m: f'{m.group(1)}/{m.group(2)}' if is_simple_term(
                          m.group(1)) and is_simple_term(m.group(2)) else m.group(0),
                      expr)

        return expr

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

        # Convert LaTeX bracket commands
        latex_str = latex_str.replace(r'\lbrack', '[')
        latex_str = latex_str.replace(r'\rbrack', ']')
        latex_str = latex_str.replace(r'\lbrace', '{')
        latex_str = latex_str.replace(r'\rbrace', '}')

        # Convert fractions: frac{num}{den} → (num)/(den)
        # Use regex to find nested fractions
        while 'frac{' in latex_str or r'\frac{' in latex_str:
            # Match \frac{...}{...} where ... can contain nested braces
            match = re.search(
                r'\\?frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', latex_str)
            if match:
                num = match.group(1).strip()
                den = match.group(2).strip()
                # Format as (num)/(den)
                replacement = f'({num})/({den})'
                latex_str = latex_str[:match.start()] + \
                    replacement + latex_str[match.end():]
            else:
                # Fallback: simple replacement
                latex_str = latex_str.replace(r'\frac', 'frac')
                break

        # Convert Greek letters
        latex_str = latex_str.replace(r'\pi', 'π')
        latex_str = latex_str.replace(r'\theta', 'θ')
        latex_str = latex_str.replace(r'\alpha', 'α')
        latex_str = latex_str.replace(r'\beta', 'β')
        latex_str = latex_str.replace(r'\gamma', 'γ')
        latex_str = latex_str.replace(r'\delta', 'δ')

        # Convert trig functions
        latex_str = latex_str.replace(r'\sin', 'sin')
        latex_str = latex_str.replace(r'\cos', 'cos')
        latex_str = latex_str.replace(r'\tan', 'tan')

        # Convert sqrt
        latex_str = latex_str.replace(r'\sqrt', '√')

        # Convert operators and symbols
        latex_str = latex_str.replace(r'\infty', '∞')
        latex_str = latex_str.replace(r'\cdot', '·')
        latex_str = latex_str.replace(r'\times', '×')
        latex_str = latex_str.replace(r'\div', '÷')
        latex_str = latex_str.replace(r'\pm', '±')
        latex_str = latex_str.replace(r'\leq', '≤')
        latex_str = latex_str.replace(r'\le', '≤')  # Short form
        latex_str = latex_str.replace(r'\geq', '≥')
        latex_str = latex_str.replace(r'\ge', '≥')  # Short form
        latex_str = latex_str.replace(r'\neq', '≠')
        latex_str = latex_str.replace(r'\approx', '≈')

        # Handle interval notation: [a,b[ → [a,b)  (half-open intervals)
        # Only convert the closing bracket if preceded by a comma (to avoid breaking other bracket uses)
        latex_str = re.sub(r'([0-9π]),\s*([0-9π]+)\[', r'\1, \2)', latex_str)

        # Simplify parentheses around single terms in fractions: (23π)/(6) → 23π/6
        # Helper to check if a term needs parentheses
        def needs_parens(term):
            term = term.strip()
            # Keep parens if empty or just parens
            if not term or term == '()':
                return True
            # Keep parens if term contains operators (but allow division for nested fractions)
            if any(op in term for op in ['+', '-', '*', '÷', '·', '×']):
                # Exception: if it's just a leading minus sign, that's okay
                if term.startswith('-') and not any(op in term[1:] for op in ['+', '-', '*', '÷', '·', '×']):
                    return False
                return True
            # Check for spaces, but allow spaces between numbers and Greek letters
            # (e.g., "7 π" is still a simple term)
            if ' ' in term:
                # Pattern for number followed by space and Greek letter
                if not re.match(r'^-?\d+(\.\d+)?\s*[πθαβγδ]$', term):
                    return True
            # Keep parens for function calls (has parentheses)
            if '(' in term:
                return True
            return False

        # Simplify fractions: (num)/(den) → simplified
        # Match pattern with non-greedy matching for nested parens
        def simplify_match(match):
            full = match.group(0)
            num = match.group(1).strip()
            den = match.group(2).strip()

            # Simplify
            num_display = num if needs_parens(num) else num
            den_display = den if needs_parens(den) else den

            # Rebuild
            num_final = f'({num_display})' if needs_parens(
                num) else num_display
            den_final = f'({den_display})' if needs_parens(
                den) else den_display

            return f'{num_final}/{den_final}'

        # Apply multiple times to handle nested cases
        # Use a pattern that matches balanced parentheses better
        prev = None
        while prev != latex_str:
            prev = latex_str
            # Match simple (content)/(content) where content has no unmatched parens
            latex_str = re.sub(
                r'\(([^()]+)\)/\(([^()]+)\)', simplify_match, latex_str)

        # Clean up extra spaces
        latex_str = re.sub(r'\s+', ' ', latex_str).strip()
        return latex_str

    # Inline math: \(...\) - use proper escaping
    text = re.sub(r'\\\((.+?)\\\)',
                  lambda m: f'[ {clean_latex(m.group(1))} ]', text)
    # Inline math: $...$  (but not $$)
    text = re.sub(
        r'(?<!\$)\$(?!\$)([^$]+)\$', lambda m: f'[ {clean_latex(m.group(1))} ]', text)
    # Display math: \[...\]
    text = re.sub(
        r'\\\[(.+?)\\\]', lambda m: f'\n\n  {clean_latex(m.group(1))}\n\n', text, flags=re.DOTALL)
    # Display math: $$...$$
    text = re.sub(r'\$\$(.+?)\$\$',
                  lambda m: f'\n\n  {clean_latex(m.group(1))}\n\n', text, flags=re.DOTALL)

    return text


# Test
html = r"Simplify $$\frac{6}{4}$$."
print(f"Input: {html}")
print(f"Output: {format_math(html)}")
