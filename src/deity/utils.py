#!/usr/bin/env python3
"""utils.py in src/deity."""

import glob
from pathlib import Path
from typing import Tuple

import pandas as pd
from loguru import logger


DEFAULT_PATTERN = "[SL]([A-Z][SDFNA]?)-\\d{2}-\\d{5,6}"


def get_file_list(input_dir: Path, extension: str = "txt,jpg,png") -> list:
    """Get list of files in input directory with specified extensions."""
    # convert extension string to list of extensions
    extension = extension.split(",")

    # remove leading dot from extensions
    extension = [ext.lstrip(".") for ext in extension]

    file_list = []
    for ext in extension:
        search_path = str(input_dir.joinpath(f"**/*.{ext}"))
        file_list.extend(glob.glob(search_path, recursive=True))
    return file_list


def rename_files(df_file_rename: pd.DataFrame) -> None:
    """Rename files based on pandas DataFrame."""
    logger.info("Renaming files...")
    df_file_rename.apply(
        lambda row: row["old_filepath"].rename(row["new_filepath"]),
        axis=1,
    )


def create_df_sql(
    df: pd.DataFrame, table_name: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create pandas DataFrame from SQL query."""
    df_file_rename = df[["old_filepath", "new_filepath"]].copy()

    # rename columns
    column_name = "accession" if table_name == "specimens" else "mrn"

    df_sql = df.rename(
        columns={
            "identifier": f"{column_name}",
            "short_hash": f"{column_name}_short_hash",
            "full_hash": f"{column_name}_full_hash",
            "new_filepath": "filepath",
        }
    )
    # convert old_filepath from Path to str
    df_sql["old_filepath"] = df_sql["old_filepath"].astype(str)

    return df_file_rename, df_sql


def find_existing_file(path: Path, extensions: str) -> Path:
    """Find existing file with alternate extension."""
    if not path.exists():
        for ext in extensions.split(","):
            new_path = path.with_suffix(f".{ext.strip()}")
            if new_path.exists():
                return new_path
    return path
