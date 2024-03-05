#!/usr/bin/env python3
"""qr_codes.py in src/deity/barcodes.

Generates QR/MicroQR codes from a list of identifiers, according to ISO/IEC 18004:2015(E).
"""
from pathlib import Path
from typing import Optional
from typing import Union

import segno
from segno import QRCode

from deity.encode import encode_single


VALID_EXTENSIONS = ["png", "svg", "eps", "txt", "pdf", "tex"]


def create_qr_single(
    text: str,
    encode: bool = True,
    micro: bool = False,
) -> QRCode:
    """Create QR codes from a list of identifiers."""
    # if output_dir is None:
    #     output_dir = Path.cwd().joinpath("qr_codes")
    #
    # output_dir = Path(output_dir)
    # output_dir.mkdir(parents=True, exist_ok=True)

    # loop through identifiers and create QR codes
    text = encode_single(text)[1] if encode else text
    text = text.name if isinstance(text, Path) else text

    return segno.make(text, micro=micro)


def create_qr_list(
    identifiers: list[str],
    output_dir: Optional[Union[str, Path]] = None,
    encode: bool = True,
    scale: int = 1,
    ext: str = "png",
    micro: bool = False,
) -> None:
    """Create QR codes from a list of identifiers."""
    if output_dir is None:
        output_dir = Path.cwd().joinpath("qr_codes")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if ext not in VALID_EXTENSIONS:
        raise ValueError(f"Expected one of {VALID_EXTENSIONS}, but received {ext}")

    # loop through identifiers and create QR codes
    for identifier in identifiers:
        qr = create_qr_single(identifier, encode, ext, micro)
        qr.scale = scale
        output_filename = output_dir.joinpath(f"{identifier}.{ext}")
        qr.save(output_filename.as_posix())
