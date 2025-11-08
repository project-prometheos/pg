"""Graph macro implementations mirroring PGgraphmacros.pl."""

from __future__ import annotations

from typing import Any, Iterable

from .runtime.graph import GraphBuilder
from .runtime.render import sanitize_html


def init_graph(xmin: float, ymin: float, xmax: float, ymax: float, **options: Any) -> GraphBuilder:
    """Create a graph builder with PG-compatible defaults."""
    return GraphBuilder(xmin, ymin, xmax, ymax, **options)


def add_functions(graph: GraphBuilder, *function_specs: tuple[str, str | None, str | None, int | None]) -> GraphBuilder:
    """Add functions to the graph (expression, color, style, weight)."""
    for spec in function_specs:
        expr = spec[0]
        color = spec[1] if len(spec) > 1 and spec[1] is not None else 'black'
        style = spec[2] if len(spec) > 2 and spec[2] is not None else 'solid'
        weight = spec[3] if len(spec) > 3 and spec[3] is not None else 1
        graph.add_function(expr, color=color, style=style, weight=weight)
    return graph


def add_label(graph: GraphBuilder, x: float, y: float, text: str, *, align: str = 'center', valign: str = 'middle') -> GraphBuilder:
    graph.add_label(x=x, y=y, text=text, align=align, valign=valign)
    return graph


def graph_to_html(graph: GraphBuilder) -> str:
    """Render a deterministic HTML stub summarizing the graph."""
    snapshot = graph.snapshot()
    meta_parts = [
        f"bounds=({snapshot['bounds']['xmin']},{snapshot['bounds']['ymin']},{snapshot['bounds']['xmax']},{snapshot['bounds']['ymax']})",
        f"size={snapshot['size'][0]}x{snapshot['size'][1]}",
        f"functions={len(snapshot['functions'])}",
        f"labels={len(snapshot['labels'])}",
    ]
    return sanitize_html(f"<div class=\"pg-graph\" data-meta='{';'.join(meta_parts)}'></div>")


def graph_metadata(graph: GraphBuilder) -> dict[str, Any]:
    """Expose serialized metadata for golden tests."""
    return graph.snapshot()


__exports__ = {
    'init_graph': init_graph,
    'add_functions': add_functions,
    'add_label': add_label,
    'graph_to_html': graph_to_html,
    'graph_metadata': graph_metadata,
}

__all__ = list(__exports__.keys())
