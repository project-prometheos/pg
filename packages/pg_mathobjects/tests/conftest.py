"""
Pytest configuration and fixtures for pg_mathobjects tests.
"""

import pytest
from pg_mathobjects import context as ctx_module


@pytest.fixture(autouse=True)
def reset_context():
    """Reset context state before each test."""
    # Save original state
    original_contexts = ctx_module._contexts.copy()
    original_current = ctx_module._current_context
    
    # Reset
    ctx_module._contexts = {}
    ctx_module._current_context = None
    
    yield
    
    # Restore
    ctx_module._contexts = original_contexts
    ctx_module._current_context = original_current
