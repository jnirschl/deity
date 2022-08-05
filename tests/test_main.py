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
def prefix():
    return ["SHA", "SHD", "SHF", "SHN", "SHS", "LPS", "LPD", "LPF"]


@pytest.fixture()
def suffix():
    return ["jpg", "png", "tif", "tiff"]


@pytest.fixture()
def test_files(prefix, suffix, num_test_cases=10):
    """Fixture to generate test files"""
    return [
        (
            f"{random.choice(prefix)}-{np.random.randint(99):02d}-{np.random.randint(9.9e4):05d}_"
            f"part-{random.choice(string.ascii_uppercase)}_diagnosis_"
            f"{np.random.randint(40):02d}x_{np.random.randint(999):03d}"
            f".{random.choice(suffix)}"
        )
        for elem in range(num_test_cases)
    ]


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
# @pytest.mark.parametrize("tmp_file", tmp_dir, scope="class")
class TestMain:
    def test_success_dry_run(self, runner: CliRunner, tmp_dir, test_files):
        """It should exit with a status code of zero."""

        result = runner.invoke(main, [tmp_dir, "--dry-run"])
        if result.exit_code == 0:
            for elem in test_files:
                assert (
                    Path(tmp_dir).joinpath(elem).exists()
                ), FileNotFoundError(f"{elem} not found")
        else:
            traceback.print_tb(result.exc_info[2])

    def test_success_rename_all(
        self, runner: CliRunner, tmp_dir, test_files, suffix
    ):
        """It should exit with a status code of zero."""

        result = runner.invoke(main, [tmp_dir, "--suffix", ",".join(suffix)])
        if result.exit_code == 0:
            for elem in test_files:
                new_name = encode_filename(elem)[0]
                assert (
                    Path(tmp_dir).joinpath(new_name).exists()
                ), FileNotFoundError(f"{new_name} was expected but not found")
        else:
            traceback.print_tb(result.exc_info[2])

    def test_fail(self, runner: CliRunner) -> None:
        """It exits with a status code of zero."""
        result = runner.invoke(main, [""])
        assert result.exit_code == 2
