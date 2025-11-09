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
                while i < len(lines) and brace_depth > 0:
                    current_line = lines[i]
                    closure_lines.append(current_line)
                    brace_depth += current_line.count('{') - current_line.count('}')
                    i += 1

                first_line = closure_lines[0]
                last_line = closure_lines[-1] if closure_lines else ''
                param_match = re.search(r'(\w+)\s*=>\s*sub\s*\{', first_line)
                if param_match:
                    sub_start = first_line.find('sub')
                    prefix = first_line[:sub_start]
                    suffix = ''
                    close_brace_match = re.search(r'\}(.*)$', last_line)
                    if close_brace_match:
                        suffix = close_brace_match.group(1)
                    stubbed_line = f"{prefix}lambda *args, **kwargs: None{suffix}"
                    transformed = self._legacy_transform_line(stubbed_line)
                    if transformed:
                        stub_lines = transformed.split('\n')
                        for idx, stub_line in enumerate(stub_lines):
                            if idx == len(stub_lines) - 1:
                                output_lines.append(f"{stub_line}  # Stubbed Perl closure")
                            else:
                                output_lines.append(stub_line)
                else:
                    assign_match = re.search(r'(\w+)\s*=\s*sub\s*\{', first_line)
                    if assign_match:
                        var_name = assign_match.group(1)
                        indent_match = re.match(r'^(\s*)', first_line)
                        indent = indent_match.group(1) if indent_match else ''
                        stubbed_line = f"{indent}{var_name} = lambda *args, **kwargs: None"
                        transformed = self._legacy_transform_line(stubbed_line)
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
                output_lines.append(f'while True:')
                for bl in body_lines:
                    output_lines.append('    ' + bl)
                output_lines.append(f'    if not ({compiled_cond}):')
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
                    # Emit Python loop
                    output_lines.append(f'while not ({compiled_cond}):')
                    for cb in compiled_body:
                        output_lines.append('    ' + cb)
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
        """Return the Lark grammar for parsing simple PG statements.

        The grammar is designed to avoid reduce/reduce conflicts by not
        allowing function calls to appear both as top-level statements
        and as unary expressions.  Instead, calls are always parsed
        as expressions (call_expr) and then wrapped into an expr_stmt
        when they appear as standalone statements.  This grammar is
        intentionally permissive; unknown constructs fall back to the
        Pygments rewrite.
        """
        return r"""
            start: (stmt ";"?)*

            stmt: decl
                | assign
                | expr_stmt
                | document
                | enddocument

            document: "DOCUMENT" "(" ")"            -> document_call
            enddocument: "ENDDOCUMENT" "(" ")"      -> enddocument_call
            loadmacros: "loadMacros" "(" /[^)]*/ ")" -> loadmacros_call

            decl: "my" var "=" expr               -> assign_stmt
            assign: var "=" expr                -> assign_stmt
            expr_stmt: expr                      -> expr_stmt

            args: expr ("," expr)*

            ?expr: or_expr
            ?or_expr: and_expr ("||" and_expr)*      -> binary_expr
            ?and_expr: add_expr ("&&" add_expr)*     -> binary_expr
            ?add_expr: mul_expr (("+"|"-"|".") mul_expr)* -> binary_expr
            ?mul_expr: unary_expr (("*"|"/"|"%") unary_expr)* -> binary_expr
            ?unary_expr: call_expr | var | atom

            call_expr: NAME "(" args? ")"          -> call_expr

            var: VAR
            atom: NUMBER | STRING | NAME

            NAME: /[A-Za-z_][A-Za-z0-9_]*/
            VAR: /[\$@%][A-Za-z_][A-Za-z0-9_]*/
            STRING: /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/
            NUMBER: /[0-9]+(?:\.[0-9]+)?/

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
                # Lark wraps the top-level rule in a Tree; return a plain list
                return list(stmts)

            def stmt(self, item):
                """Unwrap the single child of a stmt production."""
                # Each stmt rule has exactly one child (the IR tuple)
                return item
            def document_call(self):
                return ("call", "DOCUMENT", [])

            def enddocument_call(self):
                return ("call", "ENDDOCUMENT", [])

            def loadmacros_call(self, *args):
                # loadMacros calls are dropped in sandbox mode; produce no output
                return ("noop", )

            def assign_stmt(self, var, expr):
                """Lower a variable declaration or assignment."""
                return ("assign", var, expr)

            def call_expr(self, name, *args):
                """Lower a function call expression."""
                arglist = args[0] if args else []
                return ("call", name, arglist)

            def expr_stmt(self, expr):
                """Lower an expression statement (e.g. a call used as a statement)."""
                return ("expr", expr)

            def binary_expr(self, left, *rest):
                # Combine binary operations; for now just fold into a list for later reconstruction
                expr = left
                for op, right in zip(rest[::2], rest[1::2]):
                    expr = ("bin", expr, op, right)
                return expr

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
                """Unwrap the var rule to return its child (the ('var', name) tuple)."""
                return child

            def atom(self, child):
                """Unwrap the atom rule to return its child (string or token)."""
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

        legacy_output = self._legacy_transform_line(line)
        if legacy_output != line or not legacy_output:
            if not legacy_output:
                return []
            return legacy_output.split('\n')

        # Fall back to Pygments rewrite
        rewritten = self._rewrite_with_pygments(stripped)
        if not rewritten:
            return []
        if indent_prefix:
            rewritten = indent_prefix + rewritten
        return [rewritten]

    def _compile_expr(self, expr: str) -> str:
        """Compile a small expression using the grammar or fallback rewrite.

        Returns a string containing Python code representing the expression.
        """
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
        """Convert IR nodes into Python code lines.  Returns None for no output."""
        typ = ir[0]
        if typ == "noop":
            return None
        if typ == "assign":
            _, var, expr = ir
            var_name = self._desigil(var[1] if isinstance(var, tuple) else var)
            expr_py = self._expr_to_py(expr)
            return f"{var_name} = {expr_py}"
        if typ == "call":
            _, name, args = ir
            # Special case: skip empty loadMacros calls
            if name == "loadMacros":
                return None
            py_args = []
            for a in args:
                py_args.append(self._expr_to_py(a))
            return f"{name}({', '.join(py_args)})"
        if typ == "expr":
            _, expr = ir
            return self._expr_to_py(expr)
        if typ == "bin":
            return self._expr_to_py(ir)
        # Unknown IR: produce raw comment
        return f"# {ir}"

    def _expr_to_py(self, expr: Any) -> str:
        """Lower an expression IR into a Python expression string."""
        if isinstance(expr, tuple):
            head = expr[0]
            if head == "var":
                # expr[1] contains the original sigiled name
                return self._desigil(expr[1])
            if head == "bin":
                _, left, op, right = expr
                py_left = self._expr_to_py(left)
                py_right = self._expr_to_py(right)
                # Convert Perl string concat '.' to Python '+'
                if op in ("eq", "ne", "lt", "gt"):
                    op_map = {"eq": "==", "ne": "!=", "lt": "<", "gt": ">"}
                    py_op = op_map[op]
                elif op == ".":
                    py_op = "+"
                else:
                    py_op = op
                return f"({py_left} {py_op} {py_right})"
            if head == "call":
                _, name, args = expr
                arg_strings = [self._expr_to_py(a) for a in args]
                return f"{name}({', '.join(arg_strings)})"
            if head == "expr":
                return self._expr_to_py(expr[1])
            if head == "assign":
                _, var, val = expr
                return f"{self._desigil(var[1])} = {self._expr_to_py(val)}"
        # Otherwise, treat as raw string and apply rewrite
        return self._rewrite_with_pygments(str(expr))

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
            # Strings are left untouched
            if ttype in Token.Literal.String:
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
        # Condense spaces around equals inserted from fat comma conversion
        # e.g. "k  =  k" -> "k = k"
        rewritten = re.sub(r'\s+=\s+', ' = ', rewritten)
        return rewritten

    def _legacy_transform_line(self, line: str) -> str:
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

        # Handle } else { followed by content → split into else: and content on next line
        # This happens when line joining joins } else { with the next line
        else_match = re.match(r'^(\s*)\}\s*else\s*\{\s*(.+)$', line)
        if else_match:
            # Return just "else:" and let the content be handled separately
            # But we can't split it here since we return a single line
            # Instead, we'll need to NOT join these lines in the first place
            # For now, just handle the transformation
            indent = else_match.group(1)
            rest = else_match.group(2)
            # Transform the rest and return as "else: <content>" but that's not valid Python
            # We need to return multiple lines, but _transform_line returns a single string
            # WORKAROUND: Return with embedded newline
            transformed_rest = self._legacy_transform_line(rest)
            return f'{indent}else:\n{indent}    {transformed_rest}'
        
        # Handle } else { → else:
        else_bracket_match = re.match(r'^\s*\}\s*else\s*\{\s*$', line)
        if else_bracket_match:
            # Don't preserve indentation - else should be at same level as if
            return 'else:'
        
        # Handle multi-line if statements: if (...) { → if (...)  :
        # This handles if blocks that span multiple lines (body on next line)
        if_block_match = re.match(r'^(\s*)(if|elsif|while|for|foreach|until|unless)\s*\(([^)]+)\)\s*\{\s*(.*)$', line, re.IGNORECASE)
        if if_block_match:
            indent = if_block_match.group(1)
            keyword = if_block_match.group(2).lower()
            condition = if_block_match.group(3)
            rest = if_block_match.group(4).strip()
            
            # Convert elsif → elif
            if keyword == 'elsif':
                keyword = 'elif'
            # Convert unless → if not
            if keyword == 'unless':
                keyword = 'if not'
            
            # If there's content after the {, we need to handle it differently
            # For now, just convert the opening line
            if rest:
                # Single-line block with content: if (...) { stmt
                # This will be handled by inline-if pattern or needs special handling
                # For now, convert to: if (...): stmt
                transformed_condition = self._legacy_transform_line(condition)
                transformed_rest = self._legacy_transform_line(rest)
                return f'{indent}{keyword} ({transformed_condition}):\n{indent}    {transformed_rest}'
            else:
                # Multi-line block: if (...) {
                # Convert to: if (...):
                transformed_condition = self._legacy_transform_line(condition)
                return f'{indent}{keyword} ({transformed_condition}):'
        
        # Handle closing braces (convert to pass or remove)
        if re.match(r'^\s*\}\s*$', line):
            return ''  # Remove standalone closing braces
        
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
                    # First, escape literal braces that should remain as-is
                    # In f-strings, { and } need to be {{ and }} if they're literal
                    # We need to escape braces BEFORE converting $var to {var}
                    escaped_content = content.replace('{', '{{').replace('}', '}}')
                    
                    # Now convert $var to {var} - these will be unescaped single braces
                    new_content = re.sub(
                        r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'{\1}', escaped_content)
                    return f'f"{new_content}"'

            # Return as-is for single quotes or strings without variables
            return match.group(0)

        # Match strings carefully (handle escaped quotes)
        line = re.sub(r'(["\'])([^\1]*?)\1',
                      convert_string_interpolation, line)

        # Transform Perl $#array (last index): $#arr → len(arr)-1
        # Must do BEFORE stripping $ sigils
        # Example: random(0, $#functions) → random(0, len(functions)-1)
        line = re.sub(r'\$\#([a-zA-Z_][a-zA-Z0-9_]*)', r'len(\1)-1', line)

        # Transform Perl reference operator: ~~&func → func
        # Example: install_problem_grader(~~&custom_grader) → install_problem_grader(custom_grader)
        # In Perl, ~~& creates a reference to a subroutine; in Python, just use the function name
        line = re.sub(r'~~&([a-zA-Z_][a-zA-Z0-9_]*)', r'\1', line)

        # Transform Perl scalar variables: $var → var (outside of strings now)
        # Use negative lookbehind to avoid matching in strings
        line = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'\1', line)

        # Transform Perl logical operators: || → or, && → and
        # These are used in conditionals: if (x != 0 || y != 0)
        # Be careful not to match inside strings (already handled by string protection)
        line = line.replace('||', ' or ')
        line = line.replace('&&', ' and ')

        # Transform Perl method call operator: -> → .
        # Special case: ->with( becomes .with_params( to avoid Python keyword
        # But preserve method names like ->withPostFilter(, ->withUnitsFor(, etc.
        line = line.replace('->with(', '.with_params(')
        # Don't split method names starting with 'with' - they're valid Python identifiers
        line = line.replace('->', '.')

        # Add parentheses to Perl method calls that don't have them
        # In Perl: $obj->method is equivalent to $obj->method()
        # In Python: obj.method() is a call, obj.method is a property
        # Pattern: .method_name followed by whitespace, semicolon, closing paren/bracket, or end of line
        # Match: .cmp; or .cmp) or .cmp at end of line
        # Don't match: .reduce() (already has parens) or .key (hash access)
        # Common PG methods without parens: cmp, eval, TeX, string, value, etc.
        line = re.sub(r'\.([a-zA-Z_][a-zA-Z0-9_]*)(?=\s*[;,)\]\}]|\s*$)', r'.\1()', line)

        # Remove empty parentheses after methods that should be properties
        # In Perl, ->reduce() and ->reduce are equivalent
        # In Python, we made these properties, so remove the ()
        line = re.sub(r'\.reduce\(\)', '.reduce', line)

        # Transform chained hash access: .{key} or ){key} → ['key']
        # After -> to . conversion, Context()->{error}{msg} becomes Context().{error}.{msg}
        # We need to convert .{key} and ){key} patterns to ['key']
        # This handles: Context().{error} → Context()['error']
        #               obj.{key1}.{key2} → obj['key1']['key2']
        # Handle quoted keys: {'key'} → ['key'] (don't double-quote)
        # Need to capture the dot to remove it: .{key} → ['key'] not .['key']
        def transform_hash_access(match):
            prefix = match.group(1)
            key = match.group(2)
            # Check if key is already quoted
            if (key.startswith("'") and key.endswith("'")) or (key.startswith('"') and key.endswith('"')):
                bracket = f"[{key}]"
            else:
                bracket = f"['{key}']"
            # If prefix is '.', replace it; otherwise keep it
            if prefix == '.':
                return bracket
            else:
                return prefix + bracket

        while True:
            new_line = re.sub(r"([.\)\]'])\{([^}]+)\}", transform_hash_access, line)
            if new_line == line:
                break
            line = new_line

        # Transform Perl hash/dict operator: => → = (for kwargs) or : (for dict literals)
        # Context-dependent transformation:
        # - Inside {} braces: => becomes : for dict literals
        # - In function calls: name => value becomes name=value for keyword arguments
        # - As array separator: => becomes ,
        def replace_hash_arrow(text: str) -> str:
            """Replace => appropriately based on context."""
            result = []
            i = 0
            in_string = False
            string_char = None
            escaped = False
            brace_depth = 0  # Track {} braces for dict literals

            while i < len(text):
                char = text[i]

                if escaped:
                    result.append(char)
                    escaped = False
                    i += 1
                    continue

                if char == '\\':
                    result.append(char)
                    escaped = True
                    i += 1
                    continue

                if char in ('"', "'"):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                    result.append(char)
                    i += 1
                    continue

                # Track brace depth outside strings
                if not in_string:
                    if char == '{':
                        brace_depth += 1
                    elif char == '}':
                        brace_depth -= 1

                # Check for => outside of strings
                if not in_string and i + 1 < len(text) and text[i:i+2] == '=>':
                    # Inside {} braces: dict literal, use :
                    # Outside braces: keyword argument, use =
                    if brace_depth > 0:
                        result.append(':')
                    else:
                        result.append('=')
                    i += 2
                    continue

                result.append(char)
                i += 1

            return ''.join(result)

        line = replace_hash_arrow(line)

        # Special case: ] => [ pattern (array fat comma in argument lists)
        # This is Perl's way of creating pairs: [ arr1 ] => [ arr2 ]
        # Transform to tuple syntax: ], [ which becomes ([ arr1 ], [ arr2 ]) in function args
        # Must do this AFTER general => replacement to override it
        line = re.sub(r'\]\s*=\s*\[', '], [', line)

        # Special case: name = value inside array literals (from => in arrays)
        # Perl: [ 'text', key => value ] becomes [ 'text', key = value ] (invalid Python)
        # Fix: Transform to [ 'text', {'key': value} ]
        # Pattern: , identifier = value inside [ ... ]
        # First try: immediate before ] (single line)
        line = re.sub(
            r',\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(\d+|\'[^\']*\'|\"[^\"]*\"|True|False)\s*\]',
            r", {'\1': \2} ]",
            line
        )
        # Second try: anywhere after comma (multi-line arrays)
        # This catches cases like: ..., \n        replaceMessage = 1
        # Only transform if line starts with whitespace (continuation) and has assignment
        if line.strip() and not line[0].isalpha() and '=' in line:
            # Look for pattern: leading whitespace, identifier = value
            # Can be followed by comma, ], or end of line
            line = re.sub(
                r'^(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(\d+|True|False)(\s*[,\]]|\s*$)',
                r"\1{'\2': \3}\4",
                line
            )

        # Special case: Function(...) = value (expression can't be assigned to)
        # This happens with AnswerHints( Formula(...) => "msg", ... )
        # Transform to tuple pairs: (Formula(...), "msg")
        # Pattern: CapitalizedWord(...) = "string" or CapitalizedWord(...) = number
        # Wrap in parens to make it a tuple element
        # String pattern handles both double and single quotes with any content
        # IMPORTANT: Use negative lookbehind (?<![a-z]) to ensure we don't match
        # capital letters that are part of a camelCase method name like withPostFilter
        line = re.sub(
            r'(?<![a-z])([A-Z][a-zA-Z0-9_]*\([^)]*\))\s*=\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
            r'(\1, \2)',
            line
        )

        # Special case: 'string' = value (string literal can't be keyword arg)
        # This happens with parserFunction('f(x,y)' => 'definition')
        # Also: "y'" = 'Real' in Context().variables.are() calls
        # Transform to comma-separated arguments: 'string', value
        # Pattern: quoted string = quoted value
        # Use more general pattern that handles quotes inside strings
        line = re.sub(
            r'"([^"]*?)"\s*=\s*(["\'][^"\']*["\'])',
            r'"\1", \2',
            line
        )
        line = re.sub(
            r"'([^']*?)'\s*=\s*([\"'][^\"']*[\"'])",
            r"'\1', \2",
            line
        )

        # Special case: identifier = { dict } in .add() calls (should be 'identifier', { dict })
        # This happens with Context().functions.add(name => { ... })
        # The => was converted to = by replace_hash_arrow, but should be string + comma
        # Pattern: .add( word = {
        # Convert to: .add( 'word', {
        # Only apply after .add( to avoid breaking legitimate keyword arguments
        line = re.sub(
            r'(\.add\(\s*)([a-z_][a-zA-Z0-9_]*)\s*=\s*\{',
            r"\1'\2', {",
            line
        )

        # Special case: Wrap [ ... ], [ ... ] pairs in parens for AnswerHints
        # After transforming ] => [ to ], [ we need to wrap in parens to make a tuple
        # This is ONLY for AnswerHints( [ arr1 ], [ arr2 ] ) patterns, not all functions
        # Other functions like random_coprime expect separate arguments, not a tuple
        if '], [' in line and 'AnswerHints' in line:
            # Wrap [ ... ], [ ... ] patterns in AnswerHints calls
            # Match: [ ... ], [ ... ] where arrays can span lines (use non-greedy)
            line = re.sub(
                r'(\(|\,)\s*(\[(?:[^\[\]]|\[[^\]]*\])*\])\s*,\s*(\[(?:[^\[\]]|\[[^\]]*\])*\])',
                r'\1 (\2, \3)',
                line
            )

        # Transform Perl string comparison operators (must be done carefully)
        # eq → == (string equality)
        # ne → != (string inequality)
        # lt → < (less than)
        # gt → > (greater than)
        # le → <= (less than or equal)
        # ge → >= (greater than or equal)
        # Use word boundaries to avoid matching inside identifiers
        # Use negative lookahead to avoid matching variable names (followed by =, ., (, [)
        # This prevents: $gt = ... from becoming > = ...
        line = re.sub(r'\beq\b(?!\s*[=\.\(\[])', '==', line)
        line = re.sub(r'\bne\b(?!\s*[=\.\(\[])', '!=', line)
        line = re.sub(r'\blt\b(?!\s*[=\.\(\[])', '<', line)
        line = re.sub(r'\bgt\b(?!\s*[=\.\(\[])', '>', line)
        line = re.sub(r'\ble\b(?!\s*[=\.\(\[])', '<=', line)
        line = re.sub(r'\bge\b(?!\s*[=\.\(\[])', '>=', line)

        # Transform Perl namespace separator: Package::Function → Package.Function
        line = re.sub(
            r'([a-zA-Z_][a-zA-Z0-9_]*)::([a-zA-Z_][a-zA-Z0-9_]*)', r'\1.\2', line)

        # Transform Perl string concatenation operator: ' . ' → ' + '
        # Only when surrounded by spaces or between string literals/variables
        # Match: 'str' . 'str' or var . 'str' or 'str' . var
        # Special handling for expressions: wrap non-string operands in str()
        # Case 1: When second operand is ( expression ), wrap in str()
        line = re.sub(r'(\)|\'|\"|\w)\s+\.\s+(\([^)]+\))', r'\1 + str(\2)', line)
        # Case 2: Regular concatenation with strings/variables
        line = re.sub(r'(\)|\'|\"|\w)\s+\.\s+(\'|\"|\w)', r'\1 + \2', line)

        # Also handle continuation lines starting with . (Perl string concat)
        # Match: ^\s+. "string" and convert to + "string"
        # If it's . (expr), wrap in str()
        line = re.sub(r'^(\s+)\.\s+(\([^)]+\))', r'\1+ str(\2)', line)
        # Otherwise just convert . to +
        line = re.sub(r'^(\s+)\.\s+', r'\1+ ', line)

        # Transform Perl string repetition operator: x → *
        # Match: 'str' x 3 or var x num
        # Use word boundaries to avoid matching variable named 'x'
        # Pattern: (value) x (number) where x is surrounded by spaces
        line = re.sub(r'(\)|\'|\"|\w)\s+x\s+(\d+|\w+)', r'\1 * \2', line)

        # Transform Perl regex literals: qr/pattern/flags → r"pattern"
        # Example: qr/[ty]'*/i → r"[ty]'*"
        # Common flags: i (case insensitive), m (multiline), s (single line)
        # For now, convert to raw string and ignore flags (most patterns don't need compilation)
        def convert_qr_regex(match):
            pattern = match.group(1)
            # Escape any double quotes in the pattern
            escaped_pattern = pattern.replace('"', '\\"')
            return f'r"{escaped_pattern}"'

        line = re.sub(r'qr/([^/]+)/\w*', convert_qr_regex, line)

        # Note: do-while/do-until loops are handled in main preprocess loop
        # to allow multi-line output

        # Transform Perl for-loops to Python for-in loops
        # Patterns:
        # 1. for VAR (EXPR) { → for VAR in EXPR:
        # 2. for my VAR (EXPR) { → for VAR in EXPR:  (remove 'my' keyword)
        # 3. Handle Perl range: (START .. END) → range(START, END+1)

        # Convert for-loop syntax FIRST (before range conversion)
        # This captures the expression and handles Perl range within it
        def convert_for_loop(match):
            var = match.group(1)
            expr = match.group(2)
            # Handle Perl range inside expression: START .. END → range(START, END+1)
            expr = re.sub(r'(\d+|[a-zA-Z_]\w*)\s*\.\.\s*(\d+|[a-zA-Z_]\w*)',
                         lambda m: f'range({m.group(1).strip()}, {m.group(2).strip()}+1)',
                         expr)
            return f'for {var} in {expr}:'

        # Pattern: for my? VAR (EXPR) { → for VAR in EXPR:
        line = re.sub(r'\bfor\s+my\s+([a-zA-Z_]\w*)\s*\(([^)]+)\)\s*\{', convert_for_loop, line)
        line = re.sub(r'\bfor\s+([a-zA-Z_]\w*)\s*\(([^)]+)\)\s*\{', convert_for_loop, line)

        # Remove Perl 'my' keyword from variable declarations
        # Pattern: my VAR = → VAR =
        # This handles inline statements like: for i: my x = i * 2; my y = x + 1
        line = re.sub(r'\bmy\s+([a-zA-Z_]\w*)\s*=', r'\1 =', line)

        # Clean up stray closing braces from converted for-loops and blocks
        # Pattern 1: statements; } at end of line → statements (remove trailing brace + semicolon)
        line = re.sub(r';\s*}$', '', line)
        # Pattern 2: ) } at end of line (function call followed by brace)
        line = re.sub(r'\)\s*}$', ')', line)

        # Transform Perl map with blocks: map { EXPR } LIST
        # map { random(1, 10) } 0 .. 7  →  [random(1, 10) for _ in range(0, 8)]
        # map { $f->eval(x => $_) } 0 .. 2  →  [f.eval(x=_) for _ in range(0, 3)]
        map_match = re.search(r'\bmap\s*\{\s*([^}]+)\}\s+(\d+)\s*\.\.\s*(\d+)', line)
        if map_match:
            expr = map_match.group(1).strip()
            # Fix: map { } blocks had => converted to : by replace_hash_arrow
            # Inside map blocks, => should be = (keyword args), not : (dict)
            # Convert : back to = for function arguments
            # Pattern: identifier : expression (but not inside nested strings)
            expr = re.sub(r'(\w+)\s*:\s*', r'\1=', expr)
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

        # Transform Perl ternary operator: condition ? true_value : false_value
        # → true_value if condition else false_value
        # Handle nested ternaries by converting innermost-to-outermost
        # Loop until no more ternaries found (max 10 iterations to prevent infinite loop)
        max_iterations = 10
        iteration = 0
        while '?' in line and ':' in line and iteration < max_iterations:
            iteration += 1
            old_line = line

            # Find the LAST ? (innermost in nested ternaries)
            # Track parenthesis depth to find matching :
            question_pos = -1
            for i in range(len(line) - 1, -1, -1):
                if line[i] == '?':
                    # Check if this is inside a string
                    in_string = False
                    for j in range(i):
                        if line[j] in ('"', "'") and (j == 0 or line[j-1] != '\\'):
                            in_string = not in_string
                    if not in_string:
                        question_pos = i
                        break

            if question_pos < 0:
                break

            # Find matching : after the ?
            depth = 0
            colon_pos = -1
            for i in range(question_pos + 1, len(line)):
                ch = line[i]
                if ch in '([{':
                    depth += 1
                elif ch in ')]}':
                    depth -= 1
                elif ch == ':' and depth == 0:
                    # Check if this looks like a ternary colon (not a dict key)
                    if i > 0 and not (line[i-1].isalnum() or line[i-1] == '_'):
                        colon_pos = i
                        break

            if colon_pos < 0:
                break

            # Find start of condition (work backwards from ?)
            expr_start = 0
            depth = 0
            for j in range(question_pos - 1, -1, -1):
                ch = line[j]
                if ch in ')]}':
                    depth += 1
                elif ch in '([{':
                    depth -= 1
                    if depth < 0:
                        expr_start = j + 1
                        break
                elif depth == 0 and ch in '=,(':
                    expr_start = j + 1
                    break

            # Find end of false value (work forwards from :)
            expr_end = len(line)
            depth = 0
            for j in range(colon_pos + 1, len(line)):
                ch = line[j]
                if ch in '([{':
                    depth += 1
                elif ch in ')]}':
                    depth -= 1
                    if depth < 0:
                        expr_end = j
                        break
                elif depth == 0 and ch in ',)':
                    expr_end = j
                    break

            # Extract components
            condition = line[expr_start:question_pos].strip()
            true_value = line[question_pos+1:colon_pos].strip()
            false_value = line[colon_pos+1:expr_end].strip()

            # Reconstruct with Python ternary
            before = line[:expr_start]
            after = line[expr_end:]
            line = f"{before}{true_value} if {condition} else {false_value}{after}"

            # If line didn't change, break to avoid infinite loop
            if line == old_line:
                break

        # Transform Perl statement modifiers: STATEMENT if/unless CONDITION
        # statement if condition → if condition: statement
        # statement unless condition → if not condition: statement
        # But be careful not to transform regular if/elsif/else blocks, comment lines, or Python ternaries
        if re.search(r'\S+.*\s+(if|unless)\s+\S+', line) and not re.match(r'^\s*(if|elsif|else|unless|#)', line):
            # Skip if this is a Python ternary (has 'if' with 'else' after it)
            # Python ternary: VALUE if CONDITION else OTHER_VALUE
            if ' if ' in line and ' else ' in line:
                # Check if 'else' comes after 'if' (Python ternary pattern)
                if_pos = line.find(' if ')
                else_pos = line.find(' else ')
                if if_pos >= 0 and else_pos > if_pos:
                    # This is a Python ternary, don't transform
                    pass
                else:
                    # Not a ternary, continue with statement modifier
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
            else:
                # No 'else', so can't be a Python ternary
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

        # Quote unquoted dictionary keys: { key: value } or { key : value } → { 'key': value }
        # Match word keys followed by optional whitespace and colon
        def quote_dict_key(match):
            key = match.group(1)
            spaces = match.group(2)  # Preserve whitespace before colon
            # Check if key is already quoted or is a Python keyword/builtin
            if key in ['True', 'False', 'None']:
                return f'{key}{spaces}:'
            return f"'{key}'{spaces}:"

        line = re.sub(r'(?<=[{,\s])(\w+)(\s*):', quote_dict_key, line)

        # Remove trailing semicolons (optional in Python)
        line = re.sub(r';\s*$', '', line)

        # Pass through - Python handles # comments same as Perl/PG
        return line

    def _transform_text_block(self, content: str) -> str:
        """
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
        """
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
