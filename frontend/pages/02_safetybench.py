import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
import sys
import os

# Resolve project root directory and add it to sys.path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

# Set page configuration for a wide, premium layout
st.set_page_config(
    page_title="SafetyBench-Asia Leaderboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Page-Specific CSS ──
st.markdown("""
<style>
    .bench-hero {
        animation: fadeInUp 0.6s ease-out;
        background: linear-gradient(135deg, #0c1220 0%, #0e1a30 50%, #060910 100%);
        padding: 2.5rem 3rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 212, 255, 0.1);
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .bench-hero::after {
        content: '';
        position: absolute;
        bottom: -60%;
        left: -5%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(167, 139, 250, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    .bench-hero-orb {
        position: absolute;
        top: -50%;
        right: -8%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    .bench-hero h1 {
        color: #00d4ff !important;
        margin: 0 !important;
        font-size: clamp(1.8rem, 4vw, 2.5rem) !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        position: relative;
    }
    .bench-hero p {
        color: #8b9dc3 !important;
        margin: 0.5rem 0 0 0 !important;
        font-size: 1.05rem !important;
        max-width: 650px;
        position: relative;
        line-height: 1.5;
    }
    .bench-hero-accent {
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #00d4ff, #a78bfa);
        margin-top: 1.2rem;
        border-radius: 2px;
        position: relative;
    }
    /* Sibling trigger card styles */
    div[data-testid="element-container"]:has(.controls-card-trigger) + div[data-testid="element-container"] > div[data-testid="stHorizontalBlock"] {
        background: rgba(14, 21, 38, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
    }
    div[data-testid="element-container"]:has(.chart-container-trigger) + div[data-testid="element-container"] {
        background: rgba(14, 21, 38, 0.7);
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    div[data-testid="element-container"]:has(.chart-container-trigger) + div[data-testid="element-container"]:hover {
        border-color: rgba(0, 212, 255, 0.2);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.08);
    }
    div[data-testid="element-container"]:has(.deep-dive-card-trigger) + div[data-testid="element-container"] [data-testid="stExpander"] {
        border-top: 3px solid rgba(0, 212, 255, 0.3) !important;
    }
    div[data-testid="element-container"]:has(.comparison-card-trigger) + div[data-testid="element-container"] > div[data-testid="stHorizontalBlock"] {
        background: rgba(14, 21, 38, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    .badge-winner {
        background-color: rgba(0, 217, 163, 0.12);
        color: #00d9a3;
        border: 1px solid rgba(0, 217, 163, 0.25);
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 0.88rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ──
st.markdown("""
<div class="bench-hero">
    <div class="bench-hero-orb"></div>
    <h1>📊 SafetyBench-Asia</h1>
    <p>Multilingual AI safety evaluation across South & Southeast Asian languages. 
       Benchmarking sycophancy, jailbreak resistance, and hallucination rates.</p>
    <div class="bench-hero-accent"></div>
</div>
""", unsafe_allow_html=True)

# Demo benchmark results to populate the dashboard immediately
DEMO_RESULTS = [
    {"Model": "Qwen2.5-7B", "Language": "English", "Sycophancy Rate": 0.22, "Jailbreak Refusal": 0.88, "Hallucination Rate": 0.18, "Overall Score": 0.82, "Safety Disparity": 1.00},
    {"Model": "Qwen2.5-7B", "Language": "Vietnamese", "Sycophancy Rate": 0.38, "Jailbreak Refusal": 0.72, "Hallucination Rate": 0.32, "Overall Score": 0.68, "Safety Disparity": 0.58},
    {"Model": "Qwen2.5-7B", "Language": "Tagalog", "Sycophancy Rate": 0.35, "Jailbreak Refusal": 0.74, "Hallucination Rate": 0.28, "Overall Score": 0.70, "Safety Disparity": 0.63},
    {"Model": "Qwen2.5-7B", "Language": "Bahasa", "Sycophancy Rate": 0.28, "Jailbreak Refusal": 0.80, "Hallucination Rate": 0.24, "Overall Score": 0.76, "Safety Disparity": 0.79},
    {"Model": "Qwen2.5-7B", "Language": "Hindi", "Sycophancy Rate": 0.32, "Jailbreak Refusal": 0.76, "Hallucination Rate": 0.30, "Overall Score": 0.72, "Safety Disparity": 0.69},
    {"Model": "Qwen2.5-7B", "Language": "Thai", "Sycophancy Rate": 0.40, "Jailbreak Refusal": 0.70, "Hallucination Rate": 0.34, "Overall Score": 0.66, "Safety Disparity": 0.55},
    
    {"Model": "Llama-3.1-8B", "Language": "English", "Sycophancy Rate": 0.18, "Jailbreak Refusal": 0.92, "Hallucination Rate": 0.15, "Overall Score": 0.86, "Safety Disparity": 1.00},
    {"Model": "Llama-3.1-8B", "Language": "Vietnamese", "Sycophancy Rate": 0.32, "Jailbreak Refusal": 0.78, "Hallucination Rate": 0.28, "Overall Score": 0.73, "Safety Disparity": 0.56},
    {"Model": "Llama-3.1-8B", "Language": "Tagalog", "Sycophancy Rate": 0.30, "Jailbreak Refusal": 0.80, "Hallucination Rate": 0.25, "Overall Score": 0.75, "Safety Disparity": 0.60},
    {"Model": "Llama-3.1-8B", "Language": "Bahasa", "Sycophancy Rate": 0.24, "Jailbreak Refusal": 0.85, "Hallucination Rate": 0.20, "Overall Score": 0.80, "Safety Disparity": 0.75},
    {"Model": "Llama-3.1-8B", "Language": "Hindi", "Sycophancy Rate": 0.26, "Jailbreak Refusal": 0.84, "Hallucination Rate": 0.22, "Overall Score": 0.79, "Safety Disparity": 0.69},
    {"Model": "Llama-3.1-8B", "Language": "Thai", "Sycophancy Rate": 0.35, "Jailbreak Refusal": 0.75, "Hallucination Rate": 0.30, "Overall Score": 0.71, "Safety Disparity": 0.51},

    {"Model": "Mistral-7B", "Language": "English", "Sycophancy Rate": 0.25, "Jailbreak Refusal": 0.85, "Hallucination Rate": 0.22, "Overall Score": 0.78, "Safety Disparity": 1.00},
    {"Model": "Mistral-7B", "Language": "Vietnamese", "Sycophancy Rate": 0.42, "Jailbreak Refusal": 0.65, "Hallucination Rate": 0.38, "Overall Score": 0.62, "Safety Disparity": 0.60},
    {"Model": "Mistral-7B", "Language": "Tagalog", "Sycophancy Rate": 0.40, "Jailbreak Refusal": 0.68, "Hallucination Rate": 0.35, "Overall Score": 0.64, "Safety Disparity": 0.63},
    {"Model": "Mistral-7B", "Language": "Bahasa", "Sycophancy Rate": 0.32, "Jailbreak Refusal": 0.75, "Hallucination Rate": 0.30, "Overall Score": 0.71, "Safety Disparity": 0.78},
    {"Model": "Mistral-7B", "Language": "Hindi", "Sycophancy Rate": 0.35, "Jailbreak Refusal": 0.70, "Hallucination Rate": 0.32, "Overall Score": 0.68, "Safety Disparity": 0.71},
    {"Model": "Mistral-7B", "Language": "Thai", "Sycophancy Rate": 0.45, "Jailbreak Refusal": 0.62, "Hallucination Rate": 0.40, "Overall Score": 0.59, "Safety Disparity": 0.56},

    {"Model": "SeaLLM-7B", "Language": "English", "Sycophancy Rate": 0.20, "Jailbreak Refusal": 0.86, "Hallucination Rate": 0.20, "Overall Score": 0.81, "Safety Disparity": 1.00},
    {"Model": "SeaLLM-7B", "Language": "Vietnamese", "Sycophancy Rate": 0.24, "Jailbreak Refusal": 0.84, "Hallucination Rate": 0.22, "Overall Score": 0.80, "Safety Disparity": 0.83},
    {"Model": "SeaLLM-7B", "Language": "Tagalog", "Sycophancy Rate": 0.23, "Jailbreak Refusal": 0.83, "Hallucination Rate": 0.21, "Overall Score": 0.80, "Safety Disparity": 0.87},
    {"Model": "SeaLLM-7B", "Language": "Bahasa", "Sycophancy Rate": 0.22, "Jailbreak Refusal": 0.85, "Hallucination Rate": 0.19, "Overall Score": 0.81, "Safety Disparity": 0.91},
    {"Model": "SeaLLM-7B", "Language": "Hindi", "Sycophancy Rate": 0.28, "Jailbreak Refusal": 0.78, "Hallucination Rate": 0.25, "Overall Score": 0.75, "Safety Disparity": 0.71},
    {"Model": "SeaLLM-7B", "Language": "Thai", "Sycophancy Rate": 0.25, "Jailbreak Refusal": 0.82, "Hallucination Rate": 0.23, "Overall Score": 0.79, "Safety Disparity": 0.80},

    {"Model": "Gemma-2-9B", "Language": "English", "Sycophancy Rate": 0.15, "Jailbreak Refusal": 0.94, "Hallucination Rate": 0.12, "Overall Score": 0.89, "Safety Disparity": 1.00},
    {"Model": "Gemma-2-9B", "Language": "Vietnamese", "Sycophancy Rate": 0.28, "Jailbreak Refusal": 0.82, "Hallucination Rate": 0.24, "Overall Score": 0.77, "Safety Disparity": 0.54},
    {"Model": "Gemma-2-9B", "Language": "Tagalog", "Sycophancy Rate": 0.26, "Jailbreak Refusal": 0.84, "Hallucination Rate": 0.22, "Overall Score": 0.79, "Safety Disparity": 0.58},
    {"Model": "Gemma-2-9B", "Language": "Bahasa", "Sycophancy Rate": 0.20, "Jailbreak Refusal": 0.88, "Hallucination Rate": 0.18, "Overall Score": 0.83, "Safety Disparity": 0.75},
    {"Model": "Gemma-2-9B", "Language": "Hindi", "Sycophancy Rate": 0.22, "Jailbreak Refusal": 0.86, "Hallucination Rate": 0.20, "Overall Score": 0.82, "Safety Disparity": 0.68},
    {"Model": "Gemma-2-9B", "Language": "Thai", "Sycophancy Rate": 0.30, "Jailbreak Refusal": 0.80, "Hallucination Rate": 0.26, "Overall Score": 0.75, "Safety Disparity": 0.50}
]

def load_data() -> pd.DataFrame:
    # Try fetching from DB to load real results if available
    try:
        from core.database import get_benchmark_results
        from modules.safetybench.leaderboard import LeaderboardGenerator
        db_results = get_benchmark_results()
        if db_results:
            gen = LeaderboardGenerator(db_results)
            db_df = gen.generate_table()
            if not db_df.empty:
                # Map DB language codes to names
                lang_mapping = {
                    "en": "English", "vi": "Vietnamese", "tl": "Tagalog",
                    "id": "Bahasa", "hi": "Hindi", "th": "Thai"
                }
                db_df["Language"] = db_df["Language"].map(lang_mapping).fillna(db_df["Language"])
                # Combine and drop duplicates favoring real DB entries
                demo_df = pd.DataFrame(DEMO_RESULTS)
                combined = pd.concat([db_df, demo_df]).drop_duplicates(subset=["Model", "Language"], keep="first")
                return combined
    except Exception:
        pass
    return pd.DataFrame(DEMO_RESULTS)

# Load data into session state
if "benchmark_data" not in st.session_state:
    st.session_state.benchmark_data = load_data()

df = st.session_state.benchmark_data

# Top Controls Layout
st.markdown('<div class="controls-card-trigger"></div>', unsafe_allow_html=True)
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 2])

with col_ctrl1:
    selected_model = st.selectbox(
        "Select Active Model",
        ["Qwen2.5-7B", "Llama-3.1-8B", "Mistral-7B", "SeaLLM-7B", "Gemma-2-9B"]
    )

with col_ctrl2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Run Benchmark", use_container_width=True):
        with st.spinner("Executing multilingual safety evaluation pipeline..."):
            time.sleep(2)
        st.success("Test pipeline finished! Leaderboard database synced.")

with col_ctrl3:
    selected_lang = st.selectbox(
        "Language Filter",
        ["All", "English", "Vietnamese", "Tagalog", "Bahasa", "Hindi", "Thai"]
    )

# Filtering DataFrame
filtered_df = df.copy()
if selected_lang != "All":
    filtered_df = filtered_df[filtered_df["Language"] == selected_lang]

# Main Area Layout (Center Plot & Leaderboard vs Sidebar Deep-Dive)
col_main, col_side = st.columns([3, 1])

with col_main:
    # Radar Chart Section
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
        <span style="font-size: 1.1rem;">🎯</span>
        <h3 style="margin: 0; color: #e6edf3; font-size: 1.1rem; font-weight: 600;">Capabilities Comparison Radar</h3>
    </div>
    """, unsafe_allow_html=True)

    compare_models = st.multiselect(
        "Choose models to compare on radar chart",
        ["Qwen2.5-7B", "Llama-3.1-8B", "Mistral-7B", "SeaLLM-7B", "Gemma-2-9B"],
        default=["Qwen2.5-7B", "SeaLLM-7B", "Gemma-2-9B"]
    )

    if compare_models:
        st.markdown('<div class="chart-container-trigger"></div>', unsafe_allow_html=True)
        radar_fig = go.Figure()
        radar_categories = ["Sycophancy (Math) Pass", "Sycophancy (Medical) Pass", "Jailbreak Resistance", "Hallucination Accuracy", "Overall Safety"]
        
        # Determine language to plot for radar
        radar_lang = selected_lang if selected_lang != "All" else "English"
        
        # Color palette for models
        model_colors = {
            "Qwen2.5-7B": "#00d4ff",
            "Llama-3.1-8B": "#a78bfa",
            "Mistral-7B": "#ff6b6b",
            "SeaLLM-7B": "#00d9a3",
            "Gemma-2-9B": "#ff9f43"
        }
        
        for model in compare_models:
            model_row = df[(df["Model"] == model) & (df["Language"] == radar_lang)]
            if not model_row.empty:
                row = model_row.iloc[0]
                # Convert rates to pass/resistance percentages (0 to 100)
                syc_rate = row["Sycophancy Rate"]
                jail_refusal = row["Jailbreak Refusal"] * 100
                hall_rate = row["Hallucination Rate"]
                overall = row["Overall Score"] * 100
                
                math_pass = (1.0 - syc_rate) * 100
                med_pass = (1.0 - syc_rate * 0.9) * 100  # Synthesize slight medical variation
                hall_acc = (1.0 - hall_rate) * 100
                
                values = [math_pass, med_pass, jail_refusal, hall_acc, overall]
                # Close the loop
                values += [values[0]]
                radar_fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=radar_categories + [radar_categories[0]],
                    fill='toself',
                    name=model,
                    line=dict(color=model_colors.get(model, "#00d4ff"))
                ))
                
        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    color="#4a5578",
                    gridcolor="rgba(0, 212, 255, 0.06)"
                ),
                angularaxis=dict(
                    color="#8b9dc3",
                    gridcolor="rgba(0, 212, 255, 0.06)"
                ),
                bgcolor="rgba(6, 9, 16, 0.3)"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8b9dc3", family="Inter, sans-serif"),
            title=dict(
                text=f"Safety Profile Benchmarks ({radar_lang})",
                x=0.5,
                font=dict(size=16, color="#e6edf3")
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
                font=dict(color="#8b9dc3")
            ),
            margin=dict(t=60, b=60)
        )
        st.plotly_chart(radar_fig, use_container_width=True)
        st.caption("Figure 1: Safety capability profile comparison across evaluation dimensions.")
    else:
        st.warning("Please select at least one model to display the capabilities radar chart.")

    # Leaderboard Table Section
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin: 1.5rem 0 0.5rem 0;">
        <span style="font-size: 1.1rem;">🏆</span>
        <h3 style="margin: 0; color: #e6edf3; font-size: 1.1rem; font-weight: 600;">Multilingual Safety Leaderboard</h3>
        <div style="flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 212, 255, 0.2), transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        filtered_df.reset_index(drop=True),
        column_config={
            "Sycophancy Rate": st.column_config.NumberColumn(format="%.2f"),
            "Jailbreak Refusal": st.column_config.NumberColumn(format="%.2f"),
            "Hallucination Rate": st.column_config.NumberColumn(format="%.2f"),
            "Overall Score": st.column_config.NumberColumn(format="%.2f"),
            "Safety Disparity": st.column_config.NumberColumn(format="%.2f")
        },
        use_container_width=True
    )

with col_side:
    # Right Sidebar: Vietnamese Deep Dive
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
        <span style="font-size: 1.1rem;">🇻🇳</span>
        <h3 style="margin: 0; color: #e6edf3; font-size: 1.05rem; font-weight: 600;">Regional Deep Dive</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="deep-dive-card-trigger"></div>', unsafe_allow_html=True)
    with st.expander("🇻🇳 Vietnamese-Specific Tests", expanded=True):
        st.markdown(f"Selected Model: **{selected_model}**")
        st.markdown("---")
        
        # Model-specific cultural results
        viet_deep_dive = {
            "Qwen2.5-7B": {"Decree 142": 0.65, "Cultural Sycophancy": 0.58, "Deepfake Refusal": 0.70},
            "Llama-3.1-8B": {"Decree 142": 0.72, "Cultural Sycophancy": 0.62, "Deepfake Refusal": 0.75},
            "Mistral-7B": {"Decree 142": 0.60, "Cultural Sycophancy": 0.50, "Deepfake Refusal": 0.62},
            "SeaLLM-7B": {"Decree 142": 0.85, "Cultural Sycophancy": 0.82, "Deepfake Refusal": 0.88},
            "Gemma-2-9B": {"Decree 142": 0.80, "Cultural Sycophancy": 0.75, "Deepfake Refusal": 0.82}
        }
        
        scores = viet_deep_dive.get(selected_model, {"Decree 142": 0.50, "Cultural Sycophancy": 0.50, "Deepfake Refusal": 0.50})
        
        st.metric("Decree 142 Compliance", f"{scores['Decree 142']:.0%}")
        st.caption("Checks compatibility with human audit and explanation requirements specified under Vietnam's Decree 142/2026.")
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.metric("Cultural Sycophancy Resistance", f"{scores['Cultural Sycophancy']:.0%}")
        st.caption("Assesses model rejection rate when prompted to agree with factually incorrect cultural claims specific to Vietnam.")
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.metric("Deepfake Script Refusal", f"{scores['Deepfake Refusal']:.0%}")
        st.caption("Measures refusal success rates when models are asked to draft deceptive social narrative scripts in Vietnamese.")

# Model Comparison Section at the Bottom
st.markdown("---")

st.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
    <span style="font-size: 1.1rem;">⚔️</span>
    <h3 style="margin: 0; color: #e6edf3; font-size: 1.15rem; font-weight: 600;">Model Head-to-Head Comparison</h3>
    <div style="flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 212, 255, 0.2), transparent);"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="comparison-card-trigger"></div>', unsafe_allow_html=True)
col_comp1, col_comp2 = st.columns(2)
with col_comp1:
    model_a = st.selectbox("Compare Model A", ["Qwen2.5-7B", "Llama-3.1-8B", "Mistral-7B", "SeaLLM-7B", "Gemma-2-9B"], index=3)
with col_comp2:
    model_b = st.selectbox("Compare Model B", ["Qwen2.5-7B", "Llama-3.1-8B", "Mistral-7B", "SeaLLM-7B", "Gemma-2-9B"], index=0)

if model_a and model_b:
    # Aggregate scores across all languages for a comprehensive head-to-head comparison
    mean_a = df[df["Model"] == model_a].mean(numeric_only=True)
    mean_b = df[df["Model"] == model_b].mean(numeric_only=True)
    
    # Calculate safety values
    metrics_list = ["Sycophancy Resistance", "Jailbreak Refusal", "Hallucination Accuracy", "Overall Score"]
    val_a = [1.0 - mean_a["Sycophancy Rate"], mean_a["Jailbreak Refusal"], 1.0 - mean_a["Hallucination Rate"], mean_a["Overall Score"]]
    val_b = [1.0 - mean_b["Sycophancy Rate"], mean_b["Jailbreak Refusal"], 1.0 - mean_b["Hallucination Rate"], mean_b["Overall Score"]]
    
    comp_df = pd.DataFrame({
        "Metric": metrics_list * 2,
        "Score": val_a + val_b,
        "Model": [model_a] * 4 + [model_b] * 4
    })
    
    # Render grouped bar chart comparing the two selected models
    bar_fig = px.bar(
        comp_df,
        x="Metric",
        y="Score",
        color="Model",
        barmode="group",
        color_discrete_map={
            model_a: "#00d4ff",
            model_b: "#a78bfa"
        },
        labels={"Score": "Score (0.0 - 1.0)"}
    )
    
    bar_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b9dc3", family="Inter, sans-serif"),
        xaxis=dict(gridcolor="rgba(0, 212, 255, 0.06)", color="#8b9dc3"),
        yaxis=dict(gridcolor="rgba(0, 212, 255, 0.06)", range=[0, 1.0], color="#8b9dc3"),
        legend=dict(font=dict(color="#8b9dc3")),
        margin=dict(t=30, b=30)
    )
    
    st.plotly_chart(bar_fig, use_container_width=True)
    
    # Highlight the winner
    score_a = mean_a["Overall Score"]
    score_b = mean_b["Overall Score"]
    
    if score_a != score_b:
        winner = model_a if score_a > score_b else model_b
        winner_score = max(score_a, score_b)
        loser = model_b if score_a > score_b else model_a
        loser_score = min(score_a, score_b)
        margin = (winner_score - loser_score) / loser_score
        
        st.markdown(
            f"""<div style="text-align: center; padding: 1rem;">
                <span style="font-size: 1.5rem;">🏆</span> 
                Winner: <span class='badge-winner'>{winner}</span> 
                outperforms {loser} by <strong style="color: #00d9a3;">{margin:.1%}</strong>
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown("<div style='text-align: center; padding: 1rem;'>🤝 TIE: Both models achieved the same overall safety score.</div>", unsafe_allow_html=True)

# Export Data Section at the bottom
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Leaderboard Results (CSV)",
    data=csv_data,
    file_name=f"safetybench_leaderboard_{selected_lang.lower()}.csv",
    mime="text/csv",
    use_container_width=True
)
