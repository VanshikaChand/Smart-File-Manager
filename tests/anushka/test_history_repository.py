import unittest
from unittest.mock import MagicMock

from modules.anushka.operation.history_repository import (
    create_movement,
    update_movement,
    get_pending_movements,
)


class TestHistoryRepository(unittest.TestCase):

    def setUp(self):
        self.conn = MagicMock()
        self.cursor = self.conn.cursor.return_value.__enter__.return_value

    def test_create_movement(self):
        self.cursor.fetchone.return_value = (10,)

        result = create_movement(
            self.conn, 1, r"C:\temp\source.txt", r"C:\temp\destination.txt"
        )

        self.assertEqual(result, 10)
        self.cursor.execute.assert_called_once()
        self.conn.commit.assert_called_once()

    def test_update_movement_rejects_invalid_status(self):
        with self.assertRaises(ValueError):
            update_movement(self.conn, 10, "INVALID")

        self.conn.cursor.assert_not_called()

    def test_update_movement_commits(self):
        update_movement(self.conn, 10, "DONE")

        self.cursor.execute.assert_called_once()
        self.conn.commit.assert_called_once()

    def test_get_pending_movements(self):
        expected = [(10, 1, r"C:\temp\a.txt", r"C:\temp\b.txt")]
        self.cursor.fetchall.return_value = expected

        result = get_pending_movements(self.conn)

        self.assertEqual(result, expected)
        self.cursor.execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()