"""Tests for testing database.utils."""
import sqlite3

import pytest

from deity.database import close_connection
from deity.database import create_connection
from deity.database import create_cursor
from deity.database import execute_query


@pytest.fixture()
def conn(tmp_path_factory):
    """Fixture for a temporary in-memory database connection."""
    return create_connection(":memory:")


@pytest.fixture()
def table():
    """Fixture for table names in the database."""
    return ["subjects", "specimens"]


@pytest.fixture()
def columns():
    """Fixture for column names in the database."""
    return ["mrn", "accession"]


@pytest.fixture()
def create_table_sql(table, columns):
    """Fixture for the SQL statement to create a table."""
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
    """Fixture for the SQL statement to insert records into a table."""
    return [f"INSERT INTO {elem} VALUES (?, ?, ?, ?);" for elem in table]


@pytest.fixture()
def records():
    """Fixture for the records to insert into the database."""
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
    """Class for testing database connection and management."""

    def test_insert(self, conn, create_table_sql, insert_records, records):
        """Test creating a table and inserting a record."""
        for col in create_table_sql:
            execute_query(conn, col)

        for table, query in zip(records.keys(), insert_records):
            execute_query(conn, query, records[table])

        close_connection(conn)

    def test_insert_fail(self, conn, create_table_sql, insert_records, records):
        """Test creating a table and inserting a record."""
        for col in create_table_sql:
            execute_query(conn, col)

        for table, query in zip(records.keys(), insert_records):
            execute_query(conn, query, records[table])
            with pytest.raises(sqlite3.IntegrityError):
                execute_query(conn, query, records[table])

        close_connection(conn)

    def test_select(self, conn, create_table_sql, insert_records, records):
        """Test creating a table and selecting a record."""
        # create the table
        for col in create_table_sql:
            execute_query(conn, col)

        # insert records
        for table, query in zip(records.keys(), insert_records):
            execute_query(conn, query, records=records[table])

        # select records
        for table in records.keys():
            query = (
                "SELECT * FROM subjects;"
                if table == "subjects"
                else "SELECT * FROM specimens;"
            )
            result = execute_query(conn, query)
            assert result == records[table], AssertionError(
                f"{result} != {records[table]}"
            )

        close_connection(conn)

    def test_create_cursor(self, conn):
        """Test creating a cursor."""
        cur = create_cursor(conn)
        assert cur is not None, AssertionError(f"{cur} is None")

    def test_close(self, conn):
        """Test closing a connection."""
        conn = close_connection(conn)
        assert conn is None, AssertionError(f"{conn} is not None")
