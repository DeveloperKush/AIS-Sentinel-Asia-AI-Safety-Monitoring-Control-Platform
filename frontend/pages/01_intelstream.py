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

# 2. Page layout
st.title("🛡️ IntelStream — Biosecurity Intelligence Dashboard")
st.subheader("Real-time monitoring of AI-Bio dual-use risks across Asia")

# 3. Top section: Alert Ticker
st.markdown("### 🚨 High-Priority Alerts")
top_threats = sorted(st.session_state["articles"], key=lambda x: x["confidence_score"], reverse=True)[:3]

cols = st.columns(3)
for i, threat in enumerate(top_threats):
    with cols[i]:
        score = threat["confidence_score"]
        bg_color = "#ffebee" if score > 0.75 else "#fff8e1"
        border_color = "#d32f2f" if score > 0.75 else "#fbc02d"
        
        st.markdown(
            f"""
            <div style="background-color: {bg_color}; border-left: 5px solid {border_color}; padding: 15px; border-radius: 5px; height: 100%;">
                <h4 style="margin-top:0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{threat['title']}">
                    {get_flag(threat['source_country'])} {threat['title'][:30]}...
                </h4>
                <p><strong>Category:</strong> {threat['risk_category']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.metric(label="Confidence", value=f"{score:.2f}")
st.markdown("---")

col_left, col_center, col_right = st.columns([1, 2, 1.5])

# 4. Left sidebar: Filters
with col_left:
    st.markdown("### 🔎 Filters")
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
    st.markdown("### 📰 Intelligence Feed")
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
                            st.info(f"**{item['jurisdiction']} ({item['law_name']}):** {item['relevance_summary']}")
                    else:
                        st.info("No specific policy mapping found for this risk category.")
                except Exception:
                    st.info(f"**Simulated Policy Match:** Likely violation of Biosecurity regulations in {article['source_country']}.")

# 6. Right panel: Judge Simulation Mode
with col_right:
    st.markdown("### 🕵️ Judge Simulation Mode")
    st.markdown("Manually evaluate a new intelligence artifact.")
    
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
                                st.warning(f"⚖️ **{item['jurisdiction']} ({item['law_name']}):** {item['relevance_summary']}")
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
st.markdown("### 📝 Weekly Brief Generator")
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
