import os
from dotenv import load_dotenv

load_dotenv()

from core.llm_client import GeminiClient

client = GeminiClient()

# Test translation
result = client.translate("Xin chào thế giới", "vi", "en")
print("Translation:", result)

# Test structured output
schema = {"type": "object", "properties": {"threat_detected": {"type": "boolean"}}}
result = client.generate_structured("Is this a threat: 'AI gene synthesis tool released'", schema)
print("Structured:", result)