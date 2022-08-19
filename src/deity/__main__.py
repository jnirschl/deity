#!/usr/bin/env python3
"""Command-line interface."""
import glob
import itertools
import logging
from pathlib import Path

import click
from dotenv import find_dotenv
from dotenv import load_dotenv

from deity import database
from deity.encode import encode_all


@click.command()
@click.argument("input-dir", type=click.Path(exists=True, path_type=Path))
@click.argument("database-file", type=click.Path(path_type=Path))
@click.argument("table-name", type=click.STRING)
@click.option(
    "--output-dir", default=None, type=click.Path(exists=True, path_type=Path)
)
@click.option("--suffix", default="jpg,png", type=click.STRING, help="File extensions")
@click.option("--decode", is_flag=True, help="Decode files instead of encoding")
@click.option("--dry-run", is_flag=True, help="Dry run")
@click.version_option()
def main(
    input_dir: Path,
    database_file: Path,
    table_name: str,
    output_dir: str = None,
    suffix: str = "jpg,png",
    pattern: str = "[SL][HP][SDFNA]-\\d{2}-\\d{5}",
    decode: bool = False,
    dry_run: bool = False,
):
    """Encode or decode files in a directory."""
    logger = logging.getLogger(__name__)
    if dry_run:
        logger.info("########## Dry run ##########")

    # log input parameters
    logger.info(
        f"{'Decoding' if decode else 'Encoding'} files with ext {suffix} in {input_dir}"
    )

    # set output directory to input directory if not specified
    suffix = suffix.split(",")
    if output_dir is None:
        output_dir = input_dir

    # set database path to input directory if not specified
    if database_file.parent == Path("."):
        database_file = input_dir.joinpath(database_file)

    # set column name
    column_name = "accession" if table_name == "specimens" else "mrn"

    # set as pathlib.Path object
    output_dir = Path(output_dir)

    # glob all files in input directory
    file_list = []
    for ext in suffix:
        file_list.append(glob.glob(str(input_dir.joinpath("*." + ext))))

    # flatten list of lists
    if len(file_list) == 0:
        raise ValueError(f"No files found in {input_dir}")
    else:
        file_list = list(itertools.chain.from_iterable(file_list))
        logger.info(f"Found {len(file_list)} files in {input_dir}")

    # encode/decode files
    if not decode:
        df = encode_all(file_list, pattern=pattern, output_dir=output_dir)
    else:
        raise NotImplementedError(
            "decode_all not yet implemented"
        )  # df = database.decode_all(file_list, database_file, table_name, column_name)

    # create dataframe for renaming files
    df_file_rename = df[["old_filepath", "new_filepath"]].copy()
    df.pop("old_filepath")
    df_sql = df.rename(
        columns={
            "identifier": f"{column_name}",
            "short_hash": f"{column_name}_short_hash",
            "full_hash": f"{column_name}_full_hash",
            "new_filepath": "filepath",
        }
    )

    # connect to database
    conn = database.create_connection(database_file)

    try:
        if not dry_run:
            # update database, fail if table already exists
            logger.info("Updating database...")
            df_sql.to_sql(table_name, conn, if_exists="append", index_label="id")

            # rename files
            logger.info("Renaming files...")
            df_file_rename.apply(
                lambda row: row["old_filepath"].rename(row["new_filepath"]), axis=1
            )

    except Exception as e:
        logger.error(e)
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
