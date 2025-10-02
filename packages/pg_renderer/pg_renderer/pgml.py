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
        
        # 1. Remove PGML table constructs (simplify for MVP)
        # These are advanced layout features: [# ... #] and [. ... .]
        html = self._simplify_tables(html)
        
        # 2. Display math FIRST (before variable interpolation): [`` ... ``] → KaTeX display math
        html = re.sub(r'\[``(.*?)``\]', r'$$\1$$', html, flags=re.DOTALL)
        
        # 3. Inline math: [` ... `] → KaTeX inline math
        html = re.sub(r'\[`(.*?)`\]', r'$\1$', html)
        
        # 4. Variable interpolation: [$var] (after math, so we don't break LaTeX)
        html = re.sub(r'\[\$(\w+)\]', self._interpolate_var, html)
        
        # 5. Answer blanks: [_____]{$answer} or [_]{$answer}
        html = re.sub(r'\[_+\]\{([^}]+)\}', self._create_answer_blank, html)
        
        # 6. Formatting → Markdown
        # Bold: [*text*] → **text**
        html = re.sub(r'\[\*(.*?)\*\]', r'**\1**', html)
        # Italic: [|text|] → *text*
        html = re.sub(r'\[\|(.*?)\|\]', r'*\1*', html)
        # Underline: [_text_] → __text__ (approximation)
        html = re.sub(r'\[_(.*?)_\]', r'__\1__', html)
        
        # 7. Lists (already Markdown with leading *) - nothing to do here
        
        # 8. Paragraphs: ensure double newlines between blocks (Markdown)
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
        # Remove table options like *{ padding => [...] }
        pgml = re.sub(r'\]\*\{[^}]+\}', ']', pgml)
        
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
        value = self.variables.get(var_name, f'${var_name}')
        
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
        """Evaluate answer expression."""
        # Remove $
        expr = expr.strip().lstrip('$')
        
        # Look up variable
        return self.variables.get(expr, expr)

