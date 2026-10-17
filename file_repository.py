
import getpass
import psycopg2
from psycopg2.extras import execute_values


def get_connection(password):
    """Create and return a PostgreSQL database connection."""
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="smart_file_manager",
        user="postgres",
        password=password,
    )


def save_files(files, password=None):
    """Insert scanned files or update existing records by file path."""

    if not files:
        return True, "No files to save."

    # Terminal se run karne par password maango.
    # Dashboard password provide kar sakta hai.
    if password is None:
        password = getpass.getpass("Enter PostgreSQL password: ")

    query = """
        INSERT INTO files (
            file_name,
            file_path,
            file_extension,
            file_size,
            last_modified
        )
        VALUES %s
        ON CONFLICT (file_path)
        DO UPDATE SET
            file_name = EXCLUDED.file_name,
            file_extension = EXCLUDED.file_extension,
            file_size = EXCLUDED.file_size,
            last_modified = EXCLUDED.last_modified,
            last_scanned = CURRENT_TIMESTAMP;
    """

    values = [
        (
            file["file_name"],
            file["file_path"],
            file["file_extension"],
            file["file_size"],
            file["last_modified"],
        )
        for file in files
    ]

    connection = None

    try:
        connection = get_connection(password)

        with connection:
            with connection.cursor() as cursor:
                execute_values(cursor, query, values)

        return True, f"Successfully saved {len(files)} file records."

    except psycopg2.Error as error:
        return False, f"Could not save files: {error}"

    finally:
        if connection is not None:
            connection.close()


def get_all_files(password):
    """Fetch all file records from PostgreSQL."""

    connection = None

    try:
        connection = get_connection(password)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    file_id,
                    file_name,
                    file_path,
                    file_extension,
                    file_size,
                    last_modified,
                    last_scanned
                FROM files
                ORDER BY last_scanned DESC;
            """)

            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()

        return True, [dict(zip(columns, row)) for row in rows]

    except psycopg2.Error as error:
        return False, str(error)

    finally:
        if connection is not None:
            connection.close()
