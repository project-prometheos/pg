"""
PGML.pl - PGML rendering support

Python port of macros/core/PGML.pl
Provides PGML text rendering.

Reference: PGML.pl
"""

import sys
from pg.pgml import HTMLRenderer, PGMLParser, TeXRenderer
from pg.pgml.parser import AnswerBlank

# Export list
__exports__ = [
    "PGML",
    "BEGIN_PGML",
    "END_PGML",
]


def PGML(text: str, **kwargs) -> str:
    """
    Render PGML text to HTML.

    Args:
        text: PGML markup
        **kwargs: Rendering options (context, etc.)

    Returns:
        Rendered HTML

    Reference: PGML.pl::PGML
    """
    # Parse PGML
    doc = PGMLParser.parse_text(text)

    # Extract and register answer blanks from the parsed document
    # This is necessary because answer blanks in BEGIN_PGML blocks
    # need to be registered with the executor, not just rendered as HTML
    context = kwargs.get("context", {})
    _register_answers_from_pgml(doc, context)

    # Render to HTML
    renderer = HTMLRenderer(context=context)

    return renderer.render(doc)


def _register_answers_from_pgml(node, context):
    """
    Extract and register answer evaluators from PGML nodes.

    This walks the PGML AST and registers any answer blanks found.
    """
    # Try to get the ANS function from the calling code's scope
    ANS = None
    try:
        # Try multiple frame levels to handle different call stack depths
        for frame_level in range(2, 10):
            try:
                frame = sys._getframe(frame_level)
                if 'ANS' in frame.f_locals:
                    ANS = frame.f_locals['ANS']
                    break
                elif 'ANS' in frame.f_globals:
                    ANS = frame.f_globals['ANS']
                    break
            except ValueError:
                # Frame doesn't exist at this level, try next
                continue
    except Exception:
        pass

    if not ANS:
        return  # ANS not available, skip registering

    # Walk the AST to find answer blanks
    def find_answer_blanks(node):
        """Recursively find all AnswerBlank nodes in the AST."""
        if isinstance(node, AnswerBlank):
            yield node
        elif hasattr(node, 'blocks'):
            for block in node.blocks:
                yield from find_answer_blanks(block)
        elif hasattr(node, 'content'):
            if isinstance(node.content, list):
                for child in node.content:
                    yield from find_answer_blanks(child)
        elif hasattr(node, 'items'):
            if isinstance(node.items, list):
                for item in node.items:
                    yield from find_answer_blanks(item)

    # Register each answer blank
    for blank in find_answer_blanks(node):
        if blank.evaluator_code:
            try:
                # Evaluate the evaluator code in the context
                # The evaluator_code is something like "answer.cmp(...)"
                evaluator = eval(blank.evaluator_code, {}, context)
                # Register with ANS
                ANS(evaluator)
            except Exception:
                # If evaluation fails, just skip this answer blank
                # (it will still be rendered, just without answer checking)
                pass


# BEGIN_PGML and END_PGML are preprocessor directives, not functions
# They're handled by the PG preprocessor
# These are here for completeness in the macro system

def BEGIN_PGML() -> None:
    """Preprocessor directive - handled by preprocessor."""
    pass


def END_PGML() -> None:
    """Preprocessor directive - handled by preprocessor."""
    pass
