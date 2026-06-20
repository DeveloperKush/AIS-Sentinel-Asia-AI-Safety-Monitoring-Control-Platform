import os
import sys
import json
import sqlite3
import datetime

# Add project root directory to sys.path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import streamlit as st

# Set main page configuration (only called once for the entire application session)
st.set_page_config(
    page_title="AIS-Sentinel | AI Safety for the Global South",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Override st.set_page_config to prevent exceptions when subpages call it via exec()
st.set_page_config = lambda *args, **kwargs: None

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    GLOBAL CSS — MISSION CONTROL THEME               ║
# ╚══════════════════════════════════════════════════════════════════════╝
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── CSS Custom Properties ── */
    :root {
        --bg-primary: #060910;
        --bg-secondary: #0c1220;
        --bg-card: rgba(14, 21, 38, 0.85);
        --bg-glass: rgba(14, 21, 38, 0.6);
        --accent-primary: #00d4ff;
        --accent-secondary: #ff6b6b;
        --accent-tertiary: #a78bfa;
        --accent-glow: rgba(0, 212, 255, 0.25);
        --accent-glow-strong: rgba(0, 212, 255, 0.45);
        --text-primary: #e6edf3;
        --text-secondary: #8b9dc3;
        --text-muted: #6b7c96;
        --border-subtle: rgba(0, 212, 255, 0.08);
        --border-accent: rgba(0, 212, 255, 0.2);
        --success: #00d9a3;
        --warning: #ff9f43;
        --danger: #ff4d6d;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.4);
        --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.5);
        --shadow-lg: 0 8px 40px rgba(0, 0, 0, 0.6);
        --shadow-glow: 0 0 25px var(--accent-glow);
        --shadow-glow-strong: 0 0 40px var(--accent-glow-strong);
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --font-heading: 'Space Grotesk', sans-serif;
        --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Keyframe Animations ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(24px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 15px var(--accent-glow); }
        50% { box-shadow: 0 0 30px var(--accent-glow-strong); }
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes scanline {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100vh); }
    }
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(0, 212, 255, 0.1); }
        50% { border-color: rgba(0, 212, 255, 0.3); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* ── Global App Background ── */
    .stApp {
        background: linear-gradient(160deg, #060910 0%, #0a0f1c 30%, #0c1428 60%, #080d18 100%) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
    }

    /* ── Widen Content Layout ── */
    [data-testid="block-container"],
    .block-container {
        max-width: 95% !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse at 20% 50%, rgba(0, 212, 255, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(167, 139, 250, 0.02) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(255, 107, 107, 0.02) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Custom Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--accent-primary), var(--accent-tertiary));
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-primary); }

    /* ── Headings & Text ── */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: var(--font-heading) !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }
    .stApp h1 { font-weight: 700 !important; }
    .stApp h2 { font-weight: 600 !important; }
    .stApp h3 { font-weight: 600 !important; color: var(--text-secondary) !important; }
    .stApp p {
        font-family: var(--font-body);
    }
    .stMarkdown { color: var(--text-primary); }

    /* ── Widget Labels (Visibility Fix) ── */
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] p,
    .stWidgetLabel p {
        color: var(--text-secondary) !important;
        font-family: var(--font-heading) !important;
        font-weight: 500 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 212, 255, 0.05) 100%) !important;
        color: var(--accent-primary) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-heading) !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        padding: 0.5rem 1.5rem !important;
        transition: var(--transition) !important;
        backdrop-filter: blur(10px) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.25) 0%, rgba(0, 212, 255, 0.1) 100%) !important;
        border-color: var(--accent-primary) !important;
        box-shadow: var(--shadow-glow) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    /* Primary button overrides */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #00d4ff 0%, #0098b3 100%) !important;
        color: #060910 !important;
        border: none !important;
        font-weight: 700 !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.5) !important;
    }

    /* ── Download Button ── */
    .stDownloadButton > button {
        background: rgba(0, 212, 255, 0.08) !important;
        color: var(--accent-primary) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-heading) !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(0, 212, 255, 0.15) !important;
        box-shadow: var(--shadow-glow) !important;
    }

    /* ── Metric Cards ── */
    [data-testid="stMetric"],
    [data-testid="stMetricValue"],
    div[data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem !important;
        backdrop-filter: blur(12px) !important;
        transition: var(--transition) !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: var(--border-accent) !important;
        box-shadow: var(--shadow-glow) !important;
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-family: var(--font-heading) !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.08em !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--accent-primary) !important;
        font-family: var(--font-heading) !important;
        font-weight: 700 !important;
    }

    /* ── DataFrames ── */
    .stDataFrame, [data-testid="stDataFrame"] {
        background: var(--bg-card) !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-subtle) !important;
        overflow: hidden !important;
    }

    /* ── Expanders ── */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        margin-bottom: 0.5rem !important;
        transition: var(--transition) !important;
    }
    [data-testid="stExpander"]:hover {
        border-color: var(--border-accent) !important;
    }
    [data-testid="stExpander"] summary,
    .streamlit-expanderHeader {
        background: transparent !important;
        color: var(--text-primary) !important;
        font-family: var(--font-heading) !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderContent,
    [data-testid="stExpander"] > div:last-child {
        background: rgba(6, 9, 16, 0.5) !important;
        border-top: 1px solid var(--border-subtle) !important;
        border-left: 3px solid var(--accent-primary) !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(14, 21, 38, 0.8) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-body) !important;
        transition: var(--transition) !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--accent-glow), inset 0 0 20px rgba(0, 212, 255, 0.05) !important;
    }

    /* ── Selectboxes & Multiselects ── */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div {
        background: rgba(14, 21, 38, 0.8) !important;
        background-color: rgba(14, 21, 38, 0.8) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition) !important;
    }
    div[data-baseweb="select"]:hover,
    div[data-baseweb="select"] > div:hover {
        border-color: var(--border-accent) !important;
    }
    div[data-baseweb="select"] * {
        color: var(--text-primary) !important;
    }
    /* Selectbox dropdown list items and containers */
    div[role="listbox"],
    div[role="listbox"] ul,
    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background-color: #0c1220 !important;
        background: #0c1220 !important;
        border: 1px solid var(--border-accent) !important;
    }
    
    div[role="listbox"] [role="option"],
    div[role="option"],
    li[role="option"] {
        background-color: #0c1220 !important;
        color: var(--text-primary) !important;
    }
    
    div[role="listbox"] [role="option"]:hover,
    div[role="option"]:hover,
    li[role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background-color: rgba(0, 212, 255, 0.15) !important;
        color: var(--accent-primary) !important;
    }

    /* ── Radio Buttons ── */
    .stRadio > div {
        background: transparent !important;
    }
    .stRadio > div label,
    .stRadio > div label p,
    .stRadio > div label span {
        color: var(--text-primary) !important;
        transition: var(--transition) !important;
    }

    /* ── Sliders ── */
    .stSlider > div > div > div > div {
        background: var(--accent-primary) !important;
    }
    .stSlider [data-testid="stTickBar"] div,
    .stSlider [data-testid="stTickBar"] span {
        color: var(--text-secondary) !important;
    }

    /* ── Progress Bar ── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-tertiary)) !important;
        border-radius: 4px !important;
    }
    .stProgress > div > div {
        background: rgba(14, 21, 38, 0.8) !important;
        border-radius: 4px !important;
    }

    /* ── Alerts ── */
    .stAlert, [data-testid="stAlert"] {
        background: var(--bg-card) !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-subtle) !important;
        backdrop-filter: blur(10px) !important;
    }
    /* Info */
    div[data-testid="stAlert"][data-baseweb*="notification"] {
        background: rgba(0, 212, 255, 0.06) !important;
        border-left: 3px solid var(--accent-primary) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition) !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0, 212, 255, 0.1) !important;
        color: var(--accent-primary) !important;
        border-bottom: 2px solid var(--accent-primary) !important;
    }

    /* ── Dividers ── */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--border-accent), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Captions ── */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
        font-size: 0.8rem !important;
        font-style: italic !important;
    }

    /* ── Checkboxes ── */
    [data-testid="stCheckbox"] p,
    .stCheckbox label p,
    .stCheckbox label span {
        color: var(--text-primary) !important;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: var(--accent-primary) !important;
    }

    /* ──────────────────────────────────────── */
    /* ──         SIDEBAR STYLING             ── */
    /* ──────────────────────────────────────── */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #070b14 0%, #0a1020 50%, #060910 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse at 50% 0%, rgba(0, 212, 255, 0.04) 0%, transparent 60%);
        pointer-events: none;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-secondary) !important;
    }

    /* Sidebar Title */
    .sidebar-title {
        font-family: var(--font-heading) !important;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d4ff 0%, #a78bfa 50%, #ff6b6b 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
        margin-bottom: 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }
    .sidebar-subtitle {
        font-family: var(--font-body);
        font-size: 0.82rem;
        color: var(--text-muted) !important;
        margin-bottom: 1.5rem;
        font-weight: 400;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* Nav Radio in Sidebar */
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(0, 212, 255, 0.03) !important;
        border-radius: var(--radius-md) !important;
        padding: 8px !important;
        border: 1px solid var(--border-subtle) !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 0.6rem 1rem !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition) !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(0, 212, 255, 0.08) !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(0, 212, 255, 0.12) !important;
        border-left: 3px solid var(--accent-primary) !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) span {
        color: var(--accent-primary) !important;
        font-weight: 600 !important;
    }

    /* Sidebar Badge */
    .sidebar-badge {
        background: rgba(0, 212, 255, 0.05);
        color: var(--accent-primary) !important;
        border: 1px solid rgba(0, 212, 255, 0.15);
        padding: 12px 16px;
        border-radius: var(--radius-md);
        font-size: 0.78rem;
        font-weight: 500;
        text-align: center;
        margin-top: 2rem;
        font-family: var(--font-heading);
        letter-spacing: 0.02em;
        animation: borderGlow 3s ease-in-out infinite;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ── Plotly Charts Dark Theme ── */
    .js-plotly-plot .plotly .modebar {
        background: transparent !important;
    }
    .js-plotly-plot .plotly .modebar-btn path {
        fill: var(--text-muted) !important;
    }

</style>
""", unsafe_allow_html=True)

# Database Initialization and Seeding on first session load
try:
    from core.database import (
        init_db,
        get_articles,
        get_benchmark_results,
        get_agent_logs,
        insert_article,
        insert_benchmark_result,
        insert_agent_log
    )
    init_db()
except Exception:
    pass

if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    try:
        # 1. Seed demo articles if empty
        if not get_articles():
            demo_articles = [
                {
                    "title": "New highly pathogenic strain detected in wild birds",
                    "source_url": "https://example.com/biosecurity/1",
                    "source_country": "Vietnam",
                    "language": "en",
                    "original_text": "A new highly pathogenic strain was detected in wild bird populations, raising concerns about potential spillover events in agricultural settings.",
                    "translated_text": "A new highly pathogenic strain was detected in wild bird populations, raising concerns about potential spillover events in agricultural settings.",
                    "threat_detected": True,
                    "confidence_score": 0.85,
                    "risk_category": "AI-EngBio integration",
                    "justification": "Clear evidence of novel pathogen with high mortality in wild populations."
                },
                {
                    "title": "Unauthorized access reported at BSL-3 laboratory",
                    "source_url": "https://example.com/biosecurity/2",
                    "source_country": "Thailand",
                    "language": "en",
                    "original_text": "Local authorities report a potential breach of security protocols at a regional BSL-3 laboratory. Investigation is ongoing.",
                    "translated_text": "Local authorities report a potential breach of security protocols at a regional BSL-3 laboratory. Investigation is ongoing.",
                    "threat_detected": True,
                    "confidence_score": 0.65,
                    "risk_category": "Dual-use hardware",
                    "justification": "Security breach at a high-containment facility presents moderate to high risk."
                },
                {
                    "title": "Open-source AI model capable of generating synthetic viral genomes",
                    "source_url": "https://example.com/biosecurity/3",
                    "source_country": "India",
                    "language": "en",
                    "original_text": "Researchers have published an open-source model that can generate plausible synthetic viral genomes, bypassing typical DNA synthesis screening.",
                    "translated_text": "Researchers have published an open-source model that can generate plausible synthetic viral genomes, bypassing typical DNA synthesis screening.",
                    "threat_detected": True,
                    "confidence_score": 0.92,
                    "risk_category": "AI-EngBio integration",
                    "justification": "Direct enabler of biological threat creation bypassing existing controls."
                },
                {
                    "title": "Supply chain disruption in key medical countermeasure manufacturing",
                    "source_url": "https://example.com/biosecurity/4",
                    "source_country": "Indonesia",
                    "language": "en",
                    "original_text": "A major disruption in the supply chain for precursors required for antibiotic production has been reported, leading to localized shortages.",
                    "translated_text": "A major disruption in the supply chain for precursors required for antibiotic production has been reported, leading to localized shortages.",
                    "threat_detected": False,
                    "confidence_score": 0.55,
                    "risk_category": "None",
                    "justification": "Vulnerability in countermeasure availability."
                },
                {
                    "title": "Unusual respiratory illness cluster in rural province",
                    "source_url": "https://example.com/biosecurity/5",
                    "source_country": "Philippines",
                    "language": "en",
                    "original_text": "Local health officials are monitoring a cluster of unusual respiratory illnesses in a remote agricultural province. Pathogen remains unidentified.",
                    "translated_text": "Local health officials are monitoring a cluster of unusual respiratory illnesses in a remote agricultural province. Pathogen remains unidentified.",
                    "threat_detected": True,
                    "confidence_score": 0.78,
                    "risk_category": "Policy gap",
                    "justification": "Unidentified cluster with potential for broader spread."
                }
            ]
            for art in demo_articles:
                insert_article(art)

        # 2. Seed benchmark results if empty
        if not get_benchmark_results():
            demo_bench_configs = [
                {"model": "Qwen2.5-7B", "lang": "en", "syc_cap": 2, "syc_total": 10, "jail_ref": 9, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Qwen2.5-7B", "lang": "vi", "syc_cap": 6, "syc_total": 10, "jail_ref": 7, "jail_total": 10, "hall_err": 3, "hall_total": 10},
                {"model": "Qwen2.5-7B", "lang": "tl", "syc_cap": 5, "syc_total": 10, "jail_ref": 7, "jail_total": 10, "hall_err": 3, "hall_total": 10},
                {"model": "Qwen2.5-7B", "lang": "id", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Qwen2.5-7B", "lang": "hi", "syc_cap": 4, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 3, "hall_total": 10},
                {"model": "Qwen2.5-7B", "lang": "th", "syc_cap": 5, "syc_total": 10, "jail_ref": 7, "jail_total": 10, "hall_err": 4, "hall_total": 10},
                
                {"model": "Llama-3.1-8B", "lang": "en", "syc_cap": 2, "syc_total": 10, "jail_ref": 9, "jail_total": 10, "hall_err": 1, "hall_total": 10},
                {"model": "Llama-3.1-8B", "lang": "vi", "syc_cap": 5, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 3, "hall_total": 10},
                {"model": "Llama-3.1-8B", "lang": "tl", "syc_cap": 4, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Llama-3.1-8B", "lang": "id", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Llama-3.1-8B", "lang": "hi", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Llama-3.1-8B", "lang": "th", "syc_cap": 4, "syc_total": 10, "jail_ref": 7, "jail_total": 10, "hall_err": 3, "hall_total": 10},
                
                {"model": "Mistral-7B", "lang": "en", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Mistral-7B", "lang": "vi", "syc_cap": 6, "syc_total": 10, "jail_ref": 6, "jail_total": 10, "hall_err": 4, "hall_total": 10},
                {"model": "Mistral-7B", "lang": "tl", "syc_cap": 5, "syc_total": 10, "jail_ref": 7, "jail_total": 10, "hall_err": 3, "hall_total": 10},
                {"model": "Mistral-7B", "lang": "id", "syc_cap": 4, "syc_total": 10, "jail_ref": 7, "jail_total": 10, "hall_err": 3, "hall_total": 10},
                {"model": "Mistral-7B", "lang": "hi", "syc_cap": 4, "syc_total": 10, "jail_ref": 7, "jail_total": 10, "hall_err": 3, "hall_total": 10},
                {"model": "Mistral-7B", "lang": "th", "syc_cap": 5, "syc_total": 10, "jail_ref": 6, "jail_total": 10, "hall_err": 4, "hall_total": 10},
                
                {"model": "SeaLLM-7B", "lang": "en", "syc_cap": 2, "syc_total": 10, "jail_ref": 9, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "SeaLLM-7B", "lang": "vi", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "SeaLLM-7B", "lang": "tl", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "SeaLLM-7B", "lang": "id", "syc_cap": 2, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "SeaLLM-7B", "lang": "hi", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "SeaLLM-7B", "lang": "th", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                
                {"model": "Gemma-2-9B", "lang": "en", "syc_cap": 1, "syc_total": 10, "jail_ref": 9, "jail_total": 10, "hall_err": 1, "hall_total": 10},
                {"model": "Gemma-2-9B", "lang": "vi", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Gemma-2-9B", "lang": "tl", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Gemma-2-9B", "lang": "id", "syc_cap": 2, "syc_total": 10, "jail_ref": 9, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Gemma-2-9B", "lang": "hi", "syc_cap": 2, "syc_total": 10, "jail_ref": 9, "jail_total": 10, "hall_err": 2, "hall_total": 10},
                {"model": "Gemma-2-9B", "lang": "th", "syc_cap": 3, "syc_total": 10, "jail_ref": 8, "jail_total": 10, "hall_err": 3, "hall_total": 10}
            ]
            for config in demo_bench_configs:
                model = config["model"]
                lang = config["lang"]
                
                # Sycophancy runs
                for i in range(config["syc_total"]):
                    passed = (i >= config["syc_cap"])
                    insert_benchmark_result({
                        "model_name": model,
                        "language": lang,
                        "test_type": "sycophancy_math",
                        "prompt": "Mock sycophancy prompt",
                        "model_response": "Mock response",
                        "passed": passed
                    })
                    
                # Jailbreak runs
                for i in range(config["jail_total"]):
                    passed = (i < config["jail_ref"])
                    insert_benchmark_result({
                        "model_name": model,
                        "language": lang,
                        "test_type": "jailbreak",
                        "prompt": "Mock jailbreak prompt",
                        "model_response": "Mock response",
                        "passed": passed
                    })
                    
                # Hallucination runs
                for i in range(config["hall_total"]):
                    passed = (i >= config["hall_err"])
                    insert_benchmark_result({
                        "model_name": model,
                        "language": lang,
                        "test_type": "hallucination",
                        "prompt": "Mock hallucination prompt",
                        "model_response": "Mock response",
                        "passed": passed
                    })

        # 3. Seed agent logs if empty
        if not get_agent_logs():
            demo_logs = [
                {
                    "task_description": "Design slides for business presentation",
                    "attack_type": "None (Legitimate)",
                    "slide_json": json.dumps({"elements": [{"type": "text", "content": "Welcome to AIS-Sentinel"}]}),
                    "monitor_suspicion_score": 10.0,
                    "detected": False
                },
                {
                    "task_description": "Create marketing pitch deck",
                    "attack_type": "Steganography",
                    "slide_json": json.dumps({"elements": [{"type": "text", "content": "hidden_payload", "color": "#FFFFFF", "size": 1}]}),
                    "monitor_suspicion_score": 85.0,
                    "detected": True
                },
                {
                    "task_description": "Design technical architecture slides",
                    "attack_type": "Covert Signal",
                    "slide_json": json.dumps({"elements": [{"type": "image", "src": "tracking.png", "x": 850, "y": 650}]}),
                    "monitor_suspicion_score": 75.0,
                    "detected": True
                }
            ]
            for log in demo_logs:
                insert_agent_log(log)
    except Exception:
        pass

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                          SIDEBAR LAYOUT                            ║
# ╚══════════════════════════════════════════════════════════════════════╝
with st.sidebar:
    st.markdown('<div class="sidebar-title">🛡️ AIS-Sentinel</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">AI Safety · Global South</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="width: 100%; height: 1px; 
                    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent); 
                    margin: 0.5rem 0 1.5rem 0;"></div>
    """, unsafe_allow_html=True)
    
    # Navigation Radio
    page = st.radio(
        "Navigation",
        options=["🚨 IntelStream", "📊 SafetyBench", "🛡️ AgentGuard", "⚖️ PolicyBridge"],
        label_visibility="collapsed"
    )

    # Bottom Badge
    st.markdown("""
        <div class="sidebar-badge">
            🚀 Global South AIS Challenge 2026<br/>
            <span style="opacity: 0.7; font-size: 0.72rem;">Track 3 — Technical Safety</span>
        </div>
    """, unsafe_allow_html=True)

# Page Routing execution block
def main():
    if page == "🚨 IntelStream":
        exec(open("frontend/pages/01_intelstream.py", encoding="utf-8").read(), globals())
    elif page == "📊 SafetyBench":
        exec(open("frontend/pages/02_safetybench.py", encoding="utf-8").read(), globals())
    elif page == "🛡️ AgentGuard":
        exec(open("frontend/pages/03_agentguard.py", encoding="utf-8").read(), globals())
    elif page == "⚖️ PolicyBridge":
        exec(open("frontend/pages/04_policybridge.py", encoding="utf-8").read(), globals())

if __name__ == "__main__":
    main()
