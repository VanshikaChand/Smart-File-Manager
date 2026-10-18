
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
# SHARED THEME
# --------------------------------------------------

from ui_theme import apply_theme

apply_theme()


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sfm-brand">
            <div class="sfm-brand-mark"><span>SF</span></div>
            <div class="sfm-brand-copy">
                <div class="sfm-brand-title">SMART FILE</div>
                <div class="sfm-brand-title sfm-brand-title-second">MANAGER</div>
                <div class="sfm-brand-subtitle">FILE INTELLIGENCE</div>
            </div>
        </div>
        <div class="sfm-workspace-label">WORKSPACE</div>
        <div class="sfm-sidebar-description">Navigate your files and database tools.</div>
        """,
        unsafe_allow_html=True,
    )

    page_labels = {
        "Dashboard": "01   Overview",
        "Scan Files": "02   Scan files",
        "Database Records": "03   Database records",
        "About": "04   About project",
    }
    page = st.radio(
        "Navigation",
        ["Dashboard", "Scan Files", "Database Records", "About"],
        format_func=lambda item: page_labels[item],
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.markdown(
        """
        <div class="sfm-sidebar-spacer"></div>
        <div class="sfm-sidebar-system-card">
            <div class="sfm-system-card-top"><span class="sfm-connection-dot"></span><span>WORKSPACE STATUS</span></div>
            <div class="sfm-system-card-title">Local environment</div>
            <div class="sfm-system-card-copy">Your files stay on your machine.</div>
            <div class="sfm-system-card-footer">PYTHON <span></span> STREAMLIT <span></span> POSTGRESQL</div>
        </div>
        <div class="sfm-sidebar-version">SMART FILE MANAGER <span>•</span> LOCAL APP</div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------
header_left, header_right = st.columns([5, 1.3], vertical_alignment="center")
with header_left:
    st.markdown('<div class="sfm-eyebrow">WORKSPACE / FILE INTELLIGENCE</div>', unsafe_allow_html=True)
    st.title("Smart File Manager")
    st.markdown(
        '<div class="sfm-page-subtitle">A clear view of your scanned files, metadata, and database activity.</div>',
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown(
        '<div class="sfm-status-pill"><span class="sfm-status-dot"></span> LOCAL WORKSPACE</div>',
        unsafe_allow_html=True,
    )
st.markdown('<div class="sfm-header-rule"></div>', unsafe_allow_html=True)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.markdown('<div class="sfm-section-kicker">OVERVIEW</div>', unsafe_allow_html=True)
    st.subheader("Workspace overview")
    st.markdown('<div class="sfm-muted-copy">Inspect a folder to calculate file statistics and preview the latest scan results.</div>', unsafe_allow_html=True)

    folder_path = st.text_input(
        "Folder to inspect",
        value=r"D:\SmartFileManagerTest",
        key="dashboard_folder"
    )

    if st.button("Inspect folder", type="primary"):

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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Files found", f"{total_files:,}")
    col2.metric("Total size", f"{total_mb:.2f} MB")
    col3.metric(
        "File types",
        len(set(
            item["file_extension"] or "No extension"
            for item in files
        ))
    )
    col4.metric("Scan state", "Ready" if files else "Waiting")

    st.markdown('<div class="sfm-section-heading-row"><div><div class="sfm-section-kicker">LATEST ACTIVITY</div><h3>Recent scan results</h3></div></div>', unsafe_allow_html=True)

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

    st.markdown('<div class="sfm-section-kicker">INGESTION</div>', unsafe_allow_html=True)
    st.subheader("Scan files")
    st.markdown('<div class="sfm-muted-copy">Collect file names, paths, extensions, sizes, and modification times from a local folder.</div>', unsafe_allow_html=True)

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
            "⬇️ Download Scan Results as CSV",
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

        if st.button("💾 Save Files to Database"):

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

    st.markdown('<div class="sfm-section-kicker">POSTGRESQL</div>', unsafe_allow_html=True)
    st.subheader("Database records")
    st.markdown('<div class="sfm-muted-copy">Load and search file metadata already stored in PostgreSQL.</div>', unsafe_allow_html=True)

    password = st.text_input(
        "PostgreSQL password",
        type="password",
        key="database_password"
    )

    if st.button("📂 Load Database Records"):

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

        col1.metric("📋 Total Records", len(df))

        total_storage = df["file_size"].sum() / (1024 * 1024)

        col2.metric("💾 Total Storage", f"{total_storage:.2f} MB")

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

    st.markdown('<div class="sfm-section-kicker">PROJECT DETAILS</div>', unsafe_allow_html=True)
    st.subheader("About Smart File Manager")

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
