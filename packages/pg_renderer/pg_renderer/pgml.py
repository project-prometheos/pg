"""Render PGML markup to HTML."""

import re
from typing import Dict, Any, Tuple


class PGMLRenderer:
    """Render PGML markup to HTML."""
    
    def __init__(self, variables: Dict[str, Any]):
        self.variables = variables
        self.answer_counter = 0
        self.answer_blanks: Dict[str, str] = {}  # answer_id → correct_value
    
    def render(self, pgml: str) -> Tuple[str, Dict[str, str]]:
        """
        Render PGML to HTML.
        
        Returns:
            (html_string, answer_blanks_dict)
        """
        html = pgml
        
        # 1. Variable interpolation FIRST (before any bracket/brace processing)
        # This prevents variables like [$a] from being corrupted by table simplification
        html = re.sub(r'\[\$(\w+)\]', self._interpolate_var, html)
        
        # 2. Remove PGML table constructs (simplify for MVP)
        # These are advanced layout features: [# ... #] and [. ... .]
        html = self._simplify_tables(html)
        
        # 3. Display math: [`` ... ``] → KaTeX display math
        html = re.sub(r'\[``(.*?)``\]', r'$$\1$$', html, flags=re.DOTALL)
        
        # 4. Inline math: [` ... `] → KaTeX inline math
        html = re.sub(r'\[`(.*?)`\]', r'$\1$', html)
        
        # 5. Answer blanks: [_____]{$answer} or [_]{$answer}
        # Also handle optional width specifier: [_]{$answer}{15}
        html = re.sub(r'\[_+\]\{([^}]+)\}(?:\{[0-9]+\})?', self._create_answer_blank, html)
        
        # 6. Formatting → Markdown
        # Bold: [*text*] → **text**
        html = re.sub(r'\[\*(.*?)\*\]', r'**\1**', html)
        # Italic: [|text|] → *text*
        html = re.sub(r'\[\|(.*?)\|\]', r'*\1*', html)
        # Underline: [_text_] → __text__ (approximation)
        html = re.sub(r'\[_(.*?)_\]', r'__\1__', html)
        
        # 7. Lists (already Markdown with leading *) - nothing to do here
        
        # 8. Cleanup: Remove any remaining PGML artifacts (conservative)
        # IMPORTANT: Do not touch LaTeX curly braces or math content
        # Only remove trailing PGML table options like "]*{ ... }"
        html = re.sub(r"\]\s*\*\s*\{[^}]+\}", "]", html)
        
        # 9. Paragraphs: ensure double newlines between blocks (Markdown)
        # Normalize Windows newlines and collapse extra spaces
        html = html.replace('\r\n', '\n')
        # Ensure we have a trailing newline
        if not html.endswith('\n'):
            html += '\n'
        
        return html, self.answer_blanks
    
    def _simplify_tables(self, pgml: str) -> str:
        """
        Simplify PGML table constructs for MVP.
        
        PGML tables use [# ... #] for rows and [. ... .] for cells.
        For MVP, we extract the content and ignore the layout directives.
        """
        # Remove table options like ]*{ padding => [...] }
        # Need to handle nested braces and brackets properly
        # Match: ]* followed by { then content (including nested [] and {}) then }
        def remove_table_options(text):
            # Use a more careful approach to handle nested structures
            result = []
            i = 0
            while i < len(text):
                # Look for ]*{
                if i < len(text) - 2 and text[i:i+3] == ']*{':
                    # Find the matching }
                    brace_count = 1
                    bracket_depth = 0
                    j = i + 3
                    while j < len(text) and brace_count > 0:
                        if text[j] == '[':
                            bracket_depth += 1
                        elif text[j] == ']' and bracket_depth > 0:
                            bracket_depth -= 1
                        elif text[j] == '{' and bracket_depth == 0:
                            brace_count += 1
                        elif text[j] == '}' and bracket_depth == 0:
                            brace_count -= 1
                        j += 1
                    # Replace ]*{...} with just ]
                    result.append(']')
                    i = j
                else:
                    result.append(text[i])
                    i += 1
            return ''.join(result)
        
        pgml = remove_table_options(pgml)
        
        # Convert [# ... #] table rows to simple line breaks
        pgml = re.sub(r'\[#\s*', '', pgml)
        pgml = re.sub(r'\s*#\]', '\n', pgml)
        
        # Convert [. ... .] table cells to simple spaces
        pgml = re.sub(r'\[\.\s*', '', pgml)
        pgml = re.sub(r'\s*\.\]', ' ', pgml)
        
        return pgml
    
    def _interpolate_var(self, match: re.Match) -> str:
        """Replace [$var] with variable value."""
        var_name = match.group(1)
        
        # Check if variable exists
        if var_name not in self.variables:
            # Variable not found - return a placeholder or empty string
            # to avoid showing raw $varname
            return f'[Variable ${var_name} not found]'
        
        value = self.variables.get(var_name)
        
        # Format numbers nicely
        if isinstance(value, float):
            # Remove trailing zeros
            return f'{value:g}'
        return str(value)
    
    def _create_answer_blank(self, match: re.Match) -> str:
        """Create HTML input for answer blank."""
        answer_expr = match.group(1)
        
        # Generate unique answer ID
        self.answer_counter += 1
        answer_id = f'AnSwEr{self.answer_counter:04d}'
        
        # Evaluate answer expression to get correct value
        correct_value = self._eval_answer(answer_expr)
        self.answer_blanks[answer_id] = str(correct_value)
        
        # Return a placeholder that won't break markdown
        # The frontend will replace these with actual input fields
        return f'___ANSWER_BLANK_{answer_id}___'
    
    def _eval_answer(self, expr: str) -> Any:
        """
        Evaluate answer expression.
        
        The expression can be:
        - A simple variable: $answer
        - A Compute() expression: Compute("x >= $a")
        - A literal string: "x >= 4"
        """
        expr = expr.strip()
        
        # If it starts with $, it's a variable reference
        if expr.startswith('$'):
            var_name = expr.lstrip('$')
            result = self.variables.get(var_name, expr)
            
            # If the result is a string, interpolate any variables in it
            if isinstance(result, str):
                result = self._interpolate_variables_in_string(result)
            
            return result
        
        # Otherwise, it's a literal or expression - interpolate variables
        return self._interpolate_variables_in_string(expr)
    
    def _interpolate_variables_in_string(self, text: str) -> str:
        """Replace $variable references in a string with their values."""
        def replacer(match):
            var_name = match.group(1)
            value = self.variables.get(var_name, f'${var_name}')
            # Format numbers nicely
            if isinstance(value, float):
                return f'{value:g}'
            return str(value)
        
        return re.sub(r'\$(\w+)', replacer, text)

