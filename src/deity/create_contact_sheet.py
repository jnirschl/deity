#!/usr/bin/env python3
"""Script to arrange QR codes on a printable label sheet according to Avery Presta 94503 Round Labels."""

from pathlib import Path
from typing import Optional

import click
import pandas as pd
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger
from PIL import Image

from deity import encode_single
from deity.barcodes.create_qr import convert_qr_to_pil
from deity.barcodes.create_qr import create_qr_single


# Constants for the label sheet layout
LABEL_ROWS = 14
LABEL_COLS = 11
LABEL_SPACING = 0.5  # cm
TOP_BOTTOM_MARGIN = 2  # cm
LEFT_RIGHT_MARGIN = 1  # cm
LABEL_DIAMETER = 1.27  # cm (1/2 inch)
DPI = 300  # Assuming a printing quality of 300 dots per inch

# Calculate size in pixels (1 inch = 2.54 cm)
PIXEL_SPACING = int((LABEL_SPACING / 2.54) * DPI)
PIXEL_MARGIN_LR = int((LEFT_RIGHT_MARGIN / 2.54) * DPI)
PIXEL_MARGIN_TB = int((TOP_BOTTOM_MARGIN / 2.54) * DPI)
LABEL_DIAMETER_PX = int((LABEL_DIAMETER / 2.54) * DPI)
SHEET_WIDTH_PX = (
    (LABEL_COLS * LABEL_DIAMETER_PX) + ((LABEL_COLS - 1) * PIXEL_SPACING) + (2 * PIXEL_MARGIN_LR)
)
SHEET_HEIGHT_PX = (
    (LABEL_ROWS * LABEL_DIAMETER_PX) + ((LABEL_ROWS - 1) * PIXEL_SPACING) + (2 * PIXEL_MARGIN_TB)
)


@click.command()
@click.argument("input-file", type=click.Path(exists=True, path_type=Path))
@click.option("--output-file", default=None, help="Output file name for the label sheet.")
@click.option("--column", default="filename", help="Column name for the QR code data.")
@click.option("--dry-run", is_flag=True, help="Perform a trial run with no changes.")
def main(input_file: Path, output_file: Optional[str], column: str, dry_run: bool) -> None:
    """
    Arrange QR codes on a printable label sheet with specific dimensions and spacing.

    :param input_file: CSV file containing text data to be encoded as QR codes.
    :param output_file: Name of the file to save the generated label sheet to.
    :param column: Name of the column in the CSV file containing the text data.
    :param dry_run: If True, no actual file will be written.
    """
    output_file = output_file or input_file.with_suffix(".pdf")
    logger.info(f"Input file: {input_file}")
    logger.info(f"Output file: {output_file}")

    # Initialize the label sheet
    label_sheet = Image.new("RGB", (SHEET_WIDTH_PX, SHEET_HEIGHT_PX), "white")

    # Load csv with names to be encoded
    df = pd.read_csv(input_file, header=0)

    # Loop through the rows of the csv and create QR codes
    for index, row in df.iterrows():
        name = row[column]
        identifier, filepath, full_hash, short_hash = encode_single(name)
        qr_code = create_qr_single(name, encode=False)

        #
        if full_hash is None:
            logger.warning(f"No identifier found in {filepath.name}")
            continue

        _id, part, loc, dx = filepath.name.split("_")[:4]
        title = f"{full_hash[:8]}-{full_hash[8:12]}\n{part}_{loc[:4]}_{dx[:6]}"
        qr_png = convert_qr_to_pil(qr_code, border=0, scale=4, title=title)
        # Calculate the row and column for this QR code
        row = index // LABEL_COLS
        col = index % LABEL_COLS

        # Calculate top-left position for this QR code
        x = PIXEL_MARGIN_LR + (col * (LABEL_DIAMETER_PX + PIXEL_SPACING))
        y = PIXEL_MARGIN_TB + (row * (LABEL_DIAMETER_PX + PIXEL_SPACING))

        # Resize QR code to fit the label, if necessary, and center it
        qr_png = qr_png.resize((LABEL_DIAMETER_PX, LABEL_DIAMETER_PX), Image.LANCZOS)
        label_sheet.paste(qr_png, (x, y))

    if dry_run:
        logger.info("Dry run mode: No changes will be made.")
        return
    # Save the label sheet to the specified output file
    label_sheet.save(output_file)
    logger.info(f"Label sheet saved to {output_file}")


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main()
