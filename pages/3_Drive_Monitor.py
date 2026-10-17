
import os
import streamlit as st
import pandas as pd
import psycopg2

from modules.udit.drive_monitor import get_drive_info
from modules.udit.drive_repository import save_drive_scan


st.set_page_config(
    page_title="Drive Monitor | Smart File Manager",
    page_icon="💽",
    layout="wide",
)

st.title("💽 Drive Monitor")
st.caption("Monitor drive storage and save scan history to PostgreSQL.")

with st.sidebar:
    st.subheader("Database Connection")
    db_password = st.text_input(
        "PostgreSQL password",
        type="password",
        key="udit_db_password",
    )
    st.caption("Database: smart_file_manager_test")

def get_test_connection(password):
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="smart_file_manager_test",
        user="postgres",
        password=password,
    )

def load_records(password):
    conn = get_test_connection(password)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT mount_point, filesystem, total_bytes,
                       used_bytes, free_bytes, last_scanned_at
                FROM drives
                ORDER BY mount_point;
            """)
            drive_columns = [d[0] for d in cur.description]
            drive_rows = cur.fetchall()

            cur.execute("""
                SELECT scan_id, started_at, completed_at, status
                FROM scan_sessions
                ORDER BY scan_id DESC;
            """)
            session_columns = [d[0] for d in cur.description]
            session_rows = cur.fetchall()

            cur.execute("""
                SELECT d.mount_point, h.total_bytes, h.used_bytes,
                       h.free_bytes, h.captured_at, h.scan_id
                FROM drive_usage_history h
                JOIN drives d ON d.drive_id = h.drive_id
                ORDER BY h.captured_at DESC;
            """)
            history_columns = [d[0] for d in cur.description]
            history_rows = cur.fetchall()

        return (
            pd.DataFrame(drive_rows, columns=drive_columns),
            pd.DataFrame(session_rows, columns=session_columns),
            pd.DataFrame(history_rows, columns=history_columns),
        )
    finally:
        conn.close()


def format_bytes(value):
    return f"{value / (1024 ** 3):.2f} GB"


if "udit_scan_message" in st.session_state:
    st.success(st.session_state.pop("udit_scan_message"))

scan_col, refresh_col = st.columns(2)

with scan_col:
    if st.button("🔍 Scan drives and save", type="primary", use_container_width=True):
        if not db_password:
            st.warning("Enter your PostgreSQL password in the sidebar first.")
        else:
            try:
                drives = get_drive_info()
                if not drives:
                    st.warning("No accessible drives detected.")
                else:
                    scan_id = save_drive_scan(drives)
                    st.session_state["udit_scan_message"] = (
                        f"Scan saved successfully. Scan ID: {scan_id}"
                    )
                    st.rerun()
            except Exception as error:
                st.error(f"Scan failed: {error}")

with refresh_col:
    refresh = st.button("🔄 Refresh records", use_container_width=True)

if not db_password:
    st.info("Enter your PostgreSQL password in the sidebar to load saved records.")
else:
    try:
        drives_df, sessions_df, history_df = load_records(db_password)

        total_drives = len(drives_df)
        total_scans = len(sessions_df)
        total_used = int(drives_df["used_bytes"].sum()) if total_drives else 0
        total_free = int(drives_df["free_bytes"].sum()) if total_drives else 0

        metric1, metric2, metric3, metric4 = st.columns(4)
        metric1.metric("Registered Drives", total_drives)
        metric2.metric("Scan Sessions", total_scans)
        metric3.metric("Combined Used", format_bytes(total_used))
        metric4.metric("Combined Free", format_bytes(total_free))

        st.subheader("Current Drive Storage")
        if not drives_df.empty:
            display_df = drives_df.copy()
            display_df["Used (GB)"] = display_df["used_bytes"].apply(
                lambda x: round(x / (1024 ** 3), 2)
            )
            display_df["Free (GB)"] = display_df["free_bytes"].apply(
                lambda x: round(x / (1024 ** 3), 2)
            )
            display_df["Utilization (%)"] = (
                display_df["used_bytes"] / display_df["total_bytes"].replace(0, pd.NA) * 100
            ).round(2)
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No drive records yet. Run a scan to add them.")

        st.subheader("Scan Sessions")
        st.dataframe(sessions_df, use_container_width=True, hide_index=True)

        st.subheader("Drive Usage History")
        st.dataframe(history_df, use_container_width=True, hide_index=True)

    except psycopg2.Error as error:
        st.error(f"Could not load test database records: {error}")
    except Exception as error:
        st.error(f"Something went wrong: {error}")
