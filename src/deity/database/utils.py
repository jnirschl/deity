#!/usr/bin/env python3
"""utils.py in src/deity/database.

Utilities for database creation and management.
"""
import sqlite3
from pathlib import Path
from sqlite3 import Error

from loguru import logger


def create_connection(db_file, verbose=False) -> sqlite3.Connection:
    """Wrapper for sqlite3.connect()."""
    conn = None

    if verbose:
        if Path(db_file).exists():
            logger.info(f"Connecting to {db_file}")
        else:
            logger.info(f"Creating {db_file}")

    # try connecting to the database
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        logger.error(e)

    return conn


def create_cursor(conn) -> sqlite3.Cursor:
    """Create a cursor for the connection."""
    return conn.cursor()


def execute_query(conn, query, records=None) -> list:
    """Execute a query."""
    cur = create_cursor(conn)
    results = None
    try:
        if records:
            cur.executemany(query, records)
        else:
            cur.execute(query)

        conn.commit()
        results = cur.fetchall()
    except Error as e:
        cur.close()
        logger.error(f"Error executing query: {e}")
        raise e

    return results


def close_connection(conn) -> None:
    """Close the connection."""
    conn.close()
    return None
