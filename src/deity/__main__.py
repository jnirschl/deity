#!/usr/bin/env python3
# """Command-line interface."""
import itertools
import logging
from pathlib import Path

import click
from dotenv import find_dotenv
from dotenv import load_dotenv

import deity


@click.command()
@click.argument(
    "input_dir", type=click.Path(exists=True),
)
@click.option(
    "--output-dir", default=None, type=click.Path(exists=True), help="Output directory"
)
@click.option("--suffix", default="jpg,png", type=str, help="File extensions")
@click.option("--dry-run", is_flag=True, help="Dry run")
@click.version_option()
def main(input_dir, output_dir=None, suffix="jpg,png", dry_run=False):
    """Rename files in a directory."""

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Input directory: {input_dir}")
    if dry_run:
        logger.info("########## Dry run ##########")

    # set vars
    input_dir = Path(input_dir).resolve()
    output_dir = (
        Path(output_dir).resolve().parent if output_dir else input_dir.parents[0]
    )

    file_list = []
    for suffix in suffix.split(","):
        file_list.append(Path(input_dir).glob("**/*." + suffix))

    file_list = itertools.chain.from_iterable(file_list)
    for filepath in file_list:
        logger.info(f"filepath: {filepath}")
        if dry_run:
            logger.info(f"new_filename: {filepath.name}")
        else:
            new_filename = deity.rename(
                filepath, dry_run=dry_run, output_dir=output_dir
            )
            logger.info(f"new_filename: {new_filename}")
        # rename(filepath, output_dir=output_dir, dry_run=dry_run)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
