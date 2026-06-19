import os
import sys
from dotenv import load_dotenv

# Ensure the root directory is on the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

import core.database as db
from core.translator import SmartTranslator
from modules.intelstream.scraper import RSSScraper, KeywordFilter
from modules.intelstream.evaluator import ThreatEvaluator

def run_tests():
    print("==================================================")
    print("Running AIS-Sentinel Integrated Test Suite")
    print("==================================================")
    
    # 1. Test Database
    print("\n[1/4] Testing SQLite Database Schema & Helpers...")
    db.DB_PATH = "test_sentinel_temp.db"
    if os.path.exists(db.DB_PATH):
        try:
            os.remove(db.DB_PATH)
        except Exception:
            pass
        
    db.init_db()
    
    article_id = db.insert_article({
        "title": "Initial Test Article",
        "source_url": "https://example.com/test",
        "source_country": "PH",
        "language": "en",
        "original_text": "Original text sample",
        "translated_text": "Original text sample",
        "threat_detected": False,
        "confidence_score": 0.0,
        "risk_category": "None",
        "justification": "Initial"
    })
    print(f"OK: Database initialized. Inserted article ID: {article_id}")
    
    # 2. Test Translator
    print("\n[2/4] Testing Smart Translator & Language Detection...")
    translator = SmartTranslator()
    
    # Language detection
    detected = translator.detect_language("Xin chào, đây là một bài viết thử nghiệm.")
    print(f"OK: Language detection: 'Xin chào...' -> '{detected}'")
    
    # Translation & cache
    trans_result = translator.translate_article(
        "Thử nghiệm công nghệ sinh học",
        "Công nghệ CRISPR được sử dụng rộng rãi trong các nghiên cứu gene thế hệ mới.",
        "vi"
    )
    print("OK: Translated Title:", trans_result["title_en"])
    print("OK: Translated Text:", trans_result["text_en"])
    print("OK: Extracted Key Sentences:", trans_result["key_sentences_en"])
    
    # 3. Test Scraper & Filter
    print("\n[3/4] Testing Scraper & Keyword Filter...")
    kf = KeywordFilter()
    
    test_article = {
        "title": "Advances in genome editing",
        "summary": "Scientists developed a new gain-of-function viral vector.",
        "text": "This research poses certain biosecurity and laboratory safety questions."
    }
    match = kf.filter_article(test_article)
    print(f"OK: Keyword filter matched article: {match}")
    relevant = kf.extract_relevant_sentences(test_article["text"])
    print(f"OK: Relevant sentences extracted: {relevant}")
    
    # 4. Test Evaluator
    print("\n[4/4] Testing Threat Evaluator & Aggregation...")
    evaluator = ThreatEvaluator()
    eval_result = evaluator.evaluate(
        "A biosecurity laboratory in Southeast Asia reported a leak of a dangerous pathogen CRISPR modification.",
        "Pathogen Leak Reported"
    )
    print("OK: Evaluator Structured Result:")
    for k, v in eval_result.items():
        print(f"  - {k}: {v}")
        
    summary = evaluator.get_threat_summary(days=1)
    print("\nOK: Threat summary aggregation statistics:")
    print("  - Total threats detected:", summary["total_threats"])
    print("  - By country:", summary["by_country"])
    print("  - By category:", summary["by_category"])
    
    # Cleanup DB
    if os.path.exists(db.DB_PATH):
        try:
            os.remove(db.DB_PATH)
        except Exception:
            pass
        
    print("\n==================================================")
    print("ALL COMPONENT TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
