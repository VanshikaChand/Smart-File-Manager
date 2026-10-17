
import pandas as pd
import psycopg2
import streamlit as st

from modules.anushka.operation.notification import (
    show_success,
    show_error,
    show_info,
)


st.set_page_config(
    page_title="File Operations",
    page_icon="📋",
    layout="wide",
)

st.title("📋 File Operations")
st.caption("Anushka Module · Movement History")

show_info(
    "Read-only view: this page displays movement history from the "
    "test database. It does not move, rename, or delete files."
)

with st.sidebar:
    st.subheader("Test Database Connection")

    db_password = st.text_input(
        "SmartFM app database password",
        type="password",
        key="anushka_db_password",
    )

    connect_button = st.button(
        "Load Movement History",
        type="primary",
    )


def get_test_connection(password):
    """Connect using the restricted application database role."""
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="smart_file_manager_test",
        user="smartfm_app",
        password=password,
        connect_timeout=5,
    )


if connect_button:
    if not db_password:
        show_error("Enter the smartfm_app password in the sidebar.")

    else:
        conn = None

        try:
            conn = get_test_connection(db_password)

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT current_user, current_database()"
                )
                current_user, database_name = cur.fetchone()

                # Safety check: never load records from another account/database.
                if (
                    current_user != "smartfm_app"
                    or database_name != "smart_file_manager_test"
                ):
                    show_error(
                        "Unexpected database account or database. "
                        "No records loaded."
                    )
                    st.stop()

                cur.execute("""
                    SELECT
                        history_id,
                        file_id,
                        source_path,
                        destination_path,
                        status,
                        error_message,
                        created_at,
                        moved_at
                    FROM movement_history
                    ORDER BY history_id DESC
                """)

                rows = cur.fetchall()

            columns = [
                "History ID",
                "File ID",
                "Source Path",
                "Destination Path",
                "Status",
                "Error",
                "Created At",
                "Moved At",
            ]

            show_success(
                f"Connected as {current_user} to {database_name}"
            )

            st.metric("Movement History Records", len(rows))

            if rows:
                df = pd.DataFrame(rows, columns=columns)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                show_info("No movement history records found.")

        except (psycopg2.Error, OSError) as error:
            show_error(
                "Could not load movement history. "
                "Check the smartfm_app password and database permissions."
            )
            st.caption(str(error))

        finally:
            if conn is not None:
                conn.close()


st.caption(
    "Database: smart_file_manager_test · Read-only dashboard"
)
