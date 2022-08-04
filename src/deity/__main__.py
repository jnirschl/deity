#!/usr/bin/env python3
# """Command-line interface."""
import logging
from pathlib import Path

import click


# from dotenv import find_dotenv, load_dotenv


@click.command()
@click.argument(
    "input_dir",
    type=click.Path(exists=True),
)
@click.option("--ext", default="jpg,png", type=str, help="File extensions")
@click.version_option()
def main(input_dir, ext):
    """Click"""
    pass
    # file_list = []
    # for suffix in ext.split(","):
    #     file_list = Path(input_dir).glob()


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    main()
