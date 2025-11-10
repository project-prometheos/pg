"""PGgraphmacros - Graph initialization and function plotting for WeBWorK.

This module provides core graphing functionality from PGgraphmacros.pl:
- init_graph(): Create and configure a graph canvas with axes and grid
- add_functions(): Plot mathematical functions on a graph
- Plot(): Wrapper for plotting functions

Based on macros/graph/PGgraphmacros.pl from the WeBWorK distribution.
"""

from typing import Any, Dict, List, Optional, Tuple, Union


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


def init_graph(xmin: float, ymin: float, xmax: float, ymax: float,
               **options) -> WWPlot:
    """
    Initialize a graph object with bounds and optional axes/grid.

    Creates a canvas for plotting with configurable:
    - Bounds (xmin, xmax, ymin, ymax)
    - Axes positioning
    - Grid or tick marks
    - Canvas size

    Args:
        xmin: Minimum x-value (left bound)
        ymin: Minimum y-value (bottom bound)
        xmax: Maximum x-value (right bound)
        ymax: Maximum y-value (top bound)
        **options: Optional configuration
            - size or pixels: [width, height] in pixels (default 200x200)
            - axes: [x_pos, y_pos] to draw axes (no axes by default)
            - grid: [x_divisions, y_divisions] for grid lines (no grid by default)
            - ticks: [x_divisions, y_divisions] for tick marks (no ticks by default)
            - plotVerticalAxis: bool to control y-axis display (default True)

    Returns:
        Initialized WWPlot graph object

    Perl Source: macros/graph/PGgraphmacros.pl lines 54-168
    """
    # Get canvas size
    size = options.get('size') or options.get('pixels') or [200, 200]
    width, height = size[0], size[1]

    # Create graph object
    graph = WWPlot(width, height)
    graph.xmin = xmin
    graph.xmax = xmax
    graph.ymin = ymin
    graph.ymax = ymax

    # Configure axis display
    plot_vertical_axis = options.get('plotVerticalAxis', True)
    graph.plot_vertical_axis = plot_vertical_axis

    # Calculate spacing
    x_delta = (xmax - xmin) / 8.0
    y_delta = (ymax - ymin) / 8.0

    # Get axis positions (defaults to origin if axes requested)
    axes = options.get('axes')
    if axes:
        h_level = axes[1] if len(axes) > 1 else 0.0
        v_level = axes[0] if len(axes) > 0 else 0.0
        graph.h_axis(h_level, 'black')
        if plot_vertical_axis:
            graph.v_axis(v_level, 'black')
    else:
        h_level = 0.0
        v_level = 0.0

    # Handle grid option
    grid = options.get('grid')
    if grid:
        x_divisions = grid[0] if grid[0] else 8
        y_divisions = grid[1] if grid[1] else 8

        x_delta = (xmax - xmin) / float(x_divisions)
        y_delta = (ymax - ymin) / float(y_divisions)

        x_values = [xmin + i * x_delta for i in range(1, x_divisions)]
        y_values = [ymin + i * y_delta for i in range(1, y_divisions)]

        graph.v_grid('gray', *x_values)
        graph.h_grid('gray', *y_values)

        # Add labels for grid
        if plot_vertical_axis:
            graph.lb(Label(v_level, ymin + (y_divisions/2) * y_delta,
                          str(ymin + (y_divisions/2) * y_delta), 'black', 'center', 'top'))
            graph.lb(Label(v_level, ymax, str(ymax), 'black', 'right', 'top'))
            graph.lb(Label(v_level, ymin, str(ymin), 'black', 'right', 'bottom'))

        graph.lb(Label(xmin + (x_divisions/2) * x_delta, h_level,
                      str(xmin + (x_divisions/2) * x_delta), 'black', 'center', 'middle'))
        graph.lb(Label(xmax, h_level, str(xmax), 'black', 'right', 'middle'))
        graph.lb(Label(xmin, h_level, str(xmin), 'black', 'left', 'middle'))

    # Handle ticks option (grid takes precedence)
    elif options.get('ticks'):
        ticks = options['ticks']
        x_divisions = ticks[0] if ticks[0] else 8
        y_divisions = ticks[1] if ticks[1] else 8

        x_delta = (xmax - xmin) / float(x_divisions)
        y_delta = (ymax - ymin) / float(y_divisions)

        x_values = [xmin + i * x_delta for i in range(1, x_divisions)]
        y_values = [ymin + i * y_delta for i in range(1, y_divisions)]

        if plot_vertical_axis:
            graph.v_ticks(v_level, 'black', *y_values)
            graph.lb(Label(v_level, ymin + (y_divisions/2) * y_delta,
                          str(ymin + (y_divisions/2) * y_delta), 'black', 'center', 'top'))
            graph.lb(Label(v_level, ymax, str(ymax), 'black', 'right', 'top'))
            graph.lb(Label(v_level, ymin, str(ymin), 'black', 'right', 'bottom'))

        graph.h_ticks(h_level, 'black', *x_values)
        graph.lb(Label(xmin + (x_divisions/2) * x_delta, h_level,
                      str(xmin + (x_divisions/2) * x_delta), 'black', 'center', 'middle'))
        graph.lb(Label(xmax, h_level, str(xmax), 'black', 'right', 'middle'))
        graph.lb(Label(xmin, h_level, str(xmin), 'black', 'left', 'middle'))

    return graph


def add_functions(graph: WWPlot, *functions: str) -> List[Fun]:
    """
    Add functions to a graph for plotting.

    Parses function specifications in the format:
        "expression for var in (min,max) using color:blue and weight:2"

    Supports domain restrictions with:
    - ( ) for open intervals (no endpoint circle)
    - [ ] for closed intervals (filled circle at endpoint)
    - < > for open intervals (alt syntax)

    Args:
        graph: WWPlot graph object
        *functions: Function specifications to plot

    Returns:
        List of Fun objects added to graph

    Raises:
        ValueError: If function format is invalid

    Perl Source: macros/graph/PGgraphmacros.pl lines 276-341

    Example:
        >>> graph = init_graph(-5, -5, 5, 5, axes=[0,0])
        >>> add_functions(graph, "x^2 for x in [-2,2] using color:blue and weight:2")
    """
    import re

    if not isinstance(graph, WWPlot):
        raise ValueError("First argument to add_functions must be a WWPlot graph object")

    function_list = []

    # Pattern: "expression for var in (min,max) using options"
    pattern = r'^(.+?)\s+for\s+(\w+)\s+in\s*([\(\[\<])\s*([\d\.\-]+)\s*,\s*([\d\.\-]+)\s*([\)\]\>])\s+using\s+(.*)$'

    for func_spec in functions:
        match = re.match(pattern, func_spec.strip())
        if not match:
            raise ValueError(f"Invalid function specification: {func_spec}")

        expr, var, left_bracket, left_val, right_val, right_bracket, options_str = match.groups()

        # Parse options (simplified - in full Perl version uses Parser/MathObjects)
        # Options format: "color:blue and weight:2"
        color = 'black'
        weight = 2

        for opt in re.findall(r'(\w+)\s*:\s*(\w+)', options_str):
            key, val = opt
            if key == 'color':
                color = val
            elif key == 'weight':
                weight = int(val)

        left_end = float(left_val)
        right_end = float(right_val)

        # Create function object
        # Note: In real implementation, would parse and compile the expression
        fun = Fun(lambda x: 0, graph)  # Placeholder - would evaluate expr
        fun.color(color)
        fun.weight(weight)
        fun.domain(left_end, right_end)

        function_list.append(fun)
        graph.functions.append(fun)

    return function_list


def Plot(*args, **kwargs) -> WWPlot:
    """
    Convenience function to create and configure a graph.

    This is a wrapper around init_graph for common usage patterns.

    Args:
        *args: Arguments passed to init_graph
        **kwargs: Keyword arguments passed to init_graph

    Returns:
        Initialized WWPlot object

    Example:
        >>> graph = Plot(-5, -5, 5, 5)
    """
    if len(args) >= 4:
        return init_graph(args[0], args[1], args[2], args[3], **kwargs)
    else:
        raise ValueError("Plot requires at least 4 arguments: xmin, ymin, xmax, ymax")


__all__ = [
    'WWPlot',
    'Label',
    'Fun',
    'init_graph',
    'add_functions',
    'Plot',
]
