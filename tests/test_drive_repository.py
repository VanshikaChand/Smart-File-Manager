
import unittest
from unittest.mock import patch, MagicMock

from modules.udit.drive_repository import save_drive_scan


class TestDriveRepository(unittest.TestCase):

    @patch("modules.udit.drive_repository.get_connection")
    def test_save_drive_scan(self, mock_get_connection):
        conn = MagicMock()
        cursor = MagicMock()

        mock_get_connection.return_value = conn
        conn.cursor.return_value.__enter__.return_value = cursor

        # First fetchone(): scan_id; second: drive_id
        cursor.fetchone.side_effect = [(3,), (2,)]

        drives = [{
            "mount_point": "C:\\",
            "filesystem": "NTFS",
            "total_bytes": 1000,
            "used_bytes": 600,
            "free_bytes": 400,
            "utilization_percent": 60.0,
        }]

        scan_id = save_drive_scan(drives)

        self.assertEqual(scan_id, 3)
        self.assertTrue(cursor.execute.called)
        conn.close.assert_called_once()

    @patch("modules.udit.drive_repository.get_connection")
    def test_empty_drive_list(self, mock_get_connection):
        conn = MagicMock()
        cursor = MagicMock()

        mock_get_connection.return_value = conn
        conn.cursor.return_value.__enter__.return_value = cursor
        cursor.fetchone.return_value = (4,)

        scan_id = save_drive_scan([])

        self.assertEqual(scan_id, 4)
        conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
