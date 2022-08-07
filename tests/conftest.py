"""Configure shared fixtures for tests."""
import random
import re
import string

import numpy as np
import pytest


@pytest.fixture()
def regex_id():
    """Returns regex for identifier."""
    return re.compile("[SL][HP][SDFNA]-\\d{2}-\\d{5}", re.IGNORECASE)


@pytest.fixture()
def temp_files(tmpdir_factories):
    """Fixture for creating temporary files."""
    return tmpdir_factories.mktemp("data")


@pytest.fixture()
def prefix():
    """Fixture for creating temporary file prefixes."""
    return ["SHA", "SHD", "SHF", "SHN", "SHS", "LPS", "LPD", "LPF"]


@pytest.fixture()
def suffix():
    """Fixture for creating temporary file extensions."""
    return ["jpg", "png", "tif", "tiff"]


@pytest.fixture()
def test_files(prefix, suffix, num_test_cases=10):
    """Fixture to generate test filename combinations."""
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
def test_input():
    """Fixture for creating test cases.

    Returns: tuple of (input, result, error)
    """
    return [
        ("SHA-00-54321", True, None),
        ("LPS-00-54321", True, None),
        ("SHS-00-54321", True, None),
        (np.random.randint(99999), False, TypeError),
        (None, False, TypeError),
        (b"SHS-00-54321", False, TypeError),
    ]
