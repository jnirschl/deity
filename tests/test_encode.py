import hashlib
import re
from pathlib import Path

import pytest

from src import deity


class TestEncode:
    """class for testing encode module functions"""

    def test_input(self, test_input):
        """test input types"""
        for filename, result, error in test_input:
            if result:
                assert deity.encode(filename)

    @pytest.mark.xfail(reason="Invalid input")
    def test_input_error(self, test_input):
        for filename, result, error in test_input:
            if error:
                with pytest.raises(error):
                    deity.encode(filename)

    def test_hash(self, test_input):
        for filename, result, error in test_input:
            if result:
                encode_hash, _ = deity.encode(filename)
                hashlib_hash = hashlib.sha256(filename.strip().encode()).hexdigest()
                assert encode_hash == hashlib_hash

    @pytest.mark.xfail(reason="Invalid input")
    def test_hash_error(self, test_input):
        for filename, result, error in test_input:
            if result:
                with pytest.raises(TypeError):
                    encode_fail, _ = deity.encode(input)


class TestEncodeFilename:
    def test_input(self, test_input):
        """test input types"""
        for filename, result, error in test_input:
            if result:
                assert deity.encode_filename(filename)

    @pytest.mark.xfail(reason="Invalid input")
    def test_input_error(self, test_input):
        for filename, result, error in test_input:
            if error:
                with pytest.raises(error):
                    deity.encode_filename(filename)

    def test_hash(self, test_input):
        for filename, result, error in test_input:
            if result:
                encode_filename, full_hash, _ = deity.encode_filename(filename)
                hashlib_hash = hashlib.sha256(filename.strip().encode()).hexdigest()
                assert full_hash == hashlib_hash

    @pytest.mark.xfail()
    def test_hash_error(self, test_input):
        for filename, result, error in test_input:
            if error:
                with pytest.raises(TypeError):
                    encode_fail, _ = deity.encode_filename(filename)

    def test_filename_success(self, test_files, regex_id):
        for fname in test_files:
            new_fname, _, _ = deity.encode_filename(fname)

            assert new_fname != fname, f"{fname} should be different from {new_fname}"
            assert not regex_id.search(new_fname), f"{new_fname} contains identifier"

    def test_filname_fail(self, test_files, regex_id):
        for fname in test_files:
            fname = Path(fname)
            reverse_fname = fname.name[::-1]
            new_rev_fname, _, _ = deity.encode_filename(reverse_fname)
            assert new_rev_fname.name[::-1] == fname.name, AssertionError(
                f"{new_rev_fname} != {fname}"
            )
            assert not regex_id.search(
                new_rev_fname.name
            ), f"{new_rev_fname} should contain identifier"
