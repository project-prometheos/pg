"""Rendering helpers for PG macro runtime."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pg_pgml import PGMLParser, HTMLRenderer, TeXRenderer


@dataclass
class RenderResult:
    """Bundle PGML rendering outputs."""

    html: str
    tex: str
    metadata: dict[str, Any]


def sanitize_html(value: str) -> str:
    """Normalize HTML for stable snapshots."""
    collapsed = re.sub(r"\s+", " ", value).strip()
    collapsed = collapsed.replace(' >', '>').replace('< ', '<')
    return collapsed


def sanitize_tex(value: str) -> str:
    """Normalize TeX output (trim redundant whitespace)."""
    collapsed = re.sub(r"\s+", " ", value).strip()
    return collapsed


def render_pgml(text: str, *, context: dict[str, Any] | None = None) -> RenderResult:
    """Render PGML to HTML + TeX, capturing renderer metadata."""
    parser = PGMLParser()
    document = parser.parse_text(text)

    html_renderer = HTMLRenderer(context=context or {})
    tex_renderer = TeXRenderer(context=context or {})

    html_output = sanitize_html(html_renderer.render(document))
    tex_output = sanitize_tex(tex_renderer.render(document))

    metadata = {
        'blocks': len(document.blocks),
        'variables': list(getattr(document, 'variables', [])) or [],
    }

    return RenderResult(html=html_output, tex=tex_output, metadata=metadata)


__all__ = ['RenderResult', 'render_pgml', 'sanitize_html', 'sanitize_tex']
