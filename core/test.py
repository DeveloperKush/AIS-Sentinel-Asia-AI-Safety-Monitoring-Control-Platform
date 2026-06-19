import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core.database import init_db
from modules.intelstream.evaluator import ThreatEvaluator

# Ensure database tables exist
init_db()

e = ThreatEvaluator()
result = e.evaluate(
    "A new open-source AI model was released that can design novel protein sequences for viral research without safety guardrails.",
    "AI Protein Designer Released"
)
print(result)
assert result["threat_detected"] is True
assert result["confidence_score"] > 0.7
assert "AI-EngBio integration" in result["risk_category"] or "Dual-use" in result["risk_category"]
print("Evaluator test PASSED")
