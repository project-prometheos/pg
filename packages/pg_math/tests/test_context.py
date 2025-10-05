"""
Tests for Context system.

Ported from pg_mathobjects to pg_math for Perl 1:1 parity migration.
"""

import pytest
from pg_math.context import Context, _create_context, VariableManager, ConstantManager


class TestContextCreation:
    """Test context creation and basic operations."""
    
    def test_context_creation(self):
        """Test creating a context."""
        ctx = Context('Numeric')
        assert ctx.name == 'Numeric'
        assert ctx.variables is not None
        assert ctx.constants is not None
        assert ctx.functions is not None
        assert ctx.operators is not None
    
    def test_context_switching(self):
        """Test switching between contexts."""
        from pg_math import context as ctx_module
        from pg_math import get_context
        
        # Reset global state
        ctx_module._contexts = {}
        ctx_module._current_context = None
        
        ctx1 = get_context('Numeric')
        assert get_context() == ctx1
        
        ctx2 = get_context('Complex')
        assert get_context() == ctx2
        assert get_context() != ctx1
    
    def test_context_get_current(self):
        """Test getting current context."""
        from pg_math import context as ctx_module
        from pg_math import get_context
        
        # Reset
        ctx_module._contexts = {}
        ctx_module._current_context = None
        
        # Should create default Numeric context
        ctx = get_context()
        assert ctx.name == 'Numeric'


class TestVariableManager:
    """Test variable management."""
    
    def test_variables_add(self):
        """Test adding variables."""
        ctx = Context('Numeric')
        ctx.variables.add('t', 'Real')
        assert 't' in ctx.variables.list()
        assert ctx.variables.get('t') == 'Real'
    
    def test_variables_remove(self):
        """Test removing variables."""
        ctx = Context('Numeric')
        ctx.variables.add('t', 'Real')
        assert 't' in ctx.variables.list()
        
        ctx.variables.remove('t')
        assert 't' not in ctx.variables.list()
    
    def test_variables_are(self):
        """Test setting all variables at once."""
        ctx = Context('Numeric')
        ctx.variables.are(t='Real', s='Real', u='Real')
        
        assert 't' in ctx.variables.list()
        assert 's' in ctx.variables.list()
        assert 'u' in ctx.variables.list()
        assert 'x' not in ctx.variables.list()  # x was in default, should be gone


class TestConstantManager:
    """Test constant management."""
    
    def test_constants_add(self):
        """Test adding constants."""
        ctx = Context('Numeric')
        ctx.constants.add('g', 9.8)
        assert 'g' in ctx.constants.list()
        assert ctx.constants.get('g') == 9.8
    
    def test_constants_set(self):
        """Test setting constant values."""
        ctx = Context('Numeric')
        ctx.constants.set('pi', 3.14)
        assert ctx.constants.get('pi') == 3.14
    
    def test_constants_remove(self):
        """Test removing constants."""
        ctx = Context('Numeric')
        ctx.constants.add('g', 9.8)
        assert 'g' in ctx.constants.list()
        
        ctx.constants.remove('g')
        assert 'g' not in ctx.constants.list()


class TestFunctionManager:
    """Test function management."""
    
    def test_functions_add(self):
        """Test adding functions."""
        ctx = Context('Numeric')
        ctx.functions.add('f', domain='Real')
        assert 'f' in ctx.functions.list()
    
    def test_functions_set(self):
        """Test setting function options."""
        ctx = Context('Numeric')
        ctx.functions.add('f')
        ctx.functions.set('f', domain='Real', range='Real')
        
        opts = ctx.functions.get('f')
        assert opts['domain'] == 'Real'
        assert opts['range'] == 'Real'


class TestContextFlags:
    """Test context flags."""
    
    def test_flags_get_set(self):
        """Test getting and setting flags."""
        ctx = Context('Numeric')
        
        # Check default tolerance
        assert ctx.flags.get('tolerance') == 0.001
        
        # Set new tolerance
        ctx.flags.set(tolerance=0.01)
        assert ctx.flags.get('tolerance') == 0.01


class TestContextCopy:
    """Test context copying."""
    
    def test_context_copy(self):
        """Test copying a context."""
        ctx1 = Context('Numeric')
        ctx1.variables.add('t', 'Real')
        ctx1.constants.add('g', 9.8)
        
        ctx2 = ctx1.copy('NewContext')
        assert ctx2.name == 'NewContext'
        assert 't' in ctx2.variables.list()
        assert ctx2.constants.get('g') == 9.8
        
        # Modifying ctx2 shouldn't affect ctx1
        ctx2.variables.add('s', 'Real')
        assert 's' in ctx2.variables.list()
        assert 's' not in ctx1.variables.list()


class TestNumericContext:
    """Test Numeric context initialization."""
    
    def test_numeric_has_standard_variables(self):
        """Test that Numeric context has x variable."""
        ctx = Context('Numeric')
        assert 'x' in ctx.variables.list()
    
    def test_numeric_has_standard_constants(self):
        """Test that Numeric context has pi and e."""
        ctx = Context('Numeric')
        assert 'pi' in ctx.constants.list()
        assert 'e' in ctx.constants.list()
    
    def test_numeric_has_standard_functions(self):
        """Test that Numeric context has standard functions."""
        ctx = Context('Numeric')
        assert 'sin' in ctx.functions.list()
        assert 'cos' in ctx.functions.list()
        assert 'ln' in ctx.functions.list()
        assert 'sqrt' in ctx.functions.list()
    
    def test_numeric_has_standard_operators(self):
        """Test that Numeric context has standard operators."""
        ctx = Context('Numeric')
        assert '+' in ctx.operators.list()
        assert '-' in ctx.operators.list()
        assert '*' in ctx.operators.list()
        assert '/' in ctx.operators.list()
        assert '^' in ctx.operators.list()
