"""
modules/aman/duplicate_detector.py
====================================
Detects duplicate files using a two-stage approach:

  Stage 1 – Group files by size.  Files with unique sizes cannot be identical.
  Stage 2 – Within each size-group, compute SHA-256 hashes using 1 MB streaming
             reads to avoid loading large files into RAM.  Files that share the
             same hash are reported as duplicates.

Design decisions
----------------
* Only *content* equality is tested.  Same name or same extension alone does not
  make two files duplicates.
* Files that are missing, non-regular (symlinks, directories), or unreadable are
  reported in the ``"errors"`` list rather than silently skipped.
* Empty files all share the same SHA-256 hash; they are grouped as duplicates if
  more than one zero-byte file is provided.
* The function never modifies, moves, or deletes any file.
"""

import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Union


_CHUNK_SIZE: int = 1024 * 1024  # 1 MiB


def calculate_sha256(file_path: Union[str, Path]) -> str:
    """
    Compute the SHA-256 hex-digest of a file using streaming reads.

    Parameters
    ----------
    file_path : str or Path
        Path to the file to hash.

    Returns
    -------
    str
        Lowercase hexadecimal SHA-256 digest.

    Raises
    ------
    OSError
        If the file cannot be opened or read.
    IsADirectoryError
        If the path points to a directory rather than a file.
    """
    digest = hashlib.sha256()
    with open(file_path, "rb") as fh:
        while chunk := fh.read(_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(paths: list) -> dict:
    """
    Identify groups of files whose contents are identical.

    Parameters
    ----------
    paths : list of str or Path
        Candidate file paths to examine.

    Returns
    -------
    dict with two keys:

    ``"duplicates"``
        A list of groups.  Each group is a dict::

            {
                "hash": "<sha256-hex>",
                "size_bytes": <int>,
                "paths": ["<path1>", "<path2>", ...]
            }

        Only groups with **two or more** paths are included.

    ``"errors"``
        A list of dicts describing files that could not be processed::

            {
                "path": "<path>",
                "error": "<human-readable reason>"
            }

    Notes
    -----
    The caller should treat the result as advisory.  Do not delete or move
    any file based solely on this output without independent verification.
    """
    size_groups: dict = defaultdict(list)   # size_bytes -> [path_str, ...]
    errors: list = []

    # ------------------------------------------------------------------ Stage 1
    for raw_path in paths:
        path = Path(raw_path)
        try:
            if not path.exists():
                errors.append({"path": str(path), "error": "File does not exist."})
                continue
            if not path.is_file():
                errors.append(
                    {"path": str(path), "error": "Path is not a regular file."}
                )
                continue
            size = path.stat().st_size
            size_groups[size].append(str(path))
        except PermissionError:
            errors.append(
                {"path": str(path), "error": "Permission denied reading file metadata."}
            )
        except OSError as exc:
            errors.append({"path": str(path), "error": f"OS error: {exc}"})

    # ------------------------------------------------------------------ Stage 2
    duplicate_groups: list = []

    for size_bytes, group_paths in size_groups.items():
        if len(group_paths) < 2:
            # Unique size → cannot have a duplicate in this batch.
            continue

        hash_groups: dict = defaultdict(list)  # sha256 -> [path, ...]

        for path_str in group_paths:
            try:
                sha256 = calculate_sha256(path_str)
                hash_groups[sha256].append(path_str)
            except PermissionError:
                errors.append(
                    {"path": path_str, "error": "Permission denied reading file contents."}
                )
            except FileNotFoundError:
                errors.append(
                    {
                        "path": path_str,
                        "error": "File disappeared between size-check and hash.",
                    }
                )
            except OSError as exc:
                errors.append({"path": path_str, "error": f"OS error during hashing: {exc}"})

        for sha256_hex, dup_paths in hash_groups.items():
            if len(dup_paths) >= 2:
                duplicate_groups.append(
                    {
                        "hash": sha256_hex,
                        "size_bytes": size_bytes,
                        "paths": dup_paths,
                    }
                )

    return {"duplicates": duplicate_groups, "errors": errors}
