import re

import pytest
import hashlib
from pathlib import Path

from src.deity import encode, encode_filename

test_cases = [  # test_success, test_fail
    ("SHA-00-54321", 54321),
    ("LPS-00-54321", None),
    ("SHS-00-54321", b"CM-00-54321"),
]


@pytest.fixture()
def regex_identifier():
    return re.compile("[SL][HP][SDFNA]-\d{2}-\d{5}", re.IGNORECASE)


@pytest.mark.parametrize("test_success, test_fail", test_cases, scope="class")
class TestEncode:
    def test_input(self, test_success, test_fail):
        assert encode(test_success)
        with pytest.raises(TypeError):
            encode(test_fail)

    def test_hash(self, test_success, test_fail):
        encode_success, _ = encode(test_success)
        hash_success = hashlib.sha256(test_success.strip().encode()).hexdigest()
        assert encode_success == hash_success

        # test fail
        with pytest.raises(TypeError):
            encode_fail, _ = encode(test_fail)


@pytest.mark.parametrize(
    "orig_filename", [Path(elem[0]) for elem in test_cases], scope="class"
)
class TestEncodeFilename:
    def test_encoded_name(self, orig_filename, regex_identifier):
        new_filename, full_hash, short_hash = encode_filename(orig_filename)
        assert new_filename != orig_filename  # new filename should be different
        assert not regex_identifier.search(new_filename)  # identifier should be absent

        orig_name_reverse = orig_filename.name[::-1]
        new_filename, full_hash, short_hash = encode_filename(orig_name_reverse)
        assert (
            new_filename.name == orig_filename.name[::-1]
        )  # new filename unchanged from orig
        assert not regex_identifier.search(new_filename.name)
