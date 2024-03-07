#!/usr/bin/env python3
"""Tests for create_qr.py."""

from random import choice

import pytest
from segno import QRCode

from deity.barcodes.create_qr import create_qr_single


VALID_EXTENSIONS = ["png", "svg", "eps", "pdf"]


@pytest.fixture
def error_level():
    return choice(["L", "M", "Q", "H"])


class TestCreateQRSingle:
    @pytest.mark.parametrize(
        "encode, micro, expected_type",
        [
            # success cases
            pytest.param(True, False, QRCode, id="encode-no-micro"),
            pytest.param(False, False, QRCode, id="no-encode-no-micro"),
            # failure cases
            # pytest.param(True, True, "L", QRCode, id="encode-micro"), # filename too large for microqr
            # pytest.param(False, True, QRCode, id="no-encode-micro"), # filename too large for microqr
        ],
    )
    def test_success(
        self,
        filename: str,
        encode: bool,
        micro: bool,
        expected_type: QRCode,
        error_level: str,
    ):
        # Act
        qr_code = create_qr_single(filename, encode=encode, micro=micro, error=error_level)

        # Assert
        assert isinstance(qr_code, expected_type)
        assert qr_code.is_micro == micro
