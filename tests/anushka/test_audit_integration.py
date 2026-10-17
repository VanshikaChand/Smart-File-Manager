
import os
import unittest

import psycopg2


def get_test_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="smart_file_manager_test",
        user="postgres",
        password=os.environ["DB_PASSWORD"],
    )


class TestAuditIntegration(unittest.TestCase):

    def setUp(self):
        self.conn = get_test_connection()
        self.file_id = None
        self.old_path = "audit_auto_test_old.txt"
        self.new_path = "audit_auto_test_new.txt"

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO test_files (file_path)
                    VALUES (%s)
                    RETURNING file_id
                    """,
                    (self.old_path,),
                )
                self.file_id = cur.fetchone()[0]

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            self.conn.close()
            raise

    def tearDown(self):
        if not self.conn.closed:
            try:
                with self.conn.cursor() as cur:
                    if self.file_id is not None:
                        cur.execute(
                            "DELETE FROM file_audit_log WHERE file_id = %s",
                            (self.file_id,),
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

    def test_path_update_creates_audit_entry(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE test_files
                SET file_path = %s
                WHERE file_id = %s
                """,
                (self.new_path, self.file_id),
            )

            cur.execute(
                """
                SELECT old_path, new_path
                FROM file_audit_log
                WHERE file_id = %s
                ORDER BY audit_id DESC
                LIMIT 1
                """,
                (self.file_id,),
            )
            audit_row = cur.fetchone()

        self.conn.commit()

        self.assertIsNotNone(
            audit_row,
            "Updating file_path should create an audit entry",
        )
        self.assertEqual(audit_row[0], self.old_path)
        self.assertEqual(audit_row[1], self.new_path)


if __name__ == "__main__":
    unittest.main()
