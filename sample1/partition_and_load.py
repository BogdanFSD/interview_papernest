import psycopg2
import pandas as pd
import os
import logging
from utility import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)



def check_table_and_partitions(cursor):
    """
    Check if the parent table and required partitions exist in the database.
    """
    # Check if the parent table exists
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'network_data'
        );
    """
    )
    table_exists = cursor.fetchone()[0]

    # Check if the partitions exist
    if table_exists:
        cursor.execute(
            """
            SELECT inhrelid::regclass AS partition_name
            FROM pg_inherits
            WHERE inhparent = 'network_data'::regclass;
        """
        )
        partitions = {row[0] for row in cursor.fetchall()}
        required_partitions = {"network_data_p1", "network_data_p2", "network_data_p3"}
        if required_partitions.issubset(partitions):
            return True  # Parent table and all required partitions exist
        else:
            logging.info(f"Missing partitions: {required_partitions - partitions}")
    return False


def main():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the parent table and partitions exist
        if check_table_and_partitions(cursor):
            logging.info(
                "Partitioned table 'network_data' and all required partitions exist. Skipping partitioning and data loading."
            )
            return

        logging.info("Creating partitioned table and loading data...")

        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS network_data CASCADE;")

        # Create partitioned table
        cursor.execute(
            """
            CREATE TABLE network_data (
                Operateur VARCHAR(10),
                x INT,
                y INT,
                g2 BOOLEAN,
                g3 BOOLEAN,
                g4 BOOLEAN
            ) PARTITION BY RANGE (x);
        """
        )

        # Define partitions, including a default partition
        cursor.execute(
            """
            CREATE TABLE network_data_p1 PARTITION OF network_data FOR VALUES FROM (102980) TO (400000);
            CREATE TABLE network_data_p2 PARTITION OF network_data FOR VALUES FROM (400000) TO (800000);
            CREATE TABLE network_data_p3 PARTITION OF network_data FOR VALUES FROM (800000) TO (1240586);
            CREATE TABLE network_data_default PARTITION OF network_data DEFAULT;
        """
        )

        # Add indexes to partitions
        cursor.execute("CREATE INDEX idx_x_y_p1 ON network_data_p1 (x, y);")
        cursor.execute("CREATE INDEX idx_x_y_p2 ON network_data_p2 (x, y);")
        cursor.execute("CREATE INDEX idx_x_y_p3 ON network_data_p3 (x, y);")

        # Load CSV into DataFrame
        df = pd.read_csv("/app/data.csv", delimiter=";")

        # Ensure all data types are standard Python types
        df["Operateur"] = df["Operateur"].astype(str)
        df["x"] = df["x"].astype(int)
        df["y"] = df["y"].astype(int)
        df["2G"] = df["2G"].astype(bool)
        df["3G"] = df["3G"].astype(bool)
        df["4G"] = df["4G"].astype(bool)

        # Insert data into the partitioned table
        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO network_data (Operateur, x, y, g2, g3, g4)
                VALUES (%s, %s, %s, %s, %s, %s);
            """,
                (row["Operateur"], row["x"], row["y"], row["2G"], row["3G"], row["4G"]),
            )

        conn.commit()
        logging.info(
            "Partitioned table created and data loaded into PostgreSQL successfully."
        )

    except psycopg2.Error as e:
        logging.error(f"Database operation failed: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
