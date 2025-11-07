"""PopUp and DropDown menu objects for answer selection."""

from typing import Any


class PopUp:
    """Legacy popup menu object."""

    def __init__(self, choices: list, correct: Any, **options):
        """
        Create a popup menu.

        Args:
            choices: List of choice strings
            correct: Correct answer (string or index)
            **options: Additional options
        """
        self.choices = self._flatten_choices(choices)
        self.correct = correct
        self.options = options

        # Resolve correct answer
        if isinstance(correct, int) and not options.get('noindex', False):
            self.correct_value = self.choices[correct] if correct < len(self.choices) else correct
        else:
            self.correct_value = correct

    def _flatten_choices(self, choices: list) -> list:
        """Flatten nested choice lists (randomization groups)."""
        result = []
        for item in choices:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result

    def cmp(self):
        """Return answer evaluator."""
        def check_answer(student_answer: str) -> dict:
            correct = str(student_answer) == str(self.correct_value)
            return {
                'correct': correct,
                'score': 1.0 if correct else 0.0,
                'message': ''
            }

        class PopUpEvaluator:
            def evaluate(self, answer: str) -> Any:
                from dataclasses import dataclass

                @dataclass
                class AnswerResult:
                    correct: bool
                    score: float
                    messages: list = None

                result = check_answer(answer)
                return AnswerResult(
                    correct=result['correct'],
                    score=result['score'],
                    messages=[]
                )

        return PopUpEvaluator()

    def __str__(self):
        return f"PopUp({self.choices}, {self.correct_value})"


class DropDown(PopUp):
    """DropDown menu object (like PopUp but with placeholder)."""

    def __init__(self, choices: list, correct: Any, **options):
        """
        Create a dropdown menu.

        Args:
            choices: List of choice strings
            correct: Correct answer (string or index)
            **options: Additional options (placeholder, etc.)
        """
        # Set default placeholder for DropDown
        if 'placeholder' not in options:
            options['placeholder'] = '?'

        super().__init__(choices, correct, **options)


def DropDownTF(correct: Any, **options) -> DropDown:
    """
    Create a True/False dropdown menu.

    Args:
        correct: Correct answer ('T', 'F', 1, 0, 'True', 'False')
        **options: Additional options

    Returns:
        DropDown object with True/False choices
    """
    # Normalize correct answer
    if correct in [1, '1', 'T', 't', 'True', 'true', 'TRUE']:
        correct_value = 'True'
    else:
        correct_value = 'False'

    # DropDownTF defaults to not showing in static output
    if 'showInStatic' not in options:
        options['showInStatic'] = 0

    return DropDown(['True', 'False'], correct_value, **options)
