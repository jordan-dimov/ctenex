from contextlib import contextmanager
from pathlib import Path

import duckdb

# TODO: Move to settings
# Initialize DuckDB connection
DB_PATH = Path(__file__).parent.parent / "data" / "orders.db"
DB_PATH.parent.mkdir(exist_ok=True)


@contextmanager
def get_db_connection():
    """Get a database connection."""
    try:
        conn = duckdb.connect(str(DB_PATH))
        try:
            yield conn
        finally:
            conn.close()
    except duckdb.IOException:
        raise
