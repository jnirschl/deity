#!/usr/bin/env python3
"""Tests for create_qr.py."""

import pytest
from segno import QRCode

from deity.barcodes.create_qr import create_qr_single


VALID_EXTENSIONS = ["png", "svg", "eps", "pdf"]


@pytest.mark.parametrize(
    "encode, micro, expected_type",
    [
        pytest.param(True, False, QRCode, id="encode-no-micro"),
        pytest.param(False, False, QRCode, id="no-encode-no-micro"),
    ],
)
def test_create_qr_single(filename, encode, micro, expected_type):
    # Act
    qr_code = create_qr_single(filename, encode, micro)

    # Assert
    assert isinstance(qr_code, expected_type)
    assert qr_code.is_micro == micro
