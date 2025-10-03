"""
PGML Parser - Parse PGML tokens into document structure.

Creates a document tree with:
- Block elements: paragraphs, lists, math blocks
- Inline elements: text, variables, emphasis, math

Reference: PGML.pl parser logic (lines 800-1200)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .tokenizer import PGMLTokenizer, Token, TokenType


# Abstract Syntax Tree Nodes


class PGMLNode(ABC):
    """Base class for PGML AST nodes."""

    @abstractmethod
    def accept(self, visitor: Any) -> Any:
        """Accept a visitor for rendering."""
        pass


# Block-level nodes


@dataclass
class Document(PGMLNode):
    """Root document node containing blocks."""

    blocks: list[PGMLNode] = field(default_factory=list)

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_document(self)


@dataclass
class Paragraph(PGMLNode):
    """Paragraph block containing inline content."""

    content: list[PGMLNode] = field(default_factory=list)

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_paragraph(self)


@dataclass
class MathBlock(PGMLNode):
    """Display math block."""

    content: str

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_math_block(self)


@dataclass
class List(PGMLNode):
    """Unordered or ordered list."""

    items: list[ListItem] = field(default_factory=list)
    ordered: bool = False

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_list(self)


@dataclass
class ListItem(PGMLNode):
    """List item containing inline content."""

    content: list[PGMLNode] = field(default_factory=list)

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_list_item(self)


# Inline nodes


@dataclass
class Text(PGMLNode):
    """Plain text."""

    content: str

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_text(self)


@dataclass
class Variable(PGMLNode):
    """Variable interpolation [$var]."""

    name: str

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_variable(self)


@dataclass
class AnswerBlank(PGMLNode):
    """Answer input blank."""

    width: int = 20  # Number of underscores or explicit width
    name: str = ""  # Optional answer name

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_answer_blank(self)


@dataclass
class Code(PGMLNode):
    """Code execution block [@code@]."""

    code: str

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_code(self)


@dataclass
class MathInline(PGMLNode):
    """Inline math [``...``]."""

    content: str

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_math_inline(self)


@dataclass
class Bold(PGMLNode):
    """Bold text."""

    content: list[PGMLNode] = field(default_factory=list)

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_bold(self)


@dataclass
class Italic(PGMLNode):
    """Italic text."""

    content: list[PGMLNode] = field(default_factory=list)

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_italic(self)


# Parser


class PGMLParser:
    """
    Parse PGML tokens into a document tree.

    The parser builds a hierarchical structure:
    - Document (root)
      - Blocks (paragraphs, lists, math blocks)
        - Inline elements (text, variables, emphasis, math)
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    @classmethod
    def parse_text(cls, text: str) -> Document:
        """Convenience method to tokenize and parse text."""
        tokenizer = PGMLTokenizer(text)
        tokens = tokenizer.tokenize()
        parser = cls(tokens)
        return parser.parse()

    def parse(self) -> Document:
        """Parse tokens into document tree."""
        blocks: list[PGMLNode] = []

        while not self._is_at_end():
            # Skip blank lines between blocks
            while self._match(TokenType.BLANK_LINE, TokenType.NEWLINE):
                pass

            if self._is_at_end():
                break

            # Parse block-level elements
            block = self._parse_block()
            if block:
                blocks.append(block)

        return Document(blocks=blocks)

    def _parse_block(self) -> PGMLNode | None:
        """Parse a block-level element."""
        # Math block
        if self._check(TokenType.MATH_BLOCK_START):
            return self._parse_math_block()

        # List
        if self._check(TokenType.LIST_ITEM) or self._check(TokenType.ORDERED_ITEM):
            return self._parse_list()

        # Paragraph (default)
        return self._parse_paragraph()

    def _parse_math_block(self) -> MathBlock:
        """Parse display math block [```...```]."""
        self._advance()  # consume [```

        content = ""
        while not self._check(TokenType.MATH_BLOCK_END) and not self._is_at_end():
            content += self._advance().value

        self._advance()  # consume ```]

        return MathBlock(content=content.strip())

    def _parse_list(self) -> List:
        """Parse a list (ordered or unordered)."""
        items: list[ListItem] = []
        ordered = self._check(TokenType.ORDERED_ITEM)

        while not self._is_at_end():
            # Check if we have a list item
            if not (self._check(TokenType.LIST_ITEM) or self._check(TokenType.ORDERED_ITEM)):
                break

            token = self._advance()

            # Extract content from [* content or [1. content (no closing bracket)
            content_text = token.value
            if token.type == TokenType.LIST_ITEM:
                # Remove [* prefix and strip whitespace
                content_text = content_text[2:].strip()
            else:  # ORDERED_ITEM
                # Remove [N. prefix and strip whitespace
                content_text = content_text.split(".", 1)[1].strip()

            # Parse inline content
            item_tokens = PGMLTokenizer(content_text).tokenize()
            item_parser = PGMLParser(item_tokens)
            inline_content = item_parser._parse_inline_elements()

            items.append(ListItem(content=inline_content))

            # Skip newline after list item (if present)
            self._match(TokenType.NEWLINE)

        return List(items=items, ordered=ordered)

    def _parse_paragraph(self) -> Paragraph:
        """Parse a paragraph (inline content until blank line)."""
        content = self._parse_inline_elements()
        return Paragraph(content=content)

    def _parse_inline_elements(self) -> list[PGMLNode]:
        """Parse inline elements until block boundary."""
        elements: list[PGMLNode] = []

        while not self._is_at_block_boundary() and not self._is_at_end():
            # Variable interpolation
            if self._check(TokenType.VAR_START):
                elements.append(self._parse_variable())

            # Answer blank
            elif self._check(TokenType.ANSWER_BLANK):
                elements.append(self._parse_answer_blank())

            # Code execution
            elif self._check(TokenType.CODE_START):
                elements.append(self._parse_code())

            # Inline math
            elif self._check(TokenType.MATH_INLINE_START):
                elements.append(self._parse_math_inline())

            # Bold
            elif self._check(TokenType.BOLD_START):
                elements.append(self._parse_bold())

            # Italic
            elif self._check(TokenType.ITALIC_START):
                elements.append(self._parse_italic())

            # Plain text
            elif self._check(TokenType.TEXT):
                elements.append(Text(content=self._advance().value))

            # Single newline (space in output)
            elif self._check(TokenType.NEWLINE):
                self._advance()
                elements.append(Text(content=" "))

            else:
                # Skip unknown token
                self._advance()

        return elements

    def _parse_variable(self) -> Variable:
        """Parse variable interpolation [$var]."""
        self._advance()  # consume [$

        var_name = ""
        if self._check(TokenType.TEXT):
            var_name = self._advance().value

        self._match(TokenType.VAR_END)  # consume ]

        return Variable(name=var_name)

    def _parse_answer_blank(self) -> AnswerBlank:
        """Parse answer blank [_____]."""
        token = self._advance()

        # Count underscores for width
        width = token.value.count("_")

        return AnswerBlank(width=width)

    def _parse_code(self) -> Code:
        """Parse code execution [@code@]."""
        self._advance()  # consume [@

        code = ""
        if self._check(TokenType.TEXT):
            code = self._advance().value

        self._match(TokenType.CODE_END)  # consume @]

        return Code(code=code.strip())

    def _parse_math_inline(self) -> MathInline:
        """Parse inline math [``...``]."""
        self._advance()  # consume [``

        content = ""
        if self._check(TokenType.TEXT):
            content = self._advance().value

        self._match(TokenType.MATH_INLINE_END)  # consume ``]

        return MathInline(content=content.strip())

    def _parse_bold(self) -> Bold:
        """Parse bold text *...* or **...**."""
        marker = self._advance().value  # * or **
        content: list[PGMLNode] = []

        # Parse content until matching end marker
        while not self._check(TokenType.BOLD_END) and not self._is_at_end():
            if self._check(TokenType.TEXT):
                content.append(Text(content=self._advance().value))
            elif self._check(TokenType.NEWLINE):
                self._advance()
                content.append(Text(content=" "))
            else:
                break

        self._match(TokenType.BOLD_END)

        return Bold(content=content)

    def _parse_italic(self) -> Italic:
        """Parse italic text _..._ or __...__."""
        marker = self._advance().value  # _ or __
        content: list[PGMLNode] = []

        # Parse content until matching end marker
        while not self._check(TokenType.ITALIC_END) and not self._is_at_end():
            if self._check(TokenType.TEXT):
                content.append(Text(content=self._advance().value))
            elif self._check(TokenType.NEWLINE):
                self._advance()
                content.append(Text(content=" "))
            else:
                break

        self._match(TokenType.ITALIC_END)

        return Italic(content=content)

    def _is_at_block_boundary(self) -> bool:
        """Check if at a block boundary."""
        return self._check(
            TokenType.BLANK_LINE,
            TokenType.MATH_BLOCK_START,
            TokenType.LIST_ITEM,
            TokenType.ORDERED_ITEM,
            TokenType.EOF,
        )

    def _check(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        if self._is_at_end():
            return False
        return self.current_token.type in token_types

    def _match(self, *token_types: TokenType) -> bool:
        """Try to match and consume any of the given token types."""
        if self._check(*token_types):
            self._advance()
            return True
        return False

    def _advance(self) -> Token:
        """Consume and return current token."""
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        return token

    def _is_at_end(self) -> bool:
        """Check if at end of token stream."""
        return self.current_token is None or self.current_token.type == TokenType.EOF
