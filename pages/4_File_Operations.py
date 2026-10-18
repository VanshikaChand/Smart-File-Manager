import html

import pandas as pd
import psycopg2
import streamlit as st

from ui_theme import apply_theme

st.set_page_config(
    page_title="File Operations | Smart File Manager",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

# -----------------------------------------------------------------------------
# Midnight Charcoal UI — this page is intentionally READ-ONLY.
# It displays movement_history from smart_file_manager_test and does not move,
# rename, copy, or delete files.
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
:root {
  --fo-bg: #07100e; --fo-panel: #0d1b17; --fo-panel2: #11251e;
  --fo-border: #244036; --fo-text: #f4f8f5; --fo-muted: #c4d2cb;
  --fo-green: #a9ec8c; --fo-bright: #63e58a; --fo-yellow: #f2d05b;
  --fo-red: #ff8178;
}
.stApp { background: radial-gradient(ellipse at 72% 0%, #142a21 0%, #07100e 58%); color: var(--fo-text); }
.block-container { max-width: 1700px; padding-top: 1.6rem; padding-bottom: 2rem; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#0b1713,#08100e); border-right: 1px solid var(--fo-border); }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--fo-muted); }
h1, h2, h3 { color: var(--fo-text) !important; letter-spacing: -.025em; }
h1 { font-size: 2.45rem !important; font-weight: 780 !important; }
[data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] p { color: var(--fo-muted); }
[data-testid="stWidgetLabel"] p, label { color: var(--fo-text) !important; }
input, textarea { color: var(--fo-text) !important; background: #10211b !important; }
[data-testid="stSelectbox"] div, [data-testid="stMultiSelect"] div { color: var(--fo-text); }
.fo-header { display:flex; align-items:center; gap:16px; margin: 0 0 1.2rem; }
.fo-header-icon { width:68px; height:68px; display:flex; align-items:center; justify-content:center; border-radius:19px; background:#123125; border:1px solid #285541; flex-shrink:0; }
.fo-header-icon svg { width:36px; height:36px; }
.fo-title { color:#fff; font-size:2.35rem; line-height:1.12; font-weight:800; letter-spacing:-.04em; }
.fo-subtitle { color:#c7d5ce; font-size:.98rem; margin-top:7px; }
.fo-card { background:linear-gradient(145deg,rgba(16,39,30,.96),rgba(9,24,19,.98)); border:1px solid var(--fo-border); border-radius:16px; padding:18px; min-height:112px; }
.fo-kpi { display:flex; align-items:center; gap:14px; }
.fo-kpi-icon { width:55px; height:55px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; background:#16402d; color:#82efa0; font-size:26px; font-weight:700; }
.fo-kpi-icon.yellow { background:#40391c; color:var(--fo-yellow); }
.fo-kpi-icon.red { background:#422624; color:var(--fo-red); }
.fo-kpi-label { color:#d7e3dc; font-size:.85rem; }
.fo-kpi-value { color:#fff; font-size:1.8rem; font-weight:800; line-height:1.25; margin:3px 0; }
.fo-kpi-note { color:#c1d0c8; font-size:.76rem; }
.fo-panel { background:rgba(10,27,21,.86); border:1px solid var(--fo-border); border-radius:17px; padding:17px; }
.fo-panel-title { font-size:1.1rem; font-weight:760; color:#f6faf7; }
.fo-panel-caption { font-size:.8rem; color:#c4d2cb; margin-top:3px; }
.fo-heading-row { display:flex; align-items:center; gap:10px; margin-bottom:14px; }
.fo-heading-icon { display:flex; align-items:center; justify-content:center; width:37px; height:37px; border-radius:11px; background:#b5e99a; color:#102017; font-size:20px; font-weight:800; }
.fo-status { display:inline-block; border:1px solid #3acb70; color:#73efa0; background:rgba(26,117,59,.15); border-radius:30px; padding:3px 10px; font-size:.75rem; font-weight:650; }
.fo-status.pending { border-color:#b99b31; color:#f3d35e; background:rgba(135,106,20,.15); }
.fo-status.failed { border-color:#d45d55; color:#ff938b; background:rgba(142,40,35,.15); }
.fo-note { border:1px solid #4b4527; background:rgba(65,54,20,.2); color:#f1e4b5; border-radius:12px; padding:12px 14px; font-size:.87rem; }
.stButton > button, .stDownloadButton > button { min-height:42px; border-radius:11px !important; font-weight:700 !important; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] { background:linear-gradient(135deg,#b5ed98,#91d978) !important; color:#102017 !important; border:1px solid #b5ed98 !important; }
.stButton > button[kind="primary"] *, .stButton > button[data-testid="stBaseButton-primary"] * { color:#102017 !important; fill:#102017 !important; opacity:1 !important; font-weight:800 !important; }
.stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]) { background:#14271f !important; color:#f5f8f6 !important; border:1px solid #355548 !important; }
.stDownloadButton > button { background:#10271e !important; color:#a9ec8c !important; border:1px solid #34724d !important; }
[data-testid="stDataFrame"] { border:1px solid var(--fo-border); border-radius:12px; overflow:hidden; }
[data-testid="stAlert"] { color:#fff !important; }
hr { border-color:var(--fo-border) !important; }
@media(max-width:900px) { .fo-title {font-size:1.8rem;} .fo-header-icon {width:54px;height:54px;} .fo-card {padding:13px;} }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar: retain the shared app navigation and provide only connection controls here.
with st.sidebar:
    st.markdown(
        "<div style='font-size:1.08rem;font-weight:800;color:#f3f8f4'>SMART FILE MANAGER</div>"
        "<div style='font-size:.78rem;color:#9fb5a8;margin-top:3px'>OS + DBMS Project</div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.subheader("Database Connection")
    db_password = st.text_input(
        "SmartFM app password", type="password", key="anushka_db_password"
    )
    st.caption("Database: smart_file_manager_test")
    st.markdown(
        "<div style='color:#72e895;font-size:.82rem'>● Local PostgreSQL connection</div>",
        unsafe_allow_html=True,
    )
    st.caption("Read-only movement history")


def get_test_connection(password):
    """Connect using the restricted application role."""
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="smart_file_manager_test",
        user="smartfm_app",
        password=password,
        connect_timeout=5,
    )


def load_history(password):
    """Read movement history only; this function performs no mutations."""
    conn = get_test_connection(password)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database()")
            current_user, database_name = cur.fetchone()
            if current_user != "smartfm_app" or database_name != "smart_file_manager_test":
                raise PermissionError("Unexpected database role or database; no records loaded.")
            cur.execute(
                """
                SELECT history_id, file_id, source_path, destination_path,
                       status, error_message, created_at, moved_at
                FROM movement_history
                ORDER BY history_id DESC
                """
            )
            rows = cur.fetchall()
            columns = [description[0] for description in cur.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()


def status_kind(value):
    value = str(value or "").strip().upper()
    if value in {"DONE", "COMPLETED", "SUCCESS", "SUCCESSFUL"}:
        return "completed"
    if value in {"PENDING", "IN PROGRESS", "IN_PROGRESS"}:
        return "pending"
    if value in {"FAILED", "ERROR"}:
        return "failed"
    return "other"


def status_badge(value):
    kind = status_kind(value)
    label = html.escape(str(value or "Unknown").title())
    css_class = "" if kind == "completed" else (" pending" if kind == "pending" else (" failed" if kind == "failed" else ""))
    return f"<span class='fo-status{css_class}'>{label}</span>"


# Header — plain text, no emoji or breadcrumb.
st.markdown(
    """
<div class="fo-header">
  <div class="fo-header-icon" aria-hidden="true">
    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5 13.5A4.5 4.5 0 0 1 9.5 9H20l4.5 5H38a5 5 0 0 1 5 5v17a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4V13.5Z" fill="#63D98A"/>
      <path d="M5 20h38v16a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4V20Z" fill="#A8EF91"/>
    </svg>
  </div>
  <div><div class="fo-title">File Operations</div><div class="fo-subtitle">Review file movement activity and operation history.</div></div>
</div>
""",
    unsafe_allow_html=True,
)

# Safe read-only action bar: no real file move/delete controls are exposed here.
left, action_col, reset_col = st.columns([5.2, 1.5, 1.0], vertical_alignment="center")
with left:
    st.markdown(
        "<div class='fo-note'>Read-only mode · This page displays movement history only. It will not move, rename, copy, or delete files.</div>",
        unsafe_allow_html=True,
    )
with action_col:
    load_clicked = st.button("Load History", type="primary", use_container_width=True)
with reset_col:
    reset_clicked = st.button("Reset", use_container_width=True)

if reset_clicked:
    for key in ("fo_history_df", "fo_history_loaded", "fo_search", "fo_status_filter"):
        st.session_state.pop(key, None)
    st.rerun()

if load_clicked:
    if not db_password:
        st.warning("Enter the smartfm_app password in the sidebar first.")
    else:
        try:
            with st.spinner("Loading movement history..."):
                st.session_state["fo_history_df"] = load_history(db_password)
                st.session_state["fo_history_loaded"] = True
            st.success("Movement history loaded successfully.")
        except PermissionError as error:
            st.error(str(error))
        except (psycopg2.Error, OSError) as error:
            st.error("Could not load movement history. Check the smartfm_app password and database permissions.")
            st.caption(str(error))
        except Exception as error:
            st.error(f"Unable to load movement history: {error}")

# Counts and table are based on records actually fetched, not illustrative values.
df = st.session_state.get("fo_history_df")
if df is None:
    df = pd.DataFrame(columns=["history_id", "file_id", "source_path", "destination_path", "status", "error_message", "created_at", "moved_at"])

if st.session_state.get("fo_history_loaded"):
    total = len(df)
    status_series = df["status"].map(status_kind) if "status" in df.columns else pd.Series(dtype=str)
    completed = int((status_series == "completed").sum())
    pending = int((status_series == "pending").sum())
    failed = int((status_series == "failed").sum())
else:
    total = completed = pending = failed = 0

k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    st.markdown(f"<div class='fo-card'><div class='fo-kpi'><div class='fo-kpi-icon'>▤</div><div><div class='fo-kpi-label'>Total Operations</div><div class='fo-kpi-value'>{total if st.session_state.get('fo_history_loaded') else '—'}</div><div class='fo-kpi-note'>Movement history records</div></div></div></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='fo-card'><div class='fo-kpi'><div class='fo-kpi-icon'>✓</div><div><div class='fo-kpi-label'>Completed</div><div class='fo-kpi-value'>{completed if st.session_state.get('fo_history_loaded') else '—'}</div><div class='fo-kpi-note'>Successful movements</div></div></div></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='fo-card'><div class='fo-kpi'><div class='fo-kpi-icon yellow'>◷</div><div><div class='fo-kpi-label'>Pending</div><div class='fo-kpi-value'>{pending if st.session_state.get('fo_history_loaded') else '—'}</div><div class='fo-kpi-note'>Awaiting completion</div></div></div></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='fo-card'><div class='fo-kpi'><div class='fo-kpi-icon red'>!</div><div><div class='fo-kpi-label'>Failed</div><div class='fo-kpi-value'>{failed if st.session_state.get('fo_history_loaded') else '—'}</div><div class='fo-kpi-note'>Operations with errors</div></div></div></div>", unsafe_allow_html=True)

st.write("")

# History workspace
st.markdown(
    "<div class='fo-panel'><div class='fo-heading-row'><div class='fo-heading-icon'>▤</div><div><div class='fo-panel-title'>Operation History</div><div class='fo-panel-caption'>Search, filter, and export file movement records.</div></div></div></div>",
    unsafe_allow_html=True,
)

search_col, status_col, export_col = st.columns([3.2, 1.3, 1.1], vertical_alignment="bottom")
with search_col:
    search_text = st.text_input("Search history", placeholder="Search file ID, source path, destination path, or error…", key="fo_search")
with status_col:
    status_filter = st.selectbox("Status", ["All statuses", "Completed", "Pending", "Failed", "Other"], key="fo_status_filter")
with export_col:
    export_source = df.copy() if st.session_state.get("fo_history_loaded") else pd.DataFrame()
    st.download_button(
        "Export CSV",
        data=export_source.to_csv(index=False).encode("utf-8-sig"),
        file_name="file_movement_history.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=not st.session_state.get("fo_history_loaded") or export_source.empty,
    )

if not st.session_state.get("fo_history_loaded"):
    st.markdown("<div class='fo-panel' style='text-align:center;padding:36px 18px'><div style='font-size:1.05rem;font-weight:750;color:#f4f8f5'>No history loaded yet</div><div style='color:#c4d2cb;margin-top:8px'>Enter your restricted database password in the sidebar, then select <b>Load History</b>.</div></div>", unsafe_allow_html=True)
elif df.empty:
    st.markdown("<div class='fo-panel' style='text-align:center;padding:30px;color:#c4d2cb'>No movement history records were found in the test database.</div>", unsafe_allow_html=True)
else:
    filtered = df.copy()
    if status_filter != "All statuses" and "status" in filtered.columns:
        wanted = {"Completed": "completed", "Pending": "pending", "Failed": "failed", "Other": "other"}[status_filter]
        filtered = filtered[filtered["status"].map(status_kind) == wanted]
    if search_text.strip():
        searchable_cols = [c for c in ["file_id", "source_path", "destination_path", "status", "error_message", "history_id"] if c in filtered.columns]
        mask = filtered[searchable_cols].fillna("").astype(str).apply(lambda col: col.str.contains(search_text.strip(), case=False, regex=False)).any(axis=1)
        filtered = filtered[mask]

    display_df = filtered.rename(columns={
        "history_id": "History ID", "file_id": "File ID", "source_path": "Source Path",
        "destination_path": "Destination Path", "status": "Status", "error_message": "Error",
        "created_at": "Created At", "moved_at": "Moved At",
    })
    st.caption(f"Showing {len(display_df):,} of {len(df):,} records")
    if display_df.empty:
        st.info("No records match your search and status filters.")
    else:
        # Keep raw status values in the data table for compatibility and easy export.
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=min(520, 180 + 42 * len(display_df)),
            column_config={
                "History ID": st.column_config.NumberColumn("History ID", format="%d"),
                "File ID": st.column_config.NumberColumn("File ID", format="%d"),
                "Source Path": st.column_config.TextColumn("Source Path", width="large"),
                "Destination Path": st.column_config.TextColumn("Destination Path", width="large"),
                "Error": st.column_config.TextColumn("Error", width="medium"),
            },
        )

st.markdown(
    "<div style='text-align:center;color:#91a69a;font-size:.76rem;padding:20px 0 4px'>SMART FILE MANAGER · FILE MOVEMENT HISTORY · READ-ONLY</div>",
    unsafe_allow_html=True,
)
