
import unittest
from unittest.mock import patch, Mock

from modules.udit.drive_monitor import get_drive_info


class TestDriveMonitor(unittest.TestCase):

    @patch("modules.udit.drive_monitor.psutil.disk_usage")
    @patch("modules.udit.drive_monitor.psutil.disk_partitions")
    def test_drive_detection(self, mock_partitions, mock_usage):
        partition = Mock()
        partition.mountpoint = "C:\\"
        partition.fstype = "NTFS"

        mock_partitions.return_value = [partition]

        usage = Mock()
        usage.total = 1000
        usage.used = 600
        usage.free = 400
        usage.percent = 60.0

        mock_usage.return_value = usage

        result = get_drive_info()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["filesystem"], "NTFS")
        self.assertEqual(result[0]["total_bytes"], 1000)
        self.assertEqual(result[0]["used_bytes"], 600)
        self.assertEqual(result[0]["free_bytes"], 400)
        self.assertEqual(result[0]["utilization_percent"], 60.0)

    @patch("modules.udit.drive_monitor.psutil.disk_partitions")
    def test_no_drives_detected(self, mock_partitions):
        mock_partitions.return_value = []

        result = get_drive_info()

        self.assertEqual(result, [])

    @patch("modules.udit.drive_monitor.psutil.disk_usage")
    @patch("modules.udit.drive_monitor.psutil.disk_partitions")
    def test_permission_error(self, mock_partitions, mock_usage):
        partition = Mock()
        partition.mountpoint = "Z:\\"
        partition.fstype = "NTFS"

        mock_partitions.return_value = [partition]
        mock_usage.side_effect = PermissionError("Access denied")

        result = get_drive_info()

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
