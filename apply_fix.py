#!/usr/bin/env python3
# Quick fix to skip method-call style blocks in standalone block detection

import re

file_path = r'd:\pg\packages\pg_translator\pg_translator\pg_preprocessor_pygment.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace line 623
old_line = '                if re.search(begin_pattern, original_line):'
new_line = '                if re.search(begin_pattern, original_line) and not re.search(r\'\\$\\w+\\s*->\\s*(BEGIN_TIKZ|BEGIN_LATEX_IMAGE)\', original_line):'

if old_line in content:
    content = content.replace(old_line, new_line, 1)
    print(f"Replaced line")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("File updated successfully")
else:
    print("Pattern not found!")
