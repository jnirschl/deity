import sqlite3

import pytest

from deity.database import close_connection
from deity.database import create_connection
from deity.database import create_cursor
from deity.database import execute_query


@pytest.fixture()
def conn(tmp_path_factory):
    temp = tmp_path_factory.mktemp("data")
    db_file = temp.joinpath("test.db")
    db_file.touch()
    return create_connection(db_file)


@pytest.fixture()
def table():
    return ["subjects", "specimens"]


@pytest.fixture()
def columns():
    return ["mrn", "accession"]


@pytest.fixture()
def create_table_sql(table, columns):
    return [
        f"CREATE TABLE IF NOT EXISTS {elem} ("
        "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,"
        f"{col} INTEGER NOT NULL UNIQUE,"
        f"{col}full_hash TEXT NOT NULL UNIQUE,"
        f"{col}_short_hash TEXT NOT NULL UNIQUE"
        ");"
        for elem, col in zip(table, columns)
    ]


@pytest.fixture()
def insert_records(table):
    return [f"INSERT INTO {elem} VALUES (?, ?, ?, ?);" for elem in table]


@pytest.fixture()
def records():
    return {
        "subjects": [
            (1, 12345, "full_hash1", "short_hash1"),
            (2, 54321, "full_hash2", "short_hash2"),
        ],
        "specimens": [
            (1, "SHS-00-12345", "full_hash1", "short_hash1"),
            (2, "SHS-99-54321", "full_hash2", "short_hash2"),
        ],
    }


@pytest.mark.debug
class TestDatabase:
    """class for testing database connection"""

    def test_create_insert(self, conn, create_table_sql, insert_records, records):
        """test creating a table and inserting a record"""
        for table, col in zip(records.keys(), create_table_sql):
            execute_query(conn, col)

        for table, query in zip(records.keys(), insert_records):
            execute_query(conn, query, records[table])

    def test_select(self, conn, create_table_sql, insert_records, records):
        """test creating a table and selecting a record"""
        # create the table
        for table, col in zip(records.keys(), create_table_sql):
            execute_query(conn, col)

        # insert records
        for table, query in zip(records.keys(), insert_records):
            execute_query(conn, query, records=records[table])

        # select records
        for table in records.keys():
            result = execute_query(conn, f"SELECT * FROM {table}")
            assert result == records[table], AssertionError(
                f"{result} != {records[table]}"
            )

    def test_create_cursor(self, conn):
        """test creating a cursor"""
        cur = create_cursor(conn)
        assert cur is not None, AssertionError(f"{cur} is None")

    def test_close(self, conn):
        """test closing a connection"""
        conn = close_connection(conn)
        assert conn is None, AssertionError(f"{conn} is not None")
