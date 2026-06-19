import os
from dotenv import load_dotenv

# Load environment variables before importing local modules
load_dotenv()

from core.database import init_db
from core.translator import SmartTranslator

# Ensure the database tables exist
init_db()

# Initialize translator
t = SmartTranslator()

# Run the test
result = t.translate_article(
    "Tin tức về CRISPR",
    "Công nghệ CRISPR mới được sử dụng trong nghiên cứu gene. Đây là bước tiến lớn.",
    "vi"
)

print("Translation Result:")
print(result)
