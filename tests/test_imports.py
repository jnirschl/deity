#!/usr/bin/env python3
"""test_imports.py in tests."""

from importlib import metadata

import pytest

import deity


@pytest.fixture(scope="session")  # type: ignore
def current_version():
    return metadata.version("deity")


@pytest.mark.smoke
def test_import():
    """Test imports."""
    import deity  # noqa: F401
    from deity import encode  # noqa: F401
    from deity import encode_all  # noqa: F401
    from deity import encode_single  # noqa: F401
    from deity.database import create_connection  # noqa: F401
    from deity.database import create_cursor  # noqa: F401
    from deity.database import create_db  # noqa: F401
    from deity.database import execute_query  # noqa: F401


def test_version(current_version):
    """Test version."""
    assert deity.__version__ == current_version
