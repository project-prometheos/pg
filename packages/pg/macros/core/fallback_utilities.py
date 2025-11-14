"""
Fallback Utilities for WeBWorK.

This module provides miscellaneous fallback functions and utilities that are
not specific to other macro categories but are needed for general problem support.

These include utility functions like array operations, compatibility helpers,
and other general-purpose stubs.

Based on various PG core utilities.
"""

from typing import Any, List, Optional


def random_subset(n: Optional[int] = None, *items: Any, **kwargs: Any) -> List[Any]:
    """
    Select a random subset of items.

    Returns the first N items from a collection.

    Args:
        n: Number of items to return
        *items: Items to choose from
        **kwargs: Additional options

    Returns:
        List of selected items

    Perl Source: Random subset selection utility
    """
    if items:
        item_list = list(items[0]) if len(items) == 1 and hasattr(
            items[0], '__iter__') and not isinstance(items[0], str) else list(items)
        num = int(n) if n is not None else len(item_list)
        return item_list[:num]
    return []


def new_match_list(*args: Any, **kwargs: Any) -> Any:
    """
    Create a matching list object for fill-in-the-blank matching problems.

    Args:
        *args: Configuration arguments
        **kwargs: Options

    Returns:
        A matching list object with default methods

    Perl Source: Matching list creation utility
    """
    class _MatchListStub:
        def __getattr__(self, name: str) -> Any:
            """Allow any method call - just return self for chaining."""
            def method(*a, **kw):
                return self
            return method

        def __iter__(self):
            return iter([])

    return _MatchListStub()


def pop_up_list_print_q(*args: Any, **kwargs: Any) -> str:
    """
    Print a pop-up list question.

    Args:
        *args: Question components
        **kwargs: Options

    Returns:
        HTML string for pop-up list

    Perl Source: Pop-up list printing utility
    """
    return ""


def splice(array: List[Any], offset: int, length: int = 1,
           replacement: Optional[Any] = None) -> List[Any]:
    """
    Splice an array - remove and replace elements.

    Similar to Perl's splice function.

    Args:
        array: Array to splice
        offset: Starting position
        length: Number of elements to remove
        replacement: Elements to insert

    Returns:
        List of removed elements

    Perl Source: Array splicing utility
    """
    if offset < 0:
        offset = len(array) + offset

    removed = array[offset:offset + length]

    if replacement is not None:
        if not isinstance(replacement, list):
            replacement = [replacement]
        array[offset:offset + length] = replacement
    else:
        del array[offset:offset + length]

    return removed


def undef() -> None:
    """
    Perl's undef - returns None.

    Used to indicate undefined/null values.

    Returns:
        None

    Perl Source: Perl undef compatibility
    """
    return None


__all__ = [
    'random_subset',
    'new_match_list',
    'pop_up_list_print_q',
    'splice',
    'undef',
]
