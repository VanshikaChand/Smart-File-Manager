import streamlit as st


# Shared Midnight Charcoal analytics design system.
# Page-specific layout and backend logic should stay in the page files.
def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
            --sfm-bg: #080f0d;
            --sfm-panel: #0e1915;
            --sfm-panel-raised: #12221b;
            --sfm-border: #263d33;
            --sfm-text: #f0f5f1;
            --sfm-text-soft: #c1cec6;
            --sfm-muted: #94a69b;
            --sfm-green: #a8edbd;
            --sfm-green-strong: #46d982;
        }
        html, body, [class*="css"] { font-family: Inter, "Segoe UI", sans-serif; }
        .stApp {
            background: radial-gradient(ellipse at 78% 0%, rgba(34,88,61,.18), transparent 36%), var(--sfm-bg);
            color: var(--sfm-text);
        }
        [data-testid="stHeader"] { background: rgba(8,15,13,.88); }
        .block-container { max-width: 1600px; padding: 2rem clamp(1rem,3vw,3rem) 3rem; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg,#0d1914 0%,#0a120f 100%); border-right: 1px solid var(--sfm-border); }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
        .sfm-brand { display:flex; align-items:center; gap:.8rem; padding:.35rem .2rem 1.4rem; border-bottom:1px solid var(--sfm-border); margin-bottom:1.2rem; }
        .sfm-brand-mark { width:42px; height:42px; display:flex; align-items:center; justify-content:center; border-radius:13px; background:linear-gradient(145deg,#a8edbd,#3ecb7b); color:#082014; font-size:.9rem; font-weight:850; letter-spacing:-.05em; }
        .sfm-brand-title { color:var(--sfm-text); font-size:.77rem; font-weight:800; letter-spacing:.06em; }
        .sfm-brand-subtitle { color:var(--sfm-muted); font-size:.65rem; letter-spacing:.09em; margin-top:.22rem; }
        .sfm-sidebar-section,.sfm-eyebrow,.sfm-section-kicker { color:#81a991; font-size:.66rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase; margin-bottom:.55rem; }
        [data-testid="stSidebar"] [data-testid="stRadio"] > label { color:var(--sfm-muted)!important; font-size:.83rem; font-weight:650; }
        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] { gap:.25rem; }
        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label { border:1px solid transparent; border-radius:10px; padding:.5rem .65rem; margin:0; }
        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover { background:#15271e; border-color:#294838; }
        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) { background:#173a29; border-color:#2c6645; color:var(--sfm-green)!important; }
        [data-testid="stSidebar"] [data-testid="stRadio"] label p { color:inherit!important; }
        .sfm-sidebar-bottom { border-top:1px solid var(--sfm-border); margin-top:2rem; padding-top:1rem; }
        .sfm-connection-dot,.sfm-status-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--sfm-green-strong); box-shadow:0 0 10px rgba(70,217,130,.4); margin-right:.45rem; vertical-align:middle; }
        .sfm-connection-label { color:#b6c9bd; font-size:.67rem; font-weight:750; letter-spacing:.08em; }
        h1,h2,h3,h4 { color:var(--sfm-text)!important; font-weight:750!important; letter-spacing:-.035em; }
        h1 { font-size:clamp(2rem,3vw,2.7rem)!important; line-height:1.12!important; margin-bottom:.35rem!important; }
        h2 { font-size:1.65rem!important; } h3 { font-size:1.15rem!important; }
        p,li,label,[data-testid="stMarkdownContainer"] { color:var(--sfm-text-soft); }
        .sfm-page-subtitle,.sfm-muted-copy { color:var(--sfm-muted); font-size:.91rem; line-height:1.65; }
        .sfm-header-rule { height:1px; background:linear-gradient(90deg,#355744,rgba(53,87,68,.05)); margin:1.5rem 0 1.8rem; }
        .sfm-status-pill { display:inline-flex; align-items:center; white-space:nowrap; border:1px solid #2c4a3a; background:rgba(18,43,30,.78); border-radius:999px; color:#b9d7c3; font-size:.66rem; font-weight:750; letter-spacing:.05em; padding:.55rem .8rem; }
        .sfm-section-heading-row { display:flex; justify-content:space-between; align-items:end; gap:1rem; margin:1.9rem 0 .9rem; }
        .sfm-section-heading-row h3 { margin:0; }
        .sfm-context-strip { display:flex; align-items:center; flex-wrap:wrap; gap:.7rem 1rem; background:#0d1b15; border:1px solid var(--sfm-border); border-radius:11px; padding:.8rem 1rem; margin:1.1rem 0 1.5rem; }
        .sfm-context-label { color:#7d9d89; font-size:.65rem; font-weight:800; letter-spacing:.12em; }
        .sfm-context-value { color:#d5e5db; font-size:.82rem; overflow-wrap:anywhere; }
        .sfm-inline-hint { color:var(--sfm-muted); font-size:.82rem; line-height:1.5; padding:.35rem 0; }
        .sfm-empty-state { border:1px dashed #355443; background:rgba(14,28,21,.7); border-radius:15px; padding:2rem; text-align:center; margin-top:.7rem; }
        .sfm-empty-state-title { color:var(--sfm-text); font-size:1rem; font-weight:750; margin-bottom:.35rem; }
        .sfm-empty-state-copy { color:var(--sfm-muted); font-size:.86rem; line-height:1.6; }
        [data-testid="stMetric"] { background:linear-gradient(145deg,#13251c 0%,#0e1a15 100%); border:1px solid var(--sfm-border); border-radius:15px; padding:1.1rem 1.15rem; min-height:108px; box-shadow:0 8px 24px rgba(0,0,0,.12); transition:transform 160ms ease,border-color 160ms ease; }
        [data-testid="stMetric"]:hover { border-color:#426b52; transform:translateY(-2px); }
        [data-testid="stMetricLabel"] { color:#a8bdb0!important; font-size:.78rem!important; font-weight:600!important; }
        [data-testid="stMetricValue"] { color:var(--sfm-green)!important; font-size:clamp(1.35rem,2vw,1.9rem)!important; font-weight:780!important; letter-spacing:-.04em; }
        .stButton > button,.stDownloadButton > button,[data-testid="stFormSubmitButton"] button { background:#a8edbd; color:#092014!important; border:1px solid #b7f4c8; border-radius:10px; min-height:2.65rem; padding:.55rem 1rem; font-size:.84rem; font-weight:800; box-shadow:none; transition:background 150ms ease,transform 150ms ease; }
        .stButton > button p,.stDownloadButton > button p,[data-testid="stFormSubmitButton"] button p { color:#092014!important; font-weight:800!important; }
        .stButton > button:hover,[data-testid="stFormSubmitButton"] button:hover { background:#c2f6ce; color:#06190e!important; border-color:#d4ffdf; transform:translateY(-1px); }
        .stButton > button:focus-visible,.stDownloadButton > button:focus-visible { outline:2px solid #f0fff4; outline-offset:2px; box-shadow:0 0 0 4px rgba(168,237,189,.25); }
        .stDownloadButton > button { background:#15291f; color:#d7e9de!important; border-color:#365846; }
        .stDownloadButton > button p { color:#d7e9de!important; }
        .stDownloadButton > button:hover { background:#1b3929; border-color:#4b795d; }
        .stTextInput input,.stTextArea textarea,.stNumberInput input { background:#0d1914!important; color:var(--sfm-text)!important; border:1px solid #30483a!important; border-radius:10px!important; min-height:2.65rem; }
        .stTextInput input::placeholder,.stTextArea textarea::placeholder { color:#71877a!important; }
        .stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus { border-color:#70b88a!important; box-shadow:0 0 0 1px #70b88a!important; }
        .stTextInput label,.stTextArea label,.stSelectbox label,.stRadio label,.stCheckbox label,.stNumberInput label { color:#c5d5cb!important; font-size:.83rem!important; font-weight:600!important; }
        [data-baseweb="select"] > div,[data-baseweb="popover"] { background:#0d1914!important; border-color:#30483a!important; color:var(--sfm-text)!important; }
        [data-baseweb="menu"] { background:#102019!important; border:1px solid #30483a!important; }
        [data-baseweb="menu"] li,[role="option"] { color:var(--sfm-text-soft)!important; }
        [data-testid="stVerticalBlockBorderWrapper"] > div { border-color:var(--sfm-border)!important; border-radius:14px!important; }
        [data-testid="stDataFrame"],[data-testid="stTable"] { border:1px solid var(--sfm-border); border-radius:12px; overflow:hidden; }
        [data-testid="stAlert"] { border-radius:11px; border:1px solid var(--sfm-border); }
        [data-testid="stCaptionContainer"],.stCaption { color:var(--sfm-muted)!important; }
        hr { border-color:var(--sfm-border)!important; margin-top:1.25rem; margin-bottom:1.25rem; }
        .stSpinner > div { border-top-color:var(--sfm-green-strong)!important; }
        * { scrollbar-color:#355443 #0b1510; scrollbar-width:thin; }
        @media (max-width:900px) { .block-container { padding:1.25rem 1rem 2rem; } .sfm-status-pill { display:none; } [data-testid="stMetric"] { min-height:95px; padding:.85rem; } }
        @media (max-width:600px) { h1 { font-size:1.8rem!important; } .sfm-context-strip { align-items:flex-start; flex-direction:column; } }
        </style>
        """,
        unsafe_allow_html=True,
    )
