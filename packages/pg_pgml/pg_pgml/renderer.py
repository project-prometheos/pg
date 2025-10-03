"""
PGML Renderers - Convert PGML AST to HTML or TeX.

Implements the Visitor pattern to traverse the AST and generate output.

Reference: PGML.pl rendering logic (lines 1200-1800)
"""

from abc import ABC, abstractmethod
from typing import Any

from .parser import (
    AnswerBlank,
    Bold,
    Code,
    Document,
    Italic,
    List,
    ListItem,
    MathBlock,
    MathInline,
    Paragraph,
    PGMLNode,
    Text,
    Variable,
)


class Renderer(ABC):
    """Base class for PGML renderers."""

    @abstractmethod
    def render(self, node: PGMLNode) -> str:
        """Render a PGML node to output format."""
        pass

    @abstractmethod
    def visit_document(self, node: Document) -> str:
        pass

    @abstractmethod
    def visit_paragraph(self, node: Paragraph) -> str:
        pass

    @abstractmethod
    def visit_math_block(self, node: MathBlock) -> str:
        pass

    @abstractmethod
    def visit_list(self, node: List) -> str:
        pass

    @abstractmethod
    def visit_list_item(self, node: ListItem) -> str:
        pass

    @abstractmethod
    def visit_text(self, node: Text) -> str:
        pass

    @abstractmethod
    def visit_variable(self, node: Variable) -> str:
        pass

    @abstractmethod
    def visit_answer_blank(self, node: AnswerBlank) -> str:
        pass

    @abstractmethod
    def visit_code(self, node: Code) -> str:
        pass

    @abstractmethod
    def visit_math_inline(self, node: MathInline) -> str:
        pass

    @abstractmethod
    def visit_bold(self, node: Bold) -> str:
        pass

    @abstractmethod
    def visit_italic(self, node: Italic) -> str:
        pass


class HTMLRenderer(Renderer):
    """
    Render PGML to HTML.

    Uses KaTeX-compatible syntax for math rendering.
    """

    def __init__(self, context: dict[str, Any] | None = None, answer_counter: int = 1):
        """
        Initialize HTML renderer.

        Args:
            context: Variable bindings for interpolation
            answer_counter: Starting number for answer blanks
        """
        self.context = context or {}
        self.answer_counter = answer_counter

    def render(self, node: PGMLNode) -> str:
        """Render a PGML node to HTML."""
        return node.accept(self)

    def visit_document(self, node: Document) -> str:
        blocks_html = "\n".join(block.accept(self) for block in node.blocks)
        return f'<div class="pgml-document">\n{blocks_html}\n</div>'

    def visit_paragraph(self, node: Paragraph) -> str:
        content_html = "".join(child.accept(self) for child in node.content)
        return f"<p>{content_html}</p>"

    def visit_math_block(self, node: MathBlock) -> str:
        # Use KaTeX display math delimiters
        escaped_math = self._escape_html(node.content)
        return f'<div class="math-block">\\[{escaped_math}\\]</div>'

    def visit_list(self, node: List) -> str:
        tag = "ol" if node.ordered else "ul"
        items_html = "\n".join(item.accept(self) for item in node.items)
        return f"<{tag}>\n{items_html}\n</{tag}>"

    def visit_list_item(self, node: ListItem) -> str:
        content_html = "".join(child.accept(self) for child in node.content)
        # Strip trailing whitespace from list items
        content_html = content_html.rstrip()
        return f"<li>{content_html}</li>"

    def visit_text(self, node: Text) -> str:
        return self._escape_html(node.content)

    def visit_variable(self, node: Variable) -> str:
        # Look up variable in context
        value = self.context.get(node.name, f"[${node.name}]")

        # Convert value to string
        if hasattr(value, "to_string"):
            value_str = value.to_string()
        else:
            value_str = str(value)

        return f'<span class="pgml-variable">{self._escape_html(value_str)}</span>'

    def visit_answer_blank(self, node: AnswerBlank) -> str:
        # Generate answer input field
        answer_name = node.name or f"AnSwEr{self.answer_counter:04d}"
        self.answer_counter += 1

        width_chars = node.width if node.width > 0 else 20
        # Approximate character width in pixels
        width_px = width_chars * 10

        return (
            f'<input type="text" '
            f'name="{answer_name}" '
            f'id="{answer_name}" '
            f'class="pgml-answer-blank" '
            f'size="{width_chars}" '
            f'style="width: {width_px}px;" '
            f'aria-label="Answer {self.answer_counter - 1}">'
        )

    def visit_code(self, node: Code) -> str:
        # Code execution placeholder (actual execution happens server-side)
        # For now, just show the result placeholder
        return f'<span class="pgml-code" data-code="{self._escape_html(node.code)}">[code result]</span>'

    def visit_math_inline(self, node: MathInline) -> str:
        # Use KaTeX inline math delimiters
        escaped_math = self._escape_html(node.content)
        return f'<span class="math-inline">\\({escaped_math}\\)</span>'

    def visit_bold(self, node: Bold) -> str:
        content_html = "".join(child.accept(self) for child in node.content)
        return f"<strong>{content_html}</strong>"

    def visit_italic(self, node: Italic) -> str:
        content_html = "".join(child.accept(self) for child in node.content)
        return f"<em>{content_html}</em>"

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )


class TeXRenderer(Renderer):
    """
    Render PGML to LaTeX/TeX.

    Generates print-ready TeX output for hardcopy generation.
    """

    def __init__(self, context: dict[str, Any] | None = None):
        """
        Initialize TeX renderer.

        Args:
            context: Variable bindings for interpolation
        """
        self.context = context or {}

    def render(self, node: PGMLNode) -> str:
        """Render a PGML node to TeX."""
        return node.accept(self)

    def visit_document(self, node: Document) -> str:
        blocks_tex = "\n\n".join(block.accept(self) for block in node.blocks)
        return blocks_tex

    def visit_paragraph(self, node: Paragraph) -> str:
        content_tex = "".join(child.accept(self) for child in node.content)
        return content_tex

    def visit_math_block(self, node: MathBlock) -> str:
        # Use LaTeX display math
        return f"\\[\n{node.content}\n\\]"

    def visit_list(self, node: List) -> str:
        env = "enumerate" if node.ordered else "itemize"
        items_tex = "\n".join(item.accept(self) for item in node.items)
        return f"\\begin{{{env}}}\n{items_tex}\n\\end{{{env}}}"

    def visit_list_item(self, node: ListItem) -> str:
        content_tex = "".join(child.accept(self) for child in node.content)
        # Strip trailing whitespace from list items
        content_tex = content_tex.rstrip()
        return f"\\item {content_tex}"

    def visit_text(self, node: Text) -> str:
        return self._escape_tex(node.content)

    def visit_variable(self, node: Variable) -> str:
        # Look up variable in context
        value = self.context.get(node.name, f"${node.name}")

        # Convert value to TeX string
        if hasattr(value, "to_tex"):
            value_str = value.to_tex()
        elif hasattr(value, "to_string"):
            value_str = self._escape_tex(value.to_string())
        else:
            value_str = self._escape_tex(str(value))

        return value_str

    def visit_answer_blank(self, node: AnswerBlank) -> str:
        # Generate answer blank line for hardcopy
        width = node.width if node.width > 0 else 20
        # Approximate width in em units
        width_em = width * 0.5
        return f"\\underline{{\\hspace{{{width_em}em}}}}"

    def visit_code(self, node: Code) -> str:
        # Code execution placeholder (should be evaluated before TeX rendering)
        return "[code result]"

    def visit_math_inline(self, node: MathInline) -> str:
        # Use LaTeX inline math
        return f"${node.content}$"

    def visit_bold(self, node: Bold) -> str:
        content_tex = "".join(child.accept(self) for child in node.content)
        return f"\\textbf{{{content_tex}}}"

    def visit_italic(self, node: Italic) -> str:
        content_tex = "".join(child.accept(self) for child in node.content)
        return f"\\textit{{{content_tex}}}"

    def _escape_tex(self, text: str) -> str:
        """Escape TeX special characters."""
        # Common TeX special characters
        replacements = {
            "\\": r"\textbackslash{}",
            "{": r"\{",
            "}": r"\}",
            "$": r"\$",
            "&": r"\&",
            "%": r"\%",
            "#": r"\#",
            "_": r"\_",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }

        result = text
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)

        return result
