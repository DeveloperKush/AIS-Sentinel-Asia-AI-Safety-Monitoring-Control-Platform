import re
import logging
from typing import List, Dict, Any, Optional

from core.llm_client import GeminiClient
from core.database import get_db_connection, insert_article

logger = logging.getLogger(__name__)

DEFAULT_KEYWORDS = [
    "safety", "security", "threat", "risk", "hazard", "attack", "jailbreak",
    "vulnerability", "exploit", "biological", "bioweapon", "pathogen", "synthesis",
    "gene", "CRISPR", "chemical", "nuclear", "weapon", "dual-use", "misuse",
    "autonomous", "agent", "alignment", "policy", "regulation", "governance",
    "critical", "infrastructure", "cybersecurity", "malware", "phishing"
]

class SmartTranslator:
    """
    A translator that translates Southeast Asian languages to English using Gemini Flash API,
    caches the results in SQLite, and extracts key safety-related sentences.
    """
    
    def __init__(self) -> None:
        """Initializes the SmartTranslator with a GeminiClient instance."""
        self.client = GeminiClient()
        
    def extract_key_sentences(self, text: str, keywords: List[str], max_sentences: int = 5) -> List[str]:
        """Splits text into sentences and returns only sentences containing at least one keyword (case-insensitive).
        
        Args:
            text: The text to extract sentences from.
            keywords: A list of keywords to search for.
            max_sentences: The maximum number of sentences to return.
            
        Returns:
            A list of matching sentences.
        """
        if not text:
            return []
        
        # Split sentences by standard sentence terminators (. ! ?) followed by whitespace or end of string
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        
        key_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw.lower() in sentence_lower for kw in keywords):
                key_sentences.append(sentence)
                if len(key_sentences) >= max_sentences:
                    break
        return key_sentences

    def translate_article(self, title: str, text: str, source_lang: str) -> Dict[str, Any]:
        """Translates an article's title and text to English, caches the result in SQLite,
        and extracts key sentences.
        
        Args:
            title: The original article title.
            text: The original article text.
            source_lang: The source language code (e.g., 'vi', 'th', 'hi', 'tl', 'id', 'en').
            
        Returns:
            A dictionary containing the English title, English text, and key sentences.
        """
        source_lang_lower = source_lang.strip().lower()
        
        # Check cache first
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT title, translated_text FROM articles WHERE original_text = ? AND translated_text IS NOT NULL AND translated_text != '' LIMIT 1",
                (text,)
            )
            row = cursor.fetchone()
            if row:
                title_en = row["title"]
                text_en = row["translated_text"]
                return {
                    "title_en": title_en,
                    "text_en": text_en,
                    "key_sentences_en": self.extract_key_sentences(text_en, DEFAULT_KEYWORDS)
                }

        # Handle pass-through for English
        if source_lang_lower == "en":
            title_en = title
            text_en = text
        else:
            # Translation prompts instructing Gemini with technical terms and formal tone requirements
            title_prompt = (
                "You are a professional translator. Translate the following article title to English.\n"
                f"Source language code: {source_lang_lower}\n"
                "Preserve technical terms (CRISPR, gene synthesis, AI model names, etc.) in English if they appear.\n"
                "Maintain a formal tone suitable for policy analysis.\n"
                "Return ONLY the translated title, with no introductory text, surrounding quotes, or explanations.\n\n"
                f"Title: {title}"
            )
            
            text_prompt = (
                "You are a professional translator. Translate the following text to English.\n"
                f"Source language code: {source_lang_lower}\n"
                "Preserve technical terms (CRISPR, gene synthesis, AI model names, etc.) in English if they appear.\n"
                "Maintain a formal tone suitable for policy analysis.\n"
                "Return ONLY the translated text, with no additional commentary, notes, or explanations.\n\n"
                f"Text:\n{text}"
            )
            
            title_en = self.client.generate(title_prompt, temperature=0.2, response_mime_type="text/plain").strip()
            text_en = self.client.generate(text_prompt, temperature=0.2, response_mime_type="text/plain").strip()

        # Cache/save the translated article
        # Check if a record with the same original text already exists to update it, otherwise insert new
        article_exists = False
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM articles WHERE original_text = ? LIMIT 1", (text,))
            row = cursor.fetchone()
            if row:
                article_exists = True
                article_id = row["id"]
                
        if article_exists:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE articles SET title = ?, translated_text = ? WHERE id = ?",
                    (title_en, text_en, article_id)
                )
                conn.commit()
        else:
            insert_article({
                "title": title_en,
                "source_url": "",
                "source_country": "",
                "language": source_lang_lower,
                "original_text": text,
                "translated_text": text_en,
                "threat_detected": False,
                "confidence_score": 0.0,
                "risk_category": "",
                "justification": ""
            })

        return {
            "title_en": title_en,
            "text_en": text_en,
            "key_sentences_en": self.extract_key_sentences(text_en, DEFAULT_KEYWORDS)
        }

    def detect_language(self, text: str) -> str:
        """Detects the language of the given text using Gemini.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The ISO 639-1 language code (e.g., 'vi', 'th', 'hi', 'tl', 'id', 'en').
        """
        if not text or not text.strip():
            return "en"
            
        prompt = (
            "Identify the language of the following text. Respond with ONLY the two-letter ISO 639-1 language code "
            "(e.g., 'vi', 'th', 'hi', 'tl', 'id', 'en'). Do not include any other text, punctuation, or explanation.\n\n"
            f"Text:\n{text[:500]}"
        )
        try:
            lang_code = self.client.generate(prompt, temperature=0.1, response_mime_type="text/plain").strip().lower()
            lang_code = re.sub(r'[^a-z]', '', lang_code)
            if len(lang_code) == 2:
                return lang_code
        except Exception as exc:
            logger.warning("Language detection failed, defaulting to 'en': %s", exc)
        return "en"
