# ==========================================================
# app.py — TalentAI v4.0  |  Premium Sidebar Design
# Luxury dark theme · Proper sidebar · Mobile responsive
# ==========================================================

import streamlit as st

st.set_page_config(
    page_title="TalentAI — Recruitment Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.database import create_database_if_not_exists

@st.cache_resource
def init_db():
    try:
        create_database_if_not_exists()
        return True
    except Exception as e:
        return str(e)

db_ok = init_db()

from modules import (
    dashboard, analytics, resume_upload, resume_ranking,
    bulk_processing, job_matching, interview_scheduler,
    report_generation, chatbot,
)

# ══════════════════════════════════════════════════════════
# MASTER CSS
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ─── RESET ─── */
*, *::before, *::after { box-sizing: border-box; }

/* ─── APP BACKGROUND ─── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background: #0A0E1A !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #CBD5E1 !important;
}

/* Animated background mesh */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 900px 600px at 15% 0%, rgba(59,130,246,0.07) 0%, transparent 70%),
        radial-gradient(ellipse 700px 500px at 85% 100%, rgba(16,185,129,0.05) 0%, transparent 70%),
        radial-gradient(ellipse 500px 400px at 50% 50%, rgba(139,92,246,0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ─── HIDE DEFAULT STREAMLIT CHROME ─── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
.stDeployButton,
[data-testid="collapsedControl"] { display: none !important; }

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: #0D1117 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    background: transparent !important;
}
[data-testid="stSidebarContent"] {
    background: transparent !important;
    padding: 0 !important;
}

/* Sidebar header */
.sb-header {
    padding: 28px 20px 24px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.05));
}
.sb-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}
.sb-logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #3B82F6, #8B5CF6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 15px rgba(59,130,246,0.4);
}
.sb-logo-text {
    font-family: 'Outfit', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.02em;
}
.sb-logo-sub {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.35);
    font-weight: 400;
    margin-left: 46px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* DB status badge */
.sb-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    margin: 14px 20px 0;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.sb-badge.live {
    background: rgba(16,185,129,0.1);
    color: #10B981;
    border: 1px solid rgba(16,185,129,0.2);
}
.sb-badge.err {
    background: rgba(239,68,68,0.1);
    color: #EF4444;
    border: 1px solid rgba(239,68,68,0.2);
}
.sb-badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    animation: sb-blink 2s ease-in-out infinite;
}
.sb-badge.live .sb-badge-dot { background: #10B981; }
.sb-badge.err  .sb-badge-dot { background: #EF4444; }
@keyframes sb-blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* Section label */
.sb-section-label {
    padding: 22px 20px 8px;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.2);
}

/* Nav items via Streamlit radio */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 2px !important;
    flex-direction: column !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 10px 20px !important;
    margin: 0 !important;
    border-radius: 0 !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,0.5) !important;
    border: none !important;
    background: transparent !important;
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.04) !important;
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-testid*="radio"]:has(input:checked),
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] {
    background: rgba(59,130,246,0.12) !important;
    color: #60A5FA !important;
    border-left: 3px solid #3B82F6 !important;
}
/* hide radio circles */
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child { display: none !important; }

/* Sidebar footer */
.sb-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 16px 20px;
    border-top: 1px solid rgba(255,255,255,0.05);
    background: rgba(0,0,0,0.2);
}
.sb-footer-text {
    font-size: 0.68rem;
    color: rgba(255,255,255,0.2);
    text-align: center;
    letter-spacing: 0.03em;
}

/* ─── MAIN CONTENT ─── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stMain"] .block-container > div:first-child {
    padding: 0 !important;
}

/* ─── PAGE TOPBAR ─── */
.page-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 32px 0;
    margin-bottom: 24px;
}
.page-title-block h1 {
    font-family: 'Outfit', sans-serif;
    font-size: clamp(1.5rem, 2.5vw, 2rem);
    font-weight: 800;
    color: #F1F5F9;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin: 0;
}
.page-title-block p {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.35);
    margin-top: 3px;
    font-weight: 400;
}
.accent { color: #3B82F6; }
.accent-green { color: #10B981; }

/* Breadcrumb-style page path */
.page-breadcrumb {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.2);
    margin-bottom: 4px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 600;
}

/* ─── CONTENT WRAPPER ─── */
.content-area {
    padding: 0 32px 32px;
    position: relative;
    z-index: 1;
}

/* ─── METRIC CARDS ─── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.2s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.4), transparent);
}
[data-testid="stMetric"]:hover {
    border-color: rgba(59,130,246,0.25) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 16px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(59,130,246,0.1) !important;
}
[data-testid="stMetric"] label {
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.35) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #F1F5F9 !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

/* ─── BUTTONS ─── */
.stButton > button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    border-radius: 10px !important;
    padding: 0.52rem 1.3rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #3B82F6 50%, #60A5FA 100%) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.35), inset 0 1px 0 rgba(255,255,255,0.1) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(37,99,235,0.5), inset 0 1px 0 rgba(255,255,255,0.15) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    color: rgba(255,255,255,0.65) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #fff !important;
    border-color: rgba(255,255,255,0.18) !important;
}
.stButton > button:not([kind]) {
    background: rgba(255,255,255,0.04) !important;
    color: rgba(255,255,255,0.6) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
.stButton > button:not([kind]):hover {
    background: rgba(255,255,255,0.07) !important;
    color: rgba(255,255,255,0.9) !important;
}

/* ─── INPUTS ─── */
.stTextInput > div > div > input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.87rem !important;
    transition: all 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: rgba(59,130,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    background: rgba(59,130,246,0.04) !important;
}
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label,
.stDateInput label, .stTimeInput label,
.stMultiselect label, .stSlider label,
.stRadio > label, .stFileUploader label,
[data-testid="stWidgetLabel"] {
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: rgba(59,130,246,0.4) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}
[data-baseweb="menu"] {
    background: #151C2C !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
[data-baseweb="option"] { background: transparent !important; color: #CBD5E1 !important; }
[data-baseweb="option"]:hover { background: rgba(59,130,246,0.12) !important; }

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(255,255,255,0.4) !important;
    border-radius: 9px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 7px 16px !important;
    border: none !important;
    transition: all 0.18s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: rgba(255,255,255,0.75) !important; }
.stTabs [aria-selected="true"] {
    background: rgba(59,130,246,0.15) !important;
    color: #60A5FA !important;
}

/* ─── DATAFRAME ─── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    overflow: hidden !important;
}

/* ─── EXPANDERS ─── */
details {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    margin-bottom: 6px !important;
    overflow: hidden !important;
    transition: border-color 0.2s !important;
}
details:hover { border-color: rgba(59,130,246,0.2) !important; }
details summary {
    padding: 12px 16px !important;
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.87rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
}
details > div { padding: 0 16px 16px !important; }

/* ─── ALERTS ─── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-size: 0.84rem !important;
    border-width: 1px !important;
}
[data-testid="stAlert"][data-baseweb="notification"] { border-radius: 12px !important; }
.stSuccess > div, [data-testid="stAlert"][kind="success"] {
    background: rgba(16,185,129,0.07) !important;
    border-color: rgba(16,185,129,0.2) !important;
    color: #6EE7B7 !important;
}
.stInfo > div, [data-testid="stAlert"][kind="info"] {
    background: rgba(59,130,246,0.07) !important;
    border-color: rgba(59,130,246,0.2) !important;
    color: #93C5FD !important;
}
.stWarning > div, [data-testid="stAlert"][kind="warning"] {
    background: rgba(245,158,11,0.07) !important;
    border-color: rgba(245,158,11,0.2) !important;
    color: #FCD34D !important;
}
.stError > div, [data-testid="stAlert"][kind="error"] {
    background: rgba(239,68,68,0.07) !important;
    border-color: rgba(239,68,68,0.2) !important;
    color: #FCA5A5 !important;
}

/* ─── FILE UPLOADER ─── */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.02) !important;
    border: 2px dashed rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(59,130,246,0.4) !important;
    background: rgba(59,130,246,0.03) !important;
}

/* ─── PROGRESS ─── */
[data-testid="stProgressBar"] > div {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 999px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #2563EB, #10B981) !important;
    border-radius: 999px !important;
}

/* ─── SLIDER ─── */
[data-baseweb="slider"] [role="slider"] {
    background: #3B82F6 !important;
    border: 2px solid rgba(255,255,255,0.8) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.25) !important;
}
[data-baseweb="slider"] [data-testid="stThumbValue"] { color: #60A5FA !important; }

/* ─── CHAT ─── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
}
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #E2E8F0 !important;
}

/* ─── DOWNLOAD BUTTON ─── */
[data-testid="stDownloadButton"] > button {
    background: rgba(16,185,129,0.1) !important;
    color: #34D399 !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(16,185,129,0.18) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(16,185,129,0.2) !important;
}

/* ─── DIVIDER ─── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 20px 0 !important; }

/* ─── MULTISELECT TAGS ─── */
[data-baseweb="tag"] {
    background: rgba(59,130,246,0.15) !important;
    border-color: rgba(59,130,246,0.25) !important;
    border-radius: 6px !important;
    color: #93C5FD !important;
}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }

/* ─── PLOTLY ─── */
.js-plotly-plot .plotly * { font-family: 'Plus Jakarta Sans', sans-serif !important; }

/* ─── CARD COMPONENT ─── */
.stat-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: all 0.2s ease;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.5), transparent);
}
.stat-card:hover {
    border-color: rgba(59,130,246,0.2);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3);
}

/* ─── PAGE CARD WRAPPER ─── */
.page-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
}

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { width: 220px !important; }
    .content-area { padding: 0 16px 20px !important; }
    .page-topbar { padding: 16px 16px 0 !important; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
}
@media (max-width: 480px) {
    [data-testid="stSidebar"] { width: 200px !important; }
    .content-area { padding: 0 10px 16px !important; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    # Logo header
    badge_cls = "live" if db_ok is True else "err"
    badge_label = "MySQL Live" if db_ok is True else "DB Error"
    st.markdown(f"""
    <div class="sb-header">
      <div class="sb-logo">
        <div class="sb-logo-icon">⚡</div>
        <span class="sb-logo-text">TalentAI</span>
      </div>
      <div class="sb-logo-sub">Enterprise Recruitment</div>
      <div class="sb-badge {badge_cls}">
        <span class="sb-badge-dot"></span>
        {badge_label}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-label">Main Navigation</div>', unsafe_allow_html=True)

    NAV = {
        "📊  Dashboard":       "Dashboard",
        "📂  Resume Upload":   "Resume Upload",
        "🤖  AI Ranking":      "AI Ranking",
        "⚡  Bulk Processing": "Bulk Processing",
        "🎯  Job Matching":    "Job Matching",
        "📅  Interviews":      "Interviews",
        "📈  Analytics":       "Analytics",
        "📄  Reports":         "Reports",
        "💬  Chatbot":         "Chatbot",
    }

    choice = st.radio(
        "nav",
        list(NAV.keys()),
        label_visibility="collapsed",
    )
    active_page = NAV[choice]

    st.markdown('<div class="sb-section-label" style="margin-top:16px">Quick Actions</div>', unsafe_allow_html=True)
    if st.button("🔄  Refresh Data", use_container_width=True, type="secondary"):
        st.cache_resource.clear()
        st.rerun()

    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;width:260px;padding:14px 20px;
         border-top:1px solid rgba(255,255,255,0.05);
         background:rgba(13,17,23,0.9);backdrop-filter:blur(10px);">
      <div style="font-size:0.65rem;color:rgba(255,255,255,0.18);text-align:center;letter-spacing:0.04em;">
        TalentAI v4.0 &nbsp;·&nbsp; MySQL + AI Powered
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE TITLES MAP
# ══════════════════════════════════════════════════════════
PAGE_META = {
    "Dashboard":      ("📊", "Dashboard",      "Live recruitment metrics from MySQL"),
    "Resume Upload":  ("📂", "Resume Upload",   "Parse · Score · Store resumes automatically"),
    "AI Ranking":     ("🤖", "AI Ranking",      "BERT-powered candidate ranking & status management"),
    "Bulk Processing":("⚡", "Bulk Processing", "Mass re-score, update or delete candidates"),
    "Job Matching":   ("🎯", "Job Matching",    "Match all candidates against any job description"),
    "Interviews":     ("📅", "Interviews",      "Schedule and manage the full interview pipeline"),
    "Analytics":      ("📈", "Analytics",       "Visual hiring insights powered by live MySQL data"),
    "Reports":        ("📄", "Reports",         "Export CSV and multi-sheet Excel reports"),
    "Chatbot":        ("💬", "HR Chatbot",      "Ask anything — powered by your live MySQL data"),
}

icon, title, subtitle = PAGE_META[active_page]

st.markdown(f"""
<div class="page-topbar">
  <div class="page-title-block">
    <div class="page-breadcrumb">TalentAI &rsaquo; {title}</div>
    <h1>{icon} &nbsp;<span class="accent">{title}</span></h1>
    <p>{subtitle}</p>
  </div>
</div>
<div class="content-area">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ROUTE
# ══════════════════════════════════════════════════════════
if   active_page == "Dashboard":       dashboard.run()
elif active_page == "Resume Upload":   resume_upload.run()
elif active_page == "AI Ranking":      resume_ranking.run()
elif active_page == "Bulk Processing": bulk_processing.run()
elif active_page == "Job Matching":    job_matching.run()
elif active_page == "Interviews":      interview_scheduler.run()
elif active_page == "Analytics":       analytics.run()
elif active_page == "Reports":         report_generation.run()
elif active_page == "Chatbot":         chatbot.run()

st.markdown("</div>", unsafe_allow_html=True)
