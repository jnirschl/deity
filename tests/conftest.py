"""Configure shared fixtures for tests."""
import random
import sqlite3
import string
from pathlib import Path
from typing import List

import numpy as np
import pytest

from src.deity.database import close_connection
from src.deity.database import create_connection
from src.deity.database import execute_query


@pytest.fixture()
def temp_dir(tmp_path_factory, test_files) -> str:
    """Fixture for a temporary file."""
    tmp_dir = tmp_path_factory.mktemp("data")
    for elem in test_files:
        tmp_dir.joinpath(elem).write_text("")
    return str(tmp_dir)


@pytest.fixture()
def test_files(num_test_cases: str = 10) -> List[str]:
    """Fixture to generate test filename combinations."""
    prefix = ["SHA", "SHD", "SHF", "SHN", "SHS", "LPS", "LPD", "LPF"]
    suffix = ["jpg", "png", "tif", "tiff", "txt"]
    temp_filenames = [
        (
            f"{random.choice(prefix)}-{np.random.randint(99):02d}-{np.random.randint(9.9e4):05d}_"
            f"part-{random.choice(string.ascii_uppercase)}_diagnosis_"
            f"{np.random.randint(40):02d}x_{np.random.randint(999):03d}"
            f".{random.choice(suffix)}"
        )
        for elem in range(num_test_cases)
    ]
    return temp_filenames


@pytest.fixture()
def conn(tmp_path_factory) -> sqlite3.Connection:
    """Fixture for a temporary in-memory database connection."""
    return create_connection(":memory:")


@pytest.fixture()
def table_list() -> List[str]:
    """Fixture for table names in the database."""
    return ["subjects", "specimens"]


@pytest.fixture()
def column_list() -> List[str]:
    """Fixture for column names in the database."""
    return ["mrn", "accession"]


@pytest.fixture()
def create_table_sql(table_list, column_list) -> List[str]:
    """Fixture for the SQL statement to create a table."""
    return [
        f"CREATE TABLE IF NOT EXISTS {elem} ("
        "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,"
        f"{col} INTEGER NOT NULL UNIQUE,"
        f"{col}_short_hash TEXT NOT NULL UNIQUE,"
        f"{col}_full_hash TEXT NOT NULL UNIQUE,"
        "filepath TEXT NOT NULL"
        ");"
        for elem, col in zip(table_list, column_list)
    ]


@pytest.fixture()
def insert_records(table_list) -> List[str]:
    """Fixture for the SQL statement to insert records into a table."""
    return [f"INSERT INTO {elem} VALUES (?, ?, ?, ?, ?);" for elem in table_list]


@pytest.fixture()
def records() -> dict:
    """Fixture for the records to insert into the database."""
    return {
        "subjects": [
            (1, 12345, "full_hash1", "short_hash1", "filepath1"),
            (2, 54321, "full_hash2", "short_hash2", "filepath2"),
        ],
        "specimens": [
            (1, "SHS-00-12345", "full_hash1", "short_hash1", "filepath1"),
            (2, "SHS-99-54321", "full_hash2", "short_hash2", "filepath2"),
        ],
    }


@pytest.fixture()
def tmp_db(tmp_path_factory: Path, create_table_sql, insert_records) -> str:
    """Fixture for creating a temporary database."""
    db_filepath = tmp_path_factory.mktemp("data").joinpath("temp.db")
    conn = create_connection(db_filepath)

    for elem in create_table_sql:
        execute_query(conn, elem)

    close_connection(conn)

    return str(db_filepath)
