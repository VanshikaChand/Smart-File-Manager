"""
modules/aman/allocation_recommender.py
========================================
Recommends a storage destination for a file based on:

  1. Available free space  – the destination must have at least ``file_size``
     bytes free after the notional placement.
  2. File-type restriction – if a destination declares ``allowed_extensions``,
     only files whose extension appears in that list are eligible.
  3. Selection policy     – among eligible destinations, the one with the lowest
     **projected** utilisation (used+file_size)/total is preferred, so space is
     spread evenly.

This module is purely advisory.  It never moves, copies, or deletes any file.
"""

from typing import Optional


def recommend_storage(
    file_size: int,
    destinations: list,
    file_extension: str = "",
) -> dict:
    """
    Recommend an eligible storage destination for a file.

    Parameters
    ----------
    file_size : int
        Size of the file in bytes.  Must be a non-negative integer.
    destinations : list of dict
        Each dict describes one storage location and must contain:

        ``name``          (str)  – human-readable identifier.
        ``total_capacity`` (int) – total space in bytes (must be > 0).
        ``used_capacity``  (int) – space already occupied in bytes
                                   (0 <= used_capacity <= total_capacity).

        Optional key:
        ``allowed_extensions`` (list of str) – e.g. ``[".pdf", ".docx"]``.
        When omitted, all file types are accepted.

    file_extension : str, optional
        Extension of the file being placed, e.g. ``".pdf"``.  Leading dot is
        normalised automatically.  Default: ``""`` (no extension).

    Returns
    -------
    dict
        On success::

            {
                "recommended": True,
                "destination": "<name>",
                "free_bytes_before": <int>,
                "projected_utilisation_pct": <float>,
                "reason": "<explanation>"
            }

        On failure::

            {
                "recommended": False,
                "destination": None,
                "reason": "<explanation>"
            }

    Raises
    ------
    ValueError
        If ``file_size`` is not a non-negative integer.
    TypeError
        If ``destinations`` is not a list.
    """
    # --- Input validation -----------------------------------------------------
    if not isinstance(file_size, int) or isinstance(file_size, bool):
        raise ValueError("file_size must be a non-negative integer.")
    if file_size < 0:
        raise ValueError("file_size cannot be negative.")
    if not isinstance(destinations, list):
        raise TypeError("destinations must be a list of dicts.")

    # Normalise file extension (ensure leading dot, lowercase).
    ext = file_extension.strip().lower()
    if ext and not ext.startswith("."):
        ext = "." + ext

    # --- Evaluate candidates --------------------------------------------------
    candidates: list = []
    skipped_reasons: list = []

    for drive in destinations:
        name = drive.get("name", "<unnamed>")
        total = drive.get("total_capacity")
        used = drive.get("used_capacity")

        # Validate numeric fields.
        if (
            not isinstance(total, int)
            or isinstance(total, bool)
            or not isinstance(used, int)
            or isinstance(used, bool)
        ):
            skipped_reasons.append(f"'{name}': invalid or missing capacity values.")
            continue

        if total <= 0:
            skipped_reasons.append(f"'{name}': total_capacity must be > 0.")
            continue
        if used < 0 or used > total:
            skipped_reasons.append(
                f"'{name}': used_capacity ({used}) is out of range [0, {total}]."
            )
            continue

        free = total - used

        # Check file-type restriction.
        allowed: Optional[list] = drive.get("allowed_extensions")
        if allowed is not None:
            normalised_allowed = [
                (e if e.startswith(".") else "." + e).lower() for e in allowed
            ]
            if ext and ext not in normalised_allowed:
                skipped_reasons.append(
                    f"'{name}': extension '{ext}' not in allowed list {normalised_allowed}."
                )
                continue

        # Check free-space requirement.
        if free < file_size:
            skipped_reasons.append(
                f"'{name}': only {free:,} bytes free; need {file_size:,} bytes."
            )
            continue

        projected_used = used + file_size
        projected_util = projected_used / total  # 0.0 – 1.0

        candidates.append(
            {
                "name": name,
                "free_bytes_before": free,
                "projected_utilisation": projected_util,
                "total_capacity": total,
            }
        )

    # --- Select best candidate ------------------------------------------------
    if not candidates:
        reason_detail = (
            "; ".join(skipped_reasons) if skipped_reasons else "No destinations provided."
        )
        return {
            "recommended": False,
            "destination": None,
            "reason": f"No eligible destination found. Details: {reason_detail}",
        }

    # Prefer lowest projected utilisation (most proportionally free after placement).
    best = min(candidates, key=lambda c: c["projected_utilisation"])

    return {
        "recommended": True,
        "destination": best["name"],
        "free_bytes_before": best["free_bytes_before"],
        "projected_utilisation_pct": round(best["projected_utilisation"] * 100, 2),
        "reason": (
            f"'{best['name']}' has {best['free_bytes_before']:,} bytes free and will reach "
            f"{best['projected_utilisation'] * 100:.1f}% utilisation after placement — "
            f"the lowest projected utilisation among eligible destinations."
        ),
    }
