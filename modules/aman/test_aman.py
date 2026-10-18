"""
modules/aman/test_aman.py
==========================
Unit tests for Aman's Smart File Manager module.

Run from the project root:
    python -m pytest modules/aman/test_aman.py -v
  or (stdlib only):
    python -m unittest modules/aman/test_aman.py -v

All tests use:
  * A fixed reference_time so results are deterministic.
  * tempfile.TemporaryDirectory() for real filesystem tests.
  * Synthetic in-memory content rather than real user files.
"""

import hashlib
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Allow running from either the project root or the module directory.
# ---------------------------------------------------------------------------
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # project root

from modules.aman.file_classifier import classify_file
from modules.aman.duplicate_detector import calculate_sha256, find_duplicates
from modules.aman.allocation_recommender import recommend_storage
from modules.aman.recommendation_service import generate_recommendation


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------
REF_TIME = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

DESTINATIONS = [
    {"name": "Drive_A", "total_capacity": 500_000_000, "used_capacity": 100_000_000},
    {"name": "Drive_B", "total_capacity": 1_000_000_000, "used_capacity": 900_000_000},
]


def _ts(days_ago: float) -> datetime:
    """Return a timezone-aware datetime that is ``days_ago`` days before REF_TIME."""
    return REF_TIME - timedelta(days=days_ago)


# ===========================================================================
# File Classifier Tests
# ===========================================================================
class TestClassifyFile(unittest.TestCase):

    # --- Category boundaries ---
    def test_active_file(self):
        result = classify_file(
            "/data/file.txt",
            modified_at=_ts(10),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Active")

    def test_active_boundary_exactly_at_threshold(self):
        """A file accessed exactly 30 days ago sits on the Active/Inactive boundary → Active."""
        result = classify_file(
            "/data/file.txt",
            last_accessed=_ts(30),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Active")

    def test_inactive_file(self):
        result = classify_file(
            "/data/old.txt",
            last_accessed=_ts(60),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Inactive")

    def test_archive_file(self):
        result = classify_file(
            "/data/ancient.log",
            last_accessed=_ts(200),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Archive")

    def test_archive_boundary_exactly_at_threshold(self):
        """A file not accessed for exactly 180 days → Inactive (boundary inclusive on upper bound)."""
        result = classify_file(
            "/data/file.txt",
            last_accessed=_ts(180),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Inactive")

    def test_just_over_archive_threshold(self):
        result = classify_file(
            "/data/file.txt",
            last_accessed=_ts(181),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Archive")

    # --- Fallback to modified_at ---
    def test_fallback_to_modified_at_when_no_access_time(self):
        result = classify_file(
            "/data/file.txt",
            modified_at=_ts(100),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Inactive")

    # --- Missing timestamps ---
    def test_no_timestamps_returns_unknown(self):
        result = classify_file("/data/ghost.dat", reference_time=REF_TIME)
        self.assertEqual(result["category"], "Unknown")
        self.assertIn("timestamp", result["reason"].lower())

    # --- Future timestamp ---
    def test_future_timestamp_returns_unknown(self):
        future = REF_TIME + timedelta(days=1)
        result = classify_file(
            "/data/file.txt",
            last_accessed=future,
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Unknown")
        self.assertIn("future", result["reason"].lower())

    # --- Custom thresholds ---
    def test_custom_thresholds(self):
        result = classify_file(
            "/data/file.txt",
            last_accessed=_ts(5),
            inactive_after_days=3,
            archive_after_days=10,
            reference_time=REF_TIME,
        )
        self.assertEqual(result["category"], "Inactive")

    # --- Naive datetime raises ---
    def test_naive_datetime_raises(self):
        naive = datetime(2025, 1, 1)  # no tzinfo
        with self.assertRaises(ValueError):
            classify_file("/data/file.txt", last_accessed=naive, reference_time=REF_TIME)

    # --- Invalid thresholds ---
    def test_invalid_thresholds_raise(self):
        with self.assertRaises(ValueError):
            classify_file(
                "/f",
                modified_at=_ts(1),
                inactive_after_days=180,
                archive_after_days=30,  # archive <= inactive → invalid
                reference_time=REF_TIME,
            )

    # --- Result keys ---
    def test_result_contains_expected_keys(self):
        result = classify_file(
            "/data/file.txt",
            last_accessed=_ts(50),
            reference_time=REF_TIME,
        )
        for key in ("file_path", "category", "age_days", "reason"):
            self.assertIn(key, result)


# ===========================================================================
# Duplicate Detector Tests
# ===========================================================================
class TestDuplicateDetector(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name: str, content: bytes) -> str:
        p = self.tmp / name
        p.write_bytes(content)
        return str(p)

    # --- SHA-256 ---
    def test_sha256_known_value(self):
        p = self._write("known.txt", b"hello world")
        expected = hashlib.sha256(b"hello world").hexdigest()
        self.assertEqual(calculate_sha256(p), expected)

    def test_sha256_empty_file(self):
        p = self._write("empty.bin", b"")
        expected = hashlib.sha256(b"").hexdigest()
        self.assertEqual(calculate_sha256(p), expected)

    # --- Identical files ---
    def test_identical_files_detected(self):
        p1 = self._write("a.bin", b"duplicate content")
        p2 = self._write("b.bin", b"duplicate content")
        result = find_duplicates([p1, p2])
        self.assertEqual(len(result["duplicates"]), 1)
        self.assertIn(p1, result["duplicates"][0]["paths"])
        self.assertIn(p2, result["duplicates"][0]["paths"])
        self.assertEqual(result["errors"], [])

    # --- Non-identical files ---
    def test_different_files_not_duplicates(self):
        p1 = self._write("x.bin", b"aaa")
        p2 = self._write("y.bin", b"bbb")
        result = find_duplicates([p1, p2])
        self.assertEqual(result["duplicates"], [])
        self.assertEqual(result["errors"], [])

    # --- Same name, different content ---
    def test_same_size_different_content(self):
        # "abc" and "xyz" are the same byte length → pass size filter, fail hash check
        p1 = self._write("f1.txt", b"abc")
        p2 = self._write("f2.txt", b"xyz")
        result = find_duplicates([p1, p2])
        self.assertEqual(result["duplicates"], [])

    # --- Empty files ---
    def test_multiple_empty_files_are_duplicates(self):
        p1 = self._write("e1.txt", b"")
        p2 = self._write("e2.txt", b"")
        result = find_duplicates([p1, p2])
        self.assertEqual(len(result["duplicates"]), 1)

    # --- Missing file ---
    def test_missing_file_reported_as_error(self):
        missing = str(self.tmp / "does_not_exist.txt")
        result = find_duplicates([missing])
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("does not exist", result["errors"][0]["error"])

    # --- Directory path ---
    def test_directory_path_reported_as_error(self):
        result = find_duplicates([str(self.tmp)])
        self.assertEqual(len(result["errors"]), 1)

    # --- Empty input ---
    def test_empty_path_list(self):
        result = find_duplicates([])
        self.assertEqual(result["duplicates"], [])
        self.assertEqual(result["errors"], [])

    # --- Three-way duplicate group ---
    def test_three_identical_files_in_one_group(self):
        content = b"shared content"
        paths = [self._write(f"dup{i}.txt", content) for i in range(3)]
        result = find_duplicates(paths)
        self.assertEqual(len(result["duplicates"]), 1)
        self.assertEqual(len(result["duplicates"][0]["paths"]), 3)

    # --- Hash stored in result ---
    def test_duplicate_group_contains_hash_and_size(self):
        p1 = self._write("a.bin", b"data")
        p2 = self._write("b.bin", b"data")
        result = find_duplicates([p1, p2])
        group = result["duplicates"][0]
        self.assertIn("hash", group)
        self.assertIn("size_bytes", group)
        self.assertEqual(group["size_bytes"], len(b"data"))


# ===========================================================================
# Storage Allocation Recommender Tests
# ===========================================================================
class TestRecommendStorage(unittest.TestCase):

    def _dests(self):
        return [
            {"name": "Drive_A", "total_capacity": 1_000, "used_capacity": 200},
            {"name": "Drive_B", "total_capacity": 1_000, "used_capacity": 800},
        ]

    # --- Basic recommendation ---
    def test_recommends_when_space_available(self):
        result = recommend_storage(file_size=100, destinations=self._dests())
        self.assertTrue(result["recommended"])
        self.assertIsNotNone(result["destination"])

    # --- Prefers lower utilisation ---
    def test_prefers_lower_utilisation(self):
        result = recommend_storage(file_size=100, destinations=self._dests())
        # Drive_A: projected (200+100)/1000 = 30%.  Drive_B: (800+100)/1000 = 90%.
        self.assertEqual(result["destination"], "Drive_A")

    # --- Not enough space ---
    def test_no_eligible_destination_when_file_too_large(self):
        # Drive_A: total=1000, used=200 → free=800
        # Drive_B: total=1000, used=800 → free=200
        # file_size=900 exceeds Drive_A's 800 free bytes → no destination fits.
        result = recommend_storage(file_size=900, destinations=self._dests())
        self.assertFalse(result["recommended"])
        self.assertIsNone(result["destination"])

    def test_recommends_drive_a_when_file_fits(self):
        # file_size=700 fits Drive_A (800 free) but not Drive_B (200 free).
        result = recommend_storage(file_size=700, destinations=self._dests())
        self.assertTrue(result["recommended"])
        self.assertEqual(result["destination"], "Drive_A")

    def test_no_eligible_destination_fully_full(self):
        dests = [{"name": "Full", "total_capacity": 100, "used_capacity": 100}]
        result = recommend_storage(file_size=1, destinations=dests)
        self.assertFalse(result["recommended"])
        self.assertIsNone(result["destination"])

    # --- File-type restriction ---
    def test_extension_restriction_respected(self):
        dests = [
            {
                "name": "PDFOnly",
                "total_capacity": 1_000,
                "used_capacity": 0,
                "allowed_extensions": [".pdf"],
            },
            {"name": "General", "total_capacity": 1_000, "used_capacity": 500},
        ]
        result = recommend_storage(
            file_size=100, destinations=dests, file_extension=".mp4"
        )
        # PDFOnly should be skipped; General should be chosen.
        self.assertTrue(result["recommended"])
        self.assertEqual(result["destination"], "General")

    def test_extension_restriction_blocks_all(self):
        dests = [
            {
                "name": "PDFOnly",
                "total_capacity": 1_000,
                "used_capacity": 0,
                "allowed_extensions": [".pdf"],
            }
        ]
        result = recommend_storage(
            file_size=100, destinations=dests, file_extension=".exe"
        )
        self.assertFalse(result["recommended"])

    # --- Invalid inputs ---
    def test_negative_file_size_raises(self):
        with self.assertRaises(ValueError):
            recommend_storage(file_size=-1, destinations=self._dests())

    def test_bool_file_size_raises(self):
        with self.assertRaises(ValueError):
            recommend_storage(file_size=True, destinations=self._dests())

    def test_invalid_capacity_values_skipped(self):
        bad_dest = [{"name": "Bad", "total_capacity": "not_int", "used_capacity": 0}]
        result = recommend_storage(file_size=10, destinations=bad_dest)
        self.assertFalse(result["recommended"])

    def test_empty_destinations_returns_no_recommendation(self):
        result = recommend_storage(file_size=100, destinations=[])
        self.assertFalse(result["recommended"])

    def test_zero_file_size_always_fits(self):
        result = recommend_storage(file_size=0, destinations=self._dests())
        self.assertTrue(result["recommended"])

    def test_projected_utilisation_in_result(self):
        result = recommend_storage(file_size=100, destinations=self._dests())
        self.assertIn("projected_utilisation_pct", result)
        self.assertIsInstance(result["projected_utilisation_pct"], float)


# ===========================================================================
# Recommendation Service Tests
# ===========================================================================
class TestGenerateRecommendation(unittest.TestCase):

    _DESTS = [
        {"name": "Drive_X", "total_capacity": 10_000, "used_capacity": 1_000},
    ]

    # --- Archive recommendation ---
    def test_archive_file_generates_archive_recommendation(self):
        result = generate_recommendation(
            file_path="/old/report.pdf",
            file_size=500,
            destinations=self._DESTS,
            last_accessed=_ts(200),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["recommendation_type"], "ARCHIVE")
        self.assertEqual(result["status"], "PENDING")
        self.assertIn("recommendation_id", result)

    # --- Inactive recommendation ---
    def test_inactive_file_generates_cleanup_recommendation(self):
        result = generate_recommendation(
            file_path="/old/file.txt",
            file_size=100,
            destinations=self._DESTS,
            last_accessed=_ts(60),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["recommendation_type"], "CLEANUP")
        self.assertEqual(result["priority"], "MEDIUM")

    # --- Active file with available destination ---
    def test_active_file_with_destination_gets_storage_recommendation(self):
        result = generate_recommendation(
            file_path="/active/doc.txt",
            file_size=100,
            destinations=self._DESTS,
            last_accessed=_ts(5),
            reference_time=REF_TIME,
        )
        self.assertEqual(result["recommendation_type"], "STORAGE")

    # --- Unknown classification ---
    def test_unknown_classification_generates_manual_review(self):
        result = generate_recommendation(
            file_path="/unknown/file.dat",
            file_size=100,
            destinations=self._DESTS,
            # No timestamps supplied
            reference_time=REF_TIME,
        )
        self.assertEqual(result["recommendation_type"], "UNKNOWN")
        self.assertEqual(result["suggested_action"], "MANUAL_REVIEW")

    # --- Result structure ---
    def test_result_has_all_required_keys(self):
        result = generate_recommendation(
            file_path="/f.txt",
            file_size=0,
            destinations=self._DESTS,
            modified_at=_ts(10),
            reference_time=REF_TIME,
        )
        required_keys = {
            "recommendation_id",
            "file_path",
            "recommendation_type",
            "suggested_action",
            "destination",
            "reason",
            "priority",
            "status",
            "created_at",
            "classification",
            "allocation",
        }
        self.assertTrue(required_keys.issubset(result.keys()))

    # --- UUID uniqueness ---
    def test_each_call_generates_unique_id(self):
        ids = {
            generate_recommendation(
                file_path=f"/f{i}.txt",
                file_size=10,
                destinations=self._DESTS,
                modified_at=_ts(5),
                reference_time=REF_TIME,
            )["recommendation_id"]
            for i in range(10)
        }
        self.assertEqual(len(ids), 10)

    # --- Invalid inputs propagate ---
    def test_invalid_file_size_raises(self):
        with self.assertRaises((ValueError, TypeError)):
            generate_recommendation(
                file_path="/f.txt",
                file_size=-1,
                destinations=self._DESTS,
                modified_at=_ts(5),
                reference_time=REF_TIME,
            )


# ===========================================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)
