#!/usr/bin/env python3
"""Tests for src/deity/__main__.py."""
import random
import traceback
from pathlib import Path

import pytest
from click.testing import CliRunner

from deity import encode_single
from deity import main


EXT_LIST = ["png", "jpg", "txt", ".pdf", ".tif", ".tiff"]


@pytest.fixture()
def table() -> str:
    """Returns table name."""
    return "specimens"


@pytest.fixture()
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


class TestMain:
    """Class for testing main module functions."""

    def test_main_dry_run(
        self,
        runner,
        temp_dir,
        tmp_db,
        table,
        test_files,
    ) -> None:
        """Perform a dry run and check that no files are renamed."""
        result = runner.invoke(main, [temp_dir, tmp_db, table, "--dry-run"])
        assert result.exit_code == 0, f"Error: {result.exception}"
        if result.exit_code == 0:
            for elem in test_files:
                assert Path(temp_dir).joinpath(elem).exists(), FileNotFoundError(
                    f"{elem} not found"
                )
        else:
            traceback.print_tb(result.exc_info[2])

    def test_main_database_creation(self, runner, temp_dir, table, test_files) -> None:
        """Test if the database is created if it doesn't exist."""
        # Prepare a new non-existent database file path
        non_existent_db = Path(temp_dir).joinpath("non_existent.db")

        # Run the main function
        result = runner.invoke(main, [temp_dir, non_existent_db.as_posix(), table])
        assert result.exit_code == 0, f"Error: {result.exception}"

        # Check if the new database file is created
        assert non_existent_db.exists(), FileNotFoundError(
            f"{non_existent_db} was expected to be created but not found"
        )

    @pytest.mark.xfail(
        reason="TODO: flaky test with occasional no files found with ext. Need to fix"
    )
    @pytest.mark.parametrize(
        "ext",
        [
            (
                ",".join(
                    random.sample(
                        EXT_LIST,
                        random.randint(1, 5),
                    )
                )
            )
            for _ in range(10)
        ],
    )
    def test_main_rename(
        self, runner, temp_dir, tmp_db, table, test_files, ext
    ) -> None:
        """Run the program and check that all files are renamed."""
        result = runner.invoke(main, [temp_dir, tmp_db, table, "--extension", ext])
        assert result.exit_code == 0, f"Error: {result.exception}"
        if result.exit_code == 0:
            for elem in test_files:
                if Path(elem).suffix.strip(".") in ext.split(","):
                    _id, new_filepath, _, _ = encode_single(elem, output_dir=temp_dir)
                    assert new_filepath.exists(), FileNotFoundError(
                        f"Error renaming {Path(temp_dir).joinpath(elem)} to {new_filepath}"
                    )
                else:
                    assert Path(temp_dir).joinpath(elem).exists(), FileNotFoundError(
                        f"{elem} not found!"
                        "\n"
                        f"{elem} was renamed to {new_filepath} when it should be unchanged."
                    )
        else:
            traceback.print_tb(result.exc_info[2])

    @pytest.mark.xfail(
        reason="TODO: flaky test with occasional no files found with ext. Need to fix"
    )
    @pytest.mark.parametrize(
        "ext",
        [
            (
                ",".join(
                    random.sample(
                        EXT_LIST,
                        random.randint(1, 5),
                    )
                )
            )
            for _ in range(10)
        ],
    )
    def test_different_extensions(
        self, runner, temp_dir, tmp_db, table, test_files, ext
    ) -> None:
        """Run the program and check that only files matching the extension are renamed."""
        result = runner.invoke(main, [temp_dir, tmp_db, table, "--extension", ext])
        assert result.exit_code == 0, f"Error: {result.exception}"
        if result.exit_code == 0:
            for elem in test_files:
                if Path(elem).suffix.strip(".") in ext.split(","):
                    _id, new_filepath, _, _ = encode_single(elem, output_dir=temp_dir)
                    assert new_filepath.exists(), FileNotFoundError(
                        f"Error renaming {Path(temp_dir).joinpath(elem)} to {new_filepath}"
                    )
                else:
                    assert Path(temp_dir).joinpath(elem).exists(), FileNotFoundError(
                        f"{elem} not found!"
                        "\n"
                        f"{elem} was renamed to {new_filepath} when it should be unchanged."
                    )

        else:
            traceback.print_tb(result.exc_info[2])

    @pytest.mark.xfail(reason="Not implemented")
    def test_main_database(self, runner, temp_dir, tmp_db, table, test_files) -> None:
        """Update the database with new files."""
        result = runner.invoke(main, [temp_dir, tmp_db, table])
        if result.exit_code == 0:
            for elem in test_files:
                _id, new_filepath, _, _ = encode_single(elem)
                assert (
                    Path(temp_dir).joinpath(new_filepath).exists()
                ), FileNotFoundError(f"{new_filepath} was expected but not found")
        else:
            traceback.print_tb(result.exc_info[2])
