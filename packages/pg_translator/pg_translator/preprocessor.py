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

    def preprocess(self, pg_source: str) -> PreprocessResult:
        """
        Preprocess PG source code.

        Args:
            pg_source: Raw PG file content

        Returns:
            PreprocessResult with transformed code and metadata
        """
        lines = pg_source.split("\n")
        output_lines: list[str] = []
        text_blocks: list[tuple[str, str]] = []
        line_map: dict[int, int] = {}

        i = 0
        while i < len(lines):
            original_line = lines[i]
            output_line_num = len(output_lines) + 1

            # Track line mapping
            line_map[output_line_num] = i + 1

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

                    # Generate Python code to accumulate this block
                    # Use valid variable names (RestrictedPython doesn't allow _)
                    block_var = f"pg_block_{len(text_blocks) - 1}"
                    if "PGML" in block_type:
                        # PGML blocks need rendering
                        output_lines.append(
                            f"{block_var} = '''\\n{self._escape_triple_quotes(block_content)}\\n'''"
                        )
                        if "SOLUTION" in block_type:
                            output_lines.append(f"pg_env.add_pgml_solution({block_var})")
                        elif "HINT" in block_type:
                            output_lines.append(f"pg_env.add_pgml_hint({block_var})")
                        else:
                            output_lines.append(f"pg_env.add_pgml_text({block_var})")
                    else:
                        # Plain TEXT blocks
                        output_lines.append(
                            f"{block_var} = '''\\n{self._escape_triple_quotes(block_content)}\\n'''"
                        )
                        if "SOLUTION" in block_type:
                            output_lines.append(f"pg_env.add_solution({block_var})")
                        elif "HINT" in block_type:
                            output_lines.append(f"pg_env.add_hint({block_var})")
                        else:
                            output_lines.append(f"pg_env.add_text({block_var})")

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
        - Comment removal (# comments)
        - PG-specific syntax transformations
        """
        # Remove comments (but preserve # in strings)
        # Simple approach: remove # to end of line if not in quotes
        # (Full implementation would need proper tokenization)

        # For now, just pass through - let Python handle comments
        # PG uses # for comments same as Python
        return line

    def _escape_triple_quotes(self, text: str) -> str:
        """Escape triple quotes in text for Python string literals."""
        return text.replace("'''", r"\'\'\'").replace('"""', r'\"\"\"')
