"""
modules/aman/recommendation_service.py
========================================
Combines file classification and storage allocation into a single advisory
recommendation record.

Responsibilities
----------------
* Calls ``classify_file`` and ``recommend_storage`` with the supplied metadata.
* Maps classification outcomes to recommendation types, actions, and priorities.
* Returns a structured dict suitable for display, logging, or insertion into the
  Recommendations table (see ``recommendations_schema.sql``).
* Never touches the filesystem beyond what the sub-functions do (which is nothing
  for classification and nothing at all for allocation).

Integration note
----------------
Duplicate detection is intentionally kept separate.  Duplicates are identified
across a *batch* of files, whereas this service generates a per-file advisory.
Once the team decides how duplicate records should be stored (shared table vs.
Aman's Recommendations table), call ``find_duplicates`` before or after this
function and append the results.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from .file_classifier import classify_file
from .allocation_recommender import recommend_storage


# ---------------------------------------------------------------------------
# Priority map by classification category
# ---------------------------------------------------------------------------
_PRIORITY_MAP: dict = {
    "Archive": "LOW",
    "Inactive": "MEDIUM",
    "Active": "LOW",   # active files rarely need action
    "Unknown": "LOW",
}

# ---------------------------------------------------------------------------
# Recommendation type constants
# ---------------------------------------------------------------------------
TYPE_ARCHIVE = "ARCHIVE"
TYPE_CLEANUP = "CLEANUP"
TYPE_STORAGE = "STORAGE"
TYPE_NO_ACTION = "NO_ACTION"
TYPE_UNKNOWN = "UNKNOWN"


def generate_recommendation(
    file_path: str,
    file_size: int,
    destinations: list,
    last_accessed: Optional[datetime] = None,
    modified_at: Optional[datetime] = None,
    file_extension: str = "",
    reference_time: Optional[datetime] = None,
) -> dict:
    """
    Generate an advisory recommendation for a single file.

    Parameters
    ----------
    file_path : str
        Path or identifier for the file.
    file_size : int
        File size in bytes (non-negative integer).
    destinations : list of dict
        Storage destinations; passed directly to ``recommend_storage``.
    last_accessed : datetime, optional
        Timezone-aware last-access timestamp.
    modified_at : datetime, optional
        Timezone-aware last-modification timestamp.
    file_extension : str, optional
        File extension (e.g. ``".pdf"``), used for destination filtering.
    reference_time : datetime, optional
        Fixed "now" for deterministic tests.

    Returns
    -------
    dict
        Recommendation record with keys:

        ``recommendation_id``   – UUID4 string (suitable as a primary key).
        ``file_path``           – normalised file path string.
        ``recommendation_type`` – one of the TYPE_* constants above.
        ``suggested_action``    – short action code (e.g. ``"REVIEW_FOR_ARCHIVING"``).
        ``destination``         – recommended destination name or ``None``.
        ``reason``              – human-readable explanation.
        ``priority``            – ``"LOW"``, ``"MEDIUM"``, or ``"HIGH"``.
        ``status``              – always ``"PENDING"`` at creation.
        ``created_at``          – ISO-8601 UTC timestamp string.
        ``classification``      – full result from ``classify_file``.
        ``allocation``          – full result from ``recommend_storage``.

    Raises
    ------
    ValueError
        Propagated from ``classify_file`` or ``recommend_storage`` for invalid
        inputs (e.g. non-integer file_size, non-timezone-aware timestamps).
    """
    created_at = datetime.now(timezone.utc).isoformat()

    # --- Classify the file ----------------------------------------------------
    classification = classify_file(
        file_path=file_path,
        last_accessed=last_accessed,
        modified_at=modified_at,
        reference_time=reference_time,
    )
    category: str = classification["category"]

    # --- Get storage recommendation -------------------------------------------
    allocation = recommend_storage(
        file_size=file_size,
        destinations=destinations,
        file_extension=file_extension,
    )
    destination: Optional[str] = allocation.get("destination")

    # --- Build the advisory record --------------------------------------------
    if category == "Archive":
        rec_type = TYPE_ARCHIVE
        action = "REVIEW_FOR_ARCHIVING"
        reason = (
            f"{classification['reason']}  "
            f"Consider archiving this file to free up primary storage."
        )
        priority = "LOW"

    elif category == "Inactive":
        rec_type = TYPE_CLEANUP
        action = "REVIEW_FOR_CLEANUP"
        reason = (
            f"{classification['reason']}  "
            f"File has been inactive; consider cleaning up or archiving."
        )
        priority = "MEDIUM"

    elif category == "Active":
        if allocation["recommended"]:
            rec_type = TYPE_STORAGE
            action = "CONSIDER_MIGRATION"
            reason = (
                f"File is active but a better-utilised destination is available: "
                f"{allocation['reason']}"
            )
            priority = "LOW"
        else:
            rec_type = TYPE_NO_ACTION
            action = "NO_ACTION"
            reason = "File is active and no storage migration is needed at this time."
            priority = "LOW"

    else:  # "Unknown"
        rec_type = TYPE_UNKNOWN
        action = "MANUAL_REVIEW"
        reason = (
            f"{classification.get('reason', 'Classification could not be determined.')}  "
            f"Manual review is recommended."
        )
        priority = "LOW"

    return {
        "recommendation_id": str(uuid4()),
        "file_path": classification["file_path"],
        "recommendation_type": rec_type,
        "suggested_action": action,
        "destination": destination,
        "reason": reason,
        "priority": priority,
        "status": "PENDING",
        "created_at": created_at,
        # Sub-results for debugging / display
        "classification": classification,
        "allocation": allocation,
    }
