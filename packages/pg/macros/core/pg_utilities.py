"""
PG Utility Functions - Mathematical and helper functions.

Common utility functions used in PG problems.
Reference: PGauxiliaryFunctions.pl
"""

import math
from typing import Any


def gcf(*args: int) -> int:
    """
    Greatest common factor (GCF) / Greatest common divisor (GCD).
    
    Args:
        *args: Two or more integers
        
    Returns:
        GCF of all arguments
        
    Examples:
        >>> gcf(12, 18)
        6
        >>> gcf(24, 36, 60)
        12
        
    Reference: PGauxiliaryFunctions.pl::gcf
    """
    if len(args) < 2:
        raise ValueError("gcf requires at least 2 arguments")
    
    result = args[0]
    for num in args[1:]:
        result = math.gcd(result, num)
    return result


def gcd(*args: int) -> int:
    """
    Alias for gcf().
    
    Reference: PGauxiliaryFunctions.pl::gcd
    """
    return gcf(*args)


def lcm(*args: int) -> int:
    """
    Least common multiple (LCM).
    
    Args:
        *args: Two or more integers
        
    Returns:
        LCM of all arguments
        
    Examples:
        >>> lcm(4, 6)
        12
        >>> lcm(3, 4, 5)
        60
        
    Reference: PGauxiliaryFunctions.pl::lcm
    """
    if len(args) < 2:
        raise ValueError("lcm requires at least 2 arguments")
    
    result = args[0]
    for num in args[1:]:
        result = abs(result * num) // math.gcd(result, num)
    return result


def reduce_fraction(num: int, den: int) -> tuple[int, int]:
    """
    Reduce a fraction to lowest terms.
    
    Args:
        num: Numerator
        den: Denominator
        
    Returns:
        Tuple of (reduced_numerator, reduced_denominator)
        
    Examples:
        >>> reduce_fraction(12, 18)
        (2, 3)
        >>> reduce_fraction(7, 5)
        (7, 5)
        
    Reference: PGauxiliaryFunctions.pl::reduce_fraction
    """
    if den == 0:
        raise ValueError("Denominator cannot be zero")
    
    g = math.gcd(abs(num), abs(den))
    return (num // g, den // g)


def sgn(x: float) -> int:
    """
    Sign function.
    
    Args:
        x: Number
        
    Returns:
        -1 if x < 0, 0 if x == 0, 1 if x > 0
        
    Examples:
        >>> sgn(-5)
        -1
        >>> sgn(0)
        0
        >>> sgn(3.7)
        1
        
    Reference: PGauxiliaryFunctions.pl::sgn
    """
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0


def max_number(*args: float) -> float:
    """
    Maximum of numbers.
    
    Args:
        *args: Numbers to compare
        
    Returns:
        Maximum value
        
    Examples:
        >>> max_number(3, 7, 2)
        7
        
    Reference: PGauxiliaryFunctions.pl::max
    """
    if not args:
        raise ValueError("max_number requires at least one argument")
    return max(args)


def min_number(*args: float) -> float:
    """
    Minimum of numbers.
    
    Args:
        *args: Numbers to compare
        
    Returns:
        Minimum value
        
    Examples:
        >>> min_number(3, 7, 2)
        2
        
    Reference: PGauxiliaryFunctions.pl::min
    """
    if not args:
        raise ValueError("min_number requires at least one argument")
    return min(args)


def step(x: float) -> int:
    """
    Unit step function (Heaviside function).
    
    Args:
        x: Input value
        
    Returns:
        0 if x < 0, 1 if x >= 0
        
    Examples:
        >>> step(-1)
        0
        >>> step(0)
        1
        >>> step(5)
        1
        
    Reference: PGauxiliaryFunctions.pl::step
    """
    return 1 if x >= 0 else 0


def fact(n: int) -> int:
    """
    Factorial function.
    
    Args:
        n: Non-negative integer
        
    Returns:
        n! = n * (n-1) * ... * 2 * 1
        
    Examples:
        >>> fact(0)
        1
        >>> fact(5)
        120
        
    Reference: PGauxiliaryFunctions.pl::fact
    """
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    return math.factorial(n)


def C(n: int, k: int) -> int:
    """
    Binomial coefficient: n choose k.
    
    Args:
        n: Total items
        k: Items to choose
        
    Returns:
        Number of ways to choose k items from n
        
    Examples:
        >>> C(5, 2)
        10
        >>> C(10, 3)
        120
        
    Reference: PGauxiliaryFunctions.pl::C
    """
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def P(n: int, k: int) -> int:
    """
    Permutations: n permute k.
    
    Args:
        n: Total items
        k: Items to arrange
        
    Returns:
        Number of ways to arrange k items from n
        
    Examples:
        >>> P(5, 2)
        20
        >>> P(10, 3)
        720
        
    Reference: PGauxiliaryFunctions.pl::P
    """
    if k < 0 or k > n:
        return 0
    return math.perm(n, k)


def lex_sort(*items: str) -> list[str]:
    """
    Lexicographic (alphabetical) sort.
    
    Args:
        *items: Strings to sort
        
    Returns:
        Sorted list of strings
        
    Examples:
        >>> lex_sort("zebra", "apple", "banana")
        ['apple', 'banana', 'zebra']
        
    Reference: PGauxiliaryFunctions.pl::lex_sort
    """
    return sorted(items)


def num_sort(*numbers: float) -> list[float]:
    """
    Numerical sort.
    
    Args:
        *numbers: Numbers to sort
        
    Returns:
        Sorted list of numbers
        
    Examples:
        >>> num_sort(5, 2, 8, 1)
        [1, 2, 5, 8]
        
    Reference: PGauxiliaryFunctions.pl::num_sort
    """
    return sorted(numbers)


def uniq(*items: Any) -> list[Any]:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        *items: Items (possibly with duplicates)
        
    Returns:
        List with duplicates removed
        
    Examples:
        >>> uniq(1, 2, 2, 3, 1, 4)
        [1, 2, 3, 4]
        
    Reference: PGauxiliaryFunctions.pl::uniq
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# Export all functions
__all__ = [
    "gcf",
    "gcd",
    "lcm",
    "reduce_fraction",
    "sgn",
    "max_number",
    "min_number",
    "step",
    "fact",
    "C",
    "P",
    "lex_sort",
    "num_sort",
    "uniq",
]

