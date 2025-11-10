import re

file_path = r'd:\pg\packages\pg_translator\pg_translator\pg_preprocessor_pygment.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find line 195-196 area and modify it
output_lines = []
for i, line in enumerate(lines):
    # Line 195 is where "if not is_comment:" is
    if i == 195 and "if not is_comment:" in line:
        output_lines.append(line)
        # Insert BEGIN block check before the next if statement
        indent = "                "
        output_lines.append(f"{indent}# Don't join lines if we're at a BEGIN_* block\n")
        output_lines.append(f"{indent}is_begin_block = re.match(r'^\s*(BEGIN_\w+)\s*$', original_line)\n")
        next_line = lines[i + 1]
        # Modify the next line's if statement
        if "if not re.match" in next_line:
            output_lines.append(f"{indent}if not is_begin_block and not re.match(r'^\s*\}}\s*else\s*\{{\s*$', original_line):\n")
            # Skip the original line
            i += 1
            continue
    else:
        output_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(output_lines)

print("File updated")
