#!/usr/bin/env python3
"""Command-line interface."""
import glob
import logging
from pathlib import Path

import click
from dotenv import find_dotenv
from dotenv import load_dotenv

from deity import database
from deity.decode import decode_all
from deity.encode import encode_all


@click.command()
@click.argument("input-dir", type=click.Path(exists=True, path_type=Path))
@click.argument("database-file", type=click.Path(path_type=Path))
@click.argument("table-name", type=click.STRING)
@click.option(
    "--output-dir", default=None, type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--extension", default="txt,jpg,png", type=click.STRING, help="Extensions"
)
@click.option("--decode", is_flag=True, help="Decode files instead of encoding")
@click.option("--dry-run", is_flag=True, help="Dry run")
@click.version_option()
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
    """Encode or decode files in a directory."""
    logger = logging.getLogger(__name__)
    if dry_run:
        logger.info("########## Dry run ##########")

    # log input parameters
    logger.info(
        f"{'Decoding' if decode else 'Encoding'} files with ext {extension} in {input_dir}"
    )

    # convert extension string to list of extensions
    extension = extension.split(",")

    # set output directory to input directory if not specified
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
    for ext in extension:
        # get files with extension recursively and add to list
        search_path = str(input_dir.joinpath(f"**/*.{ext}"))
        file_list.extend(glob.glob(search_path, recursive=True))

    # check if files were found
    if len(file_list) == 0:
        raise FileNotFoundError(f"No {extension} files found in {input_dir}")
    else:
        logger.info(f"Found {len(file_list)} files in {input_dir}")

    # encode/decode files
    if decode:
        # decode files
        logger.info(f"Decoding files from database {database_file.name}...")
        decode_all(input_dir, database_file, table_name)
    else:
        # encode files
        logger.info(f"Encoding {extension} files to database {database_file.name}...")
        df = encode_all(file_list, pattern=pattern, output_dir=output_dir)

        # create dataframe for renaming files
        df_file_rename = df[["old_filepath", "new_filepath"]].copy()

        # rename columns
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

        # connect to database
        conn = database.create_connection(database_file)

        try:
            if not dry_run:
                # update database, fail if table already exists
                if len(df_sql) > 0:
                    logger.info("Updating database...")
                    df_sql.to_sql(
                        table_name, conn, if_exists="append", index_label="id"
                    )
                    df_sql.to_csv(output_dir.joinpath(f"{table_name}.csv"), index=False)

                    # rename files
                    logger.info("Renaming files...")
                    df_file_rename.apply(
                        lambda row: row["old_filepath"].rename(row["new_filepath"]),
                        axis=1,
                    )
                else:
                    logger.info(f"No {extension} files found in {input_dir}")

        except Exception as e:
            logger.error(e)
            raise e
        finally:
            conn.close()


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
