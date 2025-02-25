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
from PIL.ImageFont import FreeTypeFont
from segno import QRCode

from deity.encode import encode_single


VALID_EXTENSIONS = ["png", "svg", "eps", "txt", "pdf", "tex"]
FONT_DIR = Path(__file__).parent.joinpath("font").as_posix()


def set_font(
    font: str = "default", font_size: int = 12, font_path: str = FONT_DIR
) -> FreeTypeFont:
    """Set the font."""
    font_path = Path(font_path)
    if isinstance(font, str) and font.lower() == "default":
        font_path = font_path.joinpath("DejaVuSansMono.ttf")
    elif isinstance(font, str) and font.lower() == "roboto":
        font_path = font_path.joinpath("RobotoMono-VariableFont_wght.ttf")
    elif isinstance(font, str) and font.lower() == "mono":
        font_path = font_path.joinpath("SpaceMono-Regular.ttf")
    elif isinstance(font, str) and Path(font).exists():
        font_path = Path(font)
    else:
        raise ValueError(f"Invalid font: {font}")

    return ImageFont.truetype(font_path.as_posix(), font_size)


def convert_qr_to_pil(
    qr: QRCode,
    scale: int = 4,
    text: Optional[str] = None,
    border: Optional[int] = None,
    font: Optional[str] = "mono",
    font_size: int = 10,
    font_color: Optional[str] = None,
    dark: str = "#000",
    light: str = "#fff",
    quiet_zone: Optional[str] = None,
    sep: str = "\n",
    output_size: Optional[tuple[int, int]] = None,
) -> Image:
    """Convert QR code to PIL image."""
    # save into memory buffer as PNG
    png = io.BytesIO()
    qr.save(png, kind="png", scale=scale, border=border, dark=dark, light=light)
    png.seek(0)  # important to let PIL load the png
    img = Image.open(png)
    img = img.convert("RGB")

    if text is None:
        return img

    # Draw the title on the QR code
    font = set_font(font=font, font_size=font_size)
    width, height = img.size
    x, y = (scale * (border if border is not None else qr.default_border_size), height)
    line_spacing = 1  # (font_size // 2) - 4
    lines = text.split(sep=sep)

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

    output_size = output_size or (width, height)
    res_img = Image.new(img.mode, output_size, color=quiet_zone or light)
    res_img.paste(img)
    draw = ImageDraw.Draw(res_img)
    font_color = font_color or dark
    draw_text = partial(
        draw.text, font=font, fill=ImageColor.getcolor(font_color, img.mode)
    )
    for line in lines:
        draw_text((x, y), line)
        y += font_size + line_spacing

    if has_palette:
        res_img = res_img.convert("P")

    if output_size:
        res_img = res_img.resize(output_size)

    return res_img


def create_qr_single(
    text: str,
    encode: bool = True,
    micro: bool = False,
    error: str = "M",
    mask: Optional[int] = None,
    boost_error: bool = True,
) -> QRCode:
    """Create QR codes from a string identifier.
    :param text:  String identifier to be encoded.
    :param encode: If True, the text will be encoded before creating the QR code.
    :param micro: If True, the QR code will be a MicroQR code.
    :param error: Error correction level (L, M, Q, H).
    :param mask: Mask pattern to be used.
    :param boost_error: If True, the error correction level will be boosted.
    :return: QR code object or PIL image.
    """
    if encode:
        filepath = encode_single(text)[1]
        text = filepath.name if isinstance(filepath, Path) else filepath

    return segno.make(text, micro=micro, error=error, mask=mask, boost_error=boost_error)


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
