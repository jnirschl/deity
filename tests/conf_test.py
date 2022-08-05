import pytest


@pytest.fixture()
def temp_files(tmpdir_factories):
    """Fixture for creating temporary files."""
    return tmpdir_factories.mktemp("data", "subdir")
