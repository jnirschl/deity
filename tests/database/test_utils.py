import sqlite3

import pytest

from deity.database import create_connection, create_cursor, execute_query, close_connection


@pytest.fixture()
def db_file(tmp_path_factory):
    temp = tmp_path_factory.mktemp("data")
    db_file = temp.joinpath("test.db")
    db_file.touch()
    return db_file

@pytest.fixture()
def conn(db_file):
    return create_connection(db_file)


@pytest.fixture()
def create_table_sql():
    return """
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        mrn INTEGER NOT NULL UNIQUE,
        mrn_full_hash TEXT NOT NULL UNIQUE,
        mrn_short_hash TEXT NOT NULL UNIQUE
        );
    """


@pytest.fixture()
def records_sql():
    return [
        ("1", "12345", "full_hash1", "short_hash1"),
        ("2", "54321", "full_hash2", "short_hash2"),
    ]

@pytest.fixture()
def insert_record_sql():
    return """
    INSERT INTO subjects
    VALUES (?, ?, ?, ?);
    """


class TestConnect():
    """ class for testing database connection """
    def test_connect(self, db_file):
        # db_file = str(db_file).replace("test", "test")
        conn = create_connection(db_file)
        assert conn is not None, AssertionError(f"Unable to connect to {db_file}")
        conn.close()

    @pytest.mark.debug
    def test_create_insert(self, conn, create_table_sql, insert_record_sql, records_sql):
        """ test creating a table and inserting a record """
        execute_query(conn, create_table_sql)
        execute_query(conn, insert_record_sql, records_sql)

        conn.close()