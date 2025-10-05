"""
List MathObject for handling comma-separated lists of values.
"""

from typing import Any, Union
from .value import Value


class List(Value):
    """
    List MathObject - represents comma-separated lists of values.

    In WeBWorK, List is used for answers that require multiple values,
    such as List(1, 2, 3) for "enter all roots" or List(Formula("x+1"), Formula("x-1")).
    
    Special values:
    - List("NONE") for problems with no solutions
    """

    def __init__(self, *items, context=None):
        """
        Create a List.

        Args:
            *items: The items in the list (can be any MathObjects or values)
            context: The Context (None = use current)
        """
        super().__init__(context)
        
        # Handle special case: List("NONE")
        if len(items) == 1 and isinstance(items[0], str) and items[0].upper() == "NONE":
            self.items = []
            self.is_none = True
        else:
            # Store items, promoting primitives to MathObjects where appropriate
            self.items = []
            self.is_none = False
            for item in items:
                self.items.append(self._promote_item(item))

    def _promote_item(self, item: Any) -> Any:
        """
        Promote primitive values to MathObjects.
        
        Args:
            item: The item to promote
            
        Returns:
            MathObject or the original item
        """
        if isinstance(item, Value):
            # Already a MathObject
            return item
        elif isinstance(item, (int, float)):
            # Promote to Real
            from .real import Real
            return Real(item, self.context)
        elif isinstance(item, str):
            # Try to parse as Formula
            try:
                from .formula import Formula
                return Formula(item, self.context)
            except:
                # If parsing fails, keep as string
                return item
        else:
            # Keep as-is
            return item

    def __str__(self) -> str:
        """String representation."""
        if self.is_none:
            return "NONE"
        return ", ".join(str(item) for item in self.items)

    def __repr__(self) -> str:
        """Python representation."""
        if self.is_none:
            return 'List("NONE")'
        items_repr = ", ".join(repr(item) for item in self.items)
        return f"List({items_repr})"

    def TeX(self) -> str:
        """LaTeX representation."""
        if self.is_none:
            return r"\text{NONE}"
        return ", ".join(
            item.TeX() if hasattr(item, 'TeX') else str(item)
            for item in self.items
        )

    def __len__(self) -> int:
        """Number of items in the list."""
        return len(self.items)

    def __getitem__(self, index: int) -> Any:
        """Get item by index."""
        return self.items[index]

    def __iter__(self):
        """Iterate over items."""
        return iter(self.items)

    def __eq__(self, other) -> bool:
        """
        Equality comparison.
        
        Two lists are equal if they have the same items in the same order
        (or any order if unordered mode is enabled).
        """
        if not isinstance(other, List):
            return False
        
        if self.is_none and other.is_none:
            return True
        
        if self.is_none != other.is_none:
            return False
        
        if len(self.items) != len(other.items):
            return False
        
        # Check if unordered comparison is enabled
        unordered = self.context.flags.get('unorderedList', False)
        
        if unordered:
            # Check if all items match (in any order)
            # This is a simplified version - proper implementation would
            # handle duplicate items correctly
            other_items = list(other.items)
            for item in self.items:
                found = False
                for i, other_item in enumerate(other_items):
                    if self._items_equal(item, other_item):
                        other_items.pop(i)
                        found = True
                        break
                if not found:
                    return False
            return len(other_items) == 0
        else:
            # Ordered comparison
            for item1, item2 in zip(self.items, other.items):
                if not self._items_equal(item1, item2):
                    return False
            return True

    def _items_equal(self, item1: Any, item2: Any) -> bool:
        """
        Check if two items are equal.
        
        Handles comparison of different types properly.
        """
        # If both have __eq__, use it
        if hasattr(item1, '__eq__'):
            return item1 == item2
        return item1 == item2

    def cmp(self, **options):
        """
        Return an answer checker for this List.

        Options:
            ordered: Whether order matters (default: True)
            partialCredit: Whether to give partial credit for some correct answers
            showLengthHints: Whether to show hints about list length

        Returns:
            ListAnswerChecker
        """
        from .answer_checker import ListAnswerChecker
        return ListAnswerChecker(self, **options)
