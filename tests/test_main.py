"""Tests for src/deity/__main__.py."""
import traceback
from pathlib import Path

import pytest
from click.testing import CliRunner

from deity import encode_single
from deity import main


@pytest.fixture()
def table():
    """Returns table name."""
    return "specimens"


@pytest.fixture()
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.mark.slow
class TestMain:
    """Class for testing main module functions."""

    def test_main_dry_run(self, runner: CliRunner, tmp_dir, tmp_db, table, test_files):
        """Perform a dry run and check that no files are renamed."""
        result = runner.invoke(main, [tmp_dir, tmp_db, table, "--dry-run"])
        assert result.exit_code == 0, f"Error: {result.exception}"
        if result.exit_code == 0:
            for elem in test_files:
                assert Path(tmp_dir).joinpath(elem).exists(), FileNotFoundError(
                    f"{elem} not found"
                )
        else:
            traceback.print_tb(result.exc_info[2])

    def test_main_rename(self, runner: CliRunner, tmp_dir, tmp_db, table, test_files):
        """Run the program and check that all files are renamed."""
        suffix = ",".join(["jpg", "png", "tif", "tiff"])
        result = runner.invoke(main, [tmp_dir, tmp_db, table, "--suffix", suffix])
        assert result.exit_code == 0, f"Error: {result.exception}"
        if result.exit_code == 0:
            for elem in test_files:
                _id, new_filepath, _, _ = encode_single(elem, output_dir=tmp_dir)
                assert new_filepath.exists(), FileNotFoundError(
                    f"Error renaming {tmp_dir.joinpath(elem)} to {new_filepath}"
                )
        else:
            traceback.print_tb(result.exc_info[2])

    @pytest.mark.xfail(reason="Not implemented")
    def test_main_database(self, runner: CliRunner, tmp_dir, tmp_db, table, test_files):
        """Update the database with new files."""
        result = runner.invoke(main, [tmp_dir, tmp_db, table])
        if result.exit_code == 0:
            for elem in test_files:
                new_name = encode_single(elem)[0]
                assert Path(tmp_dir).joinpath(new_name).exists(), FileNotFoundError(
                    f"{new_name} was expected but not found"
                )
        else:
            traceback.print_tb(result.exc_info[2])
