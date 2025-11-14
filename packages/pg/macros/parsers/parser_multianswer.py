"""
MultiAnswer Parser - Multi-part answer with custom checker.

Allows multiple answer blanks to be checked together with a custom
validation function.

Reference: macros/parsers/parserMultiAnswer.pl
"""

from __future__ import annotations

from typing import Any, Callable


class MultiAnswer:
    """
    Multi-part answer object with custom checker.

    Allows multiple related answers to be checked together,
    enabling validation across multiple input fields.

    Reference: parserMultiAnswer.pl::MultiAnswer
    """

    def __init__(self, *correct_answers):
        """
        Create a multi-part answer.

        Args:
            *correct_answers: Correct values for each part

        Usage:
            multians = MultiAnswer(3, 4, 5)
        """
        self.correct_answers = list(correct_answers)
        self.num_answers = len(correct_answers)

        # Options
        self.checker = None
        self.single_result = False
        self.named_rules = False
        self.checkTypes = True
        self.allowBlankAnswers = False
        self.separator = ", "
        self.tex_separator = ", "

        # Answer blank counter
        self._blank_count = 0

    def with_params(self, **options) -> MultiAnswer:
        """
        Set options for the multi-answer.

        Args:
            **options: Options to set
                - checker: Custom checker function
                - singleResult: Show single result for all parts
                - checkTypes: Check answer types
                - allowBlankAnswers: Allow blank answers
                - separator: Separator for display
                - tex_separator: Separator for TeX

        Returns:
            Self for chaining

        Usage:
            multians = MultiAnswer(a, b).with_(
                checker=lambda correct, student, self: ...,
                singleResult=True
            )

        Reference: parserMultiAnswer.pl::with
        """
        if 'checker' in options:
            self.checker = options['checker']
        if 'singleResult' in options:
            self.single_result = options['singleResult']
        if 'checkTypes' in options:
            self.checkTypes = options['checkTypes']
        if 'allowBlankAnswers' in options:
            self.allowBlankAnswers = options['allowBlankAnswers']
        if 'separator' in options:
            self.separator = options['separator']
        if 'tex_separator' in options:
            self.tex_separator = options['tex_separator']

        return self

    def ans_rule(self, width: int = 20) -> str:
        """
        Generate an answer blank for this multi-answer.

        Args:
            width: Width of the input field

        Returns:
            HTML input element

        Reference: parserMultiAnswer.pl::ans_rule
        """
        # Generate unique answer name
        self._blank_count += 1
        name = f"AnSwEr{self._blank_count:04d}"

        # Generate HTML input
        html = f'<input type="text" name="{name}" id="{name}" '
        html += f'size="{width}" style="width: {width * 10}px;" '
        html += f'aria-label="Answer {self._blank_count}">'

        return html

    def cmp(self) -> MultiAnswerEvaluator:
        """
        Return answer evaluator for this multi-answer.

        Returns:
            MultiAnswerEvaluator object

        Reference: parserMultiAnswer.pl::cmp
        """
        return MultiAnswerEvaluator(self)

    def __str__(self):
        return f"MultiAnswer({', '.join(str(x) for x in self.correct_answers)})"


class MultiAnswerEvaluator:
    """
    Evaluator for multi-part answers.

    Collects student answers and validates them using the checker function.
    """

    def __init__(self, multianswer: MultiAnswer):
        """
        Create evaluator for a MultiAnswer.

        Args:
            multianswer: The MultiAnswer object to evaluate
        """
        self.multianswer = multianswer

    def evaluate(self, *student_answers) -> dict:
        """
        Evaluate student answers.

        Args:
            *student_answers: Student's answers for each part

        Returns:
            Dictionary with evaluation results
        """
        ma = self.multianswer

        # Default: all parts correct if they match
        if ma.checker is None:
            # Simple equality check
            if len(student_answers) != len(ma.correct_answers):
                return {
                    'correct': False,
                    'score': 0.0,
                    'message': 'Wrong number of answers'
                }

            # Check each part
            all_correct = True
            for student, correct in zip(student_answers, ma.correct_answers):
                if str(student) != str(correct):
                    all_correct = False
                    break

            return {
                'correct': all_correct,
                'score': 1.0 if all_correct else 0.0,
                'message': ''
            }

        # Use custom checker
        try:
            # Call checker with (correct, student, self)
            # In Perl: checker->($correct, $student, $self)
            # In Python: checker(correct, student, self)
            result = ma.checker(ma.correct_answers, list(student_answers), ma)

            # Result can be boolean or dict
            if isinstance(result, bool):
                return {
                    'correct': result,
                    'score': 1.0 if result else 0.0,
                    'message': ''
                }
            elif isinstance(result, (int, float)):
                correct = result == 1 or result == 1.0
                return {
                    'correct': correct,
                    'score': float(result),
                    'message': ''
                }
            else:
                # Assume dict-like
                return result

        except Exception as e:
            return {
                'correct': False,
                'score': 0.0,
                'message': f'Checker error: {e}'
            }

    def __str__(self):
        return f"MultiAnswerEvaluator({self.multianswer})"
