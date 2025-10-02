"""Minimal problemkit core types used by the FastAPI scaffold."""
from .decorators import problem
from .models import ProblemInstance
from .registry import ProblemRegistry

__all__ = ["problem", "ProblemInstance", "ProblemRegistry"]
