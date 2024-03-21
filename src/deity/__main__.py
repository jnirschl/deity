#!/usr/bin/env python3
"""__main__.py in src/deity."""
from pathlib import Path
from typing import Optional

import click
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from deity import __version__
from deity import database
from deity.decode import decode_all
from deity.encode import encode_all
from deity.utils import create_df_sql
from deity.utils import get_file_list
from deity.utils import rename_files


@click.command()
@click.argument("input-dir", type=click.Path(exists=True, path_type=Path, resolve_path=True))
@click.option("--database-file", default="deity.db", type=click.Path(path_type=Path))
@click.option("--table-name", default="specimens", type=click.Choice(["subjects", "specimens"]))
@click.option("--output-dir", default=None, type=click.Path(path_type=Path))
@click.option("--extension", default="jpg,png,svs,txt,qpdata", type=click.STRING, help="Extension")
@click.option(
    "--pattern",
    default=None,
    type=click.STRING,
    help="Pattern",
)
@click.option("--decode", is_flag=True, help="Decode files instead of encoding")
@click.option("--dry-run", is_flag=True, help="Dry run")
@click.version_option(__version__)
def main(
    input_dir: Path,
    database_file: Path,
    table_name: str,
    output_dir: str = None,
    extension: str = "txt,jpg,png",
    pattern: Optional[str] = None,
    decode: bool = False,
    dry_run: bool = False,
) -> None:  # sourcery skip
    """Command line interface to encode or decode files in a directory."""
    logger.info("Dry run") if dry_run else None

    # database must exist if decoding
    if decode and not database_file.exists():
        raise FileNotFoundError(f"Database {database_file} does not exist")

    # set database path to input directory if not specified
    if database_file.parent == Path(".") and not dry_run:
        database_file = input_dir.joinpath(database_file)

    # glob all files in input directory
    file_list = get_file_list(input_dir, extension)

    # check if files were found
    if len(file_list) == 0:
        raise FileNotFoundError(f"No {extension} files found in {input_dir}")
    else:
        # log input parameters
        logger.info(
            f"{'Decoding' if decode else 'Encoding'} {len(file_list)} "
            f"files with ext {extension} in {input_dir}"
        )

    # encode/decode files
    if decode:
        decode_all(database_file, table_name, extension=extension, dry_run=dry_run)
    else:
        df = encode_all(file_list, pattern=pattern, output_dir=output_dir)

        # create dataframe for file renaming and sql export
        df_file_rename, df_sql = create_df_sql(df, table_name)

        # check if new_filepath is different from old_filepath
        if (df_file_rename["old_filepath"] == df_file_rename["new_filepath"]).all():
            logger.error("No files were encoded")
            raise ValueError("No files were encoded")

        # connect to database or create if it doesn't exist
        if not dry_run and not database_file.exists():
            logger.info(f"Creating {database_file}")

            conn = database.create_connection(database_file)

            database.create_update_sql(df_sql, table_name, conn, output_file=database_file)

            if len(df_file_rename) > 0:
                rename_files(df_file_rename)


if __name__ == "__main__":
    # find .env automatically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
