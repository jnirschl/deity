#!/usr/bin/env python3
"""__main__.py in src/deity."""
from pathlib import Path

import click
import pkg_resources
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from deity import database
from deity.decode import decode_all
from deity.encode import encode_all
from deity.utils import create_df_sql
from deity.utils import get_file_list
from deity.utils import rename_files


__version__ = pkg_resources.get_distribution("deity").version


@click.command()
@click.argument("input-dir", type=click.Path(exists=True, path_type=Path))
@click.argument("database-file", type=click.Path(path_type=Path))
@click.argument("table-name", type=click.STRING)
@click.option(
    "--output-dir", default=None, type=click.Path(path_type=Path)
)
@click.option(
    "--extension", default="txt,jpg,png", type=click.STRING, help="Extension"
)
@click.option(
    "--pattern",
    default="[SL][HP][SDFNA]-\\d{2}-\\d{5}",
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
    pattern: str = "[SL][HP][SDFNA]-\\d{2}-\\d{5}",
    decode: bool = False,
    dry_run: bool = False,
) -> None:
    """Command line interface to encode or decode files in a directory."""
    if dry_run:
        logger.info("Dry run")

    # log input parameters
    logger.info(
        f"{'Decoding' if decode else 'Encoding'} files with ext {extension} in {input_dir}"
    )

    # set database path to input directory if not specified
    if database_file.parent == Path("."):
        database_file = input_dir.joinpath(database_file)

    # glob all files in input directory
    file_list = get_file_list(input_dir, extension)

    # check if files were found
    if len(file_list) == 0:
        raise FileNotFoundError(f"No {extension} files found in {input_dir}")

    # encode/decode files
    if decode:
        # decode files
        # logger.info(f"Decoding files from database {database_file.name}...")
        decode_all(database_file, table_name)
    else:
        # encode files
        # logger.info(f"Encoding {extension} files to database {database_file.name}...")
        df = encode_all(file_list, pattern=pattern, output_dir=output_dir)

        # create dataframe for file renaming and sql export
        df_file_rename, df_sql = create_df_sql(df, table_name)

        # connect to database or create if it doesn't exist
        if not database_file.exists():
            logger.info(f"Creating {database_file}")
        conn = database.create_connection(database_file)

        try:
            if not dry_run:
                # update database, fail if table already exists
                if len(df_sql) > 0:
                    logger.info("Updating database...")
                    df_sql.to_sql(
                        table_name, conn, if_exists="append", index_label="id"
                    )
                    csv_filename = database_file.with_name(
                        f"{database_file.name}_{table_name}.csv"
                    )
                    df_sql.to_csv(csv_filename, index=False)

                if len(df_file_rename) > 0:
                    rename_files(df_file_rename)
        except Exception as e:
            logger.error(e)
            raise e
        finally:
            conn.close()


if __name__ == "__main__":
    # find .env automatically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
