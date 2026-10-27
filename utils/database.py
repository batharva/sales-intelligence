"""
Database connection and query execution utilities.
Manages the SQLite database lifecycle.
"""

import sqlite3
import time
import pathlib
import streamlit as st

from config import DB_PATH


@st.cache_resource
def get_connection(db_path=None) -> sqlite3.Connection:
    """
    Get a cached SQLite connection.
    Uses cache_resource so the connection persists across reruns.
    """
    if db_path is None:
        db_path = str(DB_PATH)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def close_connection(conn: sqlite3.Connection):
    """Safely close a database connection."""
    try:
        conn.close()
    except Exception:
        pass


def execute_query(sql: str, params: tuple = None) -> tuple:
    """
    Execute a SQL query and return (rows, columns, row_count, elapsed_ms).
    Safe for SELECT queries only. Raises ValueError on non-SELECT statements.
    """
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH") and not sql_upper.startswith("PRAGMA"):
        raise ValueError("Only SELECT and WITH queries are allowed.")

    conn = get_connection()
    start = time.time()
    try:
        if params:
            cursor = conn.execute(sql, params)
        else:
            cursor = conn.execute(sql)
        rows = cursor.fetchall()
        elapsed = round((time.time() - start) * 1000, 2)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return rows, columns, len(rows), elapsed
    except sqlite3.Error as e:
        elapsed = round((time.time() - start) * 1000, 2)
        raise ValueError(f"SQL execution error: {str(e)}") from e


def execute_query_df(sql: str, params: tuple = None):
    """
    Execute a SQL query and return a Pandas DataFrame.
    """
    import pandas as pd

    conn = get_connection()
    try:
        if params:
            df = pd.read_sql_query(sql, conn, params=params)
        else:
            df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        raise ValueError(f"Query execution error: {str(e)}") from e


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def get_table_row_count(table_name: str) -> int:
    """Get the row count for a table."""
    try:
        conn = get_connection()
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]
    except Exception:
        return 0


def is_database_ready(db_path=None) -> bool:
    """Check if the database is populated with data."""
    if db_path is None:
        db_path = DB_PATH

    path = pathlib.Path(db_path)
    if not path.exists() or path.stat().st_size < 1000:
        return False

    if not table_exists("orders"):
        return False

    count = get_table_row_count("orders")
    return count > 0