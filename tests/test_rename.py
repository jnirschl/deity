"""Tests for src/deity/rename.py."""
from pathlib import Path

from deity import rename


def test_rename(test_files):
    """Test that new filename is different from old filename."""
    filepath = Path(test_files[0])
    new_filename = rename(filepath, dry_run=True)
    assert new_filename != filepath, AssertionError(
        f"New filename {filepath }is identical to input filename"
    )
