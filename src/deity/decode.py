#!/usr/bin/env python3
"""decode.py in src/deity.

Helper functions to decode coded identifiers in a filename
using data store in the SQLite database.
"""
from pathlib import Path

import pandas as pd
from loguru import logger

from deity import database
from deity.utils import find_existing_file


def decode_all(
    database_file: Path, table_name: str, extension: str = None, dry_run=False
) -> None:
    """Decode files in input_dir using database_file and table_name."""
    # connect to database
    conn = database.create_connection(database_file)

    # load database
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn, index_col="id")  # noqa: S608

    # decode files
    df_file_rename = df[["old_filepath", "filepath"]].copy()

    # convert filepath from str to Path
    df_file_rename["filepath"] = df_file_rename["filepath"].apply(Path)

    #
    df_file_rename["old_filepath"] = df_file_rename.apply(
        lambda row: row["filepath"].parents[1].joinpath(row["old_filepath"]),
        axis=1,
    )

    # decode files
    try:
        # rename files
        file_list_exists = df_file_rename["filepath"].apply(Path.exists)

        # if all files do not exist, check for alternate extension
        if not file_list_exists.all() and extension is not None:
            # sum inverted boolean
            sum_missing_files = (~file_list_exists).sum()
            logger.warning(
                f"{sum_missing_files} of {len(file_list_exists)} file(s) not found."
                f" Checking for alternate extensions: {extension}..."
            )
            df_file_rename["filepath"] = df_file_rename["filepath"].apply(
                find_existing_file, extensions=extension
            )
            # update df_file_rename["old_filepath"] with new suffix from
            # df_file_rename["filepath"] but keep the original stem from old_filepath
            df_file_rename["old_filepath"] = df_file_rename.apply(
                lambda row: row["old_filepath"].with_suffix(row["filepath"].suffix),
                axis=1,
            )

            file_list_exists = df_file_rename["filepath"].apply(Path.exists)

        # rename files if all files exist
        if file_list_exists.all():
            if not dry_run:
                logger.info("Reverting files to original name...")
                df_file_rename.apply(
                    lambda row: row["filepath"].rename(row["old_filepath"]), axis=1
                )
        else:
            logger.error(f"File(s) not found: {df_file_rename[~file_list_exists]}")
            raise FileNotFoundError(
                f"File(s) not found: {df_file_rename[~file_list_exists]}"
            )

    except Exception as e:
        logger.error(e)
        raise e
    finally:
        conn.close()
