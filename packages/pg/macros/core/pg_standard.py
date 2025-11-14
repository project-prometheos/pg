"""
PGstandard.pl - Core PG functions

Reference: macros/core/PGstandard.pl (1,234 lines)
"""

from typing import Any


def TEXT(*args: Any) -> str:
    """
    Accumulate text for problem statement.
    
    Reference: PGstandard.pl::TEXT
    """
    # Convert all arguments to strings and concatenate
    return "".join(str(arg) for arg in args)


def BEGIN_TEXT() -> str:
    """
    Marker for beginning of text block.
    This is typically handled by preprocessor.
    
    Reference: PGstandard.pl::BEGIN_TEXT
    """
    return ""


def END_TEXT() -> str:
    """
    Marker for end of text block.
    
    Reference: PGstandard.pl::END_TEXT
    """
    return ""


def ANS(*evaluators: Any) -> None:
    """
    Register answer evaluators.
    
    Reference: PGstandard.pl::ANS
    """
    # In full implementation, this would register with problem environment
    # For now, placeholder
    pass


def NAMED_ANS(name: str, evaluator: Any) -> None:
    """
    Register named answer evaluator.
    
    Reference: PGstandard.pl::NAMED_ANS
    """
    pass


def image(filename: str, **options: Any) -> str:
    """
    Insert image.
    
    Reference: PGstandard.pl::image
    """
    width = options.get('width', '')
    height = options.get('height', '')
    alt = options.get('alt', '')
    
    attrs = []
    if width:
        attrs.append(f'width="{width}"')
    if height:
        attrs.append(f'height="{height}"')
    if alt:
        attrs.append(f'alt="{alt}"')
    
    attr_str = ' '.join(attrs)
    return f'<img src="{filename}" {attr_str}>'


def bold(text: str) -> str:
    """Return bolded text."""
    return f"**{text}**"


def italic(text: str) -> str:
    """Return italicized text."""
    return f"*{text}*"


def underline(text: str) -> str:
    """Return underlined text."""
    return f"<u>{text}</u>"


def ans_rule(width: int = 20) -> str:
    """
    Create answer blank.
    
    Reference: PGstandard.pl::ans_rule
    """
    return f'<input type="text" size="{width}" class="pg-answer-blank">'


def solution(*args: Any) -> str:
    """
    Create solution section.
    
    Reference: PGstandard.pl::SOLUTION
    """
    content = "".join(str(arg) for arg in args)
    return f'<div class="solution">{content}</div>'


def hint(*args: Any) -> str:
    """
    Create hint section.
    
    Reference: PGstandard.pl::HINT
    """
    content = "".join(str(arg) for arg in args)
    return f'<div class="hint">{content}</div>'


# Random number functions

import random as _random

def random(low: float = 0, high: float = 1, step: float | None = None) -> float:
    """
    Generate random number.
    
    Reference: PGstandard.pl::random
    """
    if step is not None:
        # Discrete random
        n_steps = int((high - low) / step) + 1
        return low + _random.randrange(n_steps) * step
    else:
        # Continuous random
        return _random.uniform(low, high)


def non_zero_random(low: float, high: float, step: float | None = None) -> float:
    """
    Generate non-zero random number.
    
    Reference: PGstandard.pl::non_zero_random
    """
    result = 0
    while result == 0:
        result = random(low, high, step)
    return result


def list_random(*items):
    """
    Select random item from list.
    
    Reference: PGstandard.pl::list_random
    """
    return _random.choice(items)


def shuffle(*items):
    """
    Shuffle list items.
    
    Reference: PGstandard.pl::shuffle
    """
    shuffled = list(items)
    _random.shuffle(shuffled)
    return shuffled


def random_subset(n: int, *items):
    """
    Select n random items from list without replacement.
    
    Reference: PGstandard.pl::random_subset
    """
    return _random.sample(items, n)
