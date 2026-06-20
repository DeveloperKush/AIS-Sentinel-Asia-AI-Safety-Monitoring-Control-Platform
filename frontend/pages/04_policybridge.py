import streamlit as st
import pandas as pd
import json
import sys
import os

# Resolve project root directory and add it to sys.path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from modules.policybridge.mapper import RegulatoryMapper
from modules.policybridge.reporter import ComplianceReporter

# Page configuration
st.set_page_config(
    page_title="PolicyBridge Explorer",
    page_icon="⚖️",
    layout="wide"
)

# ── Page-Specific CSS ──
st.markdown("""
<style>
    .policy-hero {
        animation: fadeInUp 0.6s ease-out;
        background: linear-gradient(135deg, #0c1220 0%, #0f1a2e 50%, #060910 100%);
        padding: 2.5rem 3rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 212, 255, 0.1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .policy-hero::after {
        content: '';
        position: absolute;
        bottom: -50%;
        left: 10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255, 159, 67, 0.06) 0%, transparent 70%);
        pointer-events: none;
    }
    .policy-hero-orb {
        position: absolute;
        top: -50%;
        right: -5%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .policy-hero h1 {
        color: #00d4ff !important;
        margin: 0 !important;
        font-size: clamp(1.8rem, 4vw, 2.5rem) !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        position: relative;
    }
    .policy-hero p {
        color: #8b9dc3 !important;
        margin: 0.5rem 0 0 0 !important;
        font-size: 1.05rem !important;
        max-width: 650px;
        position: relative;
        line-height: 1.5;
    }
    .policy-hero-accent {
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #ff9f43, #00d4ff);
        margin-top: 1.2rem;
        border-radius: 2px;
        position: relative;
    }
    .threat-card {
        background: rgba(14, 21, 38, 0.85);
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    .threat-card-critical {
        border-left: 4px solid #ff4d6d;
    }
    .threat-card-critical::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        box-shadow: 0 0 15px rgba(255, 77, 109, 0.4);
    }
    .threat-card-high {
        border-left: 4px solid #ff9f43;
    }
    .threat-card-medium {
        border-left: 4px solid #a78bfa;
    }
    .threat-card-low {
        border-left: 4px solid #00d9a3;
    }
    .severity-badge {
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 14px;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .severity-critical {
        background-color: rgba(255, 77, 109, 0.12);
        color: #ff4d6d;
        border: 1px solid rgba(255, 77, 109, 0.25);
        box-shadow: 0 0 12px rgba(255, 77, 109, 0.15);
    }
    .severity-high {
        background-color: rgba(255, 159, 67, 0.12);
        color: #ff9f43;
        border: 1px solid rgba(255, 159, 67, 0.25);
    }
    .severity-medium {
        background-color: rgba(167, 139, 250, 0.12);
        color: #a78bfa;
        border: 1px solid rgba(167, 139, 250, 0.25);
    }
    .severity-low {
        background-color: rgba(0, 217, 163, 0.12);
        color: #00d9a3;
        border: 1px solid rgba(0, 217, 163, 0.25);
    }
    div[data-testid="element-container"]:has(.selector-card-trigger) + div[data-testid="element-container"] > div[data-testid="stHorizontalBlock"] {
        background: rgba(14, 21, 38, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
    }
    div[data-testid="column"]:has(.comparison-panel-trigger) {
        background: rgba(14, 21, 38, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    div[data-testid="element-container"]:has(.remediation-checklist-trigger) ~ div[data-testid="element-container"]:has(.stCheckbox) {
        background: rgba(14, 21, 38, 0.4);
        border: 1px solid rgba(0, 212, 255, 0.05);
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 0.4rem;
        transition: all 0.3s ease;
    }
    div[data-testid="element-container"]:has(.remediation-checklist-trigger) ~ div[data-testid="element-container"]:has(.stCheckbox):hover {
        background: rgba(0, 212, 255, 0.04);
        border-color: rgba(0, 212, 255, 0.12);
    }
    div[data-testid="element-container"]:has(.report-card-trigger) + div[data-testid="element-container"] > div[data-testid="stHorizontalBlock"] {
        background: rgba(14, 21, 38, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    .gap-warning {
        background: rgba(255, 159, 67, 0.06);
        border-left: 4px solid #ff9f43;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ──
st.markdown("""
<div class="policy-hero">
    <div class="policy-hero-orb"></div>
    <h1>⚖️ PolicyBridge</h1>
    <p>Map AI safety threats to regional regulatory frameworks across Global South jurisdictions. 
       Generate compliance reports and identify regulatory gaps in real-time.</p>
    <div class="policy-hero-accent"></div>
</div>
""", unsafe_allow_html=True)

# Pre-loaded demo scenarios mapped to regional laws
DEMO_SCENARIOS = {
    "AI-EngBio integration": {
        "title": "Autonomous modification of dual-use viral vectors",
        "risk_category": "AI-EngBio integration",
        "severity": "Critical",
        "confidence_score": 0.94,
        "justification": "The model designed a modified pathogen sequence using CRISPR design tools, bypassing standard biosafety registration screening filters."
    },
    "Dual-use hardware": {
        "title": "Optimizing high-performance military controller firmware",
        "risk_category": "Dual-use hardware",
        "severity": "Medium",
        "confidence_score": 0.82,
        "justification": "System attempt to optimize design constraints for unverified dual-use drone guidance system micro-controllers."
    },
    "Data sovereignty risk": {
        "title": "Exfiltration of regional health dataset prompt logs",
        "risk_category": "Data sovereignty risk",
        "severity": "High",
        "confidence_score": 0.88,
        "justification": "The generative model logged PII from clinical prompts and synchronized it with external cloud servers across national borders."
    },
    "Policy gap": {
        "title": "Autonomous system operating on critical public grids",
        "risk_category": "Policy gap",
        "severity": "High",
        "confidence_score": 0.85,
        "justification": "An autonomous AI agent controls public grid routing without active human-in-the-loop fallback override pipelines."
    }
}

# ASEAN side-by-side comparison matrix database
ASEAN_COMPARISON = {
    "AI-EngBio integration": {
        "Vietnam": {"Has law": "✅", "HITL?": "✅", "Penalty": "High", "Effective Date": "2025-06-01"},
        "India": {"Has law": "✅", "HITL?": "❌", "Penalty": "High", "Effective Date": "2025-12-01"},
        "Singapore": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "Indonesia": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "EU": {"Has law": "✅", "HITL?": "✅", "Penalty": "High", "Effective Date": "2026-08-01"}
    },
    "Data sovereignty risk": {
        "Vietnam": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "India": {"Has law": "✅", "HITL?": "❌", "Penalty": "High", "Effective Date": "2024-09-01"},
        "Singapore": {"Has law": "✅", "HITL?": "❌", "Penalty": "Medium", "Effective Date": "2021-02-01"},
        "Indonesia": {"Has law": "✅", "HITL?": "✅", "Penalty": "High", "Effective Date": "2024-10-17"},
        "EU": {"Has law": "✅", "HITL?": "❌", "Penalty": "High", "Effective Date": "2026-08-01"}
    },
    "Dual-use hardware": {
        "Vietnam": {"Has law": "✅", "HITL?": "✅", "Penalty": "Medium", "Effective Date": "2026-01-01"},
        "India": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "Singapore": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "Indonesia": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "EU": {"Has law": "✅", "HITL?": "✅", "Penalty": "High", "Effective Date": "2026-08-01"}
    },
    "Policy gap": {
        "Vietnam": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "India": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "Singapore": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "Indonesia": {"Has law": "❌", "HITL?": "❌", "Penalty": "Low", "Effective Date": "N/A"},
        "EU": {"Has law": "✅", "HITL?": "✅", "Penalty": "High", "Effective Date": "2026-08-01"}
    }
}

# Top threat selector section
st.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
    <span style="font-size: 1.1rem;">🎯</span>
    <h3 style="margin: 0; color: #e6edf3; font-size: 1.1rem; font-weight: 600;">Threat Classification Selector</h3>
    <div style="flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 212, 255, 0.2), transparent);"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="selector-card-trigger"></div>', unsafe_allow_html=True)
col_sel1, col_sel2 = st.columns([3, 1])

with col_sel1:
    risk_category = st.selectbox(
        "Risk Category Classification",
        ["AI-EngBio integration", "Dual-use hardware", "Policy gap", "Data sovereignty risk"]
    )

# Load Threat data
if "active_threat" not in st.session_state:
    st.session_state.active_threat = DEMO_SCENARIOS["AI-EngBio integration"]

with col_sel2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Load Sample Threat", use_container_width=True):
        st.session_state.active_threat = DEMO_SCENARIOS[risk_category]
        st.success("Sample threat vector populated!")

# Threat details variables
active_threat = st.session_state.active_threat

# Active layout split (Left: Compliance Details, Right: Comparison sidebar)
col_left, col_right = st.columns([3, 1])

with col_left:
    # Summary card
    sev = active_threat["severity"]
    badge_style = f"severity-{sev.lower()}"
    card_style = f"threat-card-{sev.lower()}"
    
    st.markdown(f"""
        <div class="threat-card {card_style}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.2rem;">⚡</span>
                    <span style="color: #00d4ff; font-weight: 600; font-size: 1.05rem;">Active Threat Vector</span>
                </div>
                <span class="severity-badge {badge_style}">{sev} Severity</span>
            </div>
            <div style="color: #e6edf3; font-size: 1.15rem; font-weight: 600; margin-bottom: 10px; line-height: 1.3;">
                {active_threat['title']}
            </div>
            <div style="font-size: 0.88rem; color: #8b9dc3; margin-bottom: 6px;">
                <strong style="color: #a78bfa;">Confidence Score:</strong> {active_threat['confidence_score']:.0%}
            </div>
            <div style="font-size: 0.88rem; color: #8b9dc3; line-height: 1.5;">
                <strong style="color: #a78bfa;">Justification:</strong> {active_threat['justification']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Applicable laws listing
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
        <span style="font-size: 1.1rem;">📜</span>
        <h3 style="margin: 0; color: #e6edf3; font-size: 1.1rem; font-weight: 600;">Applicable Regional Frameworks</h3>
    </div>
    """, unsafe_allow_html=True)
    
    mapper = RegulatoryMapper()
    reporter = ComplianceReporter()
    
    laws = mapper.map_threat(risk_category)
    
    for l in laws:
        country_flag = {
            "Vietnam": "🇻🇳", "India": "🇮🇳", "Singapore": "🇸🇬",
            "Indonesia": "🇮🇩", "EU": "🇪🇺"
        }.get(l.get("jurisdiction", ""), "🌐")
        
        with st.expander(f"{country_flag} {l.get('jurisdiction')} — {l.get('law_name')}", expanded=True):
            st.markdown(f"**Article/Section:** <span style='color: #00d4ff;'>{l.get('article')}</span>", unsafe_allow_html=True)
            st.markdown(f"**Requirement:** {l.get('requirement')}")
            st.markdown(f"**Effective Date:** {l.get('effective_date')}")
            st.markdown(f"<span style='color: #ff4d6d; font-weight: 500;'><strong>Penalty:</strong> {l.get('penalty')}</span>", unsafe_allow_html=True)

    # Recommended Actions Checklist
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin: 1.5rem 0 0.5rem 0;">
        <span style="font-size: 1.1rem;">✅</span>
        <h3 style="margin: 0; color: #e6edf3; font-size: 1.1rem; font-weight: 600;">Recommended Remediation Checklist</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="remediation-checklist-trigger"></div>', unsafe_allow_html=True)
    remediation_actions = reporter._get_remediation_actions(risk_category)
    for a in remediation_actions:
        st.checkbox(a, value=False)

with col_right:
    st.markdown('<div class="comparison-panel-trigger"></div>', unsafe_allow_html=True)
    # Sidebar: ASEAN Comparison
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
        <span style="font-size: 1.1rem;">🌏</span>
        <h3 style="margin: 0; color: #e6edf3; font-size: 1.05rem; font-weight: 600;">Regional Comparison</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Load comparison row data
    comparison_map = ASEAN_COMPARISON.get(risk_category, {})
    comp_rows = []
    for country, details in comparison_map.items():
        comp_rows.append({
            "Jurisdiction": country,
            "Has specific law?": details["Has law"],
            "Human-in-the-loop required?": details["HITL?"],
            "Penalty severity": details["Penalty"],
            "Effective date": details["Effective Date"]
        })
    
    comp_df = pd.DataFrame(comp_rows)
    
    # Stylized Cell Painting
    def style_dataframe(val_df):
        def color_rules(val):
            if val == "✅":
                return 'background-color: rgba(0, 217, 163, 0.1); color: #00d9a3; text-align: center;'
            elif val == "❌":
                return 'background-color: rgba(255, 77, 109, 0.1); color: #ff4d6d; text-align: center;'
            elif val == "High":
                return 'background-color: rgba(255, 77, 109, 0.06); color: #ff4d6d;'
            elif val == "Medium":
                return 'background-color: rgba(255, 159, 67, 0.06); color: #ff9f43;'
            elif val == "Low":
                return 'background-color: rgba(0, 217, 163, 0.06); color: #00d9a3;'
            return ''
        
        styler = val_df.style
        if hasattr(styler, "map"):
            return styler.map(color_rules)
        return styler.applymap(color_rules)

    st.dataframe(
        style_dataframe(comp_df),
        use_container_width=True,
        hide_index=True
    )

    # Regulatory Gap analysis warning cards
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 6px; margin: 1rem 0 0.3rem 0;">
        <span style="font-size: 1rem;">⚠️</span>
        <span style="color: #ff9f43; font-weight: 600; font-size: 0.95rem;">Regulatory Gap Analysis</span>
    </div>
    """, unsafe_allow_html=True)

    gaps = [country for country, details in comparison_map.items() if details["Has law"] == "❌"]
    
    if gaps:
        st.markdown(f"""
        <div class="gap-warning">
            <div style="color: #ff9f43; font-weight: 600; margin-bottom: 6px;">
                ⚠️ Coverage Gaps Detected
            </div>
            <div style="color: #8b9dc3; font-size: 0.88rem; line-height: 1.5;">
                The following jurisdictions lack specific regulatory frameworks governing 
                <strong style="color: #e6edf3;">{risk_category}</strong>: 
                <strong style="color: #ff9f43;">{', '.join(gaps)}</strong>. 
                In these regions, compliance defaults to general guidelines, creating higher liability.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("All analyzed jurisdictions have specific laws covering this threat category.")

# Report Generation and Downloads at the Bottom
st.markdown("---")

st.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
    <span style="font-size: 1.1rem;">📋</span>
    <h3 style="margin: 0; color: #e6edf3; font-size: 1.15rem; font-weight: 600;">Report Export Hub</h3>
    <div style="flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 212, 255, 0.2), transparent);"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="report-card-trigger"></div>', unsafe_allow_html=True)

html_report = reporter.generate_report(active_threat)
markdown_report = reporter.generate_markdown(active_threat)

col_rep1, col_rep2, col_rep3 = st.columns(3)

with col_rep1:
    if st.button("Generate Compliance Report HTML Preview", use_container_width=True):
        st.components.v1.html(html_report, height=600, scrolling=True)

with col_rep2:
    st.download_button(
        label="📥 Download HTML (Print to PDF)",
        data=html_report,
        file_name=f"compliance_report_{risk_category.replace(' ', '_').lower()}.html",
        mime="text/html",
        use_container_width=True
    )

with col_rep3:
    st.download_button(
        label="📥 Download Markdown Report",
        data=markdown_report,
        file_name=f"compliance_report_{risk_category.replace(' ', '_').lower()}.md",
        mime="text/markdown",
        use_container_width=True
    )
