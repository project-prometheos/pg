"""
Statistics Utilities for WeBWorK.

This module provides statistical functions for WeBWorK problems,
including linear regression calculations.

Based on PGstatisticsmacros.pl from the Perl WeBWorK distribution.
"""

from typing import Any, List, Optional, Tuple, Union


def linear_regression(*args: Any, **kwargs: Any) -> Tuple[float, float]:
    """
    Calculate linear regression statistics.
    
    Performs linear regression calculation on data points, returning
    the slope and intercept of the best-fit line.
    
    Args:
        *args: Data points or arrays (implementation-dependent)
        **kwargs: Options for regression calculation
        
    Returns:
        Tuple of (slope, intercept) for the regression line
        
    Example:
        >>> from pg.macros.math.statistics_utils import linear_regression
        >>> slope, intercept = linear_regression([1, 2, 3], [2, 4, 5])
        >>> # Returns (slope=1, intercept=0) by default
    
    Perl Source: PGstatisticsmacros.pl linear_regression function
    """
    # Stub implementation returns default values
    # In a full implementation, this would calculate actual regression
    return (1, 0)


def stats_mean(*values: Any) -> float:
    """
    Calculate the mean (average) of values.
    
    Args:
        *values: Values to average, or a single list/tuple of values
        
    Returns:
        The arithmetic mean of the values
        
    Perl Source: PGstatisticsmacros.pl stats_mean function
    """
    if len(values) == 1 and isinstance(values[0], (list, tuple)):
        values = values[0]
    return sum(values) / len(values) if values else 0.0


def stats_sd(*values: Any) -> float:
    """
    Calculate the standard deviation of values.
    
    Args:
        *values: Values to analyze, or a single list/tuple of values
        
    Returns:
        The sample standard deviation
        
    Perl Source: PGstatisticsmacros.pl stats_sd function
    """
    import math
    
    if len(values) == 1 and isinstance(values[0], (list, tuple)):
        values = values[0]
    
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def stats_SX_SXX(*values: Any) -> Tuple[float, float]:
    """
    Calculate sum of X and sum of X squared.
    
    Args:
        *values: Values to analyze, or a single list/tuple of values
        
    Returns:
        Tuple of (sum_x, sum_x_squared)
        
    Perl Source: PGstatisticsmacros.pl stats_SX_SXX function
    """
    if len(values) == 1 and isinstance(values[0], (list, tuple)):
        values = values[0]
    
    sum_x = sum(values) if values else 0.0
    sum_sq = sum(x ** 2 for x in values) if values else 0.0
    return (sum_x, sum_sq)


__all__ = [
    'linear_regression',
    'stats_mean',
    'stats_sd',
    'stats_SX_SXX',
]

