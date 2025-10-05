#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test to find the missing bracket."""

import re
from pg_translator import PGTranslator
import sys
sys.path.insert(0, '.')

# Get the raw HTML
translator = PGTranslator()
result = translator.translate('webwork_ps1_pg/ps1-prob08.pg', seed=1234)

print("="*70)
print("RAW HTML:")
print("="*70)
print(result.statement_html)
print()

# Now process it through our functions


def strip_html(html_text):
    """Remove HTML tags for terminal display."""
    # Unescape LaTeX delimiters that were escaped for HTML
    html_text = html_text.replace('\\\\(', '\\(')
    html_text = html_text.replace('\\\\)', '\\)')
    html_text = html_text.replace('\\\\[', '\\[')
    html_text = html_text.replace('\\\\]', '\\]')

    print("After unescape:")
    print(repr(html_text))
    print()

    # Clean up LaTeX placeholder notation
    html_text = re.sub(r'\[[^\].]*\\_[^\].]*\]', '___', html_text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_text)

    print("After HTML removal:")
    print(repr(text))
    print()

    # Decode common HTML entities
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ')
    # Clean up multiple spaces and newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


text = strip_html(result.statement_html)
print("="*70)
print("AFTER strip_html:")
print("="*70)
print(repr(text))
print()
print(text)
