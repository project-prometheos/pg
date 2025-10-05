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

            # Detect Perl closures: sub { ... } and stub them out
            # These are typically used for custom answer checkers
            # Example: checker => sub { ... }
            sub_match = re.search(r'(=>|=)\s*sub\s*\{', original_line)
            if sub_match:
                # Found start of a sub {} closure
                # Track brace depth to find the end
                brace_depth = original_line.count('{') - original_line.count('}')
                
                # Extract the parameter name before the =>
                prefix_match = re.match(r'^(\s*)(\w+)\s*=>\s*sub\s*\{', original_line)
                if prefix_match:
                    indent = prefix_match.group(1)
                    param_name = prefix_match.group(2)
                    # Stub out the closure with a lambda that returns None
                    output_lines.append(
                        f"{indent}{param_name} = lambda *args, **kwargs: None  # Stubbed Perl closure")
                else:
                    # Assignment form: $var = sub { ... }
                    assign_match = re.match(r'^(\s*)(\w+)\s*=\s*sub\s*\{', original_line)
                    if assign_match:
                        indent = assign_match.group(1)
                        var_name = assign_match.group(2)
                        output_lines.append(
                            f"{indent}{var_name} = lambda *args, **kwargs: None  # Stubbed Perl closure")
                    else:
                        # Unknown form, comment it out
                        output_lines.append(f"# {original_line}  # Skipped Perl closure")
                
                # Skip the rest of the closure block
                i += 1
                while i < len(lines) and brace_depth > 0:
                    current_line = lines[i]
                    brace_depth += current_line.count('{') - current_line.count('}')
                    i += 1
                
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
                # do-until executes body first, then checks condition
                output_lines.append('while True:')
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
                        # Strip original indentation since we'll re-indent for the while loop
                        compiled_body.extend(self._compile_line(ln.lstrip()))
                    compiled_cond = self._compile_expr(condition)
                    # Emit Python loop - do-until executes body first, then checks condition
                    # So we use: while True: body; if condition: break
                    output_lines.append('while True:')
                    for cb in compiled_body:
                        output_lines.append('    ' + cb)
                    output_lines.append(f'    if ({compiled_cond}):')
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
                    block_index = len(text_blocks) - 1

                    if "PGML" in block_type:
                        # PGML blocks - transform evaluators but keep as string for runtime rendering
                        stored_content = self._transform_pgml_evaluators(block_content)
                        block_var = f"pgml_block_{block_index}"
                        escaped_content = self._escape_triple_quotes(stored_content)
                        output_lines.append(f"{block_var} = '''\n{escaped_content}\n'''")
                        
                        # PGML blocks use TEXT(PGML(...)), SOLUTION(PGML(...)), HINT(PGML(...))
                        if "SOLUTION" in block_type:
                            output_lines.append(f"SOLUTION(PGML({block_var}))")
                        elif "HINT" in block_type:
                            output_lines.append(f"HINT(PGML({block_var}))")
                        else:
                            output_lines.append(f"TEXT(PGML({block_var}))")
                    else:
                        # Plain TEXT blocks - transform into Python function calls
                        transformed_content = self._transform_text_block(block_content)
                        
                        # Plain TEXT blocks use TEXT(...), SOLUTION(...), HINT(...)
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
        # Preserve leading whitespace for proper indentation
        leading_space = line[:len(line) - len(line.lstrip())]
        stripped = line.strip()
        if not stripped:
            return [""]
        # Keep comments verbatim
        if stripped.startswith('#'):
            return [line]  # Return with original indentation
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
                        result_lines.append(leading_space + out)
                return result_lines if result_lines else [""]
            except LarkError:
                pass
        # Manual parse for simple assignments and calls
        manual_ir = self._manual_parse_line(stripped)
        if manual_ir is not None:
            out = self._emit_ir(manual_ir)
            return [leading_space + out] if out is not None else [""]
        # Fall back to Pygments rewrite
        rewritten = self._rewrite_with_pygments(stripped)
        return [leading_space + rewritten]

    def _compile_expr(self, expr: str) -> str:
        """Compile a small expression using the grammar or fallback rewrite.

        Returns a string containing Python code representing the expression.
        """
        stripped = expr.strip()
        if not stripped:
            return ""

        if self._parser is not None and self._transformer is not None:
            try:
                tree = self._parser.parse(stripped)
                ir_list = self._transformer.transform(tree)
                if not isinstance(ir_list, list):
                    ir_list = [ir_list]
                for ir in ir_list:
                    if isinstance(ir, tuple) and ir and ir[0] in ("assign", "expr", "bin", "var", "call"):
                        return self._expr_to_py(ir)
            except LarkError:
                pass

        manual_ir = self._manual_parse_line(stripped)
        if manual_ir is not None:
            return self._expr_to_py(manual_ir)

        return self._rewrite_with_pygments(stripped)

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
            # Convert Perl namespace separator :: to Python .
            name = name.replace('::', '.')
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

    def _interpolate_string(self, string_token: str) -> str:
        """
        Convert Perl string interpolation to Python f-strings.
        
        Perl interpolates variables in double-quoted strings but not single-quoted.
        E.g., "$var text" becomes f"{var} text"
        """
        # Extract quote character and content
        if len(string_token) < 2:
            return string_token
        
        quote_char = string_token[0]
        
        # Only interpolate double-quoted strings (Perl behavior)
        if quote_char != '"':
            return string_token
        
        # Extract content (between quotes)
        content = string_token[1:-1]
        
        # Check if contains $var
        if '$' not in content:
            return string_token
        
        # Convert $var to {var} for f-string
        # Handle $varname (word characters only)
        new_content = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'{\1}', content)
        
        return f'f"{new_content}"'

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
            # Strings: apply interpolation for double-quoted strings with $vars
            if ttype in Token.Literal.String:
                result.append(self._interpolate_string(text))
                i += 1
                continue
            # Variables: remove sigil
            if ttype in Token.Name.Variable:
                result.append(self._desigil(text))
                i += 1
                continue
            # Namespace: convert Perl :: to Python .
            # Pygments treats "Namespace::" as a single Token.Name.Namespace
            if ttype == Token.Name.Namespace:
                result.append(text.replace('::', '.'))
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
                # Handle method arrow '->' with special case for ->with(
                if text == '-' and i + 1 < len(tokens) and tokens[i+1][2] == '>':
                    # Check if this is ->with( which needs to become .with_params(
                    # Look ahead to see if next non-empty token is 'with'
                    j = i + 2
                    while j < len(tokens) and not tokens[j][2]:  # Skip empty tokens
                        j += 1
                    if j < len(tokens) and tokens[j][2] == 'with':
                        # Check if followed by '('
                        k = j + 1
                        while k < len(tokens) and not tokens[k][2]:  # Skip empty tokens
                            k += 1
                        if k < len(tokens) and tokens[k][2] == '(':
                            result.append('.with_params')
                            i = j + 1  # Skip '-', '>', and 'with'
                            continue
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
                segments.append(func_code)
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