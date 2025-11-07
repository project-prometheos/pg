"""
PG Preprocessor - Transform PG syntactic sugar.

Handles:
- BEGIN_TEXT...END_TEXT → text accumulation
- BEGIN_PGML...END_PGML → PGML rendering
- BEGIN_SOLUTION...END_SOLUTION → solution text
- BEGIN_HINT...END_HINT → hint text
- Comment removal
- Backslash handling

Reference: Translator.pm::default_preprocess_code() (lines 1348-1378)
"""

import re
from dataclasses import dataclass

from .pgml_parser import PGMLParser, PGMLRenderer


@dataclass
class PreprocessResult:
    """Result of preprocessing a PG file."""

    code: str
    """Preprocessed Python code"""

    text_blocks: list[tuple[str, str]]
    """List of (block_type, content) for TEXT, PGML, SOLUTION, HINT blocks"""

    line_map: dict[int, int]
    """Map from preprocessed line number to original line number"""


class PGPreprocessor:
    """
    Preprocess PG files to transform syntactic sugar into executable Python.

    PG files use Perl-like syntax with special blocks:
    - BEGIN_TEXT...END_TEXT: Problem statement
    - BEGIN_PGML...END_PGML: PGML markup
    - BEGIN_SOLUTION...END_SOLUTION: Solution text
    - BEGIN_HINT...END_HINT: Hint text

    This preprocessor transforms these into Python function calls that
    accumulate text in the execution environment.
    """

    # Block markers
    BLOCK_PATTERNS = {
        "TEXT": (r"BEGIN_TEXT\s*$", r"^END_TEXT"),
        "PGML": (r"BEGIN_PGML\s*$", r"^END_PGML"),
        "SOLUTION": (r"BEGIN_SOLUTION\s*$", r"^END_SOLUTION"),
        "HINT": (r"BEGIN_HINT\s*$", r"^END_HINT"),
        "PGML_SOLUTION": (r"BEGIN_PGML_SOLUTION\s*$", r"^END_PGML_SOLUTION"),
        "PGML_HINT": (r"BEGIN_PGML_HINT\s*$", r"^END_PGML_HINT"),
    }

    def preprocess(self, pg_source: str, use_sandbox_macros: bool = True) -> PreprocessResult:
        """
        Preprocess PG source code.

        Args:
            pg_source: Raw PG file content
            use_sandbox_macros: If True, skip generating imports (sandbox provides them)

        Returns:
            PreprocessResult with transformed code and metadata
        """
        lines = pg_source.split("\n")
        output_lines: list[str] = []
        text_blocks: list[tuple[str, str]] = []
        line_map: dict[int, int] = {}

        # First pass: collect all loadMacros() calls to generate imports
        import_lines: list[str] = []
        loaded_macros_comment = None

        if not use_sandbox_macros:
            # Generate imports only if not using sandbox macros
            for line in lines:
                if "loadMacros" in line:
                    # Extract macro file names
                    match = re.search(r'loadMacros\((.*?)\)', line, re.DOTALL)
                    if match:
                        imports, comment = self._transform_load_macros(
                            match.group(1))
                        import_lines.extend(imports)
                        loaded_macros_comment = comment

        # Track if we've inserted imports yet
        imports_inserted = False

        # Track if we're inside a multiline loadMacros() call
        in_load_macros = False
        paren_depth = 0

        i = 0
        while i < len(lines):
            original_line = lines[i]

            # Join multi-line continuations (Perl allows implicit continuations)
            # If line ends with = or , and next line is indented, join them
            # Skip this for comment lines
            is_comment = original_line.lstrip(' \t').startswith('#')
            if not is_comment:
                while i + 1 < len(lines):
                    stripped = original_line.rstrip()
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""

                    # Don't join if next line is a comment
                    if next_line.lstrip(' \t').startswith('#'):
                        break

                    # Check if this looks like a continuation
                    should_join = False

                    # Case 1: Line ends with = or , or ( or [
                    if stripped and stripped[-1] in '=,([':
                        if next_line and next_line[0] in ' \t':
                            should_join = True

                    # Case 2: Unmatched parentheses/brackets
                    if not should_join:
                        open_count = stripped.count('(') + stripped.count('[') + stripped.count('{')
                        close_count = stripped.count(')') + stripped.count(']') + stripped.count('}')
                        if open_count > close_count:
                            should_join = True

                    if should_join and next_line.strip():
                        # Join the lines (preserve comment markers with lstrip(' \t'))
                        original_line = original_line.rstrip() + ' ' + next_line.lstrip(' \t')
                        i += 1
                    else:
                        break

            output_line_num = len(output_lines) + 1

            # Track line mapping
            line_map[output_line_num] = i + 1

            # Handle compound statements (e.g., DOCUMENT(); loadMacros(...); TEXT(...))
            # Split by semicolon but preserve the parts that aren't loadMacros
            if ';' in original_line and 'loadMacros' in original_line:
                parts = original_line.split(';')
                non_loadmacros_parts = []
                skip_rest_of_line = False

                for part in parts:
                    part = part.strip()
                    if 'loadMacros' in part:
                        # Check if this is a complete loadMacros call or start of multi-line
                        if '(' in part and part.count('(') == part.count(')'):
                            # Complete on this part, skip it
                            continue
                        else:
                            # Multi-line loadMacros starts here
                            in_load_macros = True
                            paren_depth = part.count('(') - part.count(')')
                            skip_rest_of_line = True
                            break
                    else:
                        # Keep non-loadMacros parts
                        if part:
                            non_loadmacros_parts.append(part)

                # If we have non-loadMacros parts, output them
                if non_loadmacros_parts:
                    combined = '; '.join(non_loadmacros_parts)
                    if combined:
                        # Process the combined line through normal transformation
                        transformed = self._transform_line(combined)
                        output_lines.append(transformed)

                i += 1
                continue

            # Check if we're entering a standalone loadMacros() call
            if 'loadMacros' in original_line and '(' in original_line:
                in_load_macros = True
                # Count opening and closing parens on this line
                paren_depth = original_line.count(
                    '(') - original_line.count(')')

                # If balanced on same line, skip it and move on
                if paren_depth == 0:
                    in_load_macros = False
                    i += 1
                    continue
                else:
                    # Multi-line loadMacros - skip this line and continue tracking
                    i += 1
                    continue

            # If we're inside a loadMacros() call, track parentheses
            if in_load_macros:
                paren_depth += original_line.count('(') - \
                    original_line.count(')')
                if paren_depth <= 0:
                    # End of loadMacros() call
                    in_load_macros = False
                i += 1
                continue

            # Check if this is DOCUMENT() - insert imports right after it (if needed)
            if not imports_inserted and re.match(r'^\s*DOCUMENT\(\s*\)', original_line):
                # Handle compound statements like: DOCUMENT(); loadMacros(...); TEXT(...)
                # Split by semicolon and process each part
                if ';' in original_line:
                    parts = original_line.split(';')
                    for part in parts:
                        part = part.strip()
                        if not part:
                            continue
                        # Skip loadMacros parts (macros pre-loaded in sandbox)
                        if 'loadMacros' in part:
                            continue
                        # Transform and add other parts
                        if part:
                            transformed = self._transform_line(part)
                            if transformed:
                                output_lines.append(transformed)
                else:
                    output_lines.append(original_line)

                # Insert imports after DOCUMENT() only if not using sandbox
                if import_lines:
                    output_lines.append("")  # Blank line
                    output_lines.extend(import_lines)
                    if loaded_macros_comment:
                        output_lines.append(loaded_macros_comment)
                    output_lines.append("")  # Blank line
                imports_inserted = True
                i += 1
                continue

            # Check for Perl closures: sub { ... } - stub them out
            # These are typically used for custom answer checkers
            # Example: checker => sub { ... }
            sub_match = re.search(r'(=>|=)\s*sub\s*\{', original_line)
            if sub_match:
                # Found start of a sub {} closure
                # Track brace depth to find the end
                closure_start_idx = i
                closure_lines = [original_line]
                brace_depth = original_line.count('{') - original_line.count('}')

                # Collect all lines of the closure
                i += 1
                while i < len(lines) and brace_depth > 0:
                    current_line = lines[i]
                    closure_lines.append(current_line)
                    brace_depth += current_line.count('{') - current_line.count('}')
                    i += 1

                # Now replace the entire sub { ... } with lambda: None
                first_line = closure_lines[0]

                # Check if this is part of a function parameter (key => sub { ... })
                param_match = re.search(r'(\w+)\s*=>\s*sub\s*\{', first_line)
                if param_match:
                    param_name = param_match.group(1)
                    # Find where the sub starts
                    sub_start = first_line.find('sub')
                    # Keep everything before 'sub'
                    prefix = first_line[:sub_start]
                    # Replace sub { ... } with lambda: None
                    # Check if there's more content after the closure on the last line
                    last_line = closure_lines[-1] if closure_lines else ""

                    # Find the closing } and any suffix
                    suffix = ""
                    close_brace_match = re.search(r'\}(.*)$', last_line)
                    if close_brace_match:
                        suffix = close_brace_match.group(1)

                    # Create the stubbed line and transform it
                    stubbed_line = f"{prefix}lambda *args, **kwargs: None{suffix}"
                    transformed = self._transform_line(stubbed_line)
                    output_lines.append(f"{transformed}  # Stubbed Perl closure")
                else:
                    # Assignment form: $var = sub { ... }
                    assign_match = re.search(r'(\w+)\s*=\s*sub\s*\{', first_line)
                    if assign_match:
                        var_name = assign_match.group(1)
                        indent = re.match(r'^(\s*)', first_line).group(1)
                        stubbed_line = f"{indent}{var_name} = lambda *args, **kwargs: None"
                        transformed = self._transform_line(stubbed_line)
                        output_lines.append(f"{transformed}  # Stubbed Perl closure")
                    else:
                        # Unknown form, comment it out
                        output_lines.append(
                            f"# {first_line}  # Skipped Perl closure")

                continue

            # Check for do { ... } until (condition) loops
            do_until_match = re.match(r'^\s*do\s*\{', original_line)
            if do_until_match:
                # Check if this is a single-line do-until
                single_line_until = re.search(
                    r'\}\s*until\s*\(([^)]+)\)', original_line)

                if single_line_until:
                    # Single-line do-until: do { body } until (condition)
                    condition = single_line_until.group(1)

                    # Transform condition
                    condition = self._transform_line(condition)

                    # Extract body between { and }
                    body_match = re.search(r'do\s*\{([^}]+)\}', original_line)
                    if body_match:
                        body = body_match.group(1).strip()
                        transformed_body = self._transform_line(body)

                        # Generate Python while loop with post-test
                        # Perl: do {...} until (condition) means repeat until condition is TRUE
                        output_lines.append(f'while True:')
                        output_lines.append(f'    {transformed_body}')
                        output_lines.append(f'    if ({condition}):')
                        output_lines.append(f'        break')

                        i += 1
                        continue

                # Multi-line do-until: collect the block
                block_lines = [original_line]
                brace_depth = original_line.count(
                    '{') - original_line.count('}')
                i += 1

                # Collect lines until we find the matching }
                while i < len(lines) and brace_depth > 0:
                    line = lines[i]
                    block_lines.append(line)
                    brace_depth += line.count('{') - line.count('}')
                    i += 1

                # Now check if the last line has "until (condition)"
                last_line = block_lines[-1] if block_lines else ""
                until_match = re.search(r'\}\s*until\s*\(([^)]+)\)', last_line)

                if until_match:
                    condition = until_match.group(1)

                    # Transform condition (convert Perl operators)
                    condition = self._transform_line(condition)

                    # Extract the body (everything between do { and } until)
                    body_lines = []
                    # First line: remove "do {"
                    first = block_lines[0].replace(
                        'do', '').replace('{', '').strip()
                    if first:
                        body_lines.append(first)

                    # Middle lines: add as-is
                    for line in block_lines[1:-1]:
                        body_lines.append(line)

                    # Last line: remove "} until (...)"
                    last = re.sub(
                        r'\}\s*until\s*\([^)]+\)', '', block_lines[-1]).strip()
                    if last:
                        body_lines.append(last)

                    # Transform body lines
                    transformed_body = []
                    for line in body_lines:
                        # Strip existing indentation and transform
                        stripped_line = line.lstrip()
                        transformed = self._transform_line(
                            stripped_line.rstrip())
                        if transformed:
                            # Add consistent 4-space indentation
                            transformed_body.append('    ' + transformed)

                    # Generate Python while loop with post-test (like do-until)
                    # Perl: do {...} until (condition) means repeat until condition is TRUE
                    # Python: while True: ... if (condition): break
                    output_lines.append('while True:')
                    output_lines.extend(transformed_body)
                    output_lines.append(f'    if ({condition}):')
                    output_lines.append(f'        break')

                    continue
                else:
                    # Not a proper do-until, fall through to normal processing
                    i = i - len(block_lines) + 1

            # Check for block markers
            block_found = False
            for block_type, (begin_pattern, end_pattern) in self.BLOCK_PATTERNS.items():
                if re.search(begin_pattern, original_line):
                    # Found block start
                    block_content_lines: list[str] = []
                    i += 1  # Move past BEGIN line

                    # Collect block content until END marker
                    while i < len(lines):
                        if re.match(end_pattern, lines[i]):
                            break
                        block_content_lines.append(lines[i])
                        i += 1

                    # Join content
                    block_content = "\n".join(block_content_lines)

                    # Store block
                    text_blocks.append((block_type, block_content))

                    # Generate Python code for this block
                    if "PGML" in block_type:
                        # PGML blocks - render at runtime with context
                        # Store the PGML content and render it during execution
                        # BUT FIRST: Transform Perl syntax to Python in evaluator expressions
                        block_content = self._transform_pgml_evaluators(
                            block_content)

                        block_var = f"pgml_block_{len(text_blocks) - 1}"
                        escaped_content = self._escape_triple_quotes(
                            block_content)
                        output_lines.append(
                            f"{block_var} = '''\\n{escaped_content}\\n'''"
                        )
                        # Call PGML renderer (will be available in sandbox)
                        if "SOLUTION" in block_type:
                            output_lines.append(f"SOLUTION(PGML({block_var}))")
                        elif "HINT" in block_type:
                            output_lines.append(f"HINT(PGML({block_var}))")
                        else:
                            output_lines.append(f"TEXT(PGML({block_var}))")
                    else:
                        # Plain TEXT blocks - convert to TEXT() calls
                        transformed_content = self._transform_text_block(
                            block_content)
                        if "SOLUTION" in block_type:
                            output_lines.append(
                                f"SOLUTION({transformed_content})")
                        elif "HINT" in block_type:
                            output_lines.append(f"HINT({transformed_content})")
                        else:
                            output_lines.append(f"TEXT({transformed_content})")

                    block_found = True
                    break

            if not block_found:
                # Check if line contains do { } until/while mid-line (after semicolon)
                if re.search(r'do\s*\{[^}]*\}\s*(until|while)\s+', original_line):
                    # Split by semicolon, process do-until separately
                    parts = original_line.split(';')
                    for part_idx, part in enumerate(parts):
                        part = part.strip()
                        if not part:
                            continue

                        # Check if this part has do-until/do-while
                        do_match = re.match(r'do\s*\{([^}]+)\}\s*(until|while)\s+(.+)', part)
                        if do_match:
                            body = do_match.group(1).strip()
                            loop_type = do_match.group(2)
                            condition = do_match.group(3).strip()

                            # Transform body and condition
                            transformed_body = self._transform_line(body)
                            transformed_condition = self._transform_line(condition)

                            # Generate while True loop with break
                            output_lines.append('while True:')
                            output_lines.append(f'    {transformed_body}')
                            if loop_type == 'until':
                                # until COND means: break if COND is true
                                output_lines.append(f'    if ({transformed_condition}):')
                            else:  # while
                                # while COND means: break if COND is false
                                output_lines.append(f'    if not ({transformed_condition}):')
                            output_lines.append(f'        break')
                        else:
                            # Regular part - transform normally
                            transformed = self._transform_line(part)
                            if transformed:
                                output_lines.append(transformed)
                else:
                    # Regular line - pass through with transformations
                    transformed = self._transform_line(original_line)
                    output_lines.append(transformed)

            i += 1

        code = "\n".join(output_lines)
        return PreprocessResult(code=code, text_blocks=text_blocks, line_map=line_map)

    def _transform_line(self, line: str) -> str:
        """
        Transform a single line of PG code.

        Handles:
        - loadMacros() → skip (handled in first pass)
        - Perl variable syntax: $var → var
        - Array syntax: @array → array
        - Hash access: $hash{key} → hash['key']
        - Comment removal (# comments)
        - Semicolon removal (optional in Python)
        """
        import re

        # Skip loadMacros() - already handled in first pass
        if 'loadMacros' in line:
            # If it's on the same line as other code, remove just the loadMacros call
            if ';' in line:
                # Split by semicolon, remove loadMacros parts
                parts = line.split(';')
                cleaned_parts = [p for p in parts if 'loadMacros' not in p]
                if cleaned_parts:
                    line = ';'.join(cleaned_parts).strip()
                    if not line:
                        return ""
                else:
                    return ""
            else:
                # Entire line is loadMacros
                return ""

        # Handle DOCUMENT() and ENDDOCUMENT() - keep as-is
        if re.match(r'^\s*(DOCUMENT|ENDDOCUMENT)\(\s*\)', line):
            return line

        # Transform hash access: $hash{key} → hash['key']
        # Match $var{...} and convert to var['...']
        line = re.sub(
            r'\$([a-zA-Z_][a-zA-Z0-9_]*)\{([^}]+)\}', r"\1['\2']", line)

        # Transform Perl array variables: @array → array
        line = re.sub(r'@([a-zA-Z_][a-zA-Z0-9_]*)', r'\1', line)

        # Transform Perl string interpolation: "$var text" → f"{var} text"
        # Find all double-quoted strings and convert those with $var to f-strings
        def convert_string_interpolation(match):
            quote_char = match.group(1)  # " or '
            content = match.group(2)

            # Only convert double-quoted strings (Perl interpolates these)
            if quote_char == '"':
                # Check if contains $var
                if '$' in content:
                    # Convert $var to {var}
                    new_content = re.sub(
                        r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'{\1}', content)
                    return f'f"{new_content}"'

            # Return as-is for single quotes or strings without variables
            return match.group(0)

        # Match strings carefully (handle escaped quotes)
        line = re.sub(r'(["\'])([^\1]*?)\1',
                      convert_string_interpolation, line)

        # Transform Perl scalar variables: $var → var (outside of strings now)
        # Use negative lookbehind to avoid matching in strings
        line = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'\1', line)

        # Transform Perl method call operator: -> → .
        # Special case: ->with( becomes .with_params( to avoid Python keyword
        line = line.replace('->with(', '.with_params(')
        line = line.replace('->', '.')

        # Transform Perl string comparison operators (must be done carefully)
        # eq → == (string equality)
        # ne → != (string inequality)
        # lt → < (less than)
        # gt → > (greater than)
        # le → <= (less than or equal)
        # ge → >= (greater than or equal)
        # Use word boundaries to avoid matching inside identifiers
        line = re.sub(r'\beq\b', '==', line)
        line = re.sub(r'\bne\b', '!=', line)
        line = re.sub(r'\blt\b', '<', line)
        line = re.sub(r'\bgt\b', '>', line)
        line = re.sub(r'\ble\b', '<=', line)
        line = re.sub(r'\bge\b', '>=', line)

        # Transform Perl namespace separator: Package::Function → Package.Function
        line = re.sub(
            r'([a-zA-Z_][a-zA-Z0-9_]*)::([a-zA-Z_][a-zA-Z0-9_]*)', r'\1.\2', line)

        # Transform Perl string concatenation operator: ' . ' → ' + '
        # Only when surrounded by spaces or between string literals/variables
        # Match: 'str' . 'str' or var . 'str' or 'str' . var
        line = re.sub(r'(\)|\'|\"|\w)\s+\.\s+(\(|\'|\"|\w)', r'\1 + \2', line)

        # Note: do-while/do-until loops are handled in main preprocess loop
        # to allow multi-line output

        # Transform Perl map with blocks: map { EXPR } LIST
        # map { random(1, 10) } 0 .. 7  →  [random(1, 10) for _ in range(0, 8)]
        map_match = re.search(r'\bmap\s*\{\s*([^}]+)\}\s+(\d+)\s*\.\.\s*(\d+)', line)
        if map_match:
            expr = map_match.group(1).strip()
            start = int(map_match.group(2))
            end = int(map_match.group(3))
            # Python range is exclusive on the right, Perl .. is inclusive
            replacement = f'[{expr} for _ in range({start}, {end}+1)]'
            line = line[:map_match.start()] + replacement + line[map_match.end():]

        # Transform Perl range operator: START .. END → range(START, END+1)
        # But only if not already handled by map
        if '..' in line and 'range(' not in line:
            line = re.sub(r'(\d+)\s*\.\.\s*(\d+)', lambda m: f'range({m.group(1)}, {int(m.group(2))+1})', line)

        # Transform Perl unless → if not
        line = re.sub(r'\bunless\s+', 'if not ', line)

        # Transform Perl statement modifiers: STATEMENT if/unless CONDITION
        # statement if condition → if condition: statement
        # statement unless condition → if not condition: statement
        # But be careful not to transform regular if/elsif/else blocks
        if re.search(r'\S+.*\s+(if|unless)\s+\S+', line) and not re.match(r'^\s*(if|elsif|else|unless)', line):
            # Check if this is a statement modifier (not a block if)
            # Statement modifiers don't have colons or blocks after them
            match = re.search(r'^(\s*)(.+?)\s+(if|unless)\s+(.+)$', line)
            if match and '{' not in match.group(2):  # No block in statement
                indent = match.group(1)
                statement = match.group(2).strip()
                modifier = match.group(3)
                condition = match.group(4).strip()

                if modifier == 'if':
                    line = f"{indent}if {condition}: {statement}"
                else:  # unless
                    line = f"{indent}if not ({condition}): {statement}"

        # Transform Perl fat comma (hash key-value): key => value
        # Context-aware conversion:
        # - Inside { ... }: key => value → key: value (Python dict)
        # - In function args: key => value → key = value (named parameter)
        # Avoid array refs: ] => [

        if '] =>' not in line and '} =>' not in line:
            # Strategy: Find all occurrences of => and determine context
            # by checking if we're inside curly braces
            result = []
            i = 0
            brace_depth = 0
            paren_depth = 0

            while i < len(line):
                ch = line[i]

                # Track brace/paren depth
                if ch == '{':
                    brace_depth += 1
                elif ch == '}':
                    brace_depth -= 1
                elif ch == '(':
                    paren_depth += 1
                elif ch == ')':
                    paren_depth -= 1

                # Check for =>
                if i < len(line) - 1 and line[i:i+2] == '=>':
                    # Decide what to replace with based on context
                    if brace_depth > 0:
                        # Inside braces: use colon for dict
                        result.append(':')
                    else:
                        # Outside braces (function params): use equals
                        result.append(' =')
                    i += 2  # Skip both characters
                else:
                    result.append(ch)
                    i += 1

            line = ''.join(result)

        # Remove trailing semicolons (optional in Python)
        line = re.sub(r';\s*$', '', line)

        # Pass through - Python handles # comments same as Perl/PG
        return line

    def _transform_text_block(self, content: str) -> str:
        r"""
        Transform TEXT block content to Python expression(s).

        Handles:
        - Variable interpolation: $a → ", a, "
        - Function calls: \{ ans_rule(20) \} → ", ans_rule(20), "
        - LaTeX math: \( ... \) → keep as-is
        - Special vars: $PAR → ", PAR(), "

        Returns:
            Python expression string suitable for TEXT() call
        """
        import re

        # Split content into segments: text, $var, \{...}
        segments = []
        pos = 0

        while pos < len(content):
            # Look for $var or \{...}
            var_match = re.search(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', content[pos:])
            func_match = re.search(r'\\{([^}]+)\\}', content[pos:])

            # Find which comes first
            next_var_pos = pos + var_match.start() if var_match else len(content)
            next_func_pos = pos + func_match.start() if func_match else len(content)

            if next_var_pos < next_func_pos:
                # Variable comes first
                # Add text before variable
                if next_var_pos > pos:
                    text_segment = content[pos:next_var_pos]
                    segments.append(repr(text_segment))

                # Add variable
                var_name = var_match.group(1)
                # Check if it's a known macro function
                if var_name in ('PAR', 'BR', 'BBOLD', 'EBOLD', 'BITALIC', 'EITALIC', 'BCENTER', 'ECENTER', 'BUL', 'EUL'):
                    segments.append(f"{var_name}()")
                else:
                    segments.append(f"str({var_name})")

                pos = next_var_pos + len(var_match.group(0))

            elif next_func_pos < len(content):
                # Function call comes first
                # Add text before function
                if next_func_pos > pos:
                    text_segment = content[pos:next_func_pos]
                    segments.append(repr(text_segment))

                # Add function call
                func_code = func_match.group(1).strip()
                segments.append(func_code)

                pos = next_func_pos + len(func_match.group(0))

            else:
                # No more variables or functions - add remaining text
                if pos < len(content):
                    text_segment = content[pos:]
                    segments.append(repr(text_segment))
                break

        # Join segments with commas for TEXT() call
        if not segments:
            return '""'

        return ", ".join(segments)

    def _escape_triple_quotes(self, text: str) -> str:
        """Escape special characters in text for Python string literals."""
        # Escape backslashes first (before escaping quotes)
        text = text.replace("\\", "\\\\")
        # Then escape triple quotes
        text = text.replace("'''", r"\'\'\'")
        text = text.replace('"""', r'\"\"\"')
        return text

    def _transform_pgml_evaluators(self, pgml_content: str) -> str:
        """
        Transform Perl syntax to Python in PGML evaluator expressions.

        PGML allows inline evaluators like: [_]{$answer->cmp()}
        We need to convert Perl method calls (->)  to Python (.).

        Args:
            pgml_content: PGML markup text

        Returns:
            Transformed PGML with Python syntax in evaluator expressions
        """
        import re

        # Pattern to match {$var->method(...)} or {$var.method(...)}
        # We want to convert -> to . inside {...} that comes after [_]
        # Use a more careful approach: find all {code} blocks and transform them

        result = []
        i = 0
        while i < len(pgml_content):
            # Look for { that might start an evaluator
            if pgml_content[i] == '{':
                # Find the matching closing brace
                brace_depth = 1
                j = i + 1
                while j < len(pgml_content) and brace_depth > 0:
                    if pgml_content[j] == '{':
                        brace_depth += 1
                    elif pgml_content[j] == '}':
                        brace_depth -= 1
                    j += 1

                if brace_depth == 0:
                    # Found matching closing brace
                    code_block = pgml_content[i+1:j-1]

                    # Transform Perl syntax to Python
                    # Convert -> to .
                    transformed = code_block.replace('->', '.')
                    # Remove Perl $ sigils from variables (keep $ in $$ for LaTeX)
                    transformed = re.sub(
                        r'\$([a-zA-Z_]\w*)', r'\1', transformed)

                    result.append('{')
                    result.append(transformed)
                    result.append('}')
                    i = j
                    continue

            result.append(pgml_content[i])
            i += 1

        return ''.join(result)

    def _transform_load_macros(self, macro_list_str: str) -> tuple[list[str], str]:
        """
        Transform loadMacros() call to Python imports.

        Args:
            macro_list_str: The content inside loadMacros(...), e.g., '"PG.pl", "PGML.pl"'

        Returns:
            Tuple of (import_lines, comment)

        Example:
            Input: '"PGstandard.pl", "MathObjects.pl", "PGML.pl"'
            Output: (['from pg_macros.core.pg_core import *', ...],
                    '# loadMacros("PGstandard.pl", "MathObjects.pl", "PGML.pl") - loaded')
        """
        import re

        # Extract quoted strings
        macros = re.findall(r'["\']([^"\']+)["\']', macro_list_str)

        # Mapping of .pl files to Python imports
        macro_imports = {
            "PG.pl": "from pg_macros.core.pg_core import DOCUMENT, TEXT, ANS, ENDDOCUMENT, SOLUTION, HINT",
            "PGstandard.pl": "from pg_macros.answers.pg_answer_macros import num_cmp, str_cmp, fun_cmp",
            "PGbasicmacros.pl": "from pg_macros.core.pg_basic_macros import ans_rule, beginproblem, PAR",
            "MathObjects.pl": "from pg_math import Context, Real, Complex, Formula, Interval",
            "PGML.pl": "from pg_pgml import PGML",
            "contextFraction.pl": "from pg_math import Fraction",
            "PGcourse.pl": "# PGcourse.pl - course-specific (skipped)",
        }

        # Generate import lines
        import_lines = []
        loaded_macros = []

        for macro in macros:
            if macro in macro_imports:
                import_line = macro_imports[macro]
                if not import_line.startswith("#"):
                    import_lines.append(import_line)
                loaded_macros.append(macro)

        # Create comment showing what was loaded
        comment = f'# loadMacros({", ".join(repr(m) for m in loaded_macros)}) - loaded' if loaded_macros else "# loadMacros() - no recognized macros"

        return (import_lines, comment)
