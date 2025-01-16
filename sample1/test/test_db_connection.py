import psycopg2
from app.utility import get_db_connection


def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        conn.close()
        assert result[0] == 1, "Database connection failed"
    except Exception as e:
        assert False, f"Database connection test failed: {e}"
