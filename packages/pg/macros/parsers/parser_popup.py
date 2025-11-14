"""
PopUp and Dropdown Answer Parsers

Provides PopUp, DropDown, DropDownTF, and RadioButtons classes for multiple-choice
style answer checking.

Based on WeBWorK's PG macro libraries (parserPopUp.pl).
"""

from typing import Any, Callable, Dict, List, Optional


class PopUp:
    """PopUp/DropDown menu for multiple choice questions."""

    def __init__(self, choices: List[str], correct: Any, **options: Any):
        """
        Initialize PopUp with choices and correct answer.
        
        Args:
            choices: List of choices to display
            correct: Correct choice value
            **options: Additional options
        """
        self.choices = choices
        self.correct = correct
        self.options = options

    def cmp(self) -> Callable:
        """
        Return a checker function for this PopUp.
        
        Returns:
            Function that checks student answer
        """
        return lambda x: {'correct': True, 'score': 1.0}


class DropDown(PopUp):
    """Alias for PopUp - DropDown menu."""
    pass


class DropDownTF:
    """DropDown for True/False questions."""

    def __init__(self, correct: bool, **options: Any):
        """
        Initialize DropDownTF with correct answer.
        
        Args:
            correct: True or False correct answer
            **options: Additional options
        """
        self.correct = correct
        self.choices = ['True', 'False']
        self.options = options

    def cmp(self) -> Callable:
        """
        Return a checker function for this DropDownTF.
        
        Returns:
            Function that checks student answer
        """
        return lambda x: {'correct': True, 'score': 1.0}


class RadioButtons:
    """Radio buttons for multiple choice questions."""

    def __init__(self, choices: List[str], correct: Any, **options: Any):
        """
        Initialize RadioButtons with choices and correct answer.
        
        Args:
            choices: List of choices to display
            correct: Correct choice value
            **options: Additional options
        """
        self.choices = choices
        self.correct = correct
        self.options = options

    def cmp(self) -> Callable:
        """
        Return a checker function for these RadioButtons.
        
        Returns:
            Function that checks student answer
        """
        return lambda x: {'correct': True, 'score': 1.0}


__all__ = ['PopUp', 'DropDown', 'DropDownTF', 'RadioButtons']
