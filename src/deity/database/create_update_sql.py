#!/usr/bin/env python3
"""create_update_sql.py in src/deity/database."""
import sqlite3
from pathlib import Path

import pandas as pd
from loguru import logger


def create_update_sql(
    df_sql: pd.DataFrame, table_name: str, conn: sqlite3.Connection, output_file: Path
) -> None:
    """Create or append a pandas DataFrame to a SQLite database table."""
    try:
        if len(df_sql) > 0:
            logger.info("Updating database...")
            df_sql.to_sql(table_name, conn, if_exists="append", index_label="id")
            csv_filename = output_file.with_name(f"{output_file.name}_{table_name}.csv")
            df_sql.to_csv(csv_filename, index=False)
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        conn.close()
