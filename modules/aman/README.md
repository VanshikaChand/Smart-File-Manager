# Aman's Module — Smart File Manager

## Overview
This module implements three OS-layer components and one DBMS integration layer for the **Smart File Manager** college project:

| Component | File | Purpose |
|---|---|---|
| File Classifier | `file_classifier.py` | Categorises files as Active / Inactive / Archive |
| Duplicate Detector | `duplicate_detector.py` | Finds identical files via SHA-256 |
| Allocation Recommender | `allocation_recommender.py` | Suggests the best storage destination |
| Recommendation Service | `recommendation_service.py` | Combines the above into one advisory record |
| DB Schema | `recommendations_schema.sql` | PostgreSQL table + indexes |
| DB Queries | `recommendation_queries.sql` | Eight reference SQL statements |

---

## Classification Policy

### Default thresholds

| Threshold | Default | Meaning |
|---|---|---|
| `inactive_after_days` | 30 | Files not accessed within 30 days are **Inactive** |
| `archive_after_days` | 180 | Files not accessed within 180 days are **Archive** |

### Timestamp preference

1. **`last_accessed`** is used when available. It captures *reading* activity, not just modification.
2. **`modified_at`** is the fallback when `last_accessed` is not supplied.
3. If neither is available, the file is classified as **Unknown**.

### Why access time is preferred
Modification time alone can be misleading — a build system may touch a log file without any human accessing it.  Access time reflects actual use.  However, on many systems (Windows with default settings, Linux with `noatime` mount option) access timestamps are disabled for performance.  The classifier accepts both and uses whichever the caller provides.

### Why a future timestamp yields Unknown
A file whose activity timestamp is in the future indicates a system clock error or corrupted metadata.  Rather than assigning a meaningless age, the result is Unknown with an explanatory reason.

---

## Duplicate Detection Algorithm

```
Input: list of file paths
        │
        ▼
Stage 1: group by file size
        │  files with a unique size → cannot be duplicates
        ▼
Stage 2: hash each group member with SHA-256 (1 MB streaming reads)
        │  files with a unique hash → not duplicates
        ▼
Output: duplicate groups  +  error list
```

- **Same name ≠ duplicate.**  Content (hash) is the only criterion.
- **Same size ≠ duplicate.**  Size is a cheap pre-filter only.
- Files that disappear or become unreadable between Stage 1 and Stage 2 are reported in the error list, not silently dropped.

---

## Storage Allocation Policy

Destinations are evaluated in this order:

1. **Skip** if `total_capacity` or `used_capacity` are missing, non-integer, or inconsistent.
2. **Skip** if `allowed_extensions` is set and the file's extension is not in the list.
3. **Skip** if `free_bytes < file_size` (not enough room).
4. **Select** the eligible destination with the lowest *projected* utilisation:
   ```
   projected = (used_capacity + file_size) / total_capacity
   ```
   This spreads files across drives rather than filling one at a time.

If no destination passes all checks, a descriptive failure message is returned.  **The recommender never moves or copies any file.**

---

## Recommendation Types

| Type | Trigger | Priority |
|---|---|---|
| `ARCHIVE` | File classified as Archive | LOW |
| `CLEANUP` | File classified as Inactive | MEDIUM |
| `STORAGE` | Active file with a better destination available | LOW |
| `NO_ACTION` | Active file, no migration needed | LOW |
| `UNKNOWN` | Classification failed | LOW |

All recommendations are created with `status = PENDING`.

---

## Integration with Teammates' Modules

> **Anushka's module** is responsible for any approved file *movement*.
> Aman's module only produces advisory records.  It never calls move, copy, or delete operations.

> The **shared Files table** join in `recommendation_queries.sql` is commented out until the team confirms the column names and schema.  Do not uncomment it until you have verified the schema with your teammates.

---

## Running the Tests

From the **project root** (`pbl3/`):

```bash
# Using unittest (no extra dependencies)
python -m unittest modules/aman/test_aman.py -v

# Using pytest (if available)
python -m pytest modules/aman/test_aman.py -v
```

Expected: **all tests pass** with no warnings.

---

## File Structure

```
modules/aman/
├── __init__.py                 # Public API exports
├── file_classifier.py          # classify_file()
├── duplicate_detector.py       # find_duplicates(), calculate_sha256()
├── allocation_recommender.py   # recommend_storage()
├── recommendation_service.py   # generate_recommendation()
├── recommendations_schema.sql  # PostgreSQL DDL
├── recommendation_queries.sql  # Reference SQL (8 queries)
├── test_aman.py                # Unit tests
└── README.md                   # This file
```

---

## Assumptions & Limitations

1. **No live database connection** is made by this module.  SQL files are reference scripts only.
2. **Hashing is not atomic** — a file could change between the size check and the hash.  In production, consider verifying metadata before and after hashing.
3. **Windows access timestamps** may not be updated if the volume is mounted without the `atime` flag.  Pass `last_accessed=None` to fall back to `modified_at`.
4. **SHA-256 collisions** are cryptographically negligible but theoretically possible.  For a college project, SHA-256 is more than sufficient.
5. **Duplicate recommendations** — the service currently handles one file at a time.  Batch duplicate records should be added by calling `find_duplicates` separately and inserting additional rows into the Recommendations table.
