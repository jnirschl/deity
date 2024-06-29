#!/usr/bin/env python3
"""Script to arrange QR codes on a printable label sheet according to Avery Presta 94503 Round Labels."""

from pathlib import Path
from typing import Optional
from uuid import uuid4

import click
import numpy as np
import pandas as pd
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger
from PIL import Image
from PIL import ImageDraw

from deity import encode_single
from deity.barcodes.create_qr import convert_qr_to_pil
from deity.barcodes.create_qr import create_qr_single
from deity.barcodes.create_qr import set_font
from deity.utils import yaml_loader


def load_config(config: str) -> dict:
    """Load the configuration file."""
    if not Path(config).exists() or not Path(config).is_file():
        logger.error(f"Config file {config} does not exist.")
        raise FileNotFoundError(f"Config file {config} does not exist.")

    config = yaml_loader(config)
    config["output_size"] = tuple(config["output_size"])
    config["page_size"] = tuple(config["page_size"])
    return config


def draw_label(
    image: Image.Image,
    xy_coord: tuple,
    text: Optional[str],
    font: str = "default",
    font_size: int = 20,
    fill: str = "black",
):
    """Draw the row number on the label sheet."""
    if text is None:
        return image

    draw = ImageDraw.Draw(image)
    font = set_font(font, font_size=font_size)
    draw.text(xy_coord, text, font=font, fill=fill)

    return image


def setup_df(df: pd.DataFrame) -> pd.DataFrame:
    """Add uuid, label_text, and new_filename columns to df."""
    if "uuid" not in df.columns:
        cols = list(df.columns)
        cols.insert(0, "uuid")
        df["uuid"] = df.apply(
            lambda x: str(uuid4()) if x.get("filename") else None, axis=1
        )
        df = df[cols].copy()
    else:
        # only update uuids that are null
        df["uuid"] = df["uuid"].apply(lambda x: str(uuid4()) if pd.isnull(x) else x)

    if "label_text" not in df.columns:
        # add empty column for label text
        df.loc[:, "label_text"] = ""

    if "new_filename" not in df.columns:
        df.loc[:, "new_filename"] = ""

    if "full_hash" not in df.columns:
        df.loc[:, "full_hash"] = ""

    if "short_hash" not in df.columns:
        df.loc[:, "short_hash"] = ""

    return df


@click.command()
@click.argument("input-file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-file", default=None, help="Output file name for the label sheet."
)
@click.option(
    "--config",
    default=None,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the configuration file.",
)
@click.option("--column", default="filename", help="Column name for the QR code data.")
@click.option(
    "--start",
    default=0,
    type=click.IntRange(0, 153),
    help="Start index for the contact sheet (0-153).",
)
@click.option(
    "--no-encode", default=False, is_flag=True, help="Do not encode the text."
)
@click.option("--dry-run", is_flag=True, help="Perform a trial run with no changes.")
@click.option("--debug", is_flag=True, help="Show debug information.")
def main(
    input_file: Path,
    output_file: Optional[str] = None,
    config: Optional[str] = None,
    column: str = "filename",
    start: int = 0,
    debug: bool = False,
    no_encode: bool = False,
    dry_run: bool = False,
) -> None:  # sourcery-skip
    """Arrange QR codes on a printable label sheet with specific dimensions and spacing.

    :param input_file: CSV file containing text data to be encoded as QR codes.
    :param output_file: Name of the file to save the generated label sheet to.
    :param config: Path to the configuration file.
    :param column: Name of the column in the CSV file containing the text data.
    :param start: Start index for the contact sheet.
    :param debug: If True, debug information will be shown.
    :param dry_run: If True, no actual file will be written.
    """
    # setup
    project_dir = Path(__file__).resolve().parents[2]
    conf_dir = project_dir.joinpath("src", "deity", "conf")
    if output_file is None:
        output_file = Path(
            str(input_file).replace("data/raw", "data/processed")
        ).with_suffix(".tif")
        output_file.parent.mkdir(parents=True, exist_ok=True)

    log_dir = project_dir.joinpath("logs")
    logger.add(
        log_dir.joinpath(f"{Path(__file__).stem}.log"),
        rotation="10 MB",
        level="INFO",
    )

    # load configuration settings
    config = config or conf_dir.joinpath("contact_sheet.yaml")
    config_dict = load_config(config)
    label_dia_px = config_dict["label_size"]["diameter"]
    px_spacing_x = config_dict["label_spacing"]["x"]
    px_spacing_y = config_dict["label_spacing"]["y"]
    margin_lr = config_dict["margins"]["left_right"]
    margin_tb = config_dict["margins"]["top_bottom"]

    # log configuration settings
    logger.info(f"Input file: {input_file}")
    logger.info(f"Output file: {output_file}")
    logger.info(f"Configuration file: {config_dict['name']}")

    # Initialize the label sheet
    label_sheet = Image.new("RGB", config_dict["page_size"], "white")

    # add filename to top of label sheet
    x = margin_lr + 100
    y = margin_tb - 140
    label_sheet = draw_label(label_sheet, (x, y), f"{output_file.stem}", font_size=32)

    # add column label above each column
    for col in range(config_dict["columns"]):
        x = margin_lr + (col * (label_dia_px + px_spacing_x))
        y = margin_tb - 80
        label_sheet = draw_label(label_sheet, (x, y), f"Col {col+1}", font_size=20)

    # add row label to the left of each row
    for row in range(config_dict["rows"]):
        x = margin_lr - 100
        y = margin_tb + (row * (label_dia_px + px_spacing_y))
        label_sheet = draw_label(label_sheet, (x, y), f"Row {row+1}", font_size=20)
        label_sheet = draw_label(
            label_sheet, (x + 10, y + 18), f"{(row*11)+1}", font_size=20
        )

    # Load csv with names to be encoded
    df = pd.read_csv(input_file, header=0)
    # fillna
    df = df.fillna("")

    # update df with new columns
    df = setup_df(df)

    # check if any rows have filenames >54 chars
    if df[column].str.len().max() > 54:
        logger.warning("Some names are longer than 54 characters")

    # Loop through the rows of the csv and create QR codes
    for idx, df_row in df.iterrows():
        name = df_row.get(column)
        if name is None or pd.isnull(name) or name == "" or "____" in name:
            # logger.warning(f"Starting new accession: {df_row['accession']}")
            # Calculate the row and column for this QR code
            row = (idx + start) // config_dict["columns"]
            col = (idx + start) % config_dict["columns"]

            # Calculate top-left position for this QR code
            x = np.round(margin_lr + (col * (label_dia_px + px_spacing_x))).astype(int)
            y = np.round(margin_tb + (row * (label_dia_px + px_spacing_y))).astype(int)

            #
            label_text = (
                f"Starting\n{df_row['accession']}\n{df.loc[idx+1, 'part']}, {df_row['stain']}"
                f"\n{df.loc[idx+1, 'uuid'][:8]}"
                if df_row["accession"]
                else None
            )
            label_sheet = draw_label(label_sheet, (x, y), label_text, font_size=18)
            df.drop(idx, inplace=True)
            continue

        # encode the name
        identifier, filepath, full_hash, short_hash = encode_single(name)

        # add filepath to column in df
        new_filename = name if no_encode else filepath.name
        df.at[idx, "new_filename"] = new_filename

        # Create the QR code
        qr_code = create_qr_single(new_filename, encode=False, error="L")

        # Extract the metadata from the filename
        _id, _part, _loc, _dx, _stain = new_filename.split("_")[:5]
        # stain = stain.replace("-", "")[:5]
        # text = f"{df_row['uuid'][:12]}\n  {full_hash[:6]}_{part}\n  {loc}_{stain}"
        text = f"{df_row['uuid'][:8]}\n{df_row['uuid'][9:18]}"

        # add text to column in df
        df.at[idx, "label_text"] = text.replace("\n  ", "_").strip()

        # Convert the QR code to a PIL image
        qr_png = convert_qr_to_pil(
            qr_code,
            border=config_dict["border"],
            scale=config_dict["scale"],
            font=config_dict["font"],
            font_size=config_dict["font_size"],
            text=text,
            output_size=config_dict["output_size"],
        )
        if qr_png.size != config_dict["output_size"]:
            logger.warning(
                f"QR code for {name} is not the correct size. "
                f"Expected {config_dict['output_size']}, but got {qr_png.size}."
            )
            logger.warning(f"QR code for {name} will be resized to {config_dict['output_size']}.")

        # Calculate the row and column for this QR code
        row = (idx + start) // config_dict["columns"]
        col = (idx + start) % config_dict["columns"]

        # Calculate top-left position for this QR code
        x = np.round(margin_lr + (col * (label_dia_px + px_spacing_x))).astype(int)
        y = np.round(margin_tb + (row * (label_dia_px + px_spacing_y))).astype(int)

        # Paste the QR code onto the label sheet
        label_sheet.paste(qr_png, (x, y))

        # add text label with block number (aka part)
        label_text = (
            f"{df_row['abbrev'][:4]} {df_row['part']} {df_row['stain']}" if df_row["part"] else f"{df_row['abbrev'][:4]} {df_row['stain']}"
        )
        label_sheet = draw_label(label_sheet, (x, y - 40), label_text, font_size=18)

    if dry_run:
        logger.info("Dry run mode: No changes will be made.")
        return

    if debug:
        # blend label_sheet with tiff named "template
        template = Image.open("template.tif")
        blend_img = Image.blend(label_sheet, template, alpha=0.5)
        blend_img.show()

    # Save the label sheet and uuid df to the specified files
    csv_file = output_file.parent.joinpath(f"{output_file.stem}_uuid.csv")
    if output_file.exists() or csv_file.exists():
        logger.warning(f"Output file {output_file} or {csv_file} already exists.")
        result = click.confirm("Do you want to overwrite?", abort=True)
        if not result:
            logger.error("Aborted by user. No files were written.")
            return

    label_sheet.save(output_file, dpi=(config_dict["dpi"], config_dict["dpi"]))
    logger.info(f"Label sheet saved to {output_file}")

    # save df with uuids to csv
    df.to_csv(csv_file, index=False)
    logger.info(f"UUIDs saved to {csv_file}")


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main()
