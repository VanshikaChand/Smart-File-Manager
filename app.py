
import streamlit as st
import os
import pandas as pd

from file_scanner import scan_folder
from file_repository import save_files, get_all_files


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart File Manager",
    page_icon="📁",
    layout="wide"
)


# --------------------------------------------------
# BASIC STYLING
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: #0b1120;
    color: #f1f5f9;
}
[data-testid="stSidebar"] {
    background: #111c30;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
[data-testid="stMetric"] {
    background: #152238;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #263954;
}
div.stButton > button {
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 0.55rem 1rem;
}
div.stButton > button:hover {
    background: #4f46e5;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.markdown("# 📁 Smart File Manager")
st.sidebar.caption("OS + DBMS Project")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Scan Files", "Database Records", "About"]
)

st.sidebar.divider()
st.sidebar.caption("Built with Python, Streamlit & PostgreSQL")

st.title("📁 Smart File Manager")
st.write("Scan, organize and manage file metadata from one dashboard.")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.subheader("Dashboard Overview")

    folder_path = st.text_input(
        "Folder to inspect",
        value=r"D:\SmartFileManagerTest",
        key="dashboard_folder"
    )

    if st.button("🔍 Inspect Folder"):

        if os.path.isdir(folder_path):

            with st.spinner("Inspecting folder..."):
                files = scan_folder(folder_path)

            st.session_state["scanned_files"] = files
            st.success(f"Found {len(files)} files.")

        else:
            st.error("Folder does not exist. Check the path.")

    files = st.session_state.get("scanned_files", [])

    total_files = len(files)
    total_size = sum(item["file_size"] for item in files)
    total_mb = total_size / (1024 * 1024)

    col1, col2, col3 = st.columns(3)

    col1.metric("Files Found", total_files)
    col2.metric("Total Size", f"{total_mb:.2f} MB")

    col3.metric(
        "File Types",
        len(set(
            item["file_extension"] or "No extension"
            for item in files
        ))
    )

    st.divider()
    st.subheader("Recent Scan Results")

    if files:

        df = pd.DataFrame(files)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

    else:
        st.info("Inspect a folder to display its files here.")


# --------------------------------------------------
# SCAN FILES
# --------------------------------------------------

elif page == "Scan Files":

    st.subheader("🔍 Scan a Folder")

    st.write(
        "Collect file names, paths, extensions, sizes "
        "and modification times."
    )

    folder_path = st.text_input(
        "Enter folder path",
        value=r"D:\SmartFileManagerTest",
        key="scan_folder_path"
    )

    if st.button("Start Scan"):

        if not os.path.isdir(folder_path):

            st.error("Folder does not exist.")

        else:

            with st.spinner("Scanning files..."):
                files = scan_folder(folder_path)

            st.session_state["scanned_files"] = files
            st.success(f"Scan complete. Found {len(files)} files.")

    files = st.session_state.get("scanned_files", [])

    if files:

        df = pd.DataFrame(files)

        st.subheader("Scanned Files")

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        st.download_button(
            "Download Scan Results as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="scan_results.csv",
            mime="text/csv"
        )

        st.divider()
        st.subheader("Save Scan Results to PostgreSQL")

        password = st.text_input(
            "PostgreSQL password",
            type="password",
            key="scan_db_password"
        )

        if st.button("Save Files to Database"):

            if not password:

                st.warning("Please enter your PostgreSQL password.")

            else:

                with st.spinner("Saving records to PostgreSQL..."):

                    success, message = save_files(
                        files,
                        password=password
                    )

                if success:
                    st.success(message)
                else:
                    st.error(message)

    else:

        st.info(
            "No scan results yet. Enter a folder path "
            "and click Start Scan."
        )


# --------------------------------------------------
# DATABASE RECORDS
# --------------------------------------------------

elif page == "Database Records":

    st.subheader("🗄️ Database Records")

    st.write("View file metadata stored in PostgreSQL.")

    password = st.text_input(
        "PostgreSQL password",
        type="password",
        key="database_password"
    )

    if st.button("Load Database Records"):

        if not password:

            st.warning("Please enter your PostgreSQL password.")

        else:

            with st.spinner("Loading database records..."):

                success, result = get_all_files(password)

            if success:

                st.session_state["database_records"] = result
                st.success(f"Loaded {len(result)} records.")

            else:

                st.error(f"Database connection failed: {result}")

    records = st.session_state.get("database_records", [])

    if records:

        df = pd.DataFrame(records)

        col1, col2 = st.columns(2)

        col1.metric("Total Records", len(df))

        total_storage = df["file_size"].sum() / (1024 * 1024)

        col2.metric("Total Storage", f"{total_storage:.2f} MB")

        st.divider()

        search = st.text_input(
            "🔎 Search by file name or path",
            key="database_search"
        )

        if search:

            mask = (
                df["file_name"].str.contains(
                    search,
                    case=False,
                    na=False,
                    regex=False
                )
                |
                df["file_path"].str.contains(
                    search,
                    case=False,
                    na=False,
                    regex=False
                )
            )

            df = df[mask]

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

    elif "database_records" in st.session_state:

        st.info("No file records found in the database.")


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

elif page == "About":

    st.subheader("About This Project")

    st.write(
        "Smart File Manager is an academic project combining "
        "Operating Systems concepts and Database Management Systems."
    )

    st.markdown("""
    **Current Modules**

    - File scanning and metadata extraction
    - PostgreSQL file metadata storage
    - Duplicate-safe record updates
    - Interactive dashboard
    - Database record search
    - CSV export

    **Planned Modules**

    - Drive monitoring
    - File classification
    - Duplicate detection
    - Safe file movement
    - Storage recommendations
    """)
