"""
parserPopUp.pl - Popup menu parser

Python port of macros/parsers/parserPopUp.pl

Reference: parserPopUp.pl
"""

from dataclasses import dataclass

from pg_answer import AnswerEvaluator
from pg_answer.evaluators.string import StringEvaluator

__exports__ = ["PopUp"]


@dataclass
class PopUp:
    """
    Popup menu for answer selection.

    Reference: parserPopUp.pl::PopUp
    """

    choices: list[str]
    correct_index: int = 0

    def __init__(self, choices: list[str], correct: str | int | None = None):
        """
        Create popup menu.

        Args:
            choices: List of choices
            correct: Correct choice (index or string)
        """
        self.choices = choices

        if correct is None:
            self.correct_index = 0
        elif isinstance(correct, int):
            self.correct_index = correct
        else:
            try:
                self.correct_index = choices.index(correct)
            except ValueError:
                raise ValueError(f"Choice '{correct}' not in list")

    def menu(self) -> str:
        """
        Generate HTML select menu.

        Returns:
            HTML select element
        """
        options = []
        for i, choice in enumerate(self.choices):
            selected = ' selected' if i == self.correct_index else ''
            options.append(f'<option value="{i}"{selected}>{choice}</option>')

        return f'<select name="answer">\n{chr(10).join(options)}\n</select>'

    def cmp(self) -> AnswerEvaluator:
        """Return answer evaluator."""
        return StringEvaluator(
            correct_answer=str(self.correct_index),
            case_sensitive=False,
        )

    def correct_ans(self) -> str:
        """Return correct answer text."""
        return self.choices[self.correct_index]
