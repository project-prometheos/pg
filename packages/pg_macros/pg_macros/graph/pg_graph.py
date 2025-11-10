"""PGgraphmacros - Graph initialization and function plotting for WeBWorK.

This module provides core graphing functionality from PGgraphmacros.pl:
- init_graph(): Create and configure a graph canvas with axes and grid
- add_functions(): Plot mathematical functions on a graph
- Plot(): Wrapper for plotting functions

Based on macros/graph/PGgraphmacros.pl from the WeBWorK distribution.
"""

from typing import Any, Dict, List, Optional, Tuple, Union


# Stub implementations - working versions of the functions
# These are imported into sandbox and used directly
def init_graph(*args, **kwargs):
    """Stub for PGgraphmacros.pl init_graph - creates graph object."""
    return type('WWPlot', (), {
        '__str__': lambda self: 'WWPlot',
        'draw': lambda *a, **k: None,
        'stamps': lambda *a, **k: None,
        'moveTo': lambda *a, **k: None,
        'lineTo': lambda *a, **k: None,
        'arrowTo': lambda *a, **k: None,
    })()


def add_functions(*args, **kwargs):
    """Stub for PGgraphmacros.pl add_functions - adds functions to graph."""
    return None


def Plot(*args, **kwargs):
    """Stub for Plot - plotting convenience function."""
    return init_graph(*args, **kwargs)


class WWPlot:
    """
    Graph canvas object for plotting in WeBWorK.

    This is a Python wrapper around the Perl WWPlot class that manages
    graph initialization, axes, grids, and function plotting.

    Attributes:
        xmin, xmax, ymin, ymax: Graph bounds in real coordinates
        width, height: Canvas size in pixels
    """

    def __init__(self, width: int = 200, height: int = 200):
        """
        Initialize a graph canvas.

        Args:
            width: Canvas width in pixels (default 200)
            height: Canvas height in pixels (default 200)
        """
        self.width = width
        self.height = height
        self.xmin = -10.0
        self.xmax = 10.0
        self.ymin = -10.0
        self.ymax = 10.0
        self.ext = '.png'
        self.image_name = None
        self.functions = []
        self.labels = []
        self.stamps = []
        self.axes_config = {}
        self.grid_config = {}
        self.tick_config = {}
        self.plot_vertical_axis = True

    def imageName(self, name: str) -> None:
        """Set the image filename for this graph."""
        self.image_name = name

    def h_axis(self, level: float, color: str = 'black') -> None:
        """
        Draw horizontal (x) axis.

        Args:
            level: y-coordinate where axis appears (usually 0)
            color: Color of axis line
        """
        self.axes_config['h_axis'] = {'level': level, 'color': color}

    def v_axis(self, level: float, color: str = 'black') -> None:
        """
        Draw vertical (y) axis.

        Args:
            level: x-coordinate where axis appears (usually 0)
            color: Color of axis line
        """
        self.axes_config['v_axis'] = {'level': level, 'color': color}

    def h_grid(self, color: str, *x_values: float) -> None:
        """
        Draw horizontal grid lines.

        Args:
            color: Color of grid lines
            x_values: x-coordinates where vertical grid lines appear
        """
        self.grid_config['h_grid'] = {'color': color, 'values': x_values}

    def v_grid(self, color: str, *y_values: float) -> None:
        """
        Draw vertical grid lines.

        Args:
            color: Color of grid lines
            y_values: y-coordinates where horizontal grid lines appear
        """
        self.grid_config['v_grid'] = {'color': color, 'values': y_values}

    def h_ticks(self, level: float, color: str, *y_values: float) -> None:
        """
        Draw horizontal tick marks.

        Args:
            level: y-coordinate where ticks appear
            color: Color of tick marks
            y_values: y-coordinates of tick positions
        """
        self.tick_config['h_ticks'] = {'level': level, 'color': color, 'values': y_values}

    def v_ticks(self, level: float, color: str, *x_values: float) -> None:
        """
        Draw vertical tick marks.

        Args:
            level: x-coordinate where ticks appear
            color: Color of tick marks
            x_values: x-coordinates of tick positions
        """
        self.tick_config['v_ticks'] = {'level': level, 'color': color, 'values': x_values}

    def lb(self, label: 'Label') -> None:
        """
        Add a label to the graph.

        Args:
            label: Label object to add
        """
        self.labels.append(label)

    def stamps(self, *stamp_objects: Any) -> None:
        """
        Add visual marks/stamps to the graph (circles, points, etc.).

        Args:
            stamp_objects: Stamp objects to add
        """
        self.stamps.extend(stamp_objects)

    def __repr__(self) -> str:
        """Return string representation of graph."""
        return f"WWPlot({self.width}x{self.height}, bounds=[{self.xmin},{self.ymin},{self.xmax},{self.ymax}])"


class Label:
    """
    Text label for placement on a graph.

    Attributes:
        x, y: Position on graph in real coordinates
        text: Label text content
        color: Color of label text
        horizontal_align: Horizontal alignment (left, center, right)
        vertical_align: Vertical alignment (top, middle, bottom)
    """

    def __init__(self, x: float, y: float, text: str, color: str = 'black',
                 horizontal_align: str = 'center', vertical_align: str = 'middle'):
        """
        Create a label for the graph.

        Args:
            x: x-coordinate position
            y: y-coordinate position
            text: Label text
            color: Text color (default 'black')
            horizontal_align: Alignment left/center/right
            vertical_align: Alignment top/middle/bottom
        """
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.horizontal_align = horizontal_align
        self.vertical_align = vertical_align


class Fun:
    """
    Function object for plotting on a graph.

    Wraps a Python function for plotting with configurable colors, weights, and domain.
    """

    def __init__(self, func: callable, graph: WWPlot):
        """
        Create a plottable function.

        Args:
            func: Python function to plot (takes x, returns y)
            graph: Graph object to associate with
        """
        self.func = func
        self.graph = graph
        self.color = 'black'
        self.weight = 2
        self.domain_min = None
        self.domain_max = None

    def color(self, color: str) -> 'Fun':
        """Set the line color."""
        self.color = color
        return self

    def weight(self, weight: int) -> 'Fun':
        """Set the line weight (width in pixels)."""
        self.weight = weight
        return self

    def domain(self, min_val: float, max_val: float) -> 'Fun':
        """
        Restrict the domain where this function is plotted.

        Args:
            min_val: Minimum x-value
            max_val: Maximum x-value
        """
        self.domain_min = min_val
        self.domain_max = max_val
        return self


__all__ = [
    'WWPlot',
    'Label',
    'Fun',
    'init_graph',
    'add_functions',
    'Plot',
]
