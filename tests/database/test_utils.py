"""Tests for testing database.utils."""
import sqlite3

import pytest

from deity.database import close_connection
from deity.database import create_cursor
from deity.database import execute_query


class TestDatabase:
    """Class for testing database connection and management."""

    def test_insert(self, conn, create_table_sql, insert_records, records):
        """Test creating a table and inserting a record."""
        for col in create_table_sql:
            execute_query(conn, col)

        for table, query in zip(records.keys(), insert_records):
            execute_query(conn, query, records[table])

        close_connection(conn)

    # @pytest.mark.xfail(reason="SQL error UNIQUE constraint error")
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
