"""
Pytest configuration for contract tests
"""
import pytest
from pathlib import Path


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "perl_required: marks tests that require Perl runtime"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture(scope="session")
def parity_lab_root():
    """Get parity lab root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def build_dir(parity_lab_root):
    """Get build directory, creating if needed."""
    build = parity_lab_root / "build"
    build.mkdir(parents=True, exist_ok=True)
    return build


@pytest.fixture(scope="session")
def snippets_dir(parity_lab_root):
    """Get snippets directory."""
    return parity_lab_root / "tests" / "snippets"
