"""AnswerFormatHelp macros providing inline help snippets."""

from __future__ import annotations

from typing import Dict

from .runtime.render import sanitize_html

_HELP_TOPICS: Dict[str, dict[str, str]] = {
    'numbers': {
        'title': 'Entering Numbers',
        'body': 'Use plain numbers like 2, -3.5, or scientific notation 4.2e-3.',
    },
    'formulas': {
        'title': 'Entering Formulas',
        'body': 'Use variables, parentheses, and operators: e.g., (x^2 + 1)/(x-3).',
    },
    'equations': {
        'title': 'Entering Equations',
        'body': 'Provide both sides, e.g., y = 2*x + 1.',
    },
}


def AnswerFormatHelp(topic: str, label: str | None = None) -> str:
    """Return formatted HTML block for the requested help topic."""
    data = _HELP_TOPICS.get(topic.lower())
    if not data:
        raise KeyError(f"Unknown AnswerFormatHelp topic: {topic}")
    title = sanitize_html(label or data['title'])
    body = sanitize_html(data['body'])
    return (
        "<div class=\"answer-format-help\">"
        f"<strong>{title}</strong>"
        f"<div class=\"answer-format-body\">{body}</div>"
        "</div>"
    )


def helpLink(topic: str, label: str | None = None) -> str:
    """Return an HTML link that expands the help content."""
    data = _HELP_TOPICS.get(topic.lower())
    if not data:
        raise KeyError(f"Unknown AnswerFormatHelp topic: {topic}")
    title = sanitize_html(label or data['title'])
    return f"<a class=\"answer-format-help-link\" data-topic=\"{topic}\">{title}</a>"


def addAnswerFormat(topic: str, *, title: str, body: str) -> None:
    """Register or override a help topic."""
    _HELP_TOPICS[topic.lower()] = {'title': title, 'body': body}


__exports__ = {
    'AnswerFormatHelp': AnswerFormatHelp,
    'helpLink': helpLink,
    'addAnswerFormat': addAnswerFormat,
}

__all__ = list(__exports__.keys())
