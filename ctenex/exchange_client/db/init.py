from ctenex.exchange_client.db.connection import get_db_connection


def init_db():
    """Initialize the database schema."""
    with get_db_connection() as conn:
        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    contract_id TEXT,
                    side TEXT,
                    quantity TEXT,
                    price TEXT,
                    status TEXT,
                    created_at TIMESTAMP
                )
            """
        )


if __name__ == "__main__":
    init_db()
