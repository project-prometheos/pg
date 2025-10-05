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

            # Check for do { ... } until (condition) loops
            do_until_match = re.match(r'^\s*do\s*\{', original_line)
            if do_until_match:
                # Collect the do-until block
                block_lines = [original_line]
                brace_depth = 1  # We've seen the opening {
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
                        transformed = self._transform_line(line.rstrip())
                        if transformed:
                            transformed_body.append('    ' + transformed)

                    # Generate Python while loop: while not (condition):
                    output_lines.append(f'while not ({condition}):')
                    output_lines.extend(transformed_body)

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

        # Transform Perl scalar variables: $var → var
        # Use negative lookbehind to avoid matching in strings
        line = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'\1', line)

        # Transform Perl method call operator: -> → .
        # Special case: ->with( becomes .with_params( to avoid Python keyword
        line = line.replace('->with(', '.with_params(')
        line = line.replace('->', '.')

        # Transform Perl namespace separator: Package::Function → Package.Function
        line = re.sub(
            r'([a-zA-Z_][a-zA-Z0-9_]*)::([a-zA-Z_][a-zA-Z0-9_]*)', r'\1.\2', line)

        # Transform Perl string concatenation operator: ' . ' → ' + '
        # Only when surrounded by spaces or between string literals/variables
        # Match: 'str' . 'str' or var . 'str' or 'str' . var
        line = re.sub(r'(\)|\'|\"|\w)\s+\.\s+(\(|\'|\"|\w)', r'\1 + \2', line)

        # Transform Perl fat comma (hash key-value): key => value → key = value
        # BUT: avoid converting when it's part of array/list syntax like ] => [
        # Only convert when it's clearly a named parameter: word => value
        if '] =>' not in line and '} =>' not in line:
            line = re.sub(r'\b(\w+)\s*=>\s*', r'\1 = ', line)

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
