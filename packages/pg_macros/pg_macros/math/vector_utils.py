"""Vector Utilities for WeBWorK.

This module provides vector manipulation and geometric utilities including
norm, unit vector calculations, and geometric line representation.

Based on Value.pm from the Perl WeBWorK distribution.
"""

import math
from typing import List, Optional, Tuple, Union


def norm(vector: Union[List[float], Tuple[float, ...], 'Vector']) -> float:
    """
    Compute the norm (magnitude/length) of a vector.
    
    The norm is calculated as: ||v|| = √(v₁² + v₂² + ... + vₙ²)
    
    Args:
        vector: A vector as a list, tuple, or Vector object
        
    Returns:
        The magnitude of the vector
        
    Example:
        >>> norm([3, 4])
        5.0
        >>> norm((1, 1, 1))
        1.7320508075688772
    
    Perl Source: Value.pm Vector methods
    """
    if hasattr(vector, 'norm'):
        # If it's a Vector object with norm method
        return vector.norm()
    
    # Fallback for list/tuple
    if not vector:
        return 0.0
    
    sum_of_squares = sum(x**2 for x in vector)
    return math.sqrt(sum_of_squares)


def unit(vector: Union[List[float], Tuple[float, ...], 'Vector']) -> Union[List[float], 'Vector']:
    """
    Compute the unit vector in the direction of the given vector.
    
    The unit vector is: u = v / ||v||
    
    Args:
        vector: A vector as a list, tuple, or Vector object
        
    Returns:
        Unit vector in the same direction as input
        
    Raises:
        ValueError: If the vector is zero (magnitude is 0)
        
    Example:
        >>> unit([3, 4])
        [0.6, 0.8]
        >>> unit((1, 0, 0))
        [1.0, 0.0, 0.0]
    
    Perl Source: Value.pm Vector methods
    """
    if hasattr(vector, 'unit'):
        # If it's a Vector object with unit method
        return vector.unit()
    
    # Fallback for list/tuple
    magnitude = norm(vector)
    
    if magnitude == 0:
        raise ValueError("Cannot compute unit vector of zero vector")
    
    # Return as list (same type as input)
    return [x / magnitude for x in vector]


class Line:
    """
    Geometric line representation in 2D or 3D space.
    
    A line can be defined by a point and a direction vector, or by
    two points that the line passes through.
    
    Attributes:
        point: A point (base point) on the line
        direction: Direction vector of the line
        point2: Optional second point for parametric definition
    """
    
    def __init__(self, point: Union[List, Tuple] = None, direction: Union[List, Tuple] = None, 
                 point2: Union[List, Tuple] = None, **kwargs):
        """
        Create a geometric line.
        
        Args:
            point: Base point on the line (e.g., [1, 2] in 2D)
            direction: Direction vector of the line (e.g., [3, 4])
            point2: Alternative second point to define the line through two points
            **kwargs: Additional options
            
        Example:
            >>> line = Line([0, 0], [1, 1])  # Line through origin with direction (1,1)
            >>> line2 = Line([1, 2], point2=[3, 4])  # Line through two points
        
        Perl Source: Value.pm Line class
        """
        self.point = point or []
        self.direction = direction or []
        self.point2 = point2
        self.options = kwargs
        
        # If point2 is provided, calculate direction vector
        if self.point2 and self.point:
            self.direction = [self.point2[i] - self.point[i] for i in range(len(self.point))]
    
    def evaluate(self, t: float) -> List[float]:
        """
        Evaluate the line at parameter value t.
        
        Returns: point + t * direction
        
        Args:
            t: Parameter value
            
        Returns:
            Point on the line at parameter t
            
        Example:
            >>> line = Line([0, 0], [1, 1])
            >>> line.evaluate(2)
            [2, 2]
        """
        return [self.point[i] + t * self.direction[i] for i in range(len(self.point))]
    
    def __str__(self) -> str:
        """Return string representation."""
        if self.point and self.direction:
            return f"Line through {self.point} with direction {self.direction}"
        return "Line"
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"Line({self.point}, {self.direction})"


__all__ = [
    'norm',
    'unit',
    'Line',
]

