#!/usr/bin/env python3
import sys

file_path = r'd:\pg\packages\pg_translator\pg_translator\pg_preprocessor_pygment.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find and fix the specific lines
for i, line in enumerate(lines):
    # Line 850: Skip whitespace - add \n to the character class
    if i == 849 and "while list_start < len(text) and text[list_start] in ' \t':" in line:
        lines[i] = line.replace("' \t':", "' \t\n':")
        print(f"Fixed line 850")
    
    # Line 873: Change space check to include tab
    if i == 872 and "elif ch == ' ' and paren_depth == 0 and bracket_depth == 0:" in line:
        lines[i] = line.replace("ch == ' '", "ch in ' \t'")
        print(f"Fixed line 873")
    
    # Line 877: Change space check in while loop
    if i == 876 and "while list_end < len(text) and text[list_end] == ' ':" in line:
        lines[i] = line.replace("text[list_end] == ' '", "text[list_end] in ' \t\n'")
        print(f"Fixed line 877")

# Now add the newline handling before "list_end += 1"
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # Insert newline handling after the break at line 881
    if i == 880 and "break" in line and "elif ch ==" not in line:
        # Add the newline handling code
        indent = "                        "
        new_lines.append(f"{indent}elif ch == '\n' and paren_depth == 0 and bracket_depth == 0:\n")
        new_lines.append(f"{indent}    # For multi-line maps, skip newlines and continue\n")
        new_lines.append(f"{indent}    list_end += 1\n")
        new_lines.append(f"{indent}    while list_end < len(text) and text[list_end] in ' \t\n':\n")
        new_lines.append(f"{indent}        list_end += 1\n")
        new_lines.append(f"{indent}    continue\n")
        print(f"Added newline handling")

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("File updated successfully")
