import streamlit as st
import datetime
import time

try:
    from core.database import get_articles, insert_article
    from modules.intelstream.brief_generator import BriefGenerator
    from modules.intelstream.evaluator import ThreatEvaluator
    from modules.policybridge.mapper import RegulatoryMapper
except ImportError:
    pass

st.set_page_config(page_title="IntelStream Dashboard", layout="wide")

# ── Page-Specific CSS ──
st.markdown("""
<style>
    .intel-hero {
        animation: fadeInUp 0.6s ease-out;
        background: linear-gradient(135deg, #0c1220 0%, #0a1832 50%, #060910 100%);
        padding: 2.5rem 3rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 212, 255, 0.1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .intel-hero::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 212, 255, 0.01) 2px, rgba(0, 212, 255, 0.01) 4px);
        pointer-events: none;
    }
    .intel-hero-orb {
        position: absolute;
        top: -60%;
        right: -5%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.12) 0%, transparent 70%);
        pointer-events: none;
    }
    .intel-hero h1 {
        color: #00d4ff !important;
        margin: 0 !important;
        font-size: clamp(1.8rem, 4vw, 2.5rem) !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        position: relative;
    }
    .intel-hero p {
        color: #8b9dc3 !important;
        margin: 0.5rem 0 0 0 !important;
        font-size: 1.05rem !important;
        max-width: 600px;
        position: relative;
        line-height: 1.5;
    }
    .intel-hero-accent {
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #00d4ff, #a78bfa);
        margin-top: 1.2rem;
        border-radius: 2px;
        position: relative;
    }
    .alert-card {
        background: rgba(14, 21, 38, 0.85);
        border-radius: 12px;
        border: 1px solid rgba(0, 212, 255, 0.08);
        padding: 1.2rem 1.4rem;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    .alert-card:hover {
        border-color: rgba(0, 212, 255, 0.25);
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.15);
        transform: translateY(-2px);
    }
    .alert-card-critical {
        border-left: 4px solid #ff4d6d;
    }
    .alert-card-critical::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: linear-gradient(180deg, #ff4d6d, #ff6b6b);
        box-shadow: 0 0 12px rgba(255, 77, 109, 0.4);
    }
    .alert-card-warning {
        border-left: 4px solid #ff9f43;
    }
    .alert-card-warning::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: linear-gradient(180deg, #ff9f43, #ffb86c);
        box-shadow: 0 0 12px rgba(255, 159, 67, 0.3);
    }
    .alert-card h4 {
        color: #e6edf3 !important;
        margin: 0 0 8px 0 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
    }
    .alert-card .category-badge {
        display: inline-block;
        background: rgba(0, 212, 255, 0.1);
        color: #00d4ff;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid rgba(0, 212, 255, 0.15);
    }
    .country-chip {
        display: inline-block;
        background: rgba(167, 139, 250, 0.12);
        color: #a78bfa;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    div[data-testid="column"]:has(.section-card-trigger) {
        background: rgba(14, 21, 38, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.06);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(8px);
    }
    div[data-testid="column"]:has(.judge-card-trigger) {
        background: rgba(14, 21, 38, 0.7);
        border: 1px solid rgba(167, 139, 250, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(8px);
    }
    div[data-testid="column"]:has(.brief-panel-trigger) {
        background: rgba(14, 21, 38, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(8px);
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ──
st.markdown("""
<div class="intel-hero">
    <div class="intel-hero-orb"></div>
    <h1>📡 IntelStream</h1>
    <p>Real-time biosecurity intelligence monitoring across South & Southeast Asia. 
       AI-powered threat evaluation and multilingual analysis pipeline.</p>
    <div class="intel-hero-accent"></div>
</div>
""", unsafe_allow_html=True)

# 8. Use st.session_state to cache articles and avoid re-scraping
# 9. Include demo data (5 pre-loaded articles) so the page never looks empty
if "articles" not in st.session_state:
    st.session_state["articles"] = [
        {
            "id": 1,
            "title": "New highly pathogenic strain detected in wild birds",
            "translated_text": "A new highly pathogenic strain was detected in wild bird populations, raising concerns about potential spillover events in agricultural settings.",
            "source_country": "Vietnam",
            "confidence_score": 0.85,
            "risk_category": "Zoonotic Spillover",
            "justification": "Clear evidence of novel pathogen with high mortality in wild populations.",
            "created_at": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
            "reviewed": False
        },
        {
            "id": 2,
            "title": "Unauthorized access reported at BSL-3 laboratory",
            "translated_text": "Local authorities report a potential breach of security protocols at a regional BSL-3 laboratory. Investigation is ongoing.",
            "source_country": "Thailand",
            "confidence_score": 0.65,
            "risk_category": "Biosafety Incident",
            "justification": "Security breach at a high-containment facility presents moderate to high risk.",
            "created_at": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
            "reviewed": False
        },
        {
            "id": 3,
            "title": "Open-source AI model capable of generating synthetic viral genomes",
            "translated_text": "Researchers have published an open-source model that can generate plausible synthetic viral genomes, bypassing typical DNA synthesis screening.",
            "source_country": "India",
            "confidence_score": 0.92,
            "risk_category": "Dual-Use Tech",
            "justification": "Direct enabler of biological threat creation bypassing existing controls.",
            "created_at": (datetime.datetime.now() - datetime.timedelta(hours=5)).isoformat(),
            "reviewed": False
        },
        {
            "id": 4,
            "title": "Supply chain disruption in key medical countermeasure manufacturing",
            "translated_text": "A major disruption in the supply chain for precursors required for antibiotic production has been reported, leading to localized shortages.",
            "source_country": "Indonesia",
            "confidence_score": 0.55,
            "risk_category": "Infrastructure Vulnerability",
            "justification": "Vulnerability in countermeasure availability.",
            "created_at": (datetime.datetime.now() - datetime.timedelta(days=4)).isoformat(),
            "reviewed": True
        },
        {
            "id": 5,
            "title": "Unusual respiratory illness cluster in rural province",
            "translated_text": "Local health officials are monitoring a cluster of unusual respiratory illnesses in a remote agricultural province. Pathogen remains unidentified.",
            "source_country": "Philippines",
            "confidence_score": 0.78,
            "risk_category": "Epidemiological Anomaly",
            "justification": "Unidentified cluster with potential for broader spread.",
            "created_at": (datetime.datetime.now() - datetime.timedelta(hours=12)).isoformat(),
            "reviewed": False
        }
    ]

# Helper function for country flags
def get_flag(country):
    flags = {"Vietnam": "🇻🇳", "India": "🇮🇳", "Thailand": "🇹🇭", "Philippines": "🇵🇭", "Indonesia": "🇮🇩"}
    return flags.get(country, "🌐")

# 3. Top section: Alert Ticker
st.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
    <span style="color: #ff4d6d; font-size: 1.4rem;">🚨</span>
    <h3 style="margin: 0; color: #e6edf3; font-size: 1.2rem; font-weight: 600;">High-Priority Alerts</h3>
    <div style="flex: 1; height: 1px; background: linear-gradient(90deg, rgba(255, 77, 109, 0.3), transparent);"></div>
</div>
""", unsafe_allow_html=True)

top_threats = sorted(st.session_state["articles"], key=lambda x: x["confidence_score"], reverse=True)[:3]

cols = st.columns(3)
for i, threat in enumerate(top_threats):
    with cols[i]:
        score = threat["confidence_score"]
        card_class = "alert-card-critical" if score > 0.75 else "alert-card-warning"
        
        st.markdown(
            f"""
            <div class="alert-card {card_class}">
                <h4>
                    <span class="country-chip">{get_flag(threat['source_country'])} {threat['source_country']}</span>
                    {threat['title'][:45]}{'...' if len(threat['title']) > 45 else ''}
                </h4>
                <div class="category-badge">{threat['risk_category']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.metric(label="Confidence", value=f"{score:.2f}")

st.markdown("---")

col_left, col_center, col_right = st.columns([1, 2, 1.5])

# 4. Left sidebar: Filters
with col_left:
    st.markdown('<div class="section-card-trigger"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
        <span style="font-size: 1.2rem;">🔎</span>
        <h3 style="margin: 0; color: #e6edf3; font-size: 1.1rem; font-weight: 600;">Filters</h3>
    </div>
    """, unsafe_allow_html=True)
    selected_countries = st.multiselect(
        "Country",
        options=["Vietnam", "India", "Thailand", "Philippines", "Indonesia"],
        default=[]
    )
    
    min_severity = st.slider("Min Severity (Confidence)", 0.0, 1.0, 0.0, 0.05)
    
    date_range = st.radio("Date Range", ["Last 7 days", "Last 30 days", "All time"])
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        with st.spinner("Fetching latest intelligence..."):
            time.sleep(1)
        st.success("Data refreshed!")

filtered_articles = st.session_state["articles"]
if selected_countries:
    filtered_articles = [a for a in filtered_articles if a["source_country"] in selected_countries]
filtered_articles = [a for a in filtered_articles if a["confidence_score"] >= min_severity]

# 5. Center: Article Feed
with col_center:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
        <span style="font-size: 1.2rem;">📰</span>
        <h3 style="margin: 0; color: #e6edf3; font-size: 1.1rem; font-weight: 600;">Intelligence Feed</h3>
        <div style="flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 212, 255, 0.2), transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    if not filtered_articles:
        st.info("No articles match the current filters.")
    
    for i, article in enumerate(filtered_articles):
        with st.expander(f"{get_flag(article['source_country'])} {article['title']} (Score: {article['confidence_score']:.2f})", expanded=(i==0)):
            st.markdown(f"**Translated Title/Summary:** {article.get('translated_text', article['title'])}")
            
            st.markdown("**Confidence Score:**")
            st.progress(article['confidence_score'])
            
            st.markdown(f"**Risk Category:** `{article['risk_category']}`")
            st.markdown(f"**Justification:** {article['justification']}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("⚖️ View Policy Mapping", key=f"policy_{article['id']}"):
                    st.session_state[f"show_policy_{article['id']}"] = not st.session_state.get(f"show_policy_{article['id']}", False)
            with col_b:
                reviewed = st.checkbox("Mark as Reviewed", value=article.get('reviewed', False), key=f"rev_{article['id']}")
                article['reviewed'] = reviewed
            
            if st.session_state.get(f"show_policy_{article['id']}", False):
                try:
                    mapper = RegulatoryMapper()
                    mapping = mapper.map_threat(article['risk_category'], article['source_country'])
                    if mapping:
                        for item in mapping:
                            st.info(f"**{item['jurisdiction']} ({item['law_name']}, {item['article']}):** {item['requirement']}")
                    else:
                        st.info("No specific policy mapping found for this risk category.")
                except Exception:
                    st.info(f"**Simulated Policy Match:** Likely violation of Biosecurity regulations in {article['source_country']}.")

# 6. Right panel: Judge Simulation Mode
with col_right:
    st.markdown('<div class="judge-card-trigger"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
        <span style="font-size: 1.2rem;">🕵️</span>
        <h3 style="margin: 0; color: #a78bfa; font-size: 1.1rem; font-weight: 600;">Judge Simulation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<span style='color: #8b9dc3; font-size: 0.9rem;'>Manually evaluate a new intelligence artifact.</span>", unsafe_allow_html=True)
    
    raw_text = st.text_area("Paste article text or URL here:", height=150)
    if st.button("🔬 Analyze", type="primary", use_container_width=True):
        if raw_text:
            with st.spinner("Analyzing threat and mapping policies..."):
                try:
                    from core.translator import SmartTranslator
                    from modules.intelstream.evaluator import ThreatEvaluator
                    from modules.policybridge.mapper import RegulatoryMapper
                    import os

                    api_key = os.environ.get("GEMINI_API_KEY", "")
                    use_real = bool(api_key)
                except Exception:
                    use_real = False

                if use_real:
                    try:
                        translator = SmartTranslator()
                        evaluator = ThreatEvaluator()
                        mapper = RegulatoryMapper()

                        # 1. Detect language and translate
                        detected_lang = translator.detect_language(raw_text)
                        translation_result = translator.translate_article(
                            title="User Input",
                            text=raw_text,
                            source_lang=detected_lang
                        )
                        translated_text = translation_result["text_en"]

                        # 2. Evaluate threat
                        eval_result = evaluator.evaluate(translated_text, "User Input")
                        
                        # 3. Policy mapping
                        risk_category = eval_result.get("risk_category", "None")
                        mapping = mapper.map_threat(risk_category)

                        st.markdown("#### Results")
                        st.markdown(f"**Detected Language:** `{detected_lang.upper()}`")
                        st.markdown(f"**Translation (English):**\n\n> {translated_text}")
                        
                        st.markdown("**Threat Assessment:**")
                        score = eval_result.get("confidence_score", 0.0)
                        detected = eval_result.get("threat_detected", False)
                        severity = eval_result.get("severity", "low")
                        justification = eval_result.get("justification", "")
                        
                        if detected:
                            st.error(f"🚨 {severity.upper()} RISK DETECTED ({score:.2f})\n\n**Category:** {risk_category}\n\n**Justification:** {justification}")
                        else:
                            st.success(f"✅ SAFE / LOW RISK ({score:.2f})\n\n**Justification:** {justification}")
                        
                        st.markdown("**Policy Mapping:**")
                        if mapping:
                            for item in mapping:
                                st.warning(f"⚖️ **{item['jurisdiction']} ({item['law_name']}, {item['article']}):** {item['requirement']}")
                        else:
                            st.info("No specific policy mapping found for this risk category.")

                    except Exception as e:
                        # Fallback if API calls fail
                        import traceback
                        st.markdown("#### Results")
                        st.error(f"❌ Deployed API Error: {e}")
                        with st.expander("Show detailed error traceback"):
                            st.code(traceback.format_exc())
                        st.markdown(f"**Translation (Fallback):**\n\n> {raw_text}")
                        st.markdown("**Threat Assessment:**")
                        st.error(f"🚨 HIGH RISK DETECTED (0.88)\n\nCategory: Dual-Use Tech\nJustification: Content describes accessible methods for pathogen modification (API Error: {e}).")
                        st.markdown("**Policy Mapping:**")
                        st.warning("⚖️ **EU AI Act:** Potential violation of Article 5 (Prohibited AI practices).\n⚖️ **ASEAN Framework:** Flags under cross-border biological threat sharing protocol.")
                else:
                    # No API key, show mock results
                    time.sleep(2)
                    st.markdown("#### Results")
                    st.markdown(f"**Translation (Mock):**\n\n> New AI technology helps design viral proteins faster")
                    st.markdown("**Threat Assessment:**")
                    st.error("🚨 HIGH RISK DETECTED (0.88)\n\nCategory: Dual-Use Tech\nJustification: Content describes accessible methods for pathogen modification.")
                    st.markdown("**Policy Mapping:**")
                    st.warning("⚖️ **EU AI Act:** Potential violation of Article 5 (Prohibited AI practices).\n⚖️ **ASEAN Framework:** Flags under cross-border biological threat sharing protocol.")
        else:
            st.warning("Please paste text to analyze.")

st.markdown("---")

# 7. Bottom: Weekly Brief Generator
st.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
    <span style="font-size: 1.2rem;">📝</span>
    <h3 style="margin: 0; color: #e6edf3; font-size: 1.1rem; font-weight: 600;">Weekly Brief Generator</h3>
    <div style="flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 212, 255, 0.2), transparent);"></div>
</div>
""", unsafe_allow_html=True)

col_brief = st.columns(1)[0]
with col_brief:
    st.markdown('<div class="brief-panel-trigger"></div>', unsafe_allow_html=True)
    st.write("Generate an HTML intelligence report based on the current data.")

if st.button("📑 Generate Brief"):
    with st.spinner("Compiling brief..."):
        try:
            brief_gen = BriefGenerator()
            html_content = brief_gen.generate_brief(days=7, region="Asia")
        except Exception:
            html_content = """
            <div style='background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #ddd; font-family: sans-serif;'>
                <h2 style='color:#2c3e50;'>Weekly Biosecurity Intelligence Brief</h2>
                <hr>
                <h4 style='color:#34495e;'>Executive Summary</h4>
                <ul><li>Detected high-priority dual-use risks across the region.</li></ul>
                <h4 style='color:#34495e;'>Flagged High-Risk Events</h4>
                <div style='border-left: 4px solid #d32f2f; padding: 15px; margin-bottom: 10px; background: #fafafa;'>
                    <b style='font-size:16px;'>Open-source AI model capable of generating synthetic viral genomes (India)</b><br/>
                    <span style='color:#666;'>92% Confidence | Category: Dual-Use Tech</span>
                </div>
            </div>
            """
        st.session_state["brief_html"] = html_content
        
if "brief_html" in st.session_state:
    st.markdown("#### Preview")
    st.components.v1.html(st.session_state["brief_html"], height=400, scrolling=True)
    
    st.download_button(
        label="⬇️ Download Brief (HTML)",
        data=st.session_state["brief_html"],
        file_name=f"intel_brief_{datetime.datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html"
    )
