#!/usr/bin/env python3
"""Configure shared fixtures for deity."""
import random
import sqlite3
import string
from pathlib import Path
from typing import List

import numpy as np
import pytest
from click.testing import CliRunner

from deity.database import close_connection
from deity.database import create_connection
from deity.database import execute_query


@pytest.fixture()
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def identifier() -> str:
    """Fixture for a random identifier."""
    # create random identifier according to the pattern
    # [SL][AHP][SDFNA]?-\\d{2}-\\d{5}"
    if random.choice([True, False]):
        # Before 2023
        prefix = (
            random.choice(["S", "L"])
            + random.choice(["H", "P"])
            + random.choice(["S", "D", "F", "N", "A"])
        )
    else:
        prefix = random.choice(["S", "L"]) + random.choice(["A", "P"])

    return f"{prefix}-{np.random.randint(99):02d}-{np.random.randint(9.9e4):05d}"


def part() -> str:
    """Fixture for a random part."""
    return f"{random.choice(string.ascii_uppercase)}"


def random_diagnosis():
    """Fixture for a random diagnosis."""
    return random.choice(
        ["adenoma", "adenocarcinoma", "glioma", "melanoma", "squamous cell carcinoma"]
    )


@pytest.fixture()
def suffix_list() -> List[str]:
    """Fixture for a random list of three file extensions."""
    return random.sample(["png", "jpg", "txt", "pdf", "tif"], 3)


@pytest.fixture()
def filename() -> str:
    """Fixture for a random filename."""
    ext = random.choice(["png", "jpg", "txt", "pdf", "tif"])
    mag = random.choice([2, 5, 10, 20, 40])
    return f"{identifier()}_{part()}_{random_diagnosis()}_{mag:02d}x_{np.random.randint(999):03d}.{ext}"


@pytest.fixture()
def filename_list() -> List[str]:
    """Fixture for a list of random filenames."""
    return [filename() for _ in range(10)]


@pytest.fixture()
def test_files(suffix_list: list, num_test_cases: str = 10) -> List[str]:
    """Fixture to generate test filename combinations."""
    prefix = ["SHA", "SHD", "SHF", "SHN", "SHS", "LPS", "LPD", "LPF"]
    temp_filenames = [
        (
            f"{random.choice(prefix)}-{np.random.randint(99):02d}-{np.random.randint(9.9e4):05d}_"
            f"part-{random.choice(string.ascii_uppercase)}_{random_diagnosis()}_"
            f"{np.random.randint(40):02d}x_{np.random.randint(999):03d}"
            f".{random.choice(suffix_list)}"
        )
        for _elem in range(num_test_cases)
    ]

    # add new test cases with different prefixes
    new_prefix = ["SA", "SC", "SR", "SP"]
    temp_filenames.extend(
        [
            f"{random.choice(new_prefix)}-{np.random.randint(99):02d}-{np.random.randint(9.9e5):06d}_"
            f"part-{random.choice(string.ascii_uppercase)}_diagnosis_"
            f"{np.random.randint(40):02d}x_{np.random.randint(999):03d}"
            f".{random.choice(suffix_list)}"
            for _elem in range(num_test_cases)
        ]
    )
    return temp_filenames


@pytest.fixture()
def temp_dir(tmp_path_factory, test_files) -> str:
    """Fixture for a temporary file."""
    tmp_dir = tmp_path_factory.mktemp("data")
    for elem in test_files:
        tmp_dir.joinpath(elem).write_text("")
    return str(tmp_dir)


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
        "old_filepath TEXT NOT NULL,"
        "filepath TEXT NOT NULL"
        ");"
        for elem, col in zip(table_list, column_list, strict=True)
    ]


@pytest.fixture()
def insert_records(table_list) -> List[str]:
    """Fixture for the SQL statement to insert records into a table."""
    return [f"INSERT INTO {elem} VALUES (?, ?, ?, ?, ?, ?);" for elem in table_list]


@pytest.fixture()
def records() -> dict:
    """Fixture for the records to insert into the database."""
    return {
        "subjects": [
            (1, 12345, "full_hash1", "short_hash1", "old_filepath1", "filepath1"),
            (2, 54321, "full_hash2", "short_hash2", "old_filepath1", "filepath2"),
        ],
        "specimens": [
            (
                1,
                "SHS-00-12345",
                "full_hash1",
                "short_hash1",
                "old_filepath1",
                "filepath1",
            ),
            (
                2,
                "SHS-99-54321",
                "full_hash2",
                "short_hash2",
                "old_filepath1",
                "filepath2",
            ),
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
