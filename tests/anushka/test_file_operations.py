import os
import tempfile
import unittest

from modules.anushka.operation.safe_move import (
    safe_move,
    calculate_checksum,
)


class TestSafeMove(unittest.TestCase):

    def test_successful_move(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = os.path.join(temp_dir, "sample.txt")
            destination = os.path.join(temp_dir, "moved.txt")

            with open(source, "w", encoding="utf-8") as file:
                file.write("Test content")

            original_checksum = calculate_checksum(source)

            result = safe_move(source, destination)

            self.assertTrue(result)
            self.assertFalse(os.path.exists(source))
            self.assertTrue(os.path.exists(destination))
            self.assertEqual(
                calculate_checksum(destination),
                original_checksum,
            )

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = os.path.join(temp_dir, "source.txt")
            destination = os.path.join(temp_dir, "destination.txt")

            with open(source, "w", encoding="utf-8") as file:
                file.write("Original source")

            with open(destination, "w", encoding="utf-8") as file:
                file.write("Keep this content")

            result = safe_move(source, destination)

            self.assertFalse(result)
            self.assertTrue(os.path.exists(source))

            with open(destination, encoding="utf-8") as file:
                self.assertEqual(file.read(), "Keep this content")


if __name__ == "__main__":
    unittest.main()
