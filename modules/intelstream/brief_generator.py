"""
modules/intelstream/brief_generator.py
Generates an HTML weekly intelligence brief from threat-detected articles.
"""

import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, BaseLoader

from core.database import get_articles


# ---------------------------------------------------------------------------
# Inline HTML/CSS template (used when no file-based template is found)
# ---------------------------------------------------------------------------
BRIEF_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly Biosecurity Intelligence Brief — {{ region }}</title>
<style>
  /* ---- Reset & Base ---- */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Helvetica Neue', Arial, Helvetica, sans-serif;
    color: #212529;
    background: #f8f9fa;
    line-height: 1.6;
    padding: 0;
    margin: 0;
  }
  .container { max-width: 960px; margin: 0 auto; padding: 24px; }

  /* ---- Header ---- */
  .header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #fff;
    padding: 32px 24px;
    border-radius: 8px;
    margin-bottom: 28px;
    text-align: center;
  }
  .header h1 { font-size: 1.65rem; font-weight: 700; margin-bottom: 6px; }
  .header .date-range { font-size: 0.95rem; opacity: 0.85; }

  /* ---- Section titles ---- */
  .section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a2e;
    border-bottom: 3px solid #0f3460;
    padding-bottom: 6px;
    margin: 28px 0 16px;
  }

  /* ---- Executive Summary ---- */
  .exec-summary {
    background: #ffffff;
    border-left: 4px solid #0f3460;
    padding: 18px 20px;
    border-radius: 6px;
    margin-bottom: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .exec-summary ul { list-style: disc inside; }
  .exec-summary li { margin-bottom: 6px; font-size: 0.95rem; }

  /* ---- Table ---- */
  .table-wrapper { overflow-x: auto; margin-bottom: 8px; }
  table {
    width: 100%;
    border-collapse: collapse;
    background: #fff;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  th {
    background: #1a1a2e;
    color: #fff;
    text-align: left;
    padding: 12px 14px;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  td { padding: 10px 14px; font-size: 0.9rem; border-bottom: 1px solid #e9ecef; }
  tr:last-child td { border-bottom: none; }
  tr:nth-child(even) td { background: #f8f9fa; }

  /* ---- Cards ---- */
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 18px; }
  .card {
    background: #fff;
    border-radius: 8px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-left: 5px solid #6c757d;
  }
  .card.critical { border-left-color: #dc3545; }
  .card.high     { border-left-color: #fd7e14; }
  .card.medium   { border-left-color: #ffc107; }
  .card.low      { border-left-color: #28a745; }

  .card .card-title { font-size: 1rem; font-weight: 700; margin-bottom: 8px; color: #212529; }
  .card .meta { font-size: 0.82rem; color: #6c757d; margin-bottom: 10px; }
  .card .meta span { margin-right: 14px; }

  /* Progress bar */
  .progress-wrap {
    background: #e9ecef;
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
    margin: 8px 0 10px;
  }
  .progress-bar {
    height: 100%;
    border-radius: 6px;
  }
  .progress-bar.critical { background: #dc3545; }
  .progress-bar.high     { background: #fd7e14; }
  .progress-bar.medium   { background: #ffc107; }
  .progress-bar.low      { background: #28a745; }

  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }
  .badge.critical { background: #dc3545; }
  .badge.high     { background: #fd7e14; }
  .badge.medium   { background: #ffc107; color: #212529; }
  .badge.low      { background: #28a745; }

  .justification { font-size: 0.88rem; color: #495057; margin-top: 8px; line-height: 1.5; }

  /* ---- Footer ---- */
  .footer {
    text-align: center;
    font-size: 0.82rem;
    color: #6c757d;
    margin-top: 36px;
    padding-top: 16px;
    border-top: 1px solid #dee2e6;
  }

  /* ---- Responsive ---- */
  @media (max-width: 560px) {
    .cards { grid-template-columns: 1fr; }
    .header h1 { font-size: 1.25rem; }
  }
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>Weekly Biosecurity Intelligence Brief &mdash; {{ region }}</h1>
    <div class="date-range">{{ date_start }} &ndash; {{ date_end }}</div>
  </div>

  <!-- Executive Summary -->
  <h2 class="section-title">Executive Summary</h2>
  <div class="exec-summary">
    <ul>
    {% for point in executive_summary %}
      <li>{{ point }}</li>
    {% endfor %}
    </ul>
  </div>

  <!-- Regional Trends -->
  <h2 class="section-title">Regional Trends</h2>
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Country</th>
          <th>Threats Detected</th>
          <th>Top Category</th>
          <th>Trend</th>
        </tr>
      </thead>
      <tbody>
      {% for row in regional_trends %}
        <tr>
          <td>{{ row.country }}</td>
          <td>{{ row.threats }}</td>
          <td>{{ row.top_category }}</td>
          <td>{{ row.trend }}</td>
        </tr>
      {% endfor %}
      {% if not regional_trends %}
        <tr><td colspan="4" style="text-align:center;color:#6c757d;">No data available</td></tr>
      {% endif %}
      </tbody>
    </table>
  </div>

  <!-- Flagged High-Risk Events -->
  <h2 class="section-title">Flagged High-Risk Events</h2>
  <div class="cards">
  {% for article in flagged_articles %}
    <div class="card {{ article.severity_class }}">
      <div class="card-title">{{ article.title or "Untitled Article" }}</div>
      <div class="meta">
        <span>&#127758; {{ article.source_country or "Unknown" }}</span>
        <span><span class="badge {{ article.severity_class }}">{{ article.risk_category or "Unclassified" }}</span></span>
      </div>
      <div style="font-size:0.82rem;color:#6c757d;">
        Confidence: {{ "%.0f" | format(article.confidence_score * 100) }}%
      </div>
      <div class="progress-wrap">
        <div class="progress-bar {{ article.severity_class }}"
             style="width:{{ (article.confidence_score * 100) | round | int }}%"></div>
      </div>
      <div class="justification">{{ article.justification or "" }}</div>
    </div>
  {% endfor %}
  {% if not flagged_articles %}
    <p style="color:#6c757d;">No high-risk events flagged this period.</p>
  {% endif %}
  </div>

  <!-- Footer -->
  <div class="footer">
    Generated by <strong>AIS-Sentinel</strong> | Global South AIS Challenge 2026
  </div>

</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _severity_class(risk_category: Optional[str]) -> str:
    """Map a risk_category string to a CSS class name."""
    if not risk_category:
        return "low"
    cat = risk_category.strip().lower()
    if cat in ("critical",):
        return "critical"
    if cat in ("high",):
        return "high"
    if cat in ("medium", "moderate"):
        return "medium"
    return "low"


def _trend_arrow(count: int) -> str:
    """Simple heuristic trend indicator."""
    if count >= 5:
        return "⬆ Rising"
    if count >= 2:
        return "➡ Stable"
    return "⬇ Low"


# ---------------------------------------------------------------------------
# BriefGenerator
# ---------------------------------------------------------------------------

class BriefGenerator:
    """Generates an HTML weekly intelligence brief from the articles database."""

    def __init__(self, template_dir: str = "assets/templates"):
        """Initialise the Jinja2 environment.

        If *template_dir* exists and contains ``brief_template.html``,
        that file is used as the template source.  Otherwise the inline
        ``BRIEF_TEMPLATE`` string embedded in this module is used.
        """
        self.template_dir = template_dir
        template_file = os.path.join(template_dir, "brief_template.html")

        if os.path.isfile(template_file):
            self.env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=True,
            )
            self.template = self.env.get_template("brief_template.html")
        else:
            # Fall back to the inline template string
            self.env = Environment(loader=BaseLoader(), autoescape=True)
            self.template = self.env.from_string(BRIEF_TEMPLATE)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def generate_brief(self, days: int = 7, region: str = "Asia") -> str:
        """Build and return the full HTML brief as a string.

        Args:
            days:   How many days back to include (default 7).
            region: Region label shown in the header.

        Returns:
            A complete HTML document as a string.
        """
        # 1. Date window
        date_end = datetime.now()
        date_start = date_end - timedelta(days=days)

        # 2. Fetch articles from the database
        all_articles = get_articles(threat_only=False, limit=500)

        # Filter to the requested time window
        articles_in_window: List[Dict[str, Any]] = []
        for art in all_articles:
            created = art.get("created_at")
            if created:
                try:
                    ts = datetime.fromisoformat(created)
                    if ts >= date_start:
                        articles_in_window.append(art)
                except (ValueError, TypeError):
                    # If timestamp can't be parsed, include it anyway
                    articles_in_window.append(art)
            else:
                articles_in_window.append(art)

        # 3. Separate threat articles
        threat_articles = [
            a for a in articles_in_window if a.get("threat_detected")
        ]

        # 4. Build executive summary
        executive_summary = self._build_executive_summary(
            articles_in_window, threat_articles, region, days
        )

        # 5. Build regional trends table
        regional_trends = self._build_regional_trends(threat_articles)

        # 6. Prepare flagged articles (sorted by confidence descending)
        flagged = sorted(
            threat_articles,
            key=lambda a: a.get("confidence_score") or 0,
            reverse=True,
        )
        for art in flagged:
            art["severity_class"] = _severity_class(art.get("risk_category"))
            # Ensure confidence_score is a float for the template
            art["confidence_score"] = float(art.get("confidence_score") or 0)

        # 7. Render
        html = self.template.render(
            region=region,
            date_start=date_start.strftime("%d %b %Y"),
            date_end=date_end.strftime("%d %b %Y"),
            executive_summary=executive_summary,
            regional_trends=regional_trends,
            flagged_articles=flagged,
        )
        return html

    def save_brief(self, html: str, filename: str) -> str:
        """Write the rendered HTML to *filename*.

        Parent directories are created if they don't exist.

        Args:
            html:     The HTML string to save.
            filename: Destination file path.

        Returns:
            The absolute path of the saved file.
        """
        dirpath = os.path.dirname(filename)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(html)

        return os.path.abspath(filename)

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_executive_summary(
        all_articles: List[Dict],
        threat_articles: List[Dict],
        region: str,
        days: int,
    ) -> List[str]:
        """Return 3-4 bullet-point strings summarising the top threats."""
        total = len(all_articles)
        threats = len(threat_articles)

        # Top risk categories
        cat_counter: Counter = Counter()
        country_counter: Counter = Counter()
        for a in threat_articles:
            cat = a.get("risk_category")
            if cat:
                cat_counter[cat] += 1
            country = a.get("source_country")
            if country:
                country_counter[country] += 1

        summary: List[str] = []

        # Bullet 1 — overview
        summary.append(
            f"{threats} potential biosecurity threat(s) identified out of "
            f"{total} article(s) scanned in the {region} region over the "
            f"past {days} day(s)."
        )

        # Bullet 2 — top category
        if cat_counter:
            top_cat, top_count = cat_counter.most_common(1)[0]
            summary.append(
                f"Dominant risk category: {top_cat} ({top_count} occurrence(s))."
            )
        else:
            summary.append("No dominant risk category identified this period.")

        # Bullet 3 — top country
        if country_counter:
            top_country, c_count = country_counter.most_common(1)[0]
            summary.append(
                f"Highest activity source: {top_country} with {c_count} flagged article(s)."
            )

        # Bullet 4 — high-confidence alerts
        high_conf = [
            a for a in threat_articles
            if (a.get("confidence_score") or 0) >= 0.8
        ]
        if high_conf:
            summary.append(
                f"{len(high_conf)} article(s) flagged with ≥80 % confidence — "
                "immediate review recommended."
            )
        else:
            summary.append(
                "No articles exceeded the 80 % confidence threshold this period."
            )

        return summary

    @staticmethod
    def _build_regional_trends(
        threat_articles: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Group threats by country and return a list of trend dicts."""
        country_data: Dict[str, List[Dict]] = defaultdict(list)
        for a in threat_articles:
            country = a.get("source_country") or "Unknown"
            country_data[country].append(a)

        trends: List[Dict[str, Any]] = []
        for country, articles in sorted(
            country_data.items(), key=lambda x: len(x[1]), reverse=True
        ):
            cat_counter: Counter = Counter(
                a.get("risk_category") or "Unclassified" for a in articles
            )
            top_category = cat_counter.most_common(1)[0][0] if cat_counter else "N/A"
            trends.append(
                {
                    "country": country,
                    "threats": len(articles),
                    "top_category": top_category,
                    "trend": _trend_arrow(len(articles)),
                }
            )
        return trends
