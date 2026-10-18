"""
modules/aman/file_classifier.py
================================
Classifies files into three categories based on activity timestamps:

  Active   – file was accessed or modified within the last `inactive_after_days` days (default: 30).
  Inactive – last activity is between 30 and 180 days ago (default thresholds).
  Archive  – last activity is older than `archive_after_days` days (default: 180).

Classification policy
---------------------
* ``last_accessed`` is preferred because it reflects *reading* activity, not just
  modification.  On some operating systems (e.g. Windows with default settings,
  Linux with ``noatime``) the access timestamp may be disabled or unreliable.
  When ``last_accessed`` is not supplied, ``modified_at`` is used as a fallback.
* If neither timestamp is available the result is ``"Unknown"``.
* Future timestamps (activity_time > reference_time) are returned as ``"Unknown"``
  rather than raising, so callers receive a consistent dict.
* All datetime arguments must be timezone-aware (``tzinfo`` set).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Default thresholds (days)
# ---------------------------------------------------------------------------
DEFAULT_INACTIVE_AFTER_DAYS: int = 30
DEFAULT_ARCHIVE_AFTER_DAYS: int = 180


def classify_file(
    file_path: str,
    last_accessed: Optional[datetime] = None,
    modified_at: Optional[datetime] = None,
    inactive_after_days: int = DEFAULT_INACTIVE_AFTER_DAYS,
    archive_after_days: int = DEFAULT_ARCHIVE_AFTER_DAYS,
    reference_time: Optional[datetime] = None,
) -> dict:
    """
    Classify a single file based on its activity timestamps.

    Parameters
    ----------
    file_path : str
        Path to the file (used only as an identifier; the file is not opened).
    last_accessed : datetime, optional
        Most recent access timestamp (timezone-aware).  Preferred activity signal.
    modified_at : datetime, optional
        Most recent modification timestamp (timezone-aware).  Used as a fallback
        when ``last_accessed`` is not available.
    inactive_after_days : int
        Files not accessed within this many days are classified as *Inactive*.
        Must be >= 0.  Default: 30.
    archive_after_days : int
        Files not accessed within this many days are classified as *Archive*.
        Must be > ``inactive_after_days``.  Default: 180.
    reference_time : datetime, optional
        The "current time" used for age calculations.  Defaults to
        ``datetime.now(timezone.utc)``.  Must be timezone-aware.
        Pass a fixed value in tests to make results deterministic.

    Returns
    -------
    dict
        Keys: ``file_path``, ``category``, ``age_days`` (when calculable),
        ``reason``.
        ``category`` is one of: ``"Active"``, ``"Inactive"``, ``"Archive"``,
        ``"Unknown"``.

    Raises
    ------
    ValueError
        If thresholds are invalid or if a supplied datetime is not timezone-aware.
    """
    # --- Validate thresholds ---------------------------------------------------
    if not isinstance(inactive_after_days, int) or isinstance(inactive_after_days, bool):
        raise ValueError("inactive_after_days must be an integer.")
    if not isinstance(archive_after_days, int) or isinstance(archive_after_days, bool):
        raise ValueError("archive_after_days must be an integer.")
    if inactive_after_days < 0:
        raise ValueError("inactive_after_days must be >= 0.")
    if archive_after_days <= inactive_after_days:
        raise ValueError(
            "archive_after_days must be strictly greater than inactive_after_days."
        )

    # --- Reference time -------------------------------------------------------
    now: datetime = reference_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("reference_time must be timezone-aware.")

    # --- Choose best activity timestamp ---------------------------------------
    # Prefer last_accessed; fall back to modified_at.
    activity_time: Optional[datetime] = last_accessed or modified_at

    if activity_time is None:
        return {
            "file_path": str(Path(file_path)),
            "category": "Unknown",
            "reason": "No usable activity timestamp is available.",
        }

    if activity_time.tzinfo is None:
        raise ValueError(
            "Activity timestamps (last_accessed, modified_at) must be timezone-aware."
        )

    # --- Calculate age --------------------------------------------------------
    age_seconds: float = (now - activity_time).total_seconds()
    age_days: float = age_seconds / 86_400

    if age_days < 0:
        return {
            "file_path": str(Path(file_path)),
            "category": "Unknown",
            "reason": "Activity timestamp is in the future.",
        }

    # --- Classify -------------------------------------------------------------
    if age_days <= inactive_after_days:
        category = "Active"
    elif age_days <= archive_after_days:
        category = "Inactive"
    else:
        category = "Archive"

    return {
        "file_path": str(Path(file_path)),
        "category": category,
        "age_days": round(age_days, 2),
        "reason": f"Last reliable activity was {age_days:.1f} days ago.",
    }
