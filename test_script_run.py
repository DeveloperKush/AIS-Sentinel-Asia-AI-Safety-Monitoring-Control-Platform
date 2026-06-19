from core.database import init_db
init_db()

from modules.intelstream.brief_generator import BriefGenerator
bg = BriefGenerator()
html = bg.generate_brief(days=30)
print("HTML length:", len(html))
print("Contains 'Executive Summary':", 'Executive Summary' in html)
print("Contains 'Flagged High-Risk':", 'Flagged High-Risk' in html)
