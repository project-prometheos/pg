"""
Tests for Macro Loader system.
"""

import pytest
from pathlib import Path
from pg_translator.macro_loader import MacroLoader, OpcodeMask
from pg_translator.sandbox import PGSandbox


def test_opcode_mask():
    """Test opcode mask definitions."""
    assert isinstance(OpcodeMask.EMPTY, set)
    assert isinstance(OpcodeMask.RESTRICTED, set)
    assert len(OpcodeMask.EMPTY) == 0
    assert "eval" in OpcodeMask.RESTRICTED


def test_macro_loader_init(mock_sandbox):
    """Test MacroLoader initialization."""
    loader = MacroLoader(mock_sandbox)

    assert loader.sandbox == mock_sandbox
    assert isinstance(loader.loaded_files, dict)
    assert isinstance(loader.init_functions, dict)
    assert isinstance(loader.search_paths, list)


def test_find_macro(mock_sandbox, tmp_path):
    """Test macro file finding."""
    loader = MacroLoader(mock_sandbox)

    # Create test macro file
    test_macro = tmp_path / "test_macro.py"
    test_macro.write_text("# Test macro")

    loader.search_paths.append(tmp_path)

    # Find by name
    found = loader.find_macro("test_macro.py")
    assert found == test_macro

    # Find with .py extension added
    found = loader.find_macro("test_macro")
    assert found == test_macro


def test_load_python_macro(mock_sandbox, tmp_path):
    """Test loading Python macro."""
    loader = MacroLoader(mock_sandbox)

    # Create test macro
    test_macro = tmp_path / "simple_macro.py")
    test_macro.write_text("""
def test_function():
    return 42

TEST_CONSTANT = 100
""")

    # Load macro
    errors = loader._load_python_macro(test_macro)
    assert errors == ""

    # Check loaded
    assert str(test_macro) in loader.loaded_files


def test_unrestricted_load(mock_sandbox, tmp_path):
    """Test unrestricted_load with init function."""
    loader = MacroLoader(mock_sandbox)

    # Create macro with init function
    test_macro = tmp_path / "init_macro.py"
    test_macro.write_text("""
initialized = False

def _init_macro_init():
    global initialized
    initialized = True

def get_status():
    return initialized
""")

    loader.search_paths.append(tmp_path)

    # Load with unrestricted
    errors = loader.unrestricted_load("init_macro.py")
    assert errors == ""

    # Check init was called
    assert test_macro.stem + "_init" in loader.init_functions


def test_load_macros_multiple(mock_sandbox, tmp_path):
    """Test loading multiple macros."""
    loader = MacroLoader(mock_sandbox)
    loader.search_paths.append(tmp_path)

    # Create multiple macros
    for i in range(3):
        macro = tmp_path / f"macro{i}.py"
        macro.write_text(f"VALUE_{i} = {i}")

    # Load all
    loader.load_macros("macro0", "macro1", "macro2")

    # Check all loaded
    assert len(loader.loaded_files) == 3


@pytest.fixture
def mock_sandbox():
    """Mock PGSandbox for testing."""
    class MockSandbox:
        def __init__(self):
            self.namespace = {}
            self._restricted_names = OpcodeMask.RESTRICTED.copy()

        def get_restricted_names(self):
            return self._restricted_names

        def set_restricted_names(self, names):
            self._restricted_names = names

        def exec(self, code, filename=None):
            exec(code, self.namespace)

        def register_file(self, eval_id, filepath):
            pass

    return MockSandbox()
