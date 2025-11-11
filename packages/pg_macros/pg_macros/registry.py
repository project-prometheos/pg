"""
Macro Registry for PG Translator.

Defines which macros are loaded by default (core) vs on-demand (optional).
This enables dynamic runtime loading similar to the Perl reference implementation.
"""

from __future__ import annotations

from typing import Any


# Core macros that are always pre-loaded for every problem
# These are essential functions that nearly all problems use
CORE_MACROS = {
    "essential": {
        "module": None,  # Built into sandbox
        "functions": [
            "DOCUMENT",
            "TEXT",
            "ANS",
            "Compute",
            "Real",
            "Context",
            "Formula",
            "String",
            "loadMacros",  # Must be available to load other macros!
        ],
        "description": "Essential PG functions required by all problems",
    },
}

# Optional macros loaded on-demand via loadMacros()
# Organized by category for easier management
OPTIONAL_MACROS = {
    # Core PG functionality
    "pg_core": {
        "module": "pg_macros.core.pg_core",
        "aliases": ["PG.pl"],
        "category": "core",
        "functions": [
            "TEXT",
            "BEGIN_TEXT",
            "END_TEXT",
            "HINT",
            "SOLUTION",
            "COMMENT",
            "ANS",
            "LABELED_ANS",
            "NAMED_ANS",
            "DOCUMENT",
            "ENDDOCUMENT",
            "loadMacros",
            "random",
            "non_zero_random",
            "list_random",
            "random_coprime",
        ],
        "description": "Core PG macro functions from pg_core.py",
    },
    # Functions from pg_standard.pl (via pg_macros.core)
    # PGstandard.pl in Perl includes everything - map to pg_macros.core which re-exports all
    "pg_standard": {
        "module": "pg_macros.core",
        "aliases": ["PGstandard.pl"],
        "category": "core",
        "functions": [
            # From pg_core
            "TEXT",
            "BEGIN_TEXT",
            "END_TEXT",
            "HINT",
            "SOLUTION",
            "COMMENT",
            "ANS",
            "LABELED_ANS",
            "NAMED_ANS",
            "DOCUMENT",
            "ENDDOCUMENT",
            "loadMacros",
            "random",
            "non_zero_random",
            "list_random",
            # From pg_standard
            "random_subset",
            "shuffle",
            "image",
            "bold",
            "italic",
            "underline",
            "ans_rule",
            "solution",
            "hint",
        ],
        "description": "Standard PG functions (PGstandard.pl)",
    },
    "pg_basic_macros": {
        "module": "pg_macros.core.pg_basic_macros",
        "aliases": ["PGbasicmacros.pl"],
        "category": "core",
        "functions": [
            "display_matrix",
            "begintable",
            "endtable",
            "row",
            "ans_rule",
            "ans_array",
            "essay_box",
            "checkbox",
            "radio",
        ],
        "description": "Basic UI and formatting macros",
    },
    "pg_answer_macros": {
        "module": "pg_macros.answers.pg_answer_macros",
        "aliases": ["PGanswermacros.pl"],
        "category": "answers",
        "functions": [
            "cmp_equal",
            "check_syntax",
            "AnswerEvaluator",
        ],
        "description": "Answer evaluation macros",
    },
    "pg_course": {
        "module": "pg_macros.core.pg_core",  # PGcourse.pl is typically empty/minimal
        "aliases": ["PGcourse.pl"],
        "category": "core",
        "functions": [],  # Usually just configuration, no functions
        "description": "Course-specific configuration (usually empty)",
    },

    # PGML
    "PGML": {
        "module": "pg_macros.core.pgml",
        "aliases": ["PGML.pl"],
        "category": "markup",
        "functions": ["PGML"],
        "description": "PG Markup Language for problem text",
    },

    # Parser macros
    "parserPopUp": {
        "module": "pg_macros.parsers.parser_popup",
        "aliases": ["parserPopUp.pl"],
        "category": "parsers",
        "functions": ["PopUp"],
        "description": "Popup menu answer type",
    },
    "parserRadioButtons": {
        "module": "pg_macros.parsers.parser_popup",
        "aliases": ["parserRadioButtons.pl"],
        "category": "parsers",
        "functions": ["RadioButtons"],
        "description": "Radio button answer type",
    },
    "parserCheckboxes": {
        "module": "pg_macros.parsers.parser_checkbox_list",
        "aliases": ["parserCheckboxes.pl"],
        "category": "parsers",
        "functions": ["CheckboxList"],
        "description": "Checkbox answer type",
    },
    "parserMultiAnswer": {
        "module": "pg_macros.parsers.parser_multianswer",
        "aliases": ["parserMultiAnswer.pl"],
        "category": "parsers",
        "functions": ["MultiAnswer"],
        "description": "Multiple related answers",
    },

    # Graphics macros (heavy - should be lazy loaded!)
    "PGgraphmacros": {
        "module": "pg_macros.graph.pg_graph",
        "aliases": ["PGgraphmacros.pl"],
        "category": "graphics",
        "functions": [
            "init_graph",
            "add_functions",
            "Plot",
            "WWPlot",
            "Label",
            "Fun",
        ],
        "description": "2D graphing functions",
        "lazy": True,  # Heavy dependency
    },
    "parserGraphTool": {
        "module": "pg_macros.graph.parser_graphtool",
        "aliases": ["parserGraphTool.pl"],
        "category": "graphics",
        "functions": ["GraphTool"],
        "description": "Interactive graph tool",
        "lazy": True,
    },
    "VectorField3D": {
        "module": "pg_macros.graph.vector_field_3d",
        "aliases": ["VectorField3D.pl"],
        "category": "graphics",
        "functions": ["VectorField3D"],
        "description": "3D vector field visualization",
        "lazy": True,
    },

    # Math macros
    "PGstatisticsmacros": {
        "module": "pg_macros.math.statistics_utils",
        "aliases": ["PGstatisticsmacros.pl"],
        "category": "math",
        "functions": [
            "stats_mean",
            "stats_sd",
            "stats_SX_SXX",
            "linear_regression",
        ],
        "description": "Statistical functions",
    },

    # Interactive macros
    "draggableProof": {
        "module": "pg_macros.math.draggable_proof",
        "aliases": ["draggableProof.pl"],
        "category": "interactive",
        "functions": ["DraggableProof"],
        "description": "Draggable proof problems",
        "lazy": True,
    },
    "draggableSubsets": {
        "module": "pg_macros.math.draggable_subsets",
        "aliases": ["draggableSubsets.pl"],
        "category": "interactive",
        "functions": ["DraggableSubsets"],
        "description": "Draggable subset selection",
        "lazy": True,
    },

    # Context macros
    # Note: contextLimitedPolynomial and contextFraction modules don't exist yet
    # They have been removed from the registry until implemented
}


def get_macro_info(macro_name: str) -> dict[str, Any] | None:
    """
    Get information about a macro.

    Args:
        macro_name: Macro name (e.g., "parserPopUp", "PG.pl")

    Returns:
        Macro information dict or None if not found
    """
    # Check optional macros
    if macro_name in OPTIONAL_MACROS:
        return OPTIONAL_MACROS[macro_name]

    # Check aliases
    for key, info in OPTIONAL_MACROS.items():
        if "aliases" in info and macro_name in info["aliases"]:
            return info

    # Check core macros
    if macro_name in CORE_MACROS:
        return CORE_MACROS[macro_name]

    return None


def is_core_macro(macro_name: str) -> bool:
    """
    Check if a macro is a core macro (pre-loaded).

    Args:
        macro_name: Macro name

    Returns:
        True if core macro, False otherwise
    """
    return macro_name in CORE_MACROS


def should_lazy_load(macro_name: str) -> bool:
    """
    Check if a macro should be lazy-loaded (not pre-loaded).

    Args:
        macro_name: Macro name

    Returns:
        True if should be lazy-loaded, False if should be pre-loaded
    """
    info = get_macro_info(macro_name)
    if info is None:
        return True  # Unknown macros are lazy-loaded

    return info.get("lazy", False)


def get_macros_by_category(category: str) -> list[str]:
    """
    Get all macro names in a category.

    Args:
        category: Category name (e.g., "graphics", "parsers")

    Returns:
        List of macro names in that category
    """
    return [
        name
        for name, info in OPTIONAL_MACROS.items()
        if info.get("category") == category
    ]


def get_all_macro_names() -> list[str]:
    """
    Get all registered macro names.

    Returns:
        List of all macro names (including aliases)
    """
    names = list(CORE_MACROS.keys()) + list(OPTIONAL_MACROS.keys())

    # Add aliases
    for info in OPTIONAL_MACROS.values():
        if "aliases" in info:
            names.extend(info["aliases"])

    return names
