import logging
import random
import string
import traceback
from pathlib import Path

import numpy as np
import pytest
from click.testing import CliRunner

from deity import encode_filename
from deity import main


@pytest.fixture()
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.fixture()
def tmp_dir(tmpdir_factory, test_files):
    """Fixture for a temporary file."""
    tmp_dir = tmpdir_factory.mktemp("data")
    for elem in test_files:
        tmp_dir.join(elem).write("")
    return str(tmp_dir)


@pytest.mark.slow
class TestMain:
    def test_success_dry_run(self, runner: CliRunner, tmp_dir, test_files):
        """It should exit with a status code of zero."""

        result = runner.invoke(main, [tmp_dir, "--dry-run"])
        assert result.exit_code == 0, f"Error: {result.output}"
        if result.exit_code == 0:
            for elem in test_files:
                assert Path(tmp_dir).joinpath(elem).exists(), FileNotFoundError(
                    f"{elem} not found"
                )

    def test_success_rename_all(self, runner: CliRunner, tmp_dir, test_files, suffix):
        """It should exit with a status code of zero."""

        result = runner.invoke(main, [tmp_dir, "--suffix", ",".join(suffix)])
        if result.exit_code == 0:
            for elem in test_files:
                new_name = encode_filename(elem)[0]
                assert Path(tmp_dir).joinpath(new_name).exists(), FileNotFoundError(
                    f"{new_name} was expected but not found"
                )
        else:
            traceback.print_tb(result.exc_info[2])

    def test_fail(self, runner: CliRunner):
        """It exits with a status code of zero."""
        result = runner.invoke(main, ["", "--dry-run"])
        assert result.exit_code == 2
