#!/usr/bin/env python3
"""decode.py in src/deity."""
import logging
from pathlib import Path

import pandas as pd

from deity import database


def decode_all(database_file: Path, table_name: str) -> None:
    """Decode files in input_dir using database_file and table_name."""
    logger = logging.getLogger(__name__)

    # connect to database
    conn = database.create_connection(database_file)

    # load database
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn, index_col="id")  # noqa: S608

    # decode files
    df_file_rename = df[["old_filepath", "filepath"]].copy()

    # convert filepath from str to Path
    df_file_rename["filepath"] = df_file_rename["filepath"].apply(Path)

    # decode files
    try:
        # rename files
        logger.info("Reverting files to original name...")
        df_file_rename.apply(
            lambda row: row["filepath"].rename(row["old_filepath"]), axis=1
        )
        print(df_file_rename)

    except Exception as e:
        logger.error(e)
        raise e
    finally:
        conn.close()
