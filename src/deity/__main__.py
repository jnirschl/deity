#!/usr/bin/env python3
# """Command-line interface."""
import glob
import itertools
import logging
import pathlib
from pathlib import Path

import click
from dotenv import find_dotenv
from dotenv import load_dotenv
from tqdm import tqdm

import deity


@click.command()
@click.argument(
    "input_dir",
    type=click.Path(exists=True, path_type=pathlib.Path),
)
@click.option(
    "--output-dir",
    default=None,
    type=click.Path(exists=True, path_type=pathlib.Path),
    help="Output directory",
)
@click.option("--suffix", default="jpg,png", type=str, help="File extensions")
@click.option("--dry-run", is_flag=True, help="Dry run")
@click.version_option()
def main(input_dir, output_dir=None, suffix="jpg,png", dry_run=False):
    """Rename files in a directory."""

    logger = logging.getLogger(__name__)
    logger.info(f"Input directory: {input_dir}")
    if dry_run:
        logger.info("########## Dry run ##########")

    # set output directory
    if output_dir is None:
        output_dir = input_dir

    # glob all files in input directory
    file_list = []
    for ext in suffix.split(","):
        file_list.append(glob.glob(str(input_dir.joinpath("*." + ext))))

    file_list = list(itertools.chain.from_iterable(file_list))
    logger.info(f"Found {len(file_list)} files in {input_dir}")

    # rename files
    for filepath in tqdm(file_list):
        new_filename = deity.rename(filepath, dry_run=dry_run, output_dir=output_dir)
        logger.info(f"new_filename: {new_filename}")


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
