
import os
import tempfile
import unittest

import psycopg2

from modules.anushka.operation.history_repository import create_movement
from modules.anushka.operation.recovery import recover_pending_movements


def get_test_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="smart_file_manager_test",
        user="postgres",
        password=os.environ["DB_PASSWORD"],
    )


class TestRecoveryIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.source = os.path.join(self.temp_dir.name, "source.txt")
        self.destination = os.path.join(
            self.temp_dir.name, "destination.txt"
        )

        # Simulate a move that completed on disk before the app crashed.
        with open(self.destination, "w", encoding="utf-8") as file:
            file.write("Recovery integration test")

        self.conn = get_test_connection()

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS test_files (
                        file_id BIGINT GENERATED ALWAYS AS IDENTITY
                            PRIMARY KEY,
                        file_path TEXT NOT NULL
                    )
                """)
                cur.execute(
                    "INSERT INTO test_files (file_path) VALUES (%s) "
                    "RETURNING file_id",
                    (self.source,),
                )
                self.file_id = cur.fetchone()[0]

            self.conn.commit()

            self.history_id = create_movement(
                self.conn,
                self.file_id,
                self.source,
                self.destination,
            )

        except Exception:
            self.conn.rollback()
            self.conn.close()
            self.temp_dir.cleanup()
            raise

    def tearDown(self):
        if hasattr(self, "conn") and not self.conn.closed:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM movement_history WHERE history_id = %s",
                        (self.history_id,),
                    )
                    cur.execute(
                        "DELETE FROM test_files WHERE file_id = %s",
                        (self.file_id,),
                    )
                self.conn.commit()
            except Exception:
                self.conn.rollback()
            finally:
                self.conn.close()

        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    def test_recovery_updates_test_file_and_history(self):
        result = recover_pending_movements(
            self.conn,
            table_name="test_files",
        )

        self.assertEqual(result["done"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["needs_review"], 0)

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT file_path FROM test_files WHERE file_id = %s",
                (self.file_id,),
            )
            file_row = cur.fetchone()

            cur.execute(
                "SELECT status FROM movement_history WHERE history_id = %s",
                (self.history_id,),
            )
            history_row = cur.fetchone()

        self.assertEqual(file_row[0], self.destination)
        self.assertEqual(history_row[0], "DONE")


if __name__ == "__main__":
    unittest.main()
