#!/usr/bin/env python3
"""qr_codes.py in src/deity/barcodes.

Generates QR/MicroQR codes from a list of identifiers, according to ISO/IEC 18004:2015(E).
"""
import io
import os
from functools import partial
from pathlib import Path
from typing import Optional
from typing import Union

import segno
from loguru import logger
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont
from segno import QRCode

from deity.encode import encode_single


VALID_EXTENSIONS = ["png", "svg", "eps", "txt", "pdf", "tex"]


def convert_qr_to_pil(
    qr: QRCode,
    scale: int = 4,
    title: Optional[str] = None,
    border: Optional[int] = None,
    font_size: int = 12,
    font_color: Optional[str] = None,
    dark: str = "#000",
    light: str = "#fff",
    quiet_zone: Optional[str] = None,
    sep: str = "\n",
) -> Image:
    """Convert QR code to PIL image."""
    # save into memory buffer as PNG
    png = io.BytesIO()
    qr.save(png, kind="png", scale=scale)
    png.seek(0)  # important to let PIL load the png
    img = Image.open(png)
    img = img.convert("RGB")

    if title is None:
        return img

    # Draw the title on the QR code
    font_path = os.path.join(os.path.dirname(__file__), "font", "DejaVuSansMono.ttf")
    font = ImageFont.truetype(font_path, font_size)
    width, height = img.size
    x, y = (scale * (border or qr.default_border_size), height)
    line_spacing = font_size // 2
    lines = title.split(sep=sep)

    # Calculate the additional space required for the text
    for line in lines:
        try:  # Pillow versions < 10
            fw, fh = font.getsize(line)
        except AttributeError:
            fw, fh = font.getbbox(line)[2:4]

        if fw > width:
            width = fw + font_size

        height += fh + line_spacing

    has_palette = img.mode == "P"
    if has_palette:
        # The palette of the resulting image may be different from the
        # palette of the original image. To avoid problems with pasting the
        # QR code image into the resulting image, convert the QR code image to RGBA
        # This operation is reverted after drawing the text
        img = img.convert("RGBA")

    res_img = Image.new(img.mode, (width, height), color=quiet_zone or light)
    res_img.paste(img)
    draw = ImageDraw.Draw(res_img)
    font_color = font_color or dark
    draw_text = partial(draw.text, font=font, fill=ImageColor.getcolor(font_color, img.mode))
    for line in lines:
        draw_text((x, y), line)
        y += font_size + line_spacing

    if has_palette:
        res_img = res_img.convert("P")

    return res_img


def create_qr_single(
    text: str,
    encode: bool = True,
    micro: bool = False,
) -> QRCode:
    """Create QR codes from a string identifier.
    :param text:  String identifier to be encoded.
    :param encode: If True, the text will be encoded before creating the QR code.
    :param micro: If True, the QR code will be a MicroQR code.
    :return: QR code object or PIL image.
    """
    if encode:
        filepath = encode_single(text)[1]
        text = filepath.name if isinstance(filepath, Path) else filepath

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
        error_msg = f"Expected one of {VALID_EXTENSIONS}, but received {ext}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # loop through identifiers and create QR codes
    for identifier in identifiers:
        qr = create_qr_single(identifier, encode, ext, micro)
        qr.scale = scale
        output_filename = output_dir.joinpath(f"{identifier}.{ext}")
        try:
            qr.save(output_filename.as_posix())
        except Exception as e:
            logger.error(f"Error saving QR code: {e}")
            continue
