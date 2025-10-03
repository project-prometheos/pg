"""
PGstandard.pl - Core PG functions

Python port of macros/core/PGstandard.pl
Provides basic PG functionality: TEXT, ANS, BEGIN_TEXT/END_TEXT, etc.

Reference: PGstandard.pl (lines 1-500)
"""

from typing import Any, Callable

from pg_answer import AnswerEvaluator

# Export list
__exports__ = [
    "TEXT",
    "ANS",
    "NAMED_ANS",
    "SOLUTION",
    "HINT",
    "image",
    "htmlLink",
    "iframe",
]


def TEXT(text: str) -> None:
    """
    Add text to problem statement.

    This is a placeholder - actual implementation happens in PGEnvironment.
    In real usage, this gets replaced by pg_env.add_text() during execution.

    Args:
        text: Text to add

    Reference: PGstandard.pl::TEXT
    """
    # This function is replaced at runtime by the executor
    # It's here for documentation and macro loading
    pass


def ANS(evaluator: AnswerEvaluator, answer_name: str | None = None) -> None:
    """
    Register an answer evaluator.

    Args:
        evaluator: Answer evaluator
        answer_name: Optional answer name (auto-generated if None)

    Reference: PGstandard.pl::ANS
    """
    # Replaced at runtime
    pass


def NAMED_ANS(answer_name: str, evaluator: AnswerEvaluator) -> None:
    """
    Register a named answer evaluator.

    Args:
        answer_name: Answer name
        evaluator: Answer evaluator

    Reference: PGstandard.pl::NAMED_ANS
    """
    # Replaced at runtime
    pass


def SOLUTION(text: str) -> None:
    """
    Add solution text.

    Args:
        text: Solution text

    Reference: PGstandard.pl::SOLUTION
    """
    # Replaced at runtime
    pass


def HINT(text: str) -> None:
    """
    Add hint text.

    Args:
        text: Hint text

    Reference: PGstandard.pl::HINT
    """
    # Replaced at runtime
    pass


def image(
    filename: str,
    width: int | None = None,
    height: int | None = None,
    alt: str = "",
    **kwargs: Any,
) -> str:
    """
    Generate HTML img tag.

    Args:
        filename: Image filename
        width: Image width in pixels
        height: Image height in pixels
        alt: Alt text
        **kwargs: Additional HTML attributes

    Returns:
        HTML img tag

    Reference: PGstandard.pl::image
    """
    attrs = []

    # Source
    attrs.append(f'src="{filename}"')

    # Dimensions
    if width:
        attrs.append(f'width="{width}"')
    if height:
        attrs.append(f'height="{height}"')

    # Alt text
    attrs.append(f'alt="{alt}"')

    # Additional attributes
    for key, value in kwargs.items():
        attrs.append(f'{key}="{value}"')

    return f"<img {' '.join(attrs)} />"


def htmlLink(url: str, text: str, target: str = "_blank", **kwargs: Any) -> str:
    """
    Generate HTML anchor tag.

    Args:
        url: Link URL
        text: Link text
        target: Link target (_blank, _self, etc.)
        **kwargs: Additional HTML attributes

    Returns:
        HTML anchor tag

    Reference: PGstandard.pl::htmlLink
    """
    attrs = [f'href="{url}"', f'target="{target}"']

    for key, value in kwargs.items():
        attrs.append(f'{key}="{value}"')

    return f"<a {' '.join(attrs)}>{text}</a>"


def iframe(
    url: str,
    width: int = 800,
    height: int = 600,
    frameborder: int = 0,
    **kwargs: Any,
) -> str:
    """
    Generate HTML iframe tag.

    Args:
        url: Iframe URL
        width: Width in pixels
        height: Height in pixels
        frameborder: Frame border width
        **kwargs: Additional HTML attributes

    Returns:
        HTML iframe tag

    Reference: PGstandard.pl::iframe
    """
    attrs = [
        f'src="{url}"',
        f'width="{width}"',
        f'height="{height}"',
        f'frameborder="{frameborder}"',
    ]

    for key, value in kwargs.items():
        attrs.append(f'{key}="{value}"')

    return f"<iframe {' '.join(attrs)}></iframe>"
