from pg_translator import PGTranslator
import re

t = PGTranslator()
r = t.translate('webwork_ps1_pg/ps1-prob01.pg', seed=1234)

html = r.statement_html
print("Original HTML (first 200 chars):")
print(repr(html[:200]))
print()

# Strip HTML
text = re.sub(r'<[^>]+>', '', html)
print("After stripping HTML:")
print(repr(text[:200]))
print()

# Check if we have \( pattern
if r'\(' in text:
    print("Found \\( pattern (escaped)")
else:
    print("No \\( pattern")

# Check actual pattern
if '\\(' in text:
    print("Found literal \\(")
    
# Try the replacement
text2 = text.replace('\\(', 'FOUND_IT')
print("\nAfter replace:")
print(text2[:200])
