
import unittest
from unittest.mock import MagicMock, patch

from modules.anushka.operation.recovery import recover_pending_movements


class TestRecovery(unittest.TestCase):

    @patch("modules.anushka.operation.recovery.update_movement")
    @patch("modules.anushka.operation.recovery.get_pending_movements")
    @patch("modules.anushka.operation.recovery.os.path.isfile")
    def test_destination_exists_source_missing(
        self, mock_isfile, mock_pending, mock_update
    ):
        conn = MagicMock()
        mock_pending.return_value = [
            (1, 10, "source.txt", "destination.txt")
        ]
        mock_isfile.side_effect = [False, True]

        result = recover_pending_movements(conn)

        self.assertEqual(result["done"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["needs_review"], 0)
        mock_update.assert_called_once_with(conn, 1, "DONE")

    @patch("modules.anushka.operation.recovery.update_movement")
    @patch("modules.anushka.operation.recovery.get_pending_movements")
    @patch("modules.anushka.operation.recovery.os.path.isfile")
    def test_source_exists_destination_missing(
        self, mock_isfile, mock_pending, mock_update
    ):
        conn = MagicMock()
        mock_pending.return_value = [
            (2, 11, "source.txt", "destination.txt")
        ]
        mock_isfile.side_effect = [True, False]

        result = recover_pending_movements(conn)

        self.assertEqual(result["done"], 0)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(result["needs_review"], 0)
        mock_update.assert_called_once_with(
            conn, 2, "FAILED", "Move did not complete"
        )

    @patch("modules.anushka.operation.recovery.get_pending_movements")
    @patch("modules.anushka.operation.recovery.os.path.isfile")
    def test_both_files_exist_needs_review(
        self, mock_isfile, mock_pending
    ):
        conn = MagicMock()
        mock_pending.return_value = [
            (3, 12, "source.txt", "destination.txt")
        ]
        mock_isfile.side_effect = [True, True]

        result = recover_pending_movements(conn)

        self.assertEqual(result["done"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["needs_review"], 1)

    @patch("modules.anushka.operation.recovery.get_pending_movements")
    @patch("modules.anushka.operation.recovery.os.path.isfile")
    def test_neither_file_exists_needs_review(
        self, mock_isfile, mock_pending
    ):
        conn = MagicMock()
        mock_pending.return_value = [
            (4, 13, "source.txt", "destination.txt")
        ]
        mock_isfile.side_effect = [False, False]

        result = recover_pending_movements(conn)

        self.assertEqual(result["done"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["needs_review"], 1)


if __name__ == "__main__":
    unittest.main()
