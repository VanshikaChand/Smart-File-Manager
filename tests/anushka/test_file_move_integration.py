
import os
import tempfile
import unittest

import psycopg2

from modules.anushka.operation.file_operations import move_file


def get_test_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="smart_file_manager_test",
        user="postgres",
        password=os.environ["DB_PASSWORD"],
    )


class TestFileMoveIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.source = os.path.join(self.temp_dir.name, "source.txt")
        self.destination = os.path.join(
            self.temp_dir.name, "destination.txt"
        )

        with open(self.source, "w", encoding="utf-8") as file:
            file.write("Safe test content")

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
                    """
                    INSERT INTO test_files (file_path)
                    VALUES (%s)
                    RETURNING file_id
                    """,
                    (self.source,),
                )
                self.file_id = cur.fetchone()[0]

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            self.conn.close()
            self.temp_dir.cleanup()
            raise

    def tearDown(self):
        if hasattr(self, "conn") and not self.conn.closed:
            self.conn.rollback()
            self.conn.close()

        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    def test_move_file(self):
        result = move_file(
            self.conn,
            self.file_id,
            self.destination,
            table_name="test_files",
        )

        self.assertTrue(result, "File movement should succeed")
        self.assertFalse(os.path.exists(self.source))
        self.assertTrue(os.path.exists(self.destination))

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT file_path FROM test_files WHERE file_id = %s",
                (self.file_id,),
            )
            row = cur.fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[0], self.destination)

            cur.execute(
                """
                SELECT status, error_message
                FROM movement_history
                WHERE file_id = %s
                  AND source_path = %s
                  AND destination_path = %s
                ORDER BY history_id DESC
                LIMIT 1
                """,
                (self.file_id, self.source, self.destination),
            )
            history = cur.fetchone()

        self.assertIsNotNone(history, "Movement history must exist")
        self.assertEqual(history[0], "DONE")
        self.assertIsNone(history[1])


if __name__ == "__main__":
    unittest.main()
