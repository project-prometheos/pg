"""
PGML Tokenizer - Lexical analysis for PGML syntax.

Recognizes PGML patterns:
- [$var] - Variable interpolation
- [_____] - Answer blank (underscores)
- [@ code @] - Code execution
- [```math```] - Math display block
- [``latex``] - Inline LaTeX
- [* item] - List item
- Bold: *text*, **text**
- Italic: _text_, __text__

Reference: PGML.pl tokenization logic (lines 500-800)
"""

import re
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """PGML token types."""

    # Text and whitespace
    TEXT = auto()
    NEWLINE = auto()
    BLANK_LINE = auto()
    INDENT = auto()

    # Variable interpolation
    VAR_START = auto()  # [$
    VAR_END = auto()  # ]

    # Answer blanks
    ANSWER_BLANK = auto()  # [_____]
    ANSWER_RULE = auto()  # [@ ans_rule(20) @]

    # Code execution
    CODE_START = auto()  # [@
    CODE_END = auto()  # @]

    # Math display
    MATH_BLOCK_START = auto()  # [```
    MATH_BLOCK_END = auto()  # ```]
    MATH_INLINE_START = auto()  # [``
    MATH_INLINE_END = auto()  # ``]

    # Formatting
    BOLD_START = auto()  # * or **
    BOLD_END = auto()
    ITALIC_START = auto()  # _ or __
    ITALIC_END = auto()

    # Lists
    LIST_ITEM = auto()  # [* item]
    ORDERED_ITEM = auto()  # [1. item]

    # Special
    EOF = auto()


@dataclass
class Token:
    """A PGML token."""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class PGMLTokenizer:
    """
    Tokenize PGML markup into a stream of tokens.

    PGML uses bracket notation for special constructs:
    - [$var] for variables
    - [_____] for answer blanks
    - [@ code @] for Perl code execution
    - [```math```] for display math
    - [``latex``] for inline math
    """

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """Tokenize the entire input text."""
        while self.pos < len(self.text):
            self._scan_token()

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def _scan_token(self) -> None:
        """Scan and emit the next token."""
        start_pos = self.pos
        start_line = self.line
        start_col = self.column

        # Check for newlines
        if self._match("\n"):
            # Check if this is a blank line (previous was also newline)
            if self.tokens and self.tokens[-1].type == TokenType.NEWLINE:
                self.tokens[-1] = Token(TokenType.BLANK_LINE, "\n\n", start_line - 1, 1)
            else:
                self._add_token(TokenType.NEWLINE, "\n", start_line, start_col)
            return

        # Check for bracket constructs
        if self._peek() == "[":
            self._scan_bracket_construct()
            return

        # Emphasis is not commonly used in PGML - bracket notation is preferred
        # Disable emphasis scanning to avoid conflicts with underscores in text
        # (If needed later, can be re-enabled with proper context checking)

        # Regular text
        self._scan_text()

    def _scan_bracket_construct(self) -> None:
        """Scan bracket-based constructs like [$var], [@code@], etc."""
        start_line = self.line
        start_col = self.column

        if not self._match("["):
            return

        # Look ahead to determine type
        next_char = self._peek()

        # Variable interpolation: [$var]
        if next_char == "$":
            self._advance()  # consume $
            self._add_token(TokenType.VAR_START, "[$", start_line, start_col)
            # Scan variable name
            var_name = self._scan_until("]")
            self._add_token(TokenType.TEXT, var_name, self.line, self.column - len(var_name))
            if self._match("]"):
                self._add_token(TokenType.VAR_END, "]", self.line, self.column - 1)
            return

        # Code execution: [@code@]
        if next_char == "@":
            self._advance()  # consume @
            self._add_token(TokenType.CODE_START, "[@", start_line, start_col)
            # Scan code until @]
            code = self._scan_until("@]")
            self._add_token(TokenType.TEXT, code, self.line, self.column - len(code))
            if self._match("@]"):
                self._add_token(TokenType.CODE_END, "@]", self.line, self.column - 2)
            return

        # Math display block: [```...```]
        if self._peek_ahead("```"):
            self._advance()  # consume `
            self._advance()  # consume `
            self._advance()  # consume `
            self._add_token(TokenType.MATH_BLOCK_START, "[```", start_line, start_col)
            # Scan math until ```]
            math = self._scan_until("```]")
            self._add_token(TokenType.TEXT, math, self.line, self.column - len(math))
            if self._match("```]"):
                self._add_token(TokenType.MATH_BLOCK_END, "```]", self.line, self.column - 4)
            return

        # Inline math: [``...``]
        if self._peek_ahead("``"):
            self._advance()  # consume `
            self._advance()  # consume `
            self._add_token(TokenType.MATH_INLINE_START, "[``", start_line, start_col)
            # Scan math until ``]
            math = self._scan_until("``]")
            self._add_token(TokenType.TEXT, math, self.line, self.column - len(math))
            if self._match("``]"):
                self._add_token(TokenType.MATH_INLINE_END, "``]", self.line, self.column - 3)
            return

        # Answer blank: [_____]
        if next_char == "_":
            underscores = ""
            while self._peek() == "_":
                underscores += self._advance()
            if self._match("]"):
                self._add_token(
                    TokenType.ANSWER_BLANK,
                    f"[{underscores}]",
                    start_line,
                    start_col,
                )
            return

        # List item: [* item (ends at newline, no closing bracket)
        if next_char == "*":
            self._advance()  # consume *
            # Scan until newline (list items don't have closing bracket)
            content = self._scan_until("\n")
            self._add_token(TokenType.LIST_ITEM, f"[*{content}", start_line, start_col)
            return

        if next_char.isdigit():
            # Check for ordered list [1. ... (ends at newline)
            num = ""
            while self._peek().isdigit():
                num += self._advance()
            if self._peek() == ".":
                self._advance()  # consume .
                content = self._scan_until("\n")
                self._add_token(
                    TokenType.ORDERED_ITEM,
                    f"[{num}.{content}",
                    start_line,
                    start_col,
                )
                return

        # Not a recognized pattern, treat as text
        self.pos -= 1  # back up
        self.column -= 1
        self._scan_text()

    def _scan_emphasis(self) -> None:
        """Scan emphasis markers (* or _)."""
        start_line = self.line
        start_col = self.column
        char = self._peek()

        # Check for double emphasis
        if self._peek_ahead(char + char):
            self._advance()
            self._advance()
            token_type = TokenType.BOLD_START if char == "*" else TokenType.ITALIC_START
            self._add_token(token_type, char + char, start_line, start_col)
        else:
            self._advance()
            token_type = TokenType.BOLD_START if char == "*" else TokenType.ITALIC_START
            self._add_token(token_type, char, start_line, start_col)

    def _scan_text(self) -> None:
        """Scan regular text until special character."""
        start_line = self.line
        start_col = self.column
        text = ""

        while self.pos < len(self.text):
            char = self._peek()
            # Stop at special characters (brackets and newlines only)
            if char in ("\n", "["):
                break
            text += self._advance()

        if text:
            self._add_token(TokenType.TEXT, text, start_line, start_col)

    def _scan_until(self, delimiter: str) -> str:
        """Scan text until delimiter is found."""
        text = ""
        while self.pos < len(self.text):
            if self._peek_ahead(delimiter):
                break
            text += self._advance()
        return text

    def _peek(self) -> str:
        """Peek at current character without consuming."""
        if self.pos >= len(self.text):
            return ""
        return self.text[self.pos]

    def _peek_ahead(self, s: str) -> bool:
        """Check if upcoming text matches string s."""
        return self.text[self.pos : self.pos + len(s)] == s

    def _match(self, s: str) -> bool:
        """Try to match and consume string s."""
        if self._peek_ahead(s):
            for _ in s:
                self._advance()
            return True
        return False

    def _advance(self) -> str:
        """Consume and return current character."""
        if self.pos >= len(self.text):
            return ""

        char = self.text[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def _add_token(self, token_type: TokenType, value: str, line: int, column: int) -> None:
        """Add a token to the list."""
        self.tokens.append(Token(token_type, value, line, column))
