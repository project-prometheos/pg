"""RadioMultiAnswer - Radio button questions with dependent answer blanks."""

from typing import List, Any, Callable, Optional, Dict


class RadioMultiAnswer:
    """
    RadioMultiAnswer ties a radio button choice with answer blanks that depend on that choice.

    Reference: macros/parsers/parserRadioMultiAnswer.pl
    """

    def __init__(self, parts: List[List[Any]], correct: int, **options):
        """
        Initialize a RadioMultiAnswer.

        Args:
            parts: List of parts, each part is a list with format string and answers
                   Example: [['Answer is %s', answer1], ['No solution']]
            correct: Index (0-based) of the correct part
            **options: Additional options (checker, labels, separator, etc.)
        """
        if not isinstance(parts, list):
            raise ValueError("RadioMultiAnswer's first argument should be a list of lists")
        if correct is None or correct == '':
            raise ValueError("RadioMultiAnswer's second argument should be the correct choice")

        self.parts = parts
        self.correct = int(correct)
        self.options = {
            'labels': 'ABC',
            'displayLabels': True,
            'labelFormat': '%s.',
            'values': [],
            'separator': '; ',
            'tex_separator': ';\\,',
            'checker': None,
            'namedRules': False,
            'checkTypes': True,
            'allowBlankAnswers': False,
            'size': None,
            'checked': None,
            'uncheckable': False,
            **options
        }

        # Extract format strings and answers from parts
        self.format_strings = []
        self.answers = []
        self.values = []

        for i, part in enumerate(parts):
            if not isinstance(part, list) or len(part) < 1:
                raise ValueError("Each part should be a list with at least a format string")

            format_str = part[0]
            part_answers = part[1:] if len(part) > 1 else []

            self.format_strings.append(format_str)
            self.answers.append(part_answers)

            # Generate value for this choice
            if i < len(self.options['values']):
                self.values.append(self.options['values'][i])
            else:
                self.values.append(f'B{i}')

        self.error_messages = []

    def label(self, index: int) -> str:
        """Get the label for a given part index."""
        labels = self.options['labels']

        if isinstance(labels, list):
            if index < len(labels):
                return labels[index]
        elif labels.upper() == 'ABC':
            # Alphabetic labels: A, B, C, ...
            if index < 26:
                return chr(ord('A') + index)
        elif labels == '123':
            # Numeric labels: 1, 2, 3, ...
            return str(index + 1)

        # Fallback: use alphabetic
        if index < 26:
            return chr(ord('A') + index)
        return str(index)

    def cmp(self, **options):
        """
        Create an answer evaluator for this RadioMultiAnswer.

        Returns an evaluator that can check student responses.
        """
        # Merge options
        merged_options = {**self.options, **options}

        # Set default checker if not provided
        if not merged_options.get('checker'):
            def default_checker(correct, student, self_obj, ans_hash):
                # Check if correct radio button selected
                if correct[0] != student[0]:
                    return 0

                # Check if all answers in selected part match
                correct_part = correct[correct[0]]
                student_part = student[correct[0]]

                if len(correct_part) != len(student_part):
                    return 0

                for c, s in zip(correct_part, student_part):
                    if c != s:
                        return 0

                return 1

            merged_options['checker'] = default_checker

        # Create evaluator
        class RadioMultiAnswerEvaluator:
            def __init__(self, rma, opts):
                self.rma = rma
                self.options = opts
                self.correct_value = rma.correct + 1  # 1-based for display

            def evaluate(self, answer: Any) -> Dict[str, Any]:
                """Evaluate the student's answer."""
                # For now, return a simple result structure
                # Full implementation would check radio selection and sub-answers
                return {
                    'correct': answer == self.correct_value,
                    'score': 1.0 if answer == self.correct_value else 0.0,
                    'message': ''
                }

        return RadioMultiAnswerEvaluator(self, merged_options)

    def ans_rule(self, size: Optional[int] = None, **options):
        """
        Generate the HTML/text for answer rules.

        Args:
            size: Size of answer blanks (default 20)
            **options: Additional options

        Returns:
            String containing the radio buttons and answer blanks
        """
        size = size or self.options.get('size') or 20

        rules = []
        for i, (format_str, part_answers) in enumerate(zip(self.format_strings, self.answers)):
            label = self.label(i)
            checked = 'checked' if i == self.options.get('checked') else ''

            # Create radio button
            radio = f'<input type="radio" name="radio_group" value="{self.values[i]}" {checked}>'

            # Create answer blanks for this part
            blank_count = format_str.count('%s')
            blanks = ['<input type="text" size="{}" />'.format(size) for _ in range(blank_count)]

            # Format the string with blanks
            try:
                content = format_str.replace('%s', '{}').format(*blanks)
            except:
                content = format_str

            # Combine radio with content
            if self.options['displayLabels']:
                label_text = self.options['labelFormat'] % label
                rules.append(f'<div>{radio} <label>{label_text} {content}</label></div>')
            else:
                rules.append(f'<div>{radio} {content}</div>')

        return '\n'.join(rules)

    def appendMessage(self, message: str):
        """Add an error message."""
        if message:
            self.error_messages.append(message)
