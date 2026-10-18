import html
import os

import pandas as pd
import psycopg2
import streamlit as st

from ui_theme import apply_theme
from modules.udit.drive_monitor import get_drive_info
from modules.udit.drive_repository import save_drive_scan


st.set_page_config(
    page_title="Drive Monitor | Smart File Manager",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

# -----------------------------------------------------------------------------
# MIDNIGHT CHARCOAL — page-specific styling; database and scan logic preserved
# -----------------------------------------------------------------------------
st.markdown("""
<style>
:root { --sm-bg:#070d0c; --sm-panel:#101b19; --sm-panel2:#14231f; --sm-border:#344a43;
        --sm-green:#b5ef96; --sm-bright:#65ee91; --sm-text:#ffffff; --sm-muted:#d0dad6; }
.stApp { background: radial-gradient(ellipse at 70% 0%, #132720 0%, #080f0d 58%); color:#ffffff; }
.stApp, .stApp p, .stApp label, .stApp li, .stApp span { color: inherit; }
[data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] p { color:#d4dfda !important; }
[data-testid="stTextInput"] label, [data-testid="stWidgetLabel"] p { color:#f3f7f5 !important; }
input, textarea { color:#ffffff !important; background-color:#14211d !important; }
[data-testid="stDataFrame"] *, [data-testid="stTable"] * { color:#f2f6f4 !important; }
[data-testid="stHeader"] { background:rgba(7,17,15,.92); }
.block-container { max-width: 1600px; padding-top: 1.35rem; padding-bottom: 2rem; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0c1715,#09110f); border-right:1px solid #20342e; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#bdc9c4; }
h1,h2,h3 { letter-spacing:-.035em; }
h1 { font-size:2.45rem !important; font-weight:750 !important; color:#ffffff !important; }
h2 { font-size:1.45rem !important; font-weight:700 !important; }
.sm-eyebrow { color:#d2ded8; font-size:.82rem; letter-spacing:.08em; text-transform:uppercase; }
.sm-title-row { display:flex; align-items:center; gap:15px; margin:0 0 4px 0; }
.sm-title-icon { width:56px;height:56px;border-radius:16px;display:flex;align-items:center;justify-content:center;
 background:linear-gradient(145deg,#1b3b2d,#10231c);border:1px solid #315542;font-size:28px; }
.sm-subtitle { color:#d0dad6; margin:0 0 1.1rem 71px; font-size:.94rem; }
.sm-card { background:linear-gradient(145deg,rgba(18,37,31,.94),rgba(10,23,20,.98)); border:1px solid #233b32;
 border-radius:17px; padding:18px 19px; min-height:104px; box-shadow:0 10px 26px rgba(0,0,0,.12); }
.sm-kpi { display:flex; gap:14px; align-items:center; height:100%; }
.sm-kpi-icon { width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:25px;flex-shrink:0;background:#1c3a2b;color:#a8ed8e; }
.sm-kpi-icon.gold { background:#40381b;color:#f7d35f; }
.sm-kpi-icon.red { background:#402a29;color:#ff8c83; }
.sm-kpi-label { color:#e1e9e5;font-size:.84rem; }
.sm-kpi-value { color:#fff;font-size:1.65rem;font-weight:750;line-height:1.25;margin:2px 0; }
.sm-kpi-note { color:#c5d1cb;font-size:.76rem; }
.sm-section { background:rgba(12,26,22,.82);border:1px solid #1e342d;border-radius:18px;padding:17px 16px 13px 16px;margin-top:13px; }
.sm-section-head { display:flex;align-items:center;gap:11px;margin-bottom:12px; }
.sm-section-icon { width:34px;height:34px;border-radius:10px;background:#c0e9a4;color:#102016;display:flex;align-items:center;justify-content:center;font-size:18px; }
.sm-section-title { font-size:1.1rem;font-weight:750;color:#f5f8f5; }
.sm-section-caption { font-size:.78rem;color:#d0dad6;margin-top:1px; }
.sm-drive { background:linear-gradient(140deg,#10231e,#0b1916);border:1px solid #223b32;border-radius:16px;padding:17px 17px 14px;height:100%; }
.sm-drive-head { display:flex;align-items:center;gap:12px;margin-bottom:15px; }
.sm-drive-icon { width:48px;height:48px;border-radius:13px;background:#17362c;display:flex;align-items:center;justify-content:center;font-size:25px; }
.sm-drive-name { font-size:1.1rem;font-weight:750;color:#f7faf8; }
.sm-drive-fs { color:#d0dad6;font-size:.8rem;margin-top:3px; }
.sm-pill { border:1px solid #3fae68;border-radius:30px;color:#79e59b;padding:3px 11px;font-size:.75rem;margin-left:7px;white-space:nowrap; }
.sm-pill.gold { border-color:#c39b22;color:#f4ce50; }
.sm-drive-body { display:flex;align-items:center;gap:16px; }
.sm-ring { width:112px;height:112px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0; }
.sm-ring-inner { width:88px;height:88px;border-radius:50%;background:#0d1c18;display:flex;flex-direction:column;align-items:center;justify-content:center; }
.sm-ring-value { font-size:1.1rem;font-weight:800;color:#fff; }
.sm-ring-label { color:#d0dad6;font-size:.75rem; }
.sm-drive-stats { flex:1;min-width:0; }
.sm-stat-line { display:flex;align-items:center;gap:8px;margin:9px 0;color:#e0e8e4;font-size:.8rem; }
.sm-stat-dot { width:9px;height:9px;border-radius:50%;display:inline-block;flex-shrink:0; }
.sm-stat-val { margin-left:auto;color:#f5f7f6;font-weight:650;white-space:nowrap; }
.sm-progress { height:12px;background:#29433b;border-radius:99px;overflow:hidden;margin-top:16px; }
.sm-progress-fill { height:100%;border-radius:99px;background:linear-gradient(90deg,#54d87c,#a7e884); }
.sm-progress-labels { display:flex;justify-content:space-between;gap:8px;margin-top:7px;color:#d0d9d5;font-size:.76rem; }
.sm-status { display:inline-block;border:1px solid #2ea95b;border-radius:30px;padding:2px 10px;color:#71e894;background:rgba(27,111,57,.16);font-size:.75rem; }
.sm-empty { padding:18px;border:1px dashed #557268;border-radius:12px;color:#e1e9e5;text-align:center; }
.stButton > button { border-radius:12px !important; min-height:43px; font-weight:650; border:1px solid #2a4038; }
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primary"] {
    background:linear-gradient(135deg,#b7e99a,#91d978) !important;
    color:#102017 !important;
    border:1px solid #b7e99a !important;
    font-weight:800 !important;
    opacity:1 !important;
}
/* Streamlit may wrap button labels in paragraph/span elements; force contrast there too. */
.stButton > button[kind="primary"] *,
.stButton > button[data-testid="stBaseButton-primary"] *,
button[data-testid="stBaseButton-primary"] * {
    color:#102017 !important;
    fill:#102017 !important;
    opacity:1 !important;
    font-weight:800 !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
.stButton > button[kind="primary"]:focus,
.stButton > button[data-testid="stBaseButton-primary"]:focus,
button[data-testid="stBaseButton-primary"]:focus {
    background:#c5f0aa !important;
    color:#102017 !important;
    border-color:#c5f0aa !important;
}
.stButton > button[kind="secondary"] { background:#172822;color:#ffffff; }
.stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]) { color:#ffffff !important; }
.stDownloadButton > button { background:#172822 !important; color:#ffffff !important; border:1px solid #557268 !important; }
[data-testid="stAlert"] { color:#ffffff !important; }
[data-testid="stDataFrame"] { border:1px solid #233a32;border-radius:12px;overflow:hidden; }
[data-testid="stMetric"] { background:transparent; }
hr { border-color:#233a32 !important; }
@media(max-width:900px) { .sm-drive-body { flex-wrap:wrap; } .sm-ring { width:95px;height:95px; } .sm-ring-inner {width:74px;height:74px;} }
</style>
""", unsafe_allow_html=True)

# Sidebar database connection — keep existing test database and credentials flow.
with st.sidebar:
    st.markdown("<div style='font-size:1.12rem;font-weight:800;color:#f2f6f3'>SMART FILE MANAGER</div><div style='color:#8fa59a;font-size:.78rem;margin-bottom:22px'>OS + DBMS Project</div>", unsafe_allow_html=True)
    st.divider()
    st.subheader("Database Connection")
    db_password = st.text_input("PostgreSQL password", type="password", key="udit_db_password")
    st.caption("Database: smart_file_manager_test")
    st.markdown("<div style='color:#72e895;font-size:.82rem'>● Local PostgreSQL connection</div>", unsafe_allow_html=True)
    st.caption("Built with Python, Streamlit & PostgreSQL")


def get_test_connection(password):
    return psycopg2.connect(
        host="127.0.0.1", port=5432,
        dbname="smart_file_manager_test", user="postgres", password=password,
    )


def load_records(password):
    conn = get_test_connection(password)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT mount_point, filesystem, total_bytes,
                       used_bytes, free_bytes, last_scanned_at
                FROM drives ORDER BY mount_point;
            """)
            drive_df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
            cur.execute("""
                SELECT scan_id, started_at, completed_at, status
                FROM scan_sessions ORDER BY scan_id DESC;
            """)
            sessions_df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
            cur.execute("""
                SELECT d.mount_point, h.total_bytes, h.used_bytes,
                       h.free_bytes, h.captured_at, h.scan_id
                FROM drive_usage_history h
                JOIN drives d ON d.drive_id = h.drive_id
                ORDER BY h.captured_at DESC;
            """)
            history_df = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
        return drive_df, sessions_df, history_df
    finally:
        conn.close()


def gb(value):
    return float(value or 0) / (1024 ** 3)


def fmt_gb(value):
    return f"{gb(value):,.2f} GB"


def safe(value):
    return html.escape(str(value if value is not None else "—"))


def render_kpi(icon, label, value, note, tone="green"):
    tone_class = " gold" if tone == "gold" else (" red" if tone == "red" else "")
    st.markdown(
        f"<div class='sm-card'><div class='sm-kpi'><div class='sm-kpi-icon{tone_class}'>{icon}</div>"
        f"<div><div class='sm-kpi-label'>{safe(label)}</div><div class='sm-kpi-value'>{safe(value)}</div>"
        f"<div class='sm-kpi-note'>{safe(note)}</div></div></div></div>", unsafe_allow_html=True
    )


def render_drive_card(row, index):
    total = int(row.get("total_bytes", 0) or 0)
    used = int(row.get("used_bytes", 0) or 0)
    free = int(row.get("free_bytes", 0) or 0)
    percent = min(100.0, max(0.0, (used / total * 100) if total else 0.0))
    mount = str(row.get("mount_point", "Drive"))
    is_system = mount.upper().startswith("C")
    badge = "System" if is_system else "Data"
    badge_class = "" if is_system else " gold"
    icon = "▦" if is_system else "▱"
    ring_color = "#61df89" if is_system else "#f1c943"
    st.markdown(
        f"<div class='sm-drive'><div class='sm-drive-head'><div class='sm-drive-icon'>{icon}</div>"
        f"<div><div class='sm-drive-name'>{safe(mount)} Drive <span class='sm-pill{badge_class}'>{badge}</span></div>"
        f"<div class='sm-drive-fs'>{safe(row.get('filesystem', 'Unknown filesystem'))} File System</div></div></div>"
        f"<div class='sm-drive-body'><div class='sm-ring' style='background:conic-gradient({ring_color} {percent:.2f}%,#263b35 0)'>"
        f"<div class='sm-ring-inner'><div class='sm-ring-value'>{percent:.2f}%</div><div class='sm-ring-label'>Used</div></div></div>"
        f"<div class='sm-drive-stats'><div class='sm-stat-line'><span class='sm-stat-dot' style='background:#69d987'></span>Total Space<span class='sm-stat-val'>{fmt_gb(total)}</span></div>"
        f"<div class='sm-stat-line'><span class='sm-stat-dot' style='background:#f2cd43'></span>Used Space<span class='sm-stat-val'>{fmt_gb(used)}</span></div>"
        f"<div class='sm-stat-line'><span class='sm-stat-dot' style='background:#aeb9c4'></span>Free Space<span class='sm-stat-val'>{fmt_gb(free)}</span></div></div></div>"
        f"<div class='sm-progress'><div class='sm-progress-fill' style='width:{percent:.2f}%'></div></div>"
        f"<div class='sm-progress-labels'><span>{fmt_gb(used)} used</span><span>{fmt_gb(free)} free</span></div></div>",
        unsafe_allow_html=True,
    )


def section_header(icon, title, caption):
    st.markdown(
        f"<div class='sm-section-head'><div class='sm-section-icon'>{icon}</div><div>"
        f"<div class='sm-section-title'>{safe(title)}</div><div class='sm-section-caption'>{safe(caption)}</div>"
        f"</div></div>", unsafe_allow_html=True
    )


# Header and actions
st.markdown("<div class='sm-title-row'><div class='sm-title-icon' aria-hidden='true'><span style='display:block;width:27px;height:17px;border:3px solid #b5ef96;border-radius:5px;position:relative;box-sizing:border-box'><span style='position:absolute;width:5px;height:3px;background:#b5ef96;right:3px;bottom:2px;border-radius:2px'></span></span></div><div><h1 style='margin:0'>Drive Monitor</h1></div></div>", unsafe_allow_html=True)
head_spacer, head_scan, head_refresh = st.columns([3.0, 1.25, 1.0], vertical_alignment="center")
with head_scan:
    scan_clicked = st.button("Scan drives and save", type="primary", use_container_width=True)
with head_refresh:
    refresh_clicked = st.button("Reset", use_container_width=True)

if "udit_scan_message" in st.session_state:
    st.success(st.session_state.pop("udit_scan_message"))

if scan_clicked:
    if not db_password:
        st.warning("Enter your PostgreSQL password in the sidebar first.")
    else:
        try:
            with st.spinner("Scanning drives and saving history..."):
                detected_drives = get_drive_info()
                if not detected_drives:
                    st.warning("No accessible drives detected.")
                else:
                    scan_id = save_drive_scan(detected_drives)
                    st.session_state["udit_scan_message"] = f"Scan saved successfully. Scan ID: {scan_id}"
                    st.rerun()
        except Exception as error:
            st.error(f"Scan failed: {error}")

if not db_password:
    st.markdown("<div class='sm-empty'>Enter your PostgreSQL password in the sidebar to load live drive details and saved scan history.</div>", unsafe_allow_html=True)
else:
    try:
        drives_df, sessions_df, history_df = load_records(db_password)
        total_drives = len(drives_df)
        total_scans = len(sessions_df)
        total_used = int(drives_df["used_bytes"].fillna(0).sum()) if total_drives else 0
        total_free = int(drives_df["free_bytes"].fillna(0).sum()) if total_drives else 0
        total_space = total_used + total_free

        k1, k2, k3, k4 = st.columns(4, gap="medium")
        with k1: render_kpi("▱", "Registered Drives", total_drives, "Detected storage volumes")
        with k2: render_kpi("▤", "Scan Sessions", total_scans, "Saved in database", "red")
        with k3: render_kpi("◔", "Combined Used", fmt_gb(total_used), "Across all drives")
        with k4: render_kpi("◷", "Combined Free", fmt_gb(total_free), "Available storage", "gold")

        storage_col, distribution_col = st.columns([3.2, 1.0], gap="small")
        with storage_col:
            section_header("▱", "Current Drive Storage", "Detailed information of all registered drives.")
            if drives_df.empty:
                st.markdown("<div class='sm-empty'>No drive records yet. Select <b>Scan drives and save</b> to create the first record.</div>", unsafe_allow_html=True)
            else:
                drive_rows = drives_df.to_dict(orient="records")
                for start in range(0, len(drive_rows), 2):
                    cols = st.columns(2, gap="small")
                    for offset, row in enumerate(drive_rows[start:start + 2]):
                        with cols[offset]:
                            render_drive_card(row, start + offset)
        with distribution_col:
            section_header("◕", "Storage Distribution", "Used vs available space")
            if total_space:
                used_pct = total_used / total_space * 100
                st.markdown(f"<div style='display:flex;justify-content:center;margin:8px 0 16px'><div class='sm-ring' style='width:178px;height:178px;background:conic-gradient(#62dc89 {used_pct:.2f}%,#4b555e 0)'><div class='sm-ring-inner' style='width:135px;height:135px'><div class='sm-ring-value' style='font-size:1.25rem'>{fmt_gb(total_space)}</div><div class='sm-ring-label'>Total space</div></div></div></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sm-stat-line'><span class='sm-stat-dot' style='background:#62dc89'></span>Used Space<span class='sm-stat-val'>{fmt_gb(total_used)} ({used_pct:.2f}%)</span></div><div class='sm-stat-line'><span class='sm-stat-dot' style='background:#4b555e'></span>Free Space<span class='sm-stat-val'>{fmt_gb(total_free)} ({100-used_pct:.2f}%)</span></div>", unsafe_allow_html=True)
            else:
                st.info("No storage data available yet.")
        sess_head, sess_btn = st.columns([4, 1], vertical_alignment="center")
        with sess_head: section_header("▤", "Scan Sessions", "List of drive scan sessions saved in the database.")
        with sess_btn:
            st.download_button("Export sessions ↓", sessions_df.to_csv(index=False).encode("utf-8"), "drive_scan_sessions.csv", "text/csv", use_container_width=True, disabled=sessions_df.empty)
        if sessions_df.empty:
            st.markdown("<div class='sm-empty'>No scan sessions saved yet.</div>", unsafe_allow_html=True)
        else:
            show_sessions = sessions_df.copy()
            if "status" in show_sessions.columns:
                show_sessions["status"] = show_sessions["status"].astype(str).str.title()
            if "started_at" in show_sessions.columns:
                show_sessions["started_at"] = show_sessions["started_at"].astype(str)
            if "completed_at" in show_sessions.columns:
                show_sessions["completed_at"] = show_sessions["completed_at"].astype(str)
            show_sessions.insert(len(show_sessions.columns), "Drives Detected", total_drives)
            st.dataframe(show_sessions, use_container_width=True, hide_index=True)
        hist_head, hist_btn = st.columns([4, 1], vertical_alignment="center")
        with hist_head: section_header("▥", "Drive Usage History", "Historical storage records for each drive from all scan sessions.")
        with hist_btn:
            st.download_button("Export history ↓", history_df.to_csv(index=False).encode("utf-8"), "drive_usage_history.csv", "text/csv", use_container_width=True, disabled=history_df.empty)
        if history_df.empty:
            st.markdown("<div class='sm-empty'>No historical drive usage records yet.</div>", unsafe_allow_html=True)
        else:
            history_display = history_df.copy()
            if "captured_at" in history_display.columns:
                history_display["captured_at"] = history_display["captured_at"].astype(str)
            st.dataframe(history_display, use_container_width=True, hide_index=True)
        st.markdown("<div style='text-align:center;color:#71877c;font-size:.76rem;padding:18px 0 2px'>SMART FILE MANAGER　•　Drive storage, scan history & PostgreSQL</div>", unsafe_allow_html=True)

    except psycopg2.Error as error:
        st.error(f"Could not load test database records: {error}")
    except Exception as error:
        st.error(f"Something went wrong: {error}")
