"""
Rewritten PG Preprocessor to use Pygments and Lark

This module exposes a `PGPreprocessor` class compatible with the original
interface. It retains the logic for processing BEGIN_TEXT/BEGIN_PGML/etc.
blocks and do‑until loops, but uses a combination of Pygments and a
Lark grammar to rewrite Perl‑like code into Python.  The primary
motivation is to replace the brittle regex based line transformations
with a more structured approach.

The high level flow of preprocessing is as follows:

1. Split the input into individual lines and maintain a mapping
   between output line numbers and original source line numbers.
2. Detect and extract special blocks (BEGIN_TEXT/BEGIN_PGML/etc.)
   using the same patterns as the original implementation.  These
   blocks are stored in the result object and replaced in the
   generated code with appropriate calls to TEXT(), PGML(),
   SOLUTION() or HINT() as before.
3. Any code that is not part of a special block is passed through
   a new `_compile_line` method which attempts to parse the line
   using a small Lark grammar.  If parsing succeeds, the AST is
   lowered into Python using helper functions.  If the parser
   raises an exception (for example because the line contains
   constructs outside of the grammar), the line is rewritten using
   a Pygments based fallback that performs conservative token
   replacements (sigil removal, `->`/`::` to `.`, hash indexing and
   fat comma handling).  Comments are preserved where possible.

4. The rewritten code is joined into a single Python string and
   returned along with the text blocks and line map.

The grammar implemented here covers a subset of the Perl syntax
commonly encountered in PG files: assignments, declarations, simple
function calls, and document control functions.  It is intentionally
permissive—unknown constructs are either passed through to the
fallback rewrite or emitted as comments in the generated code so that
information is never silently lost.

Note: This implementation assumes that the `lark` and `pygments`
packages are available.  If they are not installed, please install
them into your Python environment (for example via `pip install
lark==1.1.5 pygments==2.18.0`).

"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Tuple, Dict, Optional, Any

# Import Pygments for token aware rewriting
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

# Try importing Lark for structured parsing.  If unavailable (for example
# in restricted environments), fall back to a no‑op parser.  This
# allows the preprocessor to operate purely on the Pygments fallback
# without raising ImportError.
try:
    from lark import Lark, Transformer, v_args  # type: ignore[redefined-builtin]
    from lark.exceptions import LarkError  # type: ignore[misc]
    _LARK_AVAILABLE = True
except Exception:
    # Define dummy stand‑ins for the imported symbols
    _LARK_AVAILABLE = False
    class LarkError(Exception):
        pass
    def v_args(*args, **kwargs):
        def wrapper(func):
            return func
        return wrapper
    class Transformer:
        pass
    # The Lark class is defined later in PGPreprocessor.__init__ when not available
    Lark = None  # type: ignore[assignment]


@dataclass
class PreprocessResult:
    """Result of preprocessing a PG file."""

    code: str
    """Preprocessed Python code"""

    text_blocks: List[Tuple[str, str]]
    """List of (block_type, content) for TEXT, PGML, SOLUTION, HINT blocks"""

    line_map: Dict[int, int]
    """Map from preprocessed line number to original line number"""


class PGPreprocessor:
    """
    Preprocess PG files to transform syntactic sugar into executable Python.

    This reimplementation uses Pygments and a Lark grammar instead of
    large regular expressions.  The public API remains identical to
    the original: the `preprocess` method returns a
    :class:`PreprocessResult` containing the generated code, the
    extracted text blocks, and a map from output lines to original
    source lines.
    """

    # Block markers used to detect special PG sections
    BLOCK_PATTERNS = {
        "TEXT": (r"BEGIN_TEXT\s*$", r"^END_TEXT"),
        "PGML": (r"BEGIN_PGML\s*$", r"^END_PGML"),
        "SOLUTION": (r"BEGIN_SOLUTION\s*$", r"^END_SOLUTION"),
        "HINT": (r"BEGIN_HINT\s*$", r"^END_HINT"),
        "PGML_SOLUTION": (r"BEGIN_PGML_SOLUTION\s*$", r"^END_PGML_SOLUTION"),
        "PGML_HINT": (r"BEGIN_PGML_HINT\s*$", r"^END_PGML_HINT"),
        "TIKZ": (r"BEGIN_TIKZ\s*$", r"^END_TIKZ"),
    }

    def __init__(self) -> None:
        # Initialise Pygments lexer once
        self._perl_lexer = get_lexer_by_name("perl")
        # Attempt to prepare the Lark parser.  In restricted
        # environments where Lark is unavailable, the parser will be
        # left as None and the preprocessor will rely on manual
        # pattern matching and the Pygments fallback exclusively.
        if _LARK_AVAILABLE:
            # Use the Earley parser for our grammar to avoid reduce/reduce
            # conflicts that arise when calls appear both as statements and
            # as subexpressions.  The Earley parser is slower but more
            # forgiving for the relatively small code fragments we parse
            # here.  We still enable propagate_positions so that line
            # mapping works when we lower expressions via Lark.
            self._parser = Lark(
                self._grammar(),
                start="start",
                parser="earley",
                maybe_placeholders=True,
                propagate_positions=True,
            )
            self._transformer = self._make_transformer()
        else:
            self._parser = None
            self._transformer = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def preprocess(self, pg_source: str, use_sandbox_macros: bool = True) -> PreprocessResult:
        """
        Preprocess PG source code.

        Args:
            pg_source: Raw PG file content
            use_sandbox_macros: If True, skip generating imports (sandbox provides them)

        Returns:
            PreprocessResult with transformed code and metadata
        """
        # Convert Perl heredocs (<<END_MARKER) to Python syntax BEFORE splitting into lines
        pg_source = self._convert_heredocs_global(pg_source)
        
        lines = pg_source.split("\n")
        output_lines: List[str] = []
        text_blocks: List[Tuple[str, str]] = []
        line_map: Dict[int, int] = {}

        # Collect import lines from loadMacros when not using sandbox macros
        import_lines: List[str] = []
        loaded_macros_comment: Optional[str] = None
        if not use_sandbox_macros:
            for line in lines:
                if "loadMacros" in line:
                    match = re.search(r'loadMacros\((.*?)\)', line, re.DOTALL)
                    if match:
                        imports, comment = self._transform_load_macros(match.group(1))
                        import_lines.extend(imports)
                        loaded_macros_comment = comment

        imports_inserted = False
        in_load_macros = False
        paren_depth = 0

        i = 0
        while i < len(lines):
            original_line = lines[i]
            line_start_index = i


            # Join Perl-style implicit continuations to make downstream parsing easier
            is_comment = original_line.lstrip(' \t').startswith('#')
            if not is_comment:
                if not re.match(r'^\s*\}\s*else\s*\{\s*$', original_line):
                    while i + 1 < len(lines):
                        stripped = original_line.rstrip()
                        next_line = lines[i + 1]

                        # Stop joining if the next line is a comment or a } else { boundary
                        if next_line.lstrip(' \t').startswith('#'):
                            break
                        if re.match(r'^\s*\}\s*else\s*\{\s*$', next_line):
                            break

                        should_join = False
                        stripped_no_comment = self._strip_inline_comment(stripped)
                        # Don't join if the line ends with a semicolon (complete statement)
                        if stripped_no_comment and stripped_no_comment[-1] == ';':
                            should_join = False
                        elif stripped_no_comment and stripped_no_comment[-1] in '=,([':
                            if next_line and next_line[0] in ' \t':
                                should_join = True

                        if not should_join:
                            next_stripped = next_line.lstrip(' \t')
                            if next_stripped and next_stripped[0] in '.+-':
                                if next_stripped[0] == '.' or (
                                    next_stripped[0] in '+-'
                                    and len(next_stripped) > 1
                                    and next_stripped[1] in ' \t"\''
                                ):
                                    should_join = True

                        if not should_join:
                            next_stripped = next_line.lstrip(' \t')
                            if next_stripped and next_stripped.startswith('->'):
                                should_join = True

                        if not should_join:
                            check_line = self._strip_inline_comment(stripped)
                            # Account for $# operator which shouldn't affect paren counting
                            # Replace $#name with a placeholder
                            check_line_adjusted = re.sub(r'\$#\w+', '_placeholder_', check_line)
                            open_count = (
                                check_line_adjusted.count('(')
                                + check_line_adjusted.count('[')
                                + check_line_adjusted.count('{')
                            )
                            close_count = (
                                check_line_adjusted.count(')')
                                + check_line_adjusted.count(']')
                                + check_line_adjusted.count('}')
                            )
                            if open_count > close_count:
                                should_join = True

                        if should_join and next_line.strip():
                            line_without_comment = self._strip_inline_comment(
                                original_line.rstrip()
                            )
                            original_line = (
                                line_without_comment + ' ' + next_line.lstrip(' \t')
                            )
                            i += 1
                        else:
                            break

            output_line_num = len(output_lines) + 1
            line_map[output_line_num] = line_start_index + 1

            # Convert map/grep blocks to Python list comprehensions BEFORE parsing
            original_line = self._convert_map_grep_blocks(original_line)

            # Handle compound lines with loadMacros
            if ';' in original_line and 'loadMacros' in original_line:
                parts = original_line.split(';')
                non_loadmacros_parts: List[str] = []
                for part in parts:
                    part = part.strip()
                    if 'loadMacros' in part:
                        # Determine if this loadMacros is complete on one line
                        if '(' in part and part.count('(') == part.count(')'):
                            # Single line loadMacros: skip it
                            continue
                        else:
                            # Multi line loadMacros: start skipping
                            in_load_macros = True
                            paren_depth = part.count('(') - part.count(')')
                            break
                    else:
                        if part:
                            non_loadmacros_parts.append(part)
                if non_loadmacros_parts:
                    combined = '; '.join(non_loadmacros_parts)
                    if combined:
                        compiled_lines = self._compile_line(combined)
                        output_lines.extend(compiled_lines)
                i += 1
                continue

            # Standalone loadMacros start
            if 'loadMacros' in original_line and '(' in original_line and not in_load_macros:
                in_load_macros = True
                paren_depth = original_line.count('(') - original_line.count(')')
                if paren_depth == 0:
                    in_load_macros = False
                i += 1
                continue

            # If inside loadMacros, skip lines until parens balanced
            if in_load_macros:
                paren_depth += original_line.count('(') - original_line.count(')')
                if paren_depth <= 0:
                    in_load_macros = False
                i += 1
                continue

            # Insert imports after DOCUMENT()
            if not imports_inserted and re.match(r'^\s*DOCUMENT\(\s*\)', original_line):
                # Split multiple statements by semicolon and handle individually
                if ';' in original_line:
                    parts = [p.strip() for p in original_line.split(';') if p.strip()]
                    for part in parts:
                        if 'loadMacros' in part:
                            continue
                        compiled_lines = self._compile_line(part)
                        output_lines.extend(compiled_lines)
                else:
                    compiled_lines = self._compile_line(original_line)
                    output_lines.extend(compiled_lines)
                if import_lines:
                    output_lines.append("")
                    output_lines.extend(import_lines)
                    if loaded_macros_comment:
                        output_lines.append(loaded_macros_comment)
                    output_lines.append("")
                imports_inserted = True
                i += 1
                continue

            # Stub Perl sub { ... } closures so downstream execution sees Python callables
            sub_match = re.search(r'(=>|=)\s*sub\s*\{', original_line)
            if sub_match:
                # Check if this is a single-line closure (all braces balanced on this line)
                sub_start = original_line.find('sub {')
                after_sub = original_line[sub_start + 5:]  # Everything after "sub {"
                single_line_brace_count = after_sub.count('{') - after_sub.count('}')

                # For single-line closures where all braces are balanced, extract and replace them
                # But we need to be careful with strings, hashes, etc.
                # For now, skip this and only handle multi-line closures
                # The issue is that line joining can create single "lines" that actually contain
                # multiple statements that have been merged together.

                # Multi-line closure
                closure_lines = [original_line]
                # Start with brace depth from the opening sub {
                brace_depth = 1 + single_line_brace_count

                i += 1
                max_closure_lines = 100  # Safety limit to prevent infinite loops
                lines_collected = 0
                while i < len(lines) and brace_depth > 0 and lines_collected < max_closure_lines:
                    current_line = lines[i]
                    closure_lines.append(current_line)
                    brace_depth += current_line.count('{') - current_line.count('}')
                    i += 1
                    lines_collected += 1
                
                if lines_collected >= max_closure_lines:
                    # Hit the safety limit - something went wrong
                    # Just skip this and treat it as a comment
                    output_lines.append(f"# {original_line[:80]}... # Closure too complex, skipped")
                    continue

                first_line = closure_lines[0]
                last_line = closure_lines[-1] if closure_lines else ''

                # Look for everything after the closing brace of the closure
                # This might include }, }, );  or other closing syntax
                continuation_suffix = ''
                closing_brace_idx = None

                # Find where the closure-ending brace is on the last line
                close_brace_match = re.search(r'\}(.*)$', last_line)
                if close_brace_match:
                    # Get everything after the closing brace of the closure
                    suffix_from_last_line = close_brace_match.group(1)
                else:
                    suffix_from_last_line = ''

                # Check if there are continuation lines with more closing syntax
                temp_i = i
                continuation_lines = []
                while temp_i < len(lines) and len(continuation_lines) < 5:  # Safety limit
                    next_line = lines[temp_i].strip()
                    # Stop if we hit a line that's not just closing syntax (}, }, );, etc.)
                    if next_line and not re.match(r'^[}\);]*$', next_line):
                        break
                    if next_line:  # Don't add empty lines
                        continuation_lines.append(next_line)
                        temp_i += 1
                    else:
                        break

                # Incorporate continuation lines
                continuation_suffix = ' ' + ' '.join(continuation_lines)
                if continuation_lines:
                    i = temp_i  # Skip the lines we incorporated

                param_match = re.search(r'(\w+)\s*=>\s*sub\s*\{', first_line)
                if param_match:
                    sub_start = first_line.find('sub')
                    prefix = first_line[:sub_start]
                    suffix = suffix_from_last_line + continuation_suffix

                    # Create the stubbed line: replace 'sub { ... }' with lambda
                    stubbed_line = f"{prefix}lambda *args, **kwargs: None{suffix}"

                    # Transform the line (this handles => to =, -> to ., removes trailing ;)
                    transformed = self._rewrite_statement(stubbed_line)
                    
                    if transformed:
                        output_lines.append(transformed + "  # Stubbed Perl closure")
                else:
                    assign_match = re.search(r'(\w+)\s*=\s*sub\s*\{', first_line)
                    if assign_match:
                        var_name = assign_match.group(1)
                        indent_match = re.match(r'^(\s*)', first_line)
                        indent = indent_match.group(1) if indent_match else ''
                        stubbed_line = f"{indent}{var_name} = lambda *args, **kwargs: None"
                        transformed = self._rewrite_statement(stubbed_line)
                        if transformed:
                            stub_lines = transformed.split('\n')
                            for idx, stub_line in enumerate(stub_lines):
                                if idx == len(stub_lines) - 1:
                                    output_lines.append(f"{stub_line}  # Stubbed Perl closure")
                                else:
                                    output_lines.append(stub_line)
                    else:
                        output_lines.append(f"# {first_line}  # Skipped Perl closure")
                continue

            # Detect do { ... } until loops (single or multi line)
            do_until_single = re.match(r'^\s*do\s*\{([^}]*)\}\s*until\s*\(([^)]+)\)', original_line)
            if do_until_single:
                body = do_until_single.group(1).strip()
                condition = do_until_single.group(2).strip()
                # Compile body and condition via grammar or fallback
                body_lines = self._compile_line(body)
                # Flatten to a single statement; indent body lines
                compiled_cond = self._compile_expr(condition)
                # Strip outer parens if already present
                if compiled_cond.startswith('(') and compiled_cond.endswith(')'):
                    compiled_cond = compiled_cond[1:-1]
                # do-until means: execute body, then repeat UNTIL condition is true
                # In Python: while True: body; if condition: break
                output_lines.append(f'while True:')
                for bl in body_lines:
                    output_lines.append('    ' + bl)
                output_lines.append(f'    if ({compiled_cond}):')
                output_lines.append('        break')
                i += 1
                continue
            # Multi line do until
            do_until_start = re.match(r'^\s*do\s*\{', original_line)
            if do_until_start:
                block_lines = [original_line]
                brace_depth = original_line.count('{') - original_line.count('}')
                i += 1
                while i < len(lines) and brace_depth > 0:
                    ln = lines[i]
                    block_lines.append(ln)
                    brace_depth += ln.count('{') - ln.count('}')
                    i += 1
                last_line = block_lines[-1] if block_lines else ""
                until_match = re.search(r'\}\s*until\s*\(([^)]+)\)', last_line)
                
                # If 'until' is not on the closing brace line, check the next line
                if not until_match and i < len(lines):
                    next_line = lines[i]
                    until_match_next = re.match(r'^\s*until\s+', next_line)
                    if until_match_next:
                        # Found 'until' on the next line, need to collect the full condition
                        # which may span multiple lines (e.g., until (...) && (...) && (...);)
                        condition_lines = [next_line]
                        condition_line_idx = i
                        i += 1
                        
                        # Keep collecting lines until we find a semicolon that ends the statement
                        while i < len(lines) and ';' not in condition_lines[-1]:
                            ln = lines[i]
                            condition_lines.append(ln)
                            i += 1
                        
                        # Concatenate all condition lines
                        full_condition = ' '.join(ln.strip() for ln in condition_lines)
                        # Extract the condition from "until ... ;"
                        condition_match = re.match(r'^\s*until\s+(.+?);?\s*$', full_condition)
                        if condition_match:
                            condition_raw = condition_match.group(1).strip()
                            # Remove surrounding parens if present
                            if condition_raw.startswith('(') and condition_raw.endswith(')'):
                                condition = condition_raw[1:-1].strip()
                            else:
                                condition = condition_raw
                            until_match = True  # Mark as found
                            # DO NOT add condition lines to block_lines!
                            # They are part of the 'until' clause, not the 'do { }' body
                        else:
                            until_match = None
                    else:
                        until_match = None
                        
                if until_match:
                    if isinstance(until_match, bool):
                        # Already extracted condition from next line
                        pass
                    else:
                        # Extract from same-line pattern
                        condition = until_match.group(1).strip()
                    # Extract body lines: remove 'do {' and '} until (...)'
                    inner_lines: List[str] = []
                    
                    # All lines in block_lines are now part of the body (not the condition)
                    # since we don't add condition lines to block_lines anymore
                    
                    if len(block_lines) == 1 and block_lines[0].count('{') == block_lines[0].count('}'):
                        # Extract content between 'do {' and '}'
                        body_match = re.match(r'^\s*do\s*\{(.*)\}\s*$', block_lines[0])
                        if body_match:
                            body_content = body_match.group(1).strip()
                            if body_content:
                                inner_lines.append(body_content)
                    else:
                        # Multi-line case: shouldn't happen since we only collect until brace_depth > 0
                        # But handle it just in case
                        # Remove the first line's 'do {'
                        first_body = re.sub(r'^\s*do\s*\{', '', block_lines[0]).strip()
                        if first_body:
                            inner_lines.append(first_body)
                        
                        # Middle lines
                        body_end_idx = len(block_lines) - 1
                        
                        for middle_idx in range(1, body_end_idx):
                            inner_lines.append(block_lines[middle_idx])
                        
                        # Process the line with the closing brace (if it's not the first line)
                        if body_end_idx > 0:
                            last_body_line = block_lines[body_end_idx]
                            # Remove the closing }
                            last_body = re.sub(r'\}\s*$', '', last_body_line).strip()
                            if last_body:
                                inner_lines.append(last_body)
                    
                    # Compile body lines
                    compiled_body: List[str] = []
                    for ln in inner_lines:
                        compiled_body.extend(self._compile_line(ln))
                    compiled_cond = self._compile_expr(condition)
                    # Strip outer parens if already present
                    if compiled_cond.startswith('(') and compiled_cond.endswith(')'):
                        compiled_cond = compiled_cond[1:-1]
                    # Emit Python loop: do-until means execute body, then repeat UNTIL condition is true
                    # In Python: while True: body; if condition: break
                    output_lines.append(f'while True:')
                    for cb in compiled_body:
                        output_lines.append('    ' + cb)
                    output_lines.append(f'    if ({compiled_cond}):')
                    output_lines.append('        break')
                    continue
                else:
                    # Not a proper do-until, fall through: rewind index to process lines normally
                    i = i - len(block_lines) + 1

            # Detect Perl for/foreach loops
            for_result = self._try_rewrite_for_loop(lines, line_start_index)
            if for_result is not None:
                rewritten_loop, consumed_lines = for_result
                output_lines.extend(rewritten_loop)
                i = line_start_index + consumed_lines
                continue

            # Block detection: check for BEGIN_* markers
            block_found = False
            for block_type, (begin_pattern, end_pattern) in self.BLOCK_PATTERNS.items():
                if re.search(begin_pattern, original_line):
                    block_content_lines: List[str] = []
                    i += 1
                    while i < len(lines) and not re.match(end_pattern, lines[i]):
                        block_content_lines.append(lines[i])
                        i += 1
                    block_content = "\n".join(block_content_lines)
                    text_blocks.append((block_type, block_content))
                    # PGML blocks require evaluator transformation before storing
                    if "PGML" in block_type:
                        transformed_pgml = self._transform_pgml_evaluators(block_content)
                        block_var = f"pgml_block_{len(text_blocks) - 1}"
                        escaped_content = self._escape_triple_quotes(transformed_pgml)
                        output_lines.append(f"{block_var} = '''\n{escaped_content}\n'''")
                        if "SOLUTION" in block_type:
                            output_lines.append(f"SOLUTION(PGML({block_var}))")
                        elif "HINT" in block_type:
                            output_lines.append(f"HINT(PGML({block_var}))")
                        else:
                            output_lines.append(f"TEXT(PGML({block_var}))")
                    elif block_type == "TIKZ":
                        # Preserve raw TikZ/TeX content verbatim
                        block_var = f"tikz_block_{len(text_blocks) - 1}"
                        escaped_content = block_content.replace("'''", r"\'\'\'")
                        output_lines.append(
                            f"{block_var} = r'''\\n{escaped_content}\\n'''"
                        )
                    else:
                        transformed_content = self._transform_text_block(block_content)
                        if "SOLUTION" in block_type:
                            output_lines.append(f"SOLUTION({transformed_content})")
                        elif "HINT" in block_type:
                            output_lines.append(f"HINT({transformed_content})")
                        else:
                            output_lines.append(f"TEXT({transformed_content})")
                    block_found = True
                    break
            if block_found:
                # Skip over the END marker by incrementing i once more
                i += 1
                continue

            # Otherwise compile the current line
            compiled_lines = self._compile_line(original_line)
            output_lines.extend(compiled_lines)
            i += 1

        code = "\n".join(output_lines)
        return PreprocessResult(code=code, text_blocks=text_blocks, line_map=line_map)

    # ------------------------------------------------------------------
    # Map/Grep block conversion
    # ------------------------------------------------------------------

    def _convert_map_grep_blocks(self, line: str) -> str:
        """Convert Perl map/grep blocks to Python list comprehensions.

        Converts:
            map { EXPR } LIST     ->    [EXPR for _ in LIST]
            grep { EXPR } LIST    ->    [EXPR for _ in LIST if EXPR]
        """
        import re as re_module

        # Match map { ... } expr where expr can be a range like 0 .. 10
        # We need to handle nested braces and capture everything up to the last brace
        def find_map_grep_blocks(text):
            """Find all map/grep blocks in the text and convert them."""
            result = []
            i = 0
            while i < len(text):
                # Look for 'map {' or 'grep {'
                match = re_module.search(r'\b(map|grep)\s*\{', text[i:])
                if not match:
                    result.append(text[i:])
                    break

                # Found map or grep, add everything before it
                result.append(text[i:i + match.start()])
                keyword = match.group(1)
                block_start = i + match.end() - 1  # Position of opening brace

                # Find matching closing brace
                brace_depth = 1
                block_end = block_start + 1
                while block_end < len(text) and brace_depth > 0:
                    if text[block_end] == '{':
                        brace_depth += 1
                    elif text[block_end] == '}':
                        brace_depth -= 1
                    block_end += 1

                if brace_depth == 0:
                    # Extract block content
                    block_content = text[block_start + 1:block_end - 1]

                    # Find the list expression after the closing brace
                    list_start = block_end
                    # Skip whitespace
                    while list_start < len(text) and text[list_start] in ' \t':
                        list_start += 1

                    # Capture list expression (stops at ;, }, or end of common operators)
                    list_end = list_start
                    paren_depth = 0
                    bracket_depth = 0
                    while list_end < len(text):
                        ch = text[list_end]
                        if ch == '(':
                            paren_depth += 1
                        elif ch == ')':
                            paren_depth -= 1
                            if paren_depth < 0:
                                break
                        elif ch == '[':
                            bracket_depth += 1
                        elif ch == ']':
                            bracket_depth -= 1
                            if bracket_depth < 0:
                                break
                        elif ch in ';,}' and paren_depth == 0 and bracket_depth == 0:
                            break
                        elif ch == ' ' and paren_depth == 0 and bracket_depth == 0:
                            # Check if this is the .. range operator
                            if list_end + 3 <= len(text) and text[list_end:list_end+3] == ' ..':
                                list_end += 3
                                while list_end < len(text) and text[list_end] == ' ':
                                    list_end += 1
                                continue
                            else:
                                break
                        list_end += 1

                    list_expr = text[list_start:list_end].strip()

                    # Replace $_ with _ in block
                    block_content = re_module.sub(r'\$_\b', '_', block_content)

                    # Convert fat comma => to =
                    block_content = re_module.sub(r'\s*=>\s*', ' = ', block_content)

                    # Convert Perl range operator .. to Python range()
                    # Handle both "a .. b" and "a..b" formats
                    list_expr = re_module.sub(r'(\S+)\s*\.\.\s*(\S+)', r'range(\1, \2 + 1)', list_expr)

                    # Build the list comprehension
                    if keyword == 'map':
                        result.append(f"[{block_content} for _ in {list_expr}]")
                    else:  # grep
                        result.append(f"[_ for _ in {list_expr} if {block_content}]")

                    i = list_end
                else:
                    # No matching brace found, just add what we have
                    result.append(text[i:])
                    break

            return ''.join(result)

        return find_map_grep_blocks(line)

    # ------------------------------------------------------------------
    # Grammar and parsing
    # ------------------------------------------------------------------

    def _grammar(self) -> str:
        """Return the Lark grammar for parsing PG/Perl statements.

        This extended grammar covers most Perl constructs found in PG files:
        - Control flow: if/elsif/unless/while/for
        - Ternary operator: cond ? true : false
        - Hash/array access: $hash{key}, $array[idx]
        - Method calls: $obj->method()
        - Ranges: 0..10
        - Map/grep blocks
        - Statement modifiers: stmt if cond
        - Fat comma: key => value

        The grammar is designed to avoid reduce/reduce conflicts.
        Unparseable constructs fall back to Pygments rewriting.
        """
        return r"""
            start: (stmt ";"?)*

            stmt: if_stmt
                | while_stmt
                | for_stmt
                | foreach_stmt
                | do_until_stmt
                | decl
                | assign
                | expr_stmt
                | document
                | enddocument
                | stmt_modifier

            // Control flow statements
            if_stmt: "if" "(" expr ")" block elsif_clause* else_clause?
            elsif_clause: "elsif" "(" expr ")" block
            else_clause: "else" block
            unless_stmt: "unless" "(" expr ")" block
            while_stmt: "while" "(" expr ")" block
            for_stmt: "for" "my"? var "(" expr ")" block
            foreach_stmt: "foreach" "my"? var "(" expr ")" block
            do_until_stmt: "do" block "until" "("? expr ")"?

            block: "{" (stmt ";"?)* "}"

            // Statement modifiers (trailing conditionals)
            stmt_modifier_if: simple_stmt "if" expr        -> stmt_modifier_if
            stmt_modifier_unless: simple_stmt "unless" expr -> stmt_modifier_unless
            stmt_modifier: stmt_modifier_if | stmt_modifier_unless
            simple_stmt: decl | assign | call_expr

            document: "DOCUMENT" "(" ")"            -> document_call
            enddocument: "ENDDOCUMENT" "(" ")"      -> enddocument_call
            loadmacros: "loadMacros" "(" /[^)]*/ ")" -> loadmacros_call

            decl: "my" var "=" expr               -> assign_stmt
            assign: var "=" expr                -> assign_stmt
                  | var subscript "=" expr      -> subscript_assign
            expr_stmt: expr                      -> expr_stmt

            args: expr ("," expr)*

            // Hash/Array subscripting
            subscript: "[" expr "]"              -> array_subscript
                     | "{" expr "}"              -> hash_subscript

            // Expressions with precedence (lowest to highest)
            ?expr: ternary_expr

            // Ternary: cond ? true : false
            ?ternary_expr: or_expr ("?" or_expr ":" ternary_expr)?  -> ternary_expr

            ?or_expr: and_expr ((OR_OP | "or") and_expr)*      -> binary_expr
            ?and_expr: comp_expr ((AND_OP | "and") comp_expr)*  -> binary_expr

            // Comparison operators (eq, ne, lt, gt, le, ge, ==, !=, <, >, <=, >=)
            ?comp_expr: range_expr (comp_op range_expr)*     -> binary_expr
            comp_op: EQ | NE | LT | GT | LE | GE | EQEQ | BANGEQ | LANGLE | RANGLE | LTEQ | GTEQ
            EQ: "eq"
            NE: "ne"
            LT: "lt"
            GT: "gt"
            LE: "le"
            GE: "ge"
            EQEQ: "=="
            BANGEQ: "!="
            LANGLE: "<"
            RANGLE: ">"
            LTEQ: "<="
            GTEQ: ">="
            
            // Logical operators (must be terminals, not literal strings, to avoid Lark confusion)
            OR_OP: "||"
            AND_OP: "&&"

            // Range operator: 0..10
            ?range_expr: add_expr (".." add_expr)?           -> range_expr

            ?add_expr: mul_expr (add_op mul_expr)*           -> binary_expr
            add_op: "+" | "-" | "."  // . is string concat in Perl

            ?mul_expr: unary_expr (mul_op unary_expr)*       -> binary_expr
            mul_op: "*" | "/" | "%" | "x"  // x is string repeat in Perl

            ?unary_expr: postfix_expr
                       | "-" unary_expr                      -> unary_minus
                       | "!" unary_expr                      -> unary_not

            // Postfix: method calls, subscripts
            ?postfix_expr: primary (postfix_op)*
            postfix_op: "->" NAME "(" args? ")"              -> method_call
                      | subscript

            ?primary: call_expr | var | atom | "(" expr ")"

            call_expr: NAME "(" args? ")"          -> call_expr

            // Map and grep blocks
            map_expr: "map" "{" expr "}" expr                -> map_expr
            grep_expr: "grep" "{" expr "}" expr              -> grep_expr

            var: VAR
            atom: NUMBER | STRING | NAME | regex_literal

            regex_literal: QR "/" /[^\/]+/ "/" REGEX_FLAGS?  -> regex_literal

            QR.2: "qr"
            NAME: /[A-Za-z_][A-Za-z0-9_]*/
            VAR: /[\$@%][A-Za-z_][A-Za-z0-9_]*/
            STRING: /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/
            NUMBER: /[0-9]+(?:\.[0-9]+)?/
            REGEX_FLAGS: /[imsxo]+/

            %import common.WS
            %ignore WS
            """

    def _make_transformer(self) -> Transformer:
        """Create and return a Lark transformer that lowers parse trees."""

        @v_args(inline=True)
        class ToIR(Transformer):
            """Lower the parse tree into intermediate representation (IR)."""

            def start(self, *stmts):
                """Flatten the list of statements from the top-level start rule."""
                return list(stmts)

            def stmt(self, item):
                """Unwrap the single child of a stmt production."""
                return item

            # Document control
            def document_call(self):
                return ("call", "DOCUMENT", [])

            def enddocument_call(self):
                return ("call", "ENDDOCUMENT", [])

            def loadmacros_call(self, *args):
                return ("noop", )

            # Control flow statements
            def if_stmt(self, condition, block, *clauses):
                """Lower if statement with optional elsif/else clauses."""
                return ("if", condition, block, list(clauses))

            def elsif_clause(self, condition, block):
                return ("elsif", condition, block)

            def else_clause(self, block):
                return ("else", block)

            def unless_stmt(self, condition, block):
                """Lower unless statement (if not)."""
                return ("unless", condition, block)

            def while_stmt(self, condition, block):
                """Lower while loop."""
                return ("while", condition, block)

            def for_stmt(self, var, expr, block):
                """Lower for loop."""
                return ("for", var, expr, block)

            def foreach_stmt(self, var, expr, block):
                """Lower foreach loop."""
                return ("foreach", var, expr, block)

            def do_until_stmt(self, block, condition):
                """Lower do-until loop."""
                return ("do_until", block, condition)

            def block(self, *stmts):
                """Lower block of statements."""
                return ("block", list(stmts))

            # Statement modifiers
            def stmt_modifier(self, child):
                """Pass through stmt_modifier_if or stmt_modifier_unless."""
                return child
            
            def stmt_modifier_if(self, stmt, condition):
                """Lower statement modifier with 'if'."""
                return ("stmt_modifier", stmt, "if", condition)
            
            def stmt_modifier_unless(self, stmt, condition):
                """Lower statement modifier with 'unless'."""
                return ("stmt_modifier", stmt, "unless", condition)

            def simple_stmt(self, stmt):
                return stmt

            # Assignments
            def assign_stmt(self, var, expr):
                """Lower a variable declaration or assignment."""
                return ("assign", var, expr)

            def subscript_assign(self, var, subscript, expr):
                """Lower subscript assignment: $arr[0] = value."""
                return ("subscript_assign", var, subscript, expr)

            # Subscripting
            def array_subscript(self, expr):
                return ("array_subscript", expr)

            def hash_subscript(self, expr):
                return ("hash_subscript", expr)

            # Expressions
            def call_expr(self, name, *args):
                """Lower a function call expression."""
                arglist = args[0] if args else []
                return ("call", name, arglist)

            def expr_stmt(self, expr):
                """Lower an expression statement."""
                return ("expr", expr)

            def ternary_expr(self, *parts):
                """Lower ternary operator: cond ? true : false."""
                if len(parts) == 1:
                    return parts[0]
                elif len(parts) == 3:
                    cond, true_val, false_val = parts
                    return ("ternary", cond, true_val, false_val)
                return parts[0]
            def binary_expr(self, left, *rest):
                """Lower binary operations."""
                expr = left
                for op, right in zip(rest[::2], rest[1::2]):
                    # Extract operator string from Tree or Token
                    if hasattr(op, 'children') and op.children:
                        # If op is a Tree with children, get the first child
                        op_tok = op.children[0]
                    elif hasattr(op, 'data'):
                        # If op is a Tree without children (inline rules), use a Token
                        # This shouldn't happen with properly defined grammars
                        op_tok = op
                    else:
                        # op is already a Token or string
                        op_tok = op
                    
                    # Extract the actual operator string value
                    if hasattr(op_tok, 'value'):
                        op_str = op_tok.value
                    elif hasattr(op_tok, 'type'):
                        # Token without value attribute
                        op_str = str(op_tok)
                    else:
                        op_str = str(op_tok)
                    
                    expr = ("bin", expr, op_str, right)
                return expr

            # Operator extractors - these are needed because operators are defined as rules
            def add_op(self, *args):
                """Extract add operator token."""
                return args[0] if args else "+"

            def mul_op(self, *args):
                """Extract mul operator token."""
                return args[0] if args else "*"

            def comp_op(self, token):
                """Extract comparison operator token."""
                # Tokens like EQ, GT, etc. come through as Token objects
                if hasattr(token, 'type'):
                    # Map token types to operator strings
                    op_map = {
                        'EQ': 'eq', 'NE': 'ne', 'LT': 'lt', 'GT': 'gt',
                        'LE': 'le', 'GE': 'ge', 'EQEQ': '==', 'BANGEQ': '!=',
                        'LANGLE': '<', 'RANGLE': '>', 'LTEQ': '<=', 'GTEQ': '>='
                    }
                    return op_map.get(token.type, token.value)
                if hasattr(token, 'value'):
                    return token.value
                return str(token)

            def range_expr(self, *parts):
                """Lower range operator: 0..10."""
                if len(parts) == 2:
                    start, end = parts
                    return ("range", start, end)
                return parts[0]

            def unary_minus(self, expr):
                return ("unary", "-", expr)

            def unary_not(self, expr):
                return ("unary", "!", expr)

            def postfix_expr(self, primary, *postfix_ops):
                """Lower postfix operations (method calls, subscripts)."""
                expr = primary
                for op in postfix_ops:
                    expr = ("postfix", expr, op)
                return expr
            
            def postfix_op(self, child):
                """Pass through the postfix operation (method_call or subscript)."""
                return child

            def method_call(self, name, *args):
                """Lower method call: ->method()."""
                arglist = args[0] if args else []
                return ("method_call", name, arglist)

            # Map and grep
            def map_expr(self, block_expr, list_expr):
                """Lower map block."""
                return ("map", block_expr, list_expr)

            def grep_expr(self, block_expr, list_expr):
                """Lower grep block."""
                return ("grep", block_expr, list_expr)

            # Regex
            def regex_literal(self, *args):
                """Lower regex literal: qr/pattern/flags."""
                # Can receive (qr_token, pattern, flags) or (pattern, flags) depending on parsing
                if len(args) == 3:
                    qr, pattern, flags = args
                elif len(args) == 2:
                    pattern, flags = args
                else:
                    # Fallback
                    pattern = args[0] if args else ""
                    flags = ""
                return ("regex", str(pattern), str(flags))

            # Tokens
            def VAR(self, tok):
                return ("var", str(tok))

            def NAME(self, tok):
                return str(tok)

            def NUMBER(self, tok):
                return str(tok)

            def STRING(self, tok):
                return str(tok)

            def args(self, *exprs):
                return list(exprs)

            def var(self, child):
                """Unwrap the var rule to return its child."""
                return child

            def atom(self, child):
                """Unwrap the atom rule to return its child."""
                return child

        return ToIR()

    # ------------------------------------------------------------------
    # Compilation helpers
    # ------------------------------------------------------------------

    def _compile_line(self, line: str) -> List[str]:
        """Compile a single line of PG code into Python lines.

        This method attempts to parse the line with the Lark grammar.  On
        success, it lowers the parse tree into IR and then renders it
        into Python.  If the line cannot be parsed by the grammar, it
        is rewritten using a Pygments based fallback which performs
        conservative token replacement.
        """
        stripped = line.strip()
        indent_prefix = line[: len(line) - len(line.lstrip(' \t'))]
        if not stripped:
            return []
        # Keep comments verbatim
        if stripped.startswith('#'):
            return [stripped]
        # If a Lark parser is available, try to parse.  Fall back to
        # manual parsing and Pygments rewriting on failure.
        if self._parser is not None:
            try:
                tree = self._parser.parse(stripped)
                ir_list = self._transformer.transform(tree)
                if not isinstance(ir_list, list):
                    ir_list = [ir_list]
                result_lines: List[str] = []
                for ir in ir_list:
                    out = self._emit_ir(ir)
                    if out is not None:
                        result_lines.append(out)
                if indent_prefix and result_lines:
                    result_lines = [
                        (indent_prefix + rl) if rl else rl for rl in result_lines
                    ]
                return result_lines if result_lines else []
            except LarkError:
                pass

        # Fallback to Pygments-based token rewriting
        rewritten = self._rewrite_statement(line)
        if not rewritten:
            return []
        return rewritten.split('\n')

    def _compile_expr(self, expr: str) -> str:
        """Compile a small expression using the grammar or fallback rewrite.

        Returns a string containing Python code representing the expression.
        """
        if self._parser is not None:
            try:
                tree = self._parser.parse(expr)
                ir_list = self._transformer.transform(tree)
                # Find first expr or assign
                if not isinstance(ir_list, list):
                    ir_list = [ir_list]
                for ir in ir_list:
                    if ir[0] in ("assign", "expr", "bin", "var", "call"):
                        return self._expr_to_py(ir)
                # Fallback: use pygments rewrite
            except LarkError:
                pass
        return self._rewrite_with_pygments(expr)

    # ------------------------------------------------------------------
    # IR emission
    # ------------------------------------------------------------------

    def _emit_ir(self, ir: Any, indent: int = 0) -> Optional[str]:
        """Convert IR nodes into Python code lines. Returns None for no output."""
        typ = ir[0]
        ind = "    " * indent

        if typ == "noop":
            return None

        # Control flow statements
        if typ == "if":
            _, condition, block, clauses = ir
            cond_py = self._expr_to_py(condition)
            block_stmts = self._emit_block(block, indent + 1)
            lines = [f"{ind}if {cond_py}:"]
            lines.extend(block_stmts)

            # Handle elsif and else clauses
            for clause in clauses:
                if clause[0] == "elsif":
                    _, elif_cond, elif_block = clause
                    elif_cond_py = self._expr_to_py(elif_cond)
                    lines.append(f"{ind}elif {elif_cond_py}:")
                    lines.extend(self._emit_block(elif_block, indent + 1))
                elif clause[0] == "else":
                    _, else_block = clause
                    lines.append(f"{ind}else:")
                    lines.extend(self._emit_block(else_block, indent + 1))

            return "\n".join(lines)

        if typ == "unless":
            _, condition, block = ir
            cond_py = self._expr_to_py(condition)
            block_stmts = self._emit_block(block, indent + 1)
            lines = [f"{ind}if not ({cond_py}):"]
            lines.extend(block_stmts)
            return "\n".join(lines)

        if typ == "while":
            _, condition, block = ir
            cond_py = self._expr_to_py(condition)
            block_stmts = self._emit_block(block, indent + 1)
            lines = [f"{ind}while {cond_py}:"]
            lines.extend(block_stmts)
            return "\n".join(lines)

        if typ in {"for", "foreach"}:
            _, var, expr, block = ir
            var_name = self._desigil(var[1] if isinstance(var, tuple) else var)
            expr_py = self._expr_to_py(expr)
            block_stmts = self._emit_block(block, indent + 1)
            lines = [f"{ind}for {var_name} in {expr_py}:"]
            lines.extend(block_stmts)
            return "\n".join(lines)

        if typ == "do_until":
            _, block, condition = ir
            cond_py = self._expr_to_py(condition)
            block_stmts = self._emit_block(block, indent + 1)
            lines = [f"{ind}while True:"]
            lines.extend(block_stmts)
            lines.append(f"{ind}    if ({cond_py}):")
            lines.append(f"{ind}        break")
            return "\n".join(lines)

        if typ == "stmt_modifier":
            _, stmt, modifier, condition = ir
            stmt_py = self._emit_ir(stmt, indent)
            cond_py = self._expr_to_py(condition)
            # Strip outer parens if already present (binary exprs add them)
            if cond_py.startswith('(') and cond_py.endswith(')'):
                cond_py = cond_py[1:-1]
            if modifier == "if":
                return f"{ind}if ({cond_py}): {stmt_py.strip()}"
            else:  # unless
                return f"{ind}if not ({cond_py}): {stmt_py.strip()}"

        # Assignments
        if typ == "assign":
            _, var, expr = ir
            var_name = self._desigil(var[1] if isinstance(var, tuple) else var)
            expr_py = self._expr_to_py(expr)
            # Strip outer parens from binary exprs in assignments (cleaner output)
            if expr_py.startswith('(') and expr_py.endswith(')') and isinstance(expr, tuple) and expr[0] == "bin":
                expr_py = expr_py[1:-1]
            return f"{ind}{var_name} = {expr_py}"

        if typ == "subscript_assign":
            _, var, subscript, expr = ir
            var_name = self._desigil(var[1] if isinstance(var, tuple) else var)
            subscript_py = self._emit_subscript(subscript)
            expr_py = self._expr_to_py(expr)
            return f"{ind}{var_name}{subscript_py} = {expr_py}"

        # Function calls
        if typ == "call":
            _, name, args = ir
            if name == "loadMacros":
                return None
            py_args = [self._expr_to_py(a) for a in args]
            return f"{ind}{name}({', '.join(py_args)})"

        # Expressions
        if typ == "expr":
            _, expr = ir
            return f"{ind}{self._expr_to_py(expr)}"

        if typ == "bin":
            return f"{ind}{self._expr_to_py(ir)}"

        # Unknown IR: produce raw comment
        return f"{ind}# {ir}"

    def _emit_block(self, block_ir: Any, indent: int) -> List[str]:
        """Emit a block of statements with proper indentation."""
        if block_ir[0] != "block":
            return []

        _, stmts = block_ir
        lines = []
        for stmt in stmts:
            emitted = self._emit_ir(stmt, indent)
            if emitted:
                lines.append(emitted)

        # Ensure block has at least pass if empty
        if not lines:
            lines.append("    " * indent + "pass")

        return lines

    def _emit_subscript(self, subscript_ir: Any) -> str:
        """Emit a subscript operation (array or hash)."""
        typ = subscript_ir[0]
        _, expr = subscript_ir
        expr_py = self._expr_to_py(expr)

        if typ == "array_subscript":
            return f"[{expr_py}]"
        elif typ == "hash_subscript":
            # Quote bare words if they're not already quoted
            if expr_py and expr_py[0] not in ('"', "'"):
                return f"['{expr_py}']"
            return f"[{expr_py}]"

        return f"[{expr_py}]"

    def _expr_to_py(self, expr: Any) -> str:
        """Lower an expression IR into a Python expression string."""
        if isinstance(expr, tuple):
            head = expr[0]

            # Variables
            if head == "var":
                return self._desigil(expr[1])

            # Binary operations
            if head == "bin":
                _, left, op, right = expr
                py_left = self._expr_to_py(left)
                py_right = self._expr_to_py(right)

                # Operator mapping
                op_map = {
                    "eq": "==", "ne": "!=", "lt": "<", "gt": ">",
                    "le": "<=", "ge": ">=",
                    ".": "+",  # String concatenation
                    "x": "*",  # String repetition
                    "||": " or ", "&&": " and ",
                    "or": " or ", "and": " and "
                }
                py_op = op_map.get(op, op)
                return f"({py_left} {py_op} {py_right})"

            # Ternary operator
            if head == "ternary":
                _, cond, true_val, false_val = expr
                cond_py = self._expr_to_py(cond)
                true_py = self._expr_to_py(true_val)
                false_py = self._expr_to_py(false_val)
                return f"({true_py} if {cond_py} else {false_py})"

            # Range operator
            if head == "range":
                _, start, end = expr
                start_py = self._expr_to_py(start)
                end_py = self._expr_to_py(end)
                return f"range({start_py}, {end_py} + 1)"

            # Unary operations
            if head == "unary":
                _, op, operand = expr
                operand_py = self._expr_to_py(operand)
                if op == "!":
                    return f"(not {operand_py})"
                return f"({op}{operand_py})"

            # Postfix operations (method calls, subscripts)
            if head == "postfix":
                _, base, op = expr
                base_py = self._expr_to_py(base)

                # Handle Tree objects that weren't transformed yet
                if not isinstance(op, tuple):
                    try:
                        from lark import Tree
                        if isinstance(op, Tree):
                            # Transform the Tree to IR
                            op = self._transformer.transform(op)
                            # If it returned a list, take first item
                            if isinstance(op, list) and op:
                                op = op[0]
                    except:
                        pass

                # Now handle the postfix operation
                if isinstance(op, tuple):
                    if op[0] == "method_call":
                        _, method_name, args = op
                        # Special case: .reduce() is a property in Python MathObjects, not a method
                        # In Perl: ->reduce() and ->reduce are equivalent
                        # In Python: reduce is a @property, so .reduce() fails
                        if method_name == "reduce" and len(args) == 0:
                            return f"{base_py}.reduce"
                        arg_strs = [self._expr_to_py(a) for a in args]
                        return f"{base_py}.{method_name}({', '.join(arg_strs)})"
                    elif op[0] in ("array_subscript", "hash_subscript"):
                        subscript_py = self._emit_subscript(op)
                        return f"{base_py}{subscript_py}"

                return base_py

            # Function calls
            if head == "call":
                _, name, args = expr
                arg_strings = [self._expr_to_py(a) for a in args]
                return f"{name}({', '.join(arg_strings)})"

            # Map and grep
            if head == "map":
                _, block_expr, list_expr = expr
                block_py = self._expr_to_py(block_expr)
                list_py = self._expr_to_py(list_expr)
                return f"[{block_py} for _ in {list_py}]"

            if head == "grep":
                _, block_expr, list_expr = expr
                block_py = self._expr_to_py(block_expr)
                list_py = self._expr_to_py(list_expr)
                return f"[_ for _ in {list_py} if {block_py}]"

            # Regex literal
            if head == "regex":
                _, pattern, flags = expr
                # Convert Perl regex flags to Python re flags
                flag_map = {
                    'i': 're.IGNORECASE',
                    'm': 're.MULTILINE',
                    's': 're.DOTALL',
                    'x': 're.VERBOSE',
                }
                py_flags = ' | '.join(flag_map.get(f, '') for f in str(flags) if f in flag_map)
                if py_flags:
                    return f're.compile(r"{pattern}", {py_flags})'
                else:
                    return f're.compile(r"{pattern}")'

            # Expression statements
            if head == "expr":
                return self._expr_to_py(expr[1])

            # Assignments (in expression context)
            if head == "assign":
                _, var, val = expr
                return f"{self._desigil(var[1])} = {self._expr_to_py(val)}"

        # Otherwise, treat as raw string and apply rewrite
        rewritten = self._rewrite_with_pygments(str(expr))
        return rewritten

    # ------------------------------------------------------------------
    # Pygments based rewriting
    # ------------------------------------------------------------------

    def _desigil(self, name: str) -> str:
        """Remove leading sigil characters from Perl variable names."""
        if name and name[0] in "$@%":
            return name[1:]
        return name

    def _convert_regexes(self, code: str) -> str:
        """Convert Perl qr/pattern/flags regexes to Python re.compile() calls."""
        import re as re_module
        
        # Pattern to match Perl regex literals: qr/pattern/flags
        # This handles patterns with escaped slashes inside
        pattern = r'qr/([^/]*(?:\\.[^/]*)*)/([imsxo]*)'
        
        def replace_regex(match):
            pattern_content = match.group(1)
            flags_str = match.group(2)
            # Convert Perl regex flags to Python re flags
            flag_map = {
                'i': 're.IGNORECASE',
                'm': 're.MULTILINE',
                's': 're.DOTALL',
                'x': 're.VERBOSE',
            }
            py_flags = ' | '.join(flag_map.get(f, '') for f in flags_str if f in flag_map)
            if py_flags:
                return f're.compile(r"{pattern_content}", {py_flags})'
            else:
                return f're.compile(r"{pattern_content}")'
        
        return re_module.sub(pattern, replace_regex, code)

    def _rewrite_with_pygments(self, code: str) -> str:
        """Fallback rewrite using Pygments for conservative token replacement."""
        # First, replace qr/pattern/flags with re.compile(pattern, flags)
        import re as re_module
        code = self._convert_regexes(code)
        
        tokens = list(self._perl_lexer.get_tokens_unprocessed(code))

        result: List[str] = []
        i = 0
        # Track brace context: True if in hash literal, False if in code block
        brace_context_stack: List[bool] = []
        # Track bracket context: nesting level of [...]
        bracket_depth = 0
        
        while i < len(tokens):
            _, ttype, text = tokens[i]
            # Preserve comments verbatim
            if ttype in Token.Comment:
                result.append(text)
                i += 1
                continue
            # Quote bare words before => in hash literals
            if ttype in Token.Name and brace_context_stack and brace_context_stack[-1]:
                # We're inside a hash literal, look ahead to see if next non-whitespace token is =>
                j = i + 1
                while j < len(tokens) and tokens[j][1] in Token.Text.Whitespace:
                    j += 1
                if j < len(tokens):
                    next_token = tokens[j]
                    # Check if it's => (either as two tokens = > or single =>)
                    is_fat_comma = False
                    if next_token[2] == '=>':
                        is_fat_comma = True
                    elif next_token[2] == '=' and j + 1 < len(tokens) and tokens[j + 1][2] == '>':
                        is_fat_comma = True
                    
                    if is_fat_comma:
                        # Quote the bare word
                        result.append(f"'{text}'")
                        i += 1
                        continue
            # Handle false-positive regex tokens BEFORE string check (Regex is subclass of String)
            # Pygments misidentifies / division as regex
            if ttype in Token.Literal.String.Regex:
                # If it starts/ends with / and contains $variables, it might be division operators
                # Example: "/ 2, $b + $r * sqrt(2) /" is actually division, not regex
                if text.startswith('/') and text.endswith('/') and '$' in text:
                    # Strip the / delimiters and process as normal code
                    import re
                    content = text[1:-1] if len(text) > 2 else text
                    # Remove sigils from variables
                    converted = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'\1', content)
                    # Re-add the / as division operators
                    result.append('/' + converted + '/')
                else:
                    result.append(text)
                i += 1
                continue
            # Handle qr/pattern/flags regex literals
            if text.startswith('qr/') and '/' in text[3:]:
                # Find the closing / and extract pattern and flags
                import re as re_module
                match = re_module.match(r'qr/([^/]*)/([imsxo]*)', text)
                if match:
                    pattern = match.group(1)
                    flags_str = match.group(2)
                    # Convert Perl regex flags to Python re flags
                    flag_map = {
                        'i': 're.IGNORECASE',
                        'm': 're.MULTILINE',
                        's': 're.DOTALL',
                        'x': 're.VERBOSE',
                    }
                    py_flags = ' | '.join(flag_map.get(f, '') for f in flags_str if f in flag_map)
                    if py_flags:
                        result.append(f're.compile(r"{pattern}", {py_flags})')
                    else:
                        result.append(f're.compile(r"{pattern}")')
                else:
                    result.append(text)
                i += 1
                continue
            # String interpolation: convert Perl "$var" to Python f"{var}"
            if ttype in Token.Literal.String:
                # Only process double-quoted strings (Perl interpolates these)
                if text.startswith('"') and '$' in text:
                    # Extract content without quotes
                    content = text[1:-1] if len(text) >= 2 else text
                    # Escape backslashes first (before processing braces)
                    # This handles LaTeX sequences like \( \) \Big etc.
                    escaped = content.replace('\\', '\\\\')
                    # Escape literal braces for f-strings
                    escaped = escaped.replace('{', '{{').replace('}', '}}')
                    # Convert $var to {var}
                    import re
                    converted = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'{\1}', escaped)
                    result.append(f'f"{converted}"')
                else:
                    # For non-interpolated strings, escape backslashes
                    # This handles LaTeX in single-quoted strings
                    if '\\' in text and not text.startswith('r"') and not text.startswith("r'"):
                        # Extract quotes and content
                        if len(text) >= 2:
                            quote_char = text[0]
                            content = text[1:-1]
                            escaped_content = content.replace('\\', '\\\\')
                            result.append(f'{quote_char}{escaped_content}{quote_char}')
                        else:
                            result.append(text)
                    else:
                        result.append(text)
                i += 1
                continue
            # Variables: handle $# array last index operator specially, then remove sigil
            if ttype in Token.Name.Variable:
                if text == '$#':
                    # $# followed by array name -> len(array_name) - 1
                    # Look ahead for the array name
                    j = i + 1
                    while j < len(tokens) and tokens[j][1] in Token.Text.Whitespace:
                        j += 1
                    if j < len(tokens) and tokens[j][1] in Token.Name.Variable:
                        array_token = tokens[j][2]
                        array_name = self._desigil(array_token)
                        result.append(f"len({array_name}) - 1")
                        i = j + 1  # Skip past the array name
                        continue
                    else:
                        # No array name following, just replace $# with an underscore to avoid syntax error
                        result.append("_")
                        i += 1
                        continue
                elif text.startswith('$#'):
                    # $#array_name (shouldn't happen with current Pygments, but handle it)
                    array_name = text[2:]
                    result.append(f"len({array_name}) - 1")
                    i += 1
                    continue
                else:
                    result.append(self._desigil(text))
                    i += 1
                    continue
            # Namespace tokens: convert :: to .
            if ttype in Token.Name.Namespace:
                # Pygments returns 'parser::Assignment' as a single token
                # Convert :: to .
                converted = text.replace('::', '.')
                result.append(converted)
                i += 1
                continue
            # Hash access: $h{key} -> h['key']
            # Also handle chained subscripts: Context()->{error}{msg} -> Context()['error']['msg']
            if text == '{' and i > 0:
                prev_token = tokens[i-1]
                # Handle if previous token is a variable, closing paren, closing brace, or >
                # (> indicates we just processed -> which was converted to .)
                if (prev_token[1] in Token.Name.Variable or 
                    prev_token[2] == ')' or 
                    prev_token[2] == '}' or
                    prev_token[2] == '>'):
                    # gather until closing brace
                    inner: List[str] = []
                    depth = 1
                    j = i + 1
                    while j < len(tokens) and depth > 0:
                        _, t2, s2 = tokens[j]
                        if s2 == '{':
                            depth += 1
                        elif s2 == '}':
                            depth -= 1
                            if depth == 0:
                                break
                        inner.append(s2)
                        j += 1
                    inner_text = ''.join(inner).strip()
                    # quote bare words if not already quoted
                    if inner_text and inner_text[0] not in "'\"":
                        inner_text = f"'{inner_text}'"
                    result.append('[' + inner_text + ']')
                    i = j + 1
                    continue
            # Combine operator pairs into single tokens for arrows, namespace
            # separators and fat comma.  Pygments splits '->' into two
            # separate Operator tokens '-' and '>' and likewise '=' and '>'
            # for '=>', and ':' and ':' for '::'.  Detect these pairs
            # here.
            if ttype in Token.Operator or ttype in Token.Punctuation:
                # Handle method arrow '->'
                if text == '-' and i + 1 < len(tokens) and tokens[i+1][2] == '>':
                    i += 2
                    # Skip any empty tokens after ->
                    while i < len(tokens) and tokens[i][2] == '':
                        i += 1
                    # Check what comes after ->
                    if i < len(tokens):
                        next_idx, next_ttype, next_text = tokens[i]
                        # If next token is {, it's a hash subscript - don't append . (let [ handle it)
                        if next_text == '{':
                            # Don't append anything, let the hash subscript code handle {
                            continue
                        # Otherwise append . for method/property access
                        result.append('.')
                        # If it's a method/property name
                        if next_ttype in Token.Name or next_ttype == Token.Operator.Word:
                            # Look ahead to see what follows (skip empty tokens)
                            j = i + 1
                            while j < len(tokens) and tokens[j][2] == '':
                                j += 1
                            has_parens = False
                            has_arrow = False
                            has_brace = False
                            if j < len(tokens):
                                lookahead_idx, lookahead_ttype, lookahead_text = tokens[j]
                                if lookahead_text == '(':
                                    has_parens = True
                                elif lookahead_text == '-' and j + 1 < len(tokens) and tokens[j + 1][2] == '>':
                                    has_arrow = True  # Another -> follows, so this is property access
                                elif lookahead_text == '{':
                                    has_brace = True  # Hash subscript follows
                            # Always append the method/property name
                            result.append(next_text)
                            # Only add () if no parens AND no arrow AND no brace (i.e., final method in chain)
                            if not has_parens and not has_arrow and not has_brace:
                                result.append('()')
                            i += 1
                            continue
                    else:
                        # Nothing after ->, just append .
                        result.append('.')
                    continue
                # Handle namespace separator '::'
                if text == ':' and i + 1 < len(tokens) and tokens[i+1][2] == ':':
                    result.append('.')
                    i += 2
                    continue
                # Handle fat comma '=>'
                if text == '=' and i + 1 < len(tokens) and tokens[i+1][2] == '>':
                    # Inside hash literal, treat as dict colon
                    if brace_context_stack and brace_context_stack[-1]:
                        result.append(': ')
                    # Inside bracket (list) context, quote the key and use comma
                    elif bracket_depth > 0:
                        # Need to quote the previous bareword if it exists
                        # Look back to find it
                        j = len(result) - 1
                        while j >= 0 and result[j].strip() == '':
                            j -= 1
                        if j >= 0:
                            # Check if previous token looks like a bareword
                            prev = result[j].strip()
                            if prev and prev.isidentifier() and prev not in ('True', 'False', 'None'):
                                # Replace it with quoted version
                                result[j] = f'"{prev}"'
                        result.append(', ')
                    else:
                        # Check if previous token is ] or ) - then it's a pair separator
                        j = len(result) - 1
                        while j >= 0 and result[j].strip() == '':
                            j -= 1
                        if j >= 0 and result[j].strip() in (']', ')'):
                            # It's separating elements, use comma
                            result.append(', ')
                        else:
                            # Otherwise it's an assignment
                            result.append(' = ')
                    i += 2
                    continue
                # Handle Perl string concatenation operator '.'
                # In Perl: "str" . "ing" concatenates strings
                # In Python: "str" + "ing"
                # We need to distinguish from method access: obj.method()
                if text == '.':
                    # Check if this is string concatenation (binary operator) or method access
                    # Look at previous and next tokens to determine context
                    is_concat = False
                    if i > 0 and i + 1 < len(tokens):
                        # Skip whitespace before
                        j = i - 1
                        while j >= 0 and tokens[j][1] in Token.Text.Whitespace:
                            j -= 1
                        # Skip whitespace after
                        k = i + 1
                        while k < len(tokens) and tokens[k][1] in Token.Text.Whitespace:
                            k += 1

                        if j >= 0 and k < len(tokens):
                            prev_text = tokens[j][2]
                            prev_ttype = tokens[j][1]
                            next_text = tokens[k][2]
                            next_ttype = tokens[k][1]

                            # It's concatenation if there's whitespace around the dot
                            # In Perl: "str" . "ing" has spaces
                            # In Perl: obj.method() has no spaces
                            # Check if preceded by string, closing paren, or ends with expression
                            is_expr_before = (
                                prev_ttype in Token.Literal.String or
                                prev_text == ')' or
                                prev_text == ']' or
                                prev_ttype in Token.Literal.Number
                            )
                            # Check if followed by string, function call, or expression
                            is_expr_after = (
                                next_ttype in Token.Literal.String or
                                next_ttype in Token.Literal.Number or
                                next_ttype in Token.Name  # Function call like ans_rule()
                            )
                            # It's concatenation if both sides look like expressions
                            # and we have whitespace (i != j+1 or k != i+1)
                            if is_expr_before and is_expr_after:
                                # Check for whitespace
                                has_space_before = (j < i - 1)
                                has_space_after = (k > i + 1)
                                if has_space_before or has_space_after:
                                    is_concat = True

                    if is_concat:
                        result.append(' + ')
                        i += 1
                        continue
            # Fat comma '=>' collapsed as a single text (rare)
            if text == '=>':
                # Inside hash literal, treat as dict colon
                if brace_context_stack and brace_context_stack[-1]:
                    result.append(': ')
                # Inside bracket (list) context, quote the key and use comma
                elif bracket_depth > 0:
                    # Need to quote the previous bareword if it exists
                    j = len(result) - 1
                    while j >= 0 and result[j].strip() == '':
                        j -= 1
                    if j >= 0:
                        prev = result[j].strip()
                        if prev and prev.isidentifier() and prev not in ('True', 'False', 'None'):
                            result[j] = f'"{prev}"'
                    result.append(', ')
                else:
                    # Check if previous token is ] or ) - then it's a pair separator
                    j = len(result) - 1
                    while j >= 0 and result[j].strip() == '':
                        j -= 1
                    if j >= 0 and result[j].strip() in (']', ')'):
                        result.append(', ')
                    else:
                        result.append(' = ')
                i += 1
                continue
            # Track bracket context for list literals
            if text == '[':
                bracket_depth += 1
            elif text == ']':
                bracket_depth = max(0, bracket_depth - 1)
            
            # Track brace context for hash literal detection
            if text == '{':
                # Determine if this is a hash literal or code block
                # Hash literals typically follow: =>, (, [, ,, or start of line
                is_hash_literal = False
                if i > 0:
                    # Look back for previous non-whitespace token
                    j = i - 1
                    while j >= 0 and tokens[j][1] in Token.Text.Whitespace:
                        j -= 1
                    if j >= 0:
                        prev_token = tokens[j][2]
                        # Hash literal indicators
                        if prev_token in ('=>', '>', '(', '[', ',', '='):
                            is_hash_literal = True
                else:
                    # At start, assume hash literal
                    is_hash_literal = True
                brace_context_stack.append(is_hash_literal)
            elif text == '}':
                if brace_context_stack:
                    brace_context_stack.pop()
            # Drop trailing semicolon at end
            if text == ';' and i == len(tokens) - 1:
                i += 1
                continue
            result.append(text)
            i += 1

        rewritten = ''.join(result).rstrip()

        # Post-processing: Apply additional transformations
        import re

        # Convert .with( to .with_params( because 'with' is a Python reserved keyword
        rewritten = re.sub(r'\.with\(', '.with_params(', rewritten)

        # Convert .reduce() to .reduce (property, not method in Python MathObjects)
        # In Perl: ->reduce() and ->reduce are equivalent
        # In Python: reduce is a @property, so calling it with () fails
        rewritten = re.sub(r'\.reduce\(\)', '.reduce', rewritten)

        # Condense spaces around equals from fat comma conversion
        rewritten = re.sub(r'\s+=\s+', ' = ', rewritten)

        # Convert string comparison operators
        # Be careful: these are only operators when surrounded by expressions/values,
        # not variable names. Look for operators preceded/followed by closing parens,
        # numbers, closing brackets, or the words 'not', 'and', 'or'
        # Pattern: (expression) OPERATOR (expression)
        rewritten = re.sub(r'([)\]\w])\s+eq\s+', r'\1 == ', rewritten)
        rewritten = re.sub(r'([)\]\w])\s+ne\s+', r'\1 != ', rewritten)
        rewritten = re.sub(r'([)\]\w])\s+lt\s+', r'\1 < ', rewritten)
        rewritten = re.sub(r'([)\]\w])\s+gt\s+', r'\1 > ', rewritten)
        rewritten = re.sub(r'([)\]\w])\s+le\s+', r'\1 <= ', rewritten)
        rewritten = re.sub(r'([)\]\w])\s+ge\s+', r'\1 >= ', rewritten)

        # Convert ternary operator: cond ? true : false  -->  true if cond else false
        # This is complex because ternaries can appear in various contexts.
        # The key insight: We need to find ternaries at the RIGHT nesting level.
        # For example: `foo(bar, x > 0 ? 1 : 2)` should convert the ternary INSIDE the call.
        def convert_ternaries(text: str) -> str:
            """Recursively convert ternary operators, handling nesting correctly."""
            if '?' not in text or ':' not in text:
                return text
            
            # Find all ? positions and their matching : at the same paren/bracket depth
            depth = 0
            ternary_positions = []  # List of (question_pos, colon_pos) tuples
            
            i = 0
            while i < len(text):
                ch = text[i]
                if ch in '([{':
                    depth += 1
                elif ch in ')]}':
                    depth -= 1
                elif ch == '?' and depth >= 0:
                    # Found a ?, now find its matching :
                    question_depth = depth
                    j = i + 1
                    local_depth = depth
                    while j < len(text):
                        if text[j] in '([{':
                            local_depth += 1
                        elif text[j] in ')]}':
                            local_depth -= 1
                        elif text[j] == ':' and local_depth == question_depth:
                            ternary_positions.append((i, j))
                            break
                        j += 1
                i += 1
            
            # Process ternaries from innermost (rightmost) to outermost
            # This handles nested ternaries correctly
            for question_pos, colon_pos in reversed(ternary_positions):
                # Extract the parts
                # Need to find where this ternary starts (the condition)
                # Work backwards from ? to find the start of the condition
                # The condition starts after the previous operator or delimiter
                
                # Find the start of the condition by working backwards
                cond_start = 0
                depth = 0
                for k in range(question_pos - 1, -1, -1):
                    if text[k] in ')]}':
                        depth += 1
                    elif text[k] in '([{':
                        depth -= 1
                        if depth < 0:
                            # Hit an unmatched opening bracket
                            cond_start = k + 1
                            break
                    elif depth == 0 and text[k] in ',;=(':
                        # Hit a delimiter at depth 0
                        cond_start = k + 1
                        break
                
                # Find the end of the false value
                # Work forward from : to find where it ends
                false_end = len(text)
                depth = 0
                for k in range(colon_pos + 1, len(text)):
                    if text[k] in '([{':
                        depth += 1
                    elif text[k] in ')]}':
                        depth -= 1
                        if depth < 0:
                            # Hit an unmatched closing bracket
                            false_end = k
                            break
                    elif depth == 0 and text[k] in ',;)':
                        # Hit a delimiter at depth 0
                        false_end = k
                        break
                
                cond = text[cond_start:question_pos].strip()
                true_val = text[question_pos + 1:colon_pos].strip()
                false_val = text[colon_pos + 1:false_end].strip()
                
                # Build the replacement
                replacement = f"{true_val} if ({cond}) else {false_val}"
                
                # Replace in the text
                text = text[:cond_start] + replacement + text[false_end:]
                
                # Only process one ternary at a time, then restart
                # (because positions change after replacement)
                if len(ternary_positions) > 1:
                    return convert_ternaries(text)
                
            return text
        
        if '?' in rewritten and ':' in rewritten:
            rewritten = convert_ternaries(rewritten)

        # Convert logical operators
        rewritten = rewritten.replace('||', ' or ')
        rewritten = rewritten.replace('&&', ' and ')

        # Convert Perl $#array (last index) to len(array)-1
        rewritten = re.sub(r'\$\#([a-zA-Z_]\w*)', r'len(\1)-1', rewritten)

        # Convert Perl reference operator ~~& to just the function name
        rewritten = re.sub(r'~~&([a-zA-Z_]\w*)', r'\1', rewritten)

        # Special case: Wrap CapitalizedWord(...) = "string" patterns in parens for tuple pairs
        # This happens with AnswerHints( Formula(...) => "msg", ... )
        rewritten = re.sub(
            r'(?<![a-z])([A-Z][a-zA-Z0-9_]*\([^)]*\))\s*=\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
            r'(\1, \2)',
            rewritten,
        )

        # string literal = value (legacy keyword style) → positional args
        rewritten = re.sub(
            r'"([^"]*?)"\s*=\s*(["\'][^"\']*["\'])',
            r'"\1", \2',
            rewritten,
        )
        rewritten = re.sub(
            r"'([^']*?)'\s*=\s*([\"'][^\"']*[\"'])",
            r"'\1', \2",
            rewritten,
        )

        # Context().functions.add(name => { ... }) expects positional string key
        rewritten = re.sub(
            r'(\.add\(\s*)([a-z_][a-zA-Z0-9_]*)\s*=\s*\{',
            r"\1'\2', {",
            rewritten,
        )

        return rewritten

    # ------------------------------------------------------------------
    # Structured rewriting helpers
    # ------------------------------------------------------------------

    def _try_rewrite_for_loop(
        self, lines: List[str], start_index: int
    ) -> tuple[List[str], int] | None:
        """Rewrite simple Perl for/foreach loops into Python for loops."""
        line = lines[start_index]
        for_match = re.match(
            r"(\s*)(?:for|foreach)\s+(?:my\s+)?([$@%]?[A-Za-z_][\w]*)\s*\(([^)]*)\)\s*\{",
            line,
        )
        if not for_match:
            return None

        indent = for_match.group(1)
        iterator_token = for_match.group(2)
        iterable_expr = for_match.group(3).strip()

        block_lines: List[str] = [line]
        brace_depth = line.count('{') - line.count('}')
        idx = start_index + 1
        while idx < len(lines) and brace_depth > 0:
            current_line = lines[idx]
            block_lines.append(current_line)
            brace_depth += current_line.count('{') - current_line.count('}')
            idx += 1

        if brace_depth != 0:
            return None

        loop_var = self._desigil(iterator_token)
        iterable_py = self._convert_for_iterable(iterable_expr)
        if not iterable_py:
            return None

        body_lines: List[str] = []
        tail_lines: List[str] = []

        open_index = line.find('{')
        if open_index == -1:
            return None

        body_candidates: List[str] = [line[open_index + 1 :]]
        body_candidates.extend(block_lines[1:])

        for idx, candidate in enumerate(body_candidates):
            if candidate is None:
                continue
            candidate_text = candidate.rstrip('\n')
            is_last = idx == len(body_candidates) - 1
            if is_last:
                closing_index = candidate_text.rfind('}')
                if closing_index != -1:
                    body_part = candidate_text[:closing_index].rstrip()
                    if body_part.strip():
                        body_lines.append(body_part)
                    tail = candidate_text[closing_index + 1 :].strip()
                    if tail:
                        tail_lines.append(f"{indent}{tail}")
                else:
                    if candidate_text.strip():
                        body_lines.append(candidate_text)
            else:
                if candidate_text.strip():
                    body_lines.append(candidate_text)

        compiled_body_lines: List[str] = []
        body_indent = indent + '    '
        for body_line in body_lines:
            compiled = self._compile_line(body_line)
            for compiled_line in compiled:
                stripped_total = compiled_line.strip()
                if not stripped_total:
                    continue
                inner_indent, inner_body = self._split_indent(compiled_line)
                inner_body = re.sub(r'^my\s+', '', inner_body)
                compiled_body_lines.append(f"{body_indent}{inner_indent}{inner_body}")

        if not compiled_body_lines:
            compiled_body_lines.append(f"{body_indent}pass")

        rewritten_loop = [f"{indent}for {loop_var} in {iterable_py}:"]
        rewritten_loop.extend(compiled_body_lines)

        for tail_line in tail_lines:
            tail_compiled = self._compile_line(tail_line)
            rewritten_loop.extend(tail_compiled)

        return rewritten_loop, len(block_lines)

    def _convert_for_iterable(self, iterable_expr: str) -> str | None:
        expr = iterable_expr.strip()
        if not expr:
            return None

        if '..' in expr:
            start_raw, end_raw = expr.split('..', 1)
            start_py = self._convert_range_bound(start_raw.strip())
            end_py = self._convert_range_bound(end_raw.strip())
            if start_py is None or end_py is None:
                return None
            return f"range({start_py}, ({end_py}) + 1)"

        if expr.startswith('$#'):
            array_name = expr[2:].strip()
            if array_name.startswith('{') and array_name.endswith('}'):
                array_name = array_name[1:-1].strip()
            array_py = self._desigil(f'@{array_name}')
            return f"len({array_py}) - 1"

        compiled = self._compile_expr(expr).strip()
        if compiled.startswith('(') and compiled.endswith(')'):
            compiled = compiled[1:-1]
        return compiled

    def _convert_range_bound(self, expr: str) -> str | None:
        expr = expr.strip()
        if not expr:
            return '0'

        if expr.startswith('$#'):
            array_name = expr[2:].strip()
            if array_name.startswith('{') and array_name.endswith('}'):
                array_name = array_name[1:-1].strip()
            array_py = self._desigil(f'@{array_name}')
            return f"len({array_py}) - 1"

        if expr.startswith('$') or expr.startswith('@'):
            return self._desigil(expr)

        compiled = self._compile_expr(expr).strip()
        if compiled.startswith('(') and compiled.endswith(')'):
            compiled = compiled[1:-1]
        return compiled

    def _rewrite_statement(self, line: str) -> str:
        """Rewrite a single Perl-like statement using Pygments and helpers."""
        indent, body = self._split_indent(line)
        stripped = body.strip()
        if not stripped:
            return ''
        if stripped.startswith('#'):
            return line
        if 'loadMacros' in stripped:
            cleaned = self._strip_load_macros(stripped)
            if not cleaned:
                return ''
            stripped = cleaned
        if stripped == '}':
            return ''
        if re.fullmatch(r'\}\s*else\s*\{', stripped):
            return f'{indent}else:'

        control = self._rewrite_control_flow(indent, stripped)
        if control is not None:
            return control

        rewritten = self._rewrite_with_pygments(body)
        # Apply string interpolation (still needed for token-level $var → f-string)
        rewritten = self._convert_string_interpolation(rewritten)
        return indent + rewritten if rewritten else ''

    def _split_indent(self, line: str) -> tuple[str, str]:
        match = re.match(r'(\s*)(.*)', line)
        if not match:
            return '', line
        return match.group(1), match.group(2)

    def _strip_load_macros(self, line: str) -> str:
        if 'loadMacros' not in line:
            return line
        parts = [part for part in line.split(';') if 'loadMacros' not in part]
        return '; '.join(part.strip() for part in parts if part.strip())

    def _rewrite_control_flow(self, indent: str, stripped: str) -> str | None:
        header_keywords = ('if', 'elsif', 'unless', 'while')
        for keyword in header_keywords:
            if stripped.startswith(keyword):
                parsed = self._parse_conditional_header(stripped, keyword)
                if not parsed:
                    break
                rest, condition, tail = parsed
                cond_py = self._compile_expr(condition)
                # Strip outer parens if already present (binary exprs add them)
                if cond_py.startswith('(') and cond_py.endswith(')'):
                    cond_py = cond_py[1:-1]
                py_keyword = keyword
                if keyword == 'elsif':
                    py_keyword = 'elif'
                elif keyword == 'unless':
                    py_keyword = 'if not'
                header = f'{indent}{py_keyword} ({cond_py}):'
                tail = tail.strip()
                if tail:
                    rewritten_tail = self._rewrite_statement(f'{indent}    {tail}')
                    if rewritten_tail:
                        return f"{header}\n{rewritten_tail}"
                return header
        return None

    def _parse_conditional_header(self, stripped: str, keyword: str) -> tuple[str, str, str] | None:
        prefix_len = len(keyword)
        remainder = stripped[prefix_len:].lstrip()
        if not remainder.startswith('('):
            return None
        depth = 0
        condition_chars: List[str] = []
        tail_start = None
        for idx, ch in enumerate(remainder):
            if ch == '(':
                depth += 1
                if depth == 1:
                    continue
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    tail_start = idx + 1
                    break
            if depth >= 1:
                condition_chars.append(ch)
        if tail_start is None:
            return None
        condition = ''.join(condition_chars).strip()
        tail = remainder[tail_start:].lstrip()
        if tail.startswith('{'):
            tail = tail[1:].lstrip()
        if tail.endswith('}'):
            tail = tail[:-1].rstrip()
        return keyword, condition, tail

    def _convert_string_interpolation(self, line: str) -> str:
        def repl(match: re.Match[str]) -> str:
            quote = match.group(1)
            content = match.group(2)
            if quote == '"' and '$' in content:
                escaped = content.replace('{', '{{').replace('}', '}}')
                converted = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'{\1}', escaped)
                return f'f"{converted}"'
            return match.group(0)

        return re.sub(r'(["\'])((?:[^\\]|\\.)*?)\1', repl, line)

    # ------------------------------------------------------------------
    # Text block processing
    # ------------------------------------------------------------------

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
        segments: List[str] = []
        pos = 0
        while pos < len(content):
            var_match = re.search(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', content[pos:])
            func_match = re.search(r'\\{([^}]+)\\}', content[pos:])
            next_var_pos = pos + var_match.start() if var_match else len(content)
            next_func_pos = pos + func_match.start() if func_match else len(content)
            if next_var_pos < next_func_pos:
                if next_var_pos > pos:
                    text_segment = content[pos:next_var_pos]
                    segments.append(repr(text_segment))
                var_name = var_match.group(1)
                if var_name in ('PAR', 'BR', 'BBOLD', 'EBOLD', 'BITALIC', 'EITALIC', 'BCENTER', 'ECENTER', 'BUL', 'EUL'):
                    segments.append(f"{var_name}()")
                else:
                    segments.append(f"str({var_name})")
                pos = next_var_pos + len(var_match.group(0))
            elif next_func_pos < len(content):
                if next_func_pos > pos:
                    text_segment = content[pos:next_func_pos]
                    segments.append(repr(text_segment))
                func_code = func_match.group(1).strip()
                transformed_code = self._compile_expr(func_code)
                segments.append(transformed_code)
                pos = next_func_pos + len(func_match.group(0))
            else:
                if pos < len(content):
                    text_segment = content[pos:]
                    segments.append(repr(text_segment))
                break
        if not segments:
            return '""'
        return ', '.join(segments)

    def _escape_triple_quotes(self, text: str) -> str:
        """Escape special characters in text for Python triple quoted string literals."""
        text = text.replace("\\", "\\\\")
        text = text.replace("'''", "\'\'\'")
        text = text.replace('"""', '\"\"\"')
        return text

    def _strip_inline_comment(self, line: str) -> str:
        """
        Remove inline Perl/Python comments from a line.

        This is needed when joining multi-line statements to prevent comments
        from eating subsequent code. For example:
            func(arg1,    # comment
                 arg2)
        Should become:
            func(arg1, arg2)
        Not:
            func(arg1,    # comment arg2)

        Args:
            line: Line potentially containing # comment

        Returns:
            Line with inline comment removed, trailing whitespace stripped
        """
        # Find # that's not inside a string
        in_string = False
        string_char = None
        escaped = False

        for i, char in enumerate(line):
            if escaped:
                escaped = False
                continue

            if char == '\\':
                escaped = True
                continue

            if char in ('"', "'"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None

            elif char == '#' and not in_string:
                # Check if this is a comment or the $# operator
                # $# is a Perl operator for array last index, not a comment
                if i > 0 and line[i-1] == '$':
                    # This is $#, not a comment - continue processing
                    continue
                # Found comment start - return everything before it
                return line[:i].rstrip()

        # No comment found
        return line.rstrip()


    def _transform_pgml_evaluators(self, pgml_content: str) -> str:
        """Transform Perl syntax to Python in PGML evaluator expressions."""
        import re
        result: List[str] = []
        i = 0
        while i < len(pgml_content):
            if pgml_content[i] == '{':
                brace_depth = 1
                j = i + 1
                while j < len(pgml_content) and brace_depth > 0:
                    if pgml_content[j] == '{':
                        brace_depth += 1
                    elif pgml_content[j] == '}':
                        brace_depth -= 1
                        if brace_depth == 0:
                            break
                    j += 1
                if brace_depth == 0:
                    code_block = pgml_content[i+1:j]
                    transformed = code_block.replace('->', '.').replace('::', '.')
                    transformed = re.sub(r'\$([a-zA-Z_]\w*)', r'\1', transformed)
                    result.append('{')
                    result.append(transformed)
                    result.append('}')
                    i = j + 1
                    continue
            result.append(pgml_content[i])
            i += 1
        return ''.join(result)

    def _convert_heredocs_global(self, pg_source: str) -> str:
        """Convert Perl heredocs (<<END_MARKER) to Python triple-quoted strings at the source level.
        
        Processes the entire source before line splitting to handle heredocs properly.
        
        Converts:
            HEADER_TEXT(MODES(TeX => '', HTML => <<END_STYLE));
            <style>...</style>
            END_STYLE
        
        To a form like:
            HEADER_TEXT(MODES(TeX => '', HTML => '''<style>
            
            </style>'''))
        
        Note: The result will be re-split into lines by the caller, so embedded newlines
        in the triple-quoted strings are preserved.
        """
        import re as re_module
        
        lines = pg_source.split('\n')
        result_lines: List[str] = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line contains a heredoc start (<<MARKER)
            heredoc_match = re_module.search(r'<<([A-Z_][A-Z0-9_]*)', line)
            if heredoc_match:
                marker = heredoc_match.group(1)
                
                # Split the line at the heredoc marker
                before = line[:heredoc_match.start()]
                after_marker = line[heredoc_match.end():]  # Everything after <<MARKER on same line
                
                # Collect the content until we find the marker on its own line
                content_lines: List[str] = []
                i += 1
                while i < len(lines):
                    current = lines[i]
                    # Check if this line is just the marker (with optional whitespace)
                    if re_module.match(rf'^\s*{re_module.escape(marker)}\s*$', current):
                        break
                    content_lines.append(current)
                    i += 1
                
                # Build the replacement: join content with actual newlines
                content = '\n'.join(content_lines)
                # Escape backslashes in the content (for regex characters, etc.)
                content = content.replace('\\', '\\\\')
                # Escape triple quotes
                content = content.replace("'''", "\\'''")
                
                # Build the new line with triple-quoted string
                # Include the content with embedded newlines
                new_line = f"{before}'''{content}'''{after_marker}"
                result_lines.append(new_line)
            else:
                result_lines.append(line)
            
            i += 1
        
        return '\n'.join(result_lines)

    def _transform_load_macros(self, macro_list_str: str) -> Tuple[List[str], str]:
        """Transform loadMacros() call to Python imports."""
        import re
        macros = re.findall(r'"([^"]+)"|\'([^\']+)\'', macro_list_str)
        # Flatten the tuples into a single list of strings
        flattened = []
        for a, b in macros:
            flattened.append(a or b)
        macro_imports = {
            "PG.pl": "from pg_macros.core.pg_core import DOCUMENT, TEXT, ANS, ENDDOCUMENT, SOLUTION, HINT",
            "PGstandard.pl": "from pg_macros.answers.pg_answer_macros import num_cmp, str_cmp, fun_cmp",
            "PGbasicmacros.pl": "from pg_macros.core.pg_basic_macros import ans_rule, beginproblem, PAR",
            "MathObjects.pl": "from pg_math import Context, Real, Complex, Formula, Interval",
            "PGML.pl": "from pg_pgml import PGML",
            "contextFraction.pl": "from pg_math import Fraction",
            "PGcourse.pl": "# PGcourse.pl - course-specific (skipped)",
        }
        import_lines: List[str] = []
        loaded_macros: List[str] = []
        for macro in flattened:
            if macro in macro_imports:
                imp = macro_imports[macro]
                if not imp.startswith('#'):
                    import_lines.append(imp)
                loaded_macros.append(macro)
        comment = (f"# loadMacros({', '.join(repr(m) for m in loaded_macros)}) - loaded"
                   if loaded_macros else "# loadMacros() - no recognized macros")
        return import_lines, comment


def convert_pg_file(
    source_path: str | Path,
    *,
    output_path: str | Path | None = None,
    use_sandbox_macros: bool = True,
    overwrite: bool = False,
    encoding: str = "utf-8",
    preprocessor: PGPreprocessor | None = None,
) -> tuple[Path, PreprocessResult]:
    """Convert a .pg file to Python using the Pygments/Lark preprocessor."""

    pg_path = Path(source_path)
    if not pg_path.exists():
        raise FileNotFoundError(f"PG source file not found: {pg_path}")

    processor = preprocessor or PGPreprocessor()
    pg_source = pg_path.read_text(encoding=encoding)
    result = processor.preprocess(pg_source, use_sandbox_macros=use_sandbox_macros)

    output = Path(output_path) if output_path else pg_path.with_suffix('.pyg')
    if output.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.code, encoding=encoding)
    return output, result
