"""Tests for context flag system."""

import pytest
from pg_parser import Context


def test_get_flag_default():
    """Test getting flag with default."""
    ctx = Context.numeric()
    
    value = ctx.get_flag("nonexistent", 42)
    assert value == 42


def test_set_flag():
    """Test setting flag."""
    ctx = Context.numeric()
    
    ctx.set_flag("my_flag", True)
    assert ctx.get_flag("my_flag") == True


def test_copy_flags():
    """Test copying flags between contexts."""
    ctx1 = Context.numeric()
    ctx1.set_flag("flag1", 100)
    ctx1.set_flag("flag2", "value")
    
    ctx2 = Context.numeric()
    ctx1.copy_flags_to(ctx2)
    
    assert ctx2.get_flag("flag1") == 100
    assert ctx2.get_flag("flag2") == "value"


def test_flags_in_context_creation():
    """Test creating context with flags."""
    ctx = Context(
        name="Test",
        flags={"reduceConstants": True, "tolerance": 0.01}
    )
    
    assert ctx.get_flag("reduceConstants") == True
    assert ctx.get_flag("tolerance") == 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


