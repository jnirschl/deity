"""Tests for src/deity/encode.py."""
import hashlib
import re
from pathlib import Path

import numpy as np
import pytest

import deity


@pytest.fixture()
def regex_id():
    """Returns regex for identifier."""
    return re.compile("[SL][HP][SDFNA]-\\d{2}-\\d{5}", re.IGNORECASE)


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


class TestEncode:
    """Class for testing encode module functions."""

    def test_input(self, test_input):
        """Test input types."""
        for filename, result, _error in test_input:
            if result:
                assert deity.encode(filename)

    def test_input_error(self, test_input):
        """Raise exception if input is not a string."""
        for filename, _result, error in test_input:
            if error:
                with pytest.raises(error):
                    deity.encode(filename)

    def test_hash(self, test_input):
        """Test hash function."""
        for filename, result, _error in test_input:
            if result:
                encode_hash, _ = deity.encode(filename)
                hashlib_hash = hashlib.sha256(filename.strip().encode()).hexdigest()
                assert encode_hash == hashlib_hash

    def test_hash_error(self, test_input):
        """Raise exception if input is not a string."""
        for filename, _result, error in test_input:
            if error:
                with pytest.raises(TypeError):
                    encode_fail, _ = deity.encode(filename)


class TestEncodeFilename:
    """Class for testing encode_single module functions."""

    def test_input(self, test_input):
        """Test input types."""
        for filename, result, _error in test_input:
            if result:
                assert deity.encode_single(filename)

    def test_input_error(self, test_input):
        """Raise exception if input is not a string."""
        for filename, _result, error in test_input:
            if error:
                with pytest.raises(error):
                    deity.encode_single(filename)

    def test_hash(self, test_input):
        """Test hash function."""
        for filename, result, _error in test_input:
            if result:
                encode_single, full_hash, _ = deity.encode_single(filename)
                hashlib_hash = hashlib.sha256(filename.strip().encode()).hexdigest()
                assert full_hash == hashlib_hash

    def test_hash_error(self, test_input):
        """Raise exception if input is not a string."""
        for filename, _result, error in test_input:
            if error:
                with pytest.raises(TypeError):
                    encode_fail, _ = deity.encode_single(filename)

    def test_filename_success(self, test_files, regex_id):
        """Test that new filename is different from original filename."""
        for fname in test_files:
            new_fname, _, _ = deity.encode_single(fname)

            assert new_fname != fname, f"{fname} should be different from {new_fname}"
            assert not regex_id.search(new_fname), f"{new_fname} contains identifier"

    def test_filname_fail(self, test_files, regex_id):
        """Test with reversed filename such that regex fails and file is not renamed."""
        for fname in test_files:
            fname = Path(fname)
            reverse_fname = fname.name[::-1]
            new_rev_fname, _, _ = deity.encode_single(reverse_fname)
            assert new_rev_fname.name[::-1] == fname.name, AssertionError(
                f"{new_rev_fname} != {fname}"
            )
            assert not regex_id.search(
                new_rev_fname.name
            ), f"{new_rev_fname} should contain identifier"
