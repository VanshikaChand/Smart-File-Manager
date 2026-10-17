# Smart File Manager — Udit Module

## Overview
This module integrates Operating System drive monitoring with PostgreSQL database storage and analytics.

## Features
- Detects mounted drives using `psutil`.
- Collects filesystem, total, used, and free storage.
- Saves drive information and scan history to PostgreSQL.
- Supports storage utilization and history analytics.
- Uses database constraints and indexes for data integrity and querying.

## Folder Structure
- `drive_monitor.py` — detects drives and collects storage information.
- `drive_repository.py` — connects to PostgreSQL and saves drive scans.
- `run_drive_scan.py` — runs the monitoring and database-saving workflow.
- `udit_schema.sql` — creates the database tables and indexes.
- `analytics_queries.sql` — contains storage analytics queries.
- `test_drive_monitor.py` — drive-monitoring tests.
- `test_drive_repository.py` — database repository tests.

## Requirements
- Python
- PostgreSQL
- `psutil`
- `psycopg2-binary`

Install the Python dependencies:

```bash
python -m pip install psutil psycopg2-binary
```

## Database Setup
Create a PostgreSQL test database named `smart_file_manager_test` and execute `udit_schema.sql` in its Query Tool.

The schema contains:
- `drives`
- `scan_sessions`
- `drive_usage_history`

## Database Configuration
Set the database password in PowerShell before running the application:

```powershell
$env:DB_PASSWORD = "YOUR_POSTGRES_PASSWORD"
```

Optional environment variables:
- `DB_HOST` — defaults to `localhost`
- `DB_PORT` — defaults to `5432`
- `DB_NAME` — defaults to `smart_file_manager_test`
- `DB_USER` — defaults to `postgres`

Do not commit passwords or other credentials to version control.

## Run the Module
From the project root:

```powershell
.\.venv\Scripts\python.exe .\modules\udit\drive_monitor.py
```

To scan drives and save the results to PostgreSQL:

```powershell
.\.venv\Scripts\python.exe .\modules\udit\run_drive_scan.py
```

## Analytics
Execute the queries in `analytics_queries.sql` using pgAdmin Query Tool connected to `smart_file_manager_test`.

## Verification
The module was manually tested for:
- Drive detection and storage reporting.
- PostgreSQL connection.
- Drive record insertion/update.
- Scan-session creation and completion.
- Historical usage records.
- Storage utilization analytics.

## Integration Note
Use the shared project database only after the team reviews the schema and approves integration. Do not run experimental schema changes against the shared database.
