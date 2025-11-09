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
                        if stripped_no_comment and stripped_no_comment[-1] in '=,([':
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
                            open_count = (
                                check_line.count('(')
                                + check_line.count('[')
                                + check_line.count('{')
                            )
                            close_count = (
                                check_line.count(')')
                                + check_line.count(']')
                                + check_line.count('}')
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
            line_map[output_line_num] = i + 1

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
                closure_lines = [original_line]
                brace_depth = original_line.count('{') - original_line.count('}')
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
                
                # Check if there's a continuation line after the closure (like );)
                continuation_suffix = ''
                if i < len(lines):
                    next_line = lines[i].strip()
                    # Check for closing syntax like );
                    if re.match(r'^\s*\);?\s*$', lines[i]):
                        continuation_suffix = ' ' + next_line
                        i += 1  # Skip this line since we're incorporating it
                
                param_match = re.search(r'(\w+)\s*=>\s*sub\s*\{', first_line)
                if param_match:
                    sub_start = first_line.find('sub')
                    prefix = first_line[:sub_start]
                    suffix = ''
                    close_brace_match = re.search(r'\}(.*)$', last_line)
                    if close_brace_match:
                        suffix = close_brace_match.group(1)
                    
                    # Add any continuation suffix
                    suffix += continuation_suffix
                    
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
                # do-until means: execute body, then repeat UNTIL condition is true
                # In Python: while True: body; if condition: break
                output_lines.append(f'while True:')
                for bl in body_lines:
                    output_lines.append('    ' + bl)
                output_lines.append(f'    if {compiled_cond}:')
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
                if until_match:
                    condition = until_match.group(1).strip()
                    # Extract body lines: remove 'do {' and '} until (...)'
                    inner_lines: List[str] = []
                    # Remove the first line's 'do {'
                    first_body = re.sub(r'^\s*do\s*\{', '', block_lines[0]).strip()
                    if first_body:
                        inner_lines.append(first_body)
                    # Middle lines
                    for middle in block_lines[1:-1]:
                        inner_lines.append(middle)
                    # Remove the closing pattern
                    last_body = re.sub(r'\}\s*until\s*\([^)]+\)\s*', '', last_line).strip()
                    if last_body:
                        inner_lines.append(last_body)
                    # Compile body lines
                    compiled_body: List[str] = []
                    for ln in inner_lines:
                        compiled_body.extend(self._compile_line(ln))
                    compiled_cond = self._compile_expr(condition)
                    # Emit Python loop: do-until means execute body, then repeat UNTIL condition is true
                    # In Python: while True: body; if condition: break
                    output_lines.append(f'while True:')
                    for cb in compiled_body:
                        output_lines.append('    ' + cb)
                    output_lines.append(f'    if {compiled_cond}:')
                    output_lines.append('        break')
                    continue
                else:
                    # Not a proper do-until, fall through: rewind index to process lines normally
                    i = i - len(block_lines) + 1

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
            do_until_stmt: "do" block "until" "(" expr ")"

            block: "{" (stmt ";"?)* "}"

            // Statement modifiers (trailing conditionals)
            stmt_modifier: simple_stmt ("if"|"unless") expr
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

            ?or_expr: and_expr (("||" | "or") and_expr)*      -> binary_expr
            ?and_expr: comp_expr (("&&" | "and") comp_expr)*  -> binary_expr

            // Comparison operators (eq, ne, lt, gt, le, ge, ==, !=, <, >, <=, >=)
            ?comp_expr: range_expr (comp_op range_expr)*     -> binary_expr
            comp_op: "eq" | "ne" | "lt" | "gt" | "le" | "ge"
                   | "==" | "!=" | "<" | ">" | "<=" | ">="

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

            regex_literal: "qr" "/" /[^\/]+/ "/" REGEX_FLAGS?  -> regex_literal

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
            def stmt_modifier(self, stmt, modifier, condition):
                """Lower statement modifier (trailing if/unless)."""
                return ("stmt_modifier", stmt, modifier, condition)

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
            def add_op(self, tok):
                """Extract add operator token."""
                return tok

            def mul_op(self, tok):
                """Extract mul operator token."""
                return tok

            def comp_op(self, tok):
                """Extract comparison operator token."""
                return tok

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
            def regex_literal(self, pattern, flags):
                """Lower regex literal: qr/pattern/flags."""
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
        # Manual parse for simple assignments and calls
        manual_ir = self._manual_parse_line(stripped)
        if manual_ir is not None:
            out = self._emit_ir(manual_ir)
            if out is None:
                return []
            if indent_prefix:
                out = indent_prefix + out
            return [out]

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
            lines.append(f"{ind}    if {cond_py}:")
            lines.append(f"{ind}        break")
            return "\n".join(lines)

        if typ == "stmt_modifier":
            _, stmt, modifier, condition = ir
            stmt_py = self._emit_ir(stmt, indent)
            cond_py = self._expr_to_py(condition)
            if modifier == "if":
                return f"{ind}if {cond_py}: {stmt_py.strip()}"
            else:  # unless
                return f"{ind}if not ({cond_py}): {stmt_py.strip()}"

        # Assignments
        if typ == "assign":
            _, var, expr = ir
            var_name = self._desigil(var[1] if isinstance(var, tuple) else var)
            expr_py = self._expr_to_py(expr)
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

                if op[0] == "method_call":
                    _, method_name, args = op
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
                # Escape quotes in pattern
                escaped_pattern = pattern.replace('"', '\\"')
                return f'r"{escaped_pattern}"'

            # Expression statements
            if head == "expr":
                return self._expr_to_py(expr[1])

            # Assignments (in expression context)
            if head == "assign":
                _, var, val = expr
                return f"{self._desigil(var[1])} = {self._expr_to_py(val)}"

        # Otherwise, treat as raw string and apply rewrite
        rewritten = self._rewrite_with_pygments(str(expr))
        # Apply post-processing transformations
        rewritten = self._convert_string_operators(rewritten)
        return rewritten

    # ------------------------------------------------------------------
    # Pygments based rewriting
    # ------------------------------------------------------------------

    def _desigil(self, name: str) -> str:
        """Remove leading sigil characters from Perl variable names."""
        if name and name[0] in "$@%":
            return name[1:]
        return name

    def _rewrite_with_pygments(self, code: str) -> str:
        """Fallback rewrite using Pygments for conservative token replacement."""
        tokens = list(self._perl_lexer.get_tokens_unprocessed(code))
        result: List[str] = []
        i = 0
        while i < len(tokens):
            _, ttype, text = tokens[i]
            # Preserve comments verbatim
            if ttype in Token.Comment:
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
            # Variables: remove sigil
            if ttype in Token.Name.Variable:
                result.append(self._desigil(text))
                i += 1
                continue
            # Hash access: $h{key} -> h['key']
            if text == '{' and i > 0 and tokens[i-1][1] in Token.Name.Variable:
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
                    result.append('.')
                    i += 2
                    # Skip any empty tokens after ->
                    while i < len(tokens) and tokens[i][2] == '':
                        i += 1
                    # Check if next token is a method name without ()
                    # Only add () if it's NOT followed by another -> (chained calls)
                    if i < len(tokens):
                        next_idx, next_ttype, next_text = tokens[i]
                        # If it's a method/property name
                        if next_ttype in Token.Name or next_ttype == Token.Operator.Word:
                            # Look ahead to see what follows (skip empty tokens)
                            j = i + 1
                            while j < len(tokens) and tokens[j][2] == '':
                                j += 1
                            has_parens = False
                            has_arrow = False
                            if j < len(tokens):
                                lookahead_idx, lookahead_ttype, lookahead_text = tokens[j]
                                if lookahead_text == '(':
                                    has_parens = True
                                elif lookahead_text == '-' and j + 1 < len(tokens) and tokens[j + 1][2] == '>':
                                    has_arrow = True  # Another -> follows, so this is property access
                            # Only add () if no parens AND no arrow (i.e., final method in chain)
                            if not has_parens and not has_arrow:
                                result.append(next_text)
                                result.append('()')
                                i += 1
                                continue
                    continue
                # Handle namespace separator '::'
                if text == ':' and i + 1 < len(tokens) and tokens[i+1][2] == ':':
                    result.append('.')
                    i += 2
                    continue
                # Handle fat comma '=>'
                if text == '=' and i + 1 < len(tokens) and tokens[i+1][2] == '>':
                    result.append(' = ')
                    i += 2
                    continue
            # Fat comma '=>' collapsed as a single text (rare)
            if text == '=>':
                result.append(' = ')
                i += 1
                continue
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

        # Condense spaces around equals from fat comma conversion
        rewritten = re.sub(r'\s+=\s+', ' = ', rewritten)

        # Convert string comparison operators
        rewritten = re.sub(r'\beq\b', '==', rewritten)
        rewritten = re.sub(r'\bne\b', '!=', rewritten)
        rewritten = re.sub(r'\ble\b', '<=', rewritten)
        rewritten = re.sub(r'\bge\b', '>=', rewritten)

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
        rewritten = self._convert_string_operators(rewritten)
        rewritten = self._convert_string_interpolation(rewritten)
        rewritten = self._convert_string_comparisons(rewritten)
        rewritten = self._convert_regex_literals(rewritten)
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

    def _convert_string_operators(self, line: str) -> str:
        line = re.sub(r'(?<=\S)\s+\.\s+(?=\S)', ' + ', line)
        line = re.sub(r'(?<=\S)\s+x\s+(?=\S)', ' * ', line)
        return line

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

    def _convert_string_comparisons(self, line: str) -> str:
        replacements = {
            r'\beq\b': '==',
            r'\bne\b': '!=',
            r'\blt\b': '<',
            r'\bgt\b': '>',
            r'\ble\b': '<=',
            r'\bge\b': '>=',
        }
        for pattern, replacement in replacements.items():
            line = re.sub(pattern, replacement, line)
        return line

    def _convert_regex_literals(self, line: str) -> str:
        def repl(match: re.Match[str]) -> str:
            pattern = match.group(1)
            escaped = pattern.replace('"', '\\"')
            return f'r"{escaped}"'

        return re.sub(r'qr/([^/]+)/\w*', repl, line)

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


    # ------------------------------------------------------------------
    # Manual parsing fallback
    # ------------------------------------------------------------------

    def _manual_parse_line(self, line: str) -> Optional[Tuple[str, Any, Any]]:
        """
        Manual parser for simple PG statements.  Used when Lark is not
        available.  This recognises assignments of the form:

            my $x = expr
            $x = expr

        and function calls like `FOO(arg1, arg2)` as well as
        DOCUMENT()/ENDDOCUMENT().  All other constructs return None
        so that the caller can fall back to the Pygments rewrite.

        Returns:
            A tuple representing an IR node, or None if the line is not recognised.
        """
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            return None
        # Assignment or declaration: my $x = expr; or $x = expr;
        m = re.match(r'^(?:my\s+)?([\$@%][A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$', stripped)
        if m:
            var_name = m.group(1)
            expr = m.group(2).rstrip(';').strip()
            # Represent variable as a tuple consistent with VAR token
            return ("assign", ("var", var_name), expr)
        # Function call: NAME(args)
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*;?\s*$', stripped)
        if m:
            name = m.group(1)
            args_str = m.group(2).strip()
            args: List[str] = []
            if args_str:
                # Split by commas not inside parentheses or quotes
                # This naive splitter is sufficient for typical PG calls
                depth = 0
                start = 0
                for i, ch in enumerate(args_str):
                    if ch == '(':
                        depth += 1
                    elif ch == ')':
                        depth -= 1
                    elif ch == ',' and depth == 0:
                        args.append(args_str[start:i].strip())
                        start = i + 1
                args.append(args_str[start:].strip())
            # Special case: loadMacros should be dropped (handled elsewhere)
            if name == 'loadMacros':
                return ("noop", )
            return ("call", name, args)
        # DOCUMENT and ENDDOCUMENT as calls
        if re.match(r'^DOCUMENT\(\s*\)$', stripped):
            return ("call", "DOCUMENT", [])
        if re.match(r'^ENDDOCUMENT\(\s*\)$', stripped):
            return ("call", "ENDDOCUMENT", [])
        return None

    # ------------------------------------------------------------------
    # Text block processing (unchanged from original)
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
