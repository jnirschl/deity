#!/usr/bin/env python3
"""test_imports.py in tests."""

import pkg_resources


__version__ = pkg_resources.get_distribution("deity").version


class SmokeTest:
    """Class for testing basic functionality."""

    def test_import(self):
        """Test import."""
        import deity  # noqa: F401
        from deity import encode  # noqa: F401
        from deity import encode_all  # noqa: F401
        from deity import encode_single  # noqa: F401

    def test_version(self):
        """Test version."""
        import deity

        assert deity.__version__ == "0.0.1"
