"""Lightweight graph runtime compatible with PGgraphmacros semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Tuple

from .rng import get_rng


@dataclass
class GraphOptions:
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    size: Tuple[int, int] = (200, 200)
    axes: Tuple[float, float] | None = None
    ticks: Tuple[int, int] | None = None
    grid: Tuple[int, int] | None = None
    plot_vertical_axis: bool = True


@dataclass
class GraphFunction:
    expression: str
    color: str = 'black'
    style: str = 'solid'
    weight: int = 1


@dataclass
class GraphLabel:
    text: str
    x: float
    y: float
    align: str = 'center'
    valign: str = 'middle'


class GraphBuilder:
    """Stateful graph description for deterministic rendering."""

    def __init__(self, xmin: float, ymin: float, xmax: float, ymax: float, **options: Any):
        size = tuple(options.get('size') or options.get('pixels') or (200, 200))
        axes = tuple(options['axes']) if 'axes' in options else None
        ticks = tuple(options['ticks']) if 'ticks' in options else None
        grid = tuple(options['grid']) if 'grid' in options else None
        plot_vertical = options.get('plotVerticalAxis', True)

        self.options = GraphOptions(
            xmin=xmin,
            ymin=ymin,
            xmax=xmax,
            ymax=ymax,
            size=size,
            axes=axes,
            ticks=ticks,
            grid=grid,
            plot_vertical_axis=plot_vertical,
        )
        self.functions: List[GraphFunction] = []
        self.labels: List[GraphLabel] = []
        self.seed = options.get('seed') or get_rng().randint(1, 1_000_000)

    def add_function(self, expression: str, color: str = 'black', style: str = 'solid', weight: int = 1) -> None:
        self.functions.append(GraphFunction(expression=expression, color=color, style=style, weight=weight))

    def add_label(
        self,
        x: float,
        y: float,
        text: str,
        align: str = 'center',
        valign: str = 'middle',
    ) -> None:
        self.labels.append(GraphLabel(text=text, x=x, y=y, align=align, valign=valign))

    def snapshot(self) -> dict[str, Any]:
        return {
            'bounds': {
                'xmin': self.options.xmin,
                'ymin': self.options.ymin,
                'xmax': self.options.xmax,
                'ymax': self.options.ymax,
            },
            'size': self.options.size,
            'axes': self.options.axes,
            'ticks': self.options.ticks,
            'grid': self.options.grid,
            'plot_vertical_axis': self.options.plot_vertical_axis,
            'functions': [fn.__dict__ for fn in self.functions],
            'labels': [lb.__dict__ for lb in self.labels],
            'seed': self.seed,
        }


__all__ = ['GraphBuilder', 'GraphOptions']
