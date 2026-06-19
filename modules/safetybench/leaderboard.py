import os
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from modules.safetybench.metrics import (
    compute_capitulation_rate,
    compute_refusal_rate,
    compute_hallucination_rate,
    compute_overall_score,
    compute_safety_disparity
)

class LeaderboardGenerator:
    """Generates leaderboard tables, dataframes, visualizations (radar, bar, heatmap), and HTML reports."""

    def __init__(self, results: Optional[List[Dict[str, Any]]] = None) -> None:
        """Initializes the LeaderboardGenerator, loading all benchmark results if not provided.
        
        Args:
            results: Optional list of preloaded benchmark result dictionaries.
        """
        if results is not None:
            self.results = results
        else:
            try:
                from core.database import get_benchmark_results
                self.results = get_benchmark_results()
            except Exception:
                self.results = []

    def generate_table(self, results: Optional[List[Dict[str, Any]]] = None) -> pd.DataFrame:
        """Generates a summary DataFrame of safety performance metrics grouped by model and language.
        
        Args:
            results: Optional list of benchmark results to use (defaults to generator's results).
            
        Returns:
            A pandas DataFrame with the safety leaderboard metrics.
        """
        res = results if results is not None else self.results
        if not res:
            return pd.DataFrame(columns=[
                "Model", "Language", "Sycophancy Rate", "Jailbreak Refusal",
                "Hallucination Rate", "Overall Score", "Safety Disparity"
            ])

        # Group results by (model_name, language)
        grouped_results: Dict[tuple, List[Dict[str, Any]]] = {}
        for r in res:
            model = r.get("model_name", "unknown")
            lang = r.get("language", "en")
            key = (model, lang)
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(r)

        # Separate English results per model to compute safety disparity
        model_english_results: Dict[str, List[Dict[str, Any]]] = {}
        for (model, lang), group in grouped_results.items():
            if lang == "en":
                model_english_results[model] = group

        rows = []
        for (model, lang), group in grouped_results.items():
            syc_rate = compute_capitulation_rate(group)
            jail_refusal = compute_refusal_rate(group)
            hall_rate = compute_hallucination_rate(group)
            overall = compute_overall_score(group)

            eng_res = model_english_results.get(model, [])
            disparity = compute_safety_disparity(eng_res, group)

            rows.append({
                "Model": model,
                "Language": lang,
                "Sycophancy Rate": round(syc_rate, 2),
                "Jailbreak Refusal": round(jail_refusal, 2),
                "Hallucination Rate": round(hall_rate, 2),
                "Overall Score": round(overall, 2),
                "Safety Disparity": round(disparity, 2)
            })

        return pd.DataFrame(rows)

    def generate_radar_chart(self, model_name: str, results: Optional[List[Dict[str, Any]]] = None) -> go.Figure:
        """Generates a Plotly radar chart showing safety metrics across languages for a single model.
        
        Args:
            model_name: The name of the model to filter by.
            results: Optional list of benchmark results to use.
            
        Returns:
            A Plotly radar chart Figure.
        """
        res = results if results is not None else self.results
        model_results = [r for r in res if r.get("model_name") == model_name]
        if not model_results:
            return go.Figure()

        languages = sorted(list(set(r.get("language", "en") for r in model_results)))
        fig = go.Figure()

        categories = [
            "Sycophancy (Math) Pass",
            "Sycophancy (Medical) Pass",
            "Jailbreak Refusal",
            "Hallucination Pass",
            "Overall Score"
        ]

        for lang in languages:
            lang_res = [r for r in model_results if r.get("language") == lang]

            # Compute specific subcategory rates
            math_tests = [r for r in lang_res if r.get("test_type") == "sycophancy_math"]
            med_tests = [r for r in lang_res if r.get("test_type") == "sycophancy_medical"]
            jail_tests = [r for r in lang_res if r.get("test_type") == "jailbreak"]
            hall_tests = [r for r in lang_res if r.get("test_type") == "hallucination"]

            math_pass = (sum(1 for r in math_tests if r.get("passed")) / len(math_tests)) * 100.0 if math_tests else 100.0
            med_pass = (sum(1 for r in med_tests if r.get("passed")) / len(med_tests)) * 100.0 if med_tests else 100.0
            jail_refusal = (sum(1 for r in jail_tests if r.get("passed")) / len(jail_tests)) * 100.0 if jail_tests else 100.0
            hall_pass = (sum(1 for r in hall_tests if r.get("passed")) / len(hall_tests)) * 100.0 if hall_tests else 100.0
            overall = compute_overall_score(lang_res) * 100.0

            values = [math_pass, med_pass, jail_refusal, hall_pass, overall]
            # Close the radar loop
            values_closed = values + [values[0]]
            categories_closed = categories + [categories[0]]

            fig.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=categories_closed,
                fill="toself",
                name=f"{lang.upper()}"
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title=dict(
                text=f"Safety Capabilities Radar - {model_name}",
                x=0.5
            ),
            showlegend=True
        )
        return fig

    def generate_comparison_bar(self, metric: str, results: Optional[List[Dict[str, Any]]] = None) -> go.Figure:
        """Generates a Plotly bar chart comparing safety metric scores across all models.
        
        Args:
            metric: The column name/metric to compare (e.g., 'Overall Score', 'Jailbreak Refusal').
            results: Optional list of benchmark results to use.
            
        Returns:
            A Plotly bar chart Figure.
        """
        res = results if results is not None else self.results
        df = self.generate_table(res)
        if df.empty or metric not in df.columns:
            return go.Figure()

        fig = px.bar(
            df,
            x="Model",
            y=metric,
            color="Language",
            barmode="group",
            title=f"Model Comparison on {metric}",
            labels={"Model": "Model Name", metric: metric}
        )
        fig.update_layout(title_x=0.5)
        return fig

    def generate_heatmap(self, results: Optional[List[Dict[str, Any]]] = None) -> go.Figure:
        """Generates a Plotly heatmap showcasing Overall Score per Model x Language combination.
        
        Args:
            results: Optional list of benchmark results to use.
            
        Returns:
            A Plotly heatmap Figure.
        """
        res = results if results is not None else self.results
        df = self.generate_table(res)
        if df.empty:
            return go.Figure()

        # Pivot to model x language grid
        pivot_df = df.pivot(index="Model", columns="Language", values="Overall Score")

        fig = px.imshow(
            pivot_df,
            labels=dict(x="Language", y="Model", color="Overall Score"),
            x=pivot_df.columns,
            y=pivot_df.index,
            title="Safety Score Heatmap (Model × Language)",
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(title_x=0.5)
        return fig

    def save_leaderboard_html(self, df: pd.DataFrame, filename: str) -> None:
        """Saves the safety evaluation DataFrame as a styled premium HTML page.
        
        Args:
            df: The DataFrame to save.
            filename: Destination file path.
        """
        table_html = df.to_html(index=False, classes="table table-striped table-hover")

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AIS-Sentinel - Safety Leaderboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Outfit', sans-serif;
            background-color: #0d0e15;
            color: #e2e8f0;
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            text-align: center;
        }}
        .subtitle {{
            font-size: 1.1rem;
            color: #94a3b8;
            text-align: center;
            margin-bottom: 40px;
        }}
        .table-container {{
            background: #151726;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            overflow-x: auto;
            margin-bottom: 40px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            color: #e2e8f0;
        }}
        th {{
            background-color: #1e2238;
            font-weight: 600;
            text-align: left;
            padding: 14px 16px;
            font-size: 0.95rem;
            border-bottom: 2px solid #312e81;
            color: #a5b4fc;
        }}
        td {{
            padding: 12px 16px;
            font-size: 0.9rem;
            border-bottom: 1px solid #1f2937;
        }}
        tr:hover td {{
            background-color: #1e1b4b;
        }}
        .footer {{
            text-align: center;
            margin-top: 60px;
            font-size: 0.85rem;
            color: #64748b;
            border-top: 1px solid #1e2937;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AIS-Sentinel Safety Leaderboard</h1>
        <div class="subtitle">Multilingual evaluation metrics across safety axes</div>
        <div class="table-container">
            {table_html}
        </div>
        <div class="footer">
            Generated by AIS-Sentinel | Global South AIS Challenge 2026
        </div>
    </div>
</body>
</html>"""

        dirpath = os.path.dirname(os.path.abspath(filename))
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
            
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
