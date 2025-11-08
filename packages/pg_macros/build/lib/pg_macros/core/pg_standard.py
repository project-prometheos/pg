"""PGstandard.pl - supplemental conveniences atop PGcore."""

from __future__ import annotations

import html
from typing import Any, List

from ..runtime.render import sanitize_html
from ..runtime.rng import get_rng
from .pg_basic_macros import ans_rule as _ans_rule


def image(filename: str, **options: Any) -> str:
    """Render an ``<img>`` tag with sanitized and escaped attributes."""
    attrs: List[str] = [
        f'src="{html.escape(str(filename), quote=True)}"'
    ]
    for key, value in options.items():
        if value is None:
            continue
        attrs.append(
            f'{html.escape(str(key), quote=True)}="{html.escape(str(value), quote=True)}"'
        )
    return sanitize_html(f"<img {' '.join(attrs)}/>")


def bold(text: str) -> str:
    """Return Markdown-style bold text."""
    return f"**{text}**"


def italic(text: str) -> str:
    """Return Markdown-style italic text."""
    return f"*{text}*"


def underline(text: str) -> str:
    """Return HTML underlined text."""
    return f"<u>{text}</u>"


def shuffle(*items: Any) -> list[Any]:
    """Shuffle provided items using the PG deterministic RNG."""
    values = list(items)
    get_rng().shuffle(values)
    return values


def random_subset(n: int, *items: Any) -> list[Any]:
    """Select ``n`` unique items using the PG deterministic RNG."""
    population = list(items)
    if n > len(population):
        raise ValueError("random_subset: requested more items than available")
    return get_rng().sample(population, n)


__exports__ = [
    'image',
    'bold',
    'italic',
    'underline',
    'shuffle',
    'random_subset',
]

# Legacy exports sourced/implemented here to maintain compatibility.
ans_rule = _ans_rule


def solution(*args: Any) -> str:
    content = ''.join(str(arg) for arg in args)
    return f'<div class="solution">{content}</div>'


def hint(*args: Any) -> str:
    content = ''.join(str(arg) for arg in args)
    return f'<div class="hint">{content}</div>'


__exports__.extend(['ans_rule', 'solution', 'hint'])
