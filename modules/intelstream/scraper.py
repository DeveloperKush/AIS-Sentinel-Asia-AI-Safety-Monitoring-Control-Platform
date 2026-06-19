import json
import logging
import time
import requests
import feedparser
import re
from newspaper import Article, ArticleException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeywordFilter:
    def __init__(self, keywords_file="config/rubrics.json"):
        self.keywords_file = keywords_file
        self.keywords = [
            "CRISPR", "synthetic biology", "gene synthesis", "pathogen", 
            "biosecurity", "AI model", "bioinformatics", "genome editing", 
            "viral vector", "laboratory safety", "dual-use", "biological weapon", 
            "gain-of-function"
        ]
        self._load_keywords()

    def _load_keywords(self):
        try:
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.keywords = data
                elif isinstance(data, dict) and "keywords" in data:
                    self.keywords = data.get("keywords", self.keywords)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"Could not load keywords from {self.keywords_file}. Using default keywords.")

    def filter_article(self, article: dict) -> bool:
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        text = article.get("text", "").lower()
        content = f"{title} {summary} {text}"
        
        for keyword in self.keywords:
            if keyword.lower() in content:
                return True
        return False

    def extract_relevant_sentences(self, text: str) -> list[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword.lower() in sentence_lower for keyword in self.keywords):
                relevant_sentences.append(sentence.strip())
        return relevant_sentences

class RSSScraper:
    def __init__(self, sources_file="config/sources.json"):
        self.sources_file = sources_file
        self.rate_limit_delay = 1
        self.timeout = 10

    def load_sources(self) -> list[dict]:
        try:
            with open(self.sources_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.error(f"Failed to load sources from {self.sources_file}")
            return []

    def scrape_rss(self, source: dict) -> list[dict]:
        articles = []
        url = source.get("url")
        if not url:
            return articles
            
        try:
            # feedparser handles timeout less obviously, requests is better for enforcing timeout before parsing
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries:
                article = {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published_date": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "source_name": source.get("name", ""),
                    "text": ""
                }
                articles.append(article)
                logger.info(f"Scraped RSS article: {article['title']}")
        except requests.RequestException as e:
            logger.error(f"Network error scraping RSS from {url}: {e}")
        except Exception as e:
            logger.error(f"Error scraping RSS from {url}: {e}")
            
        return articles

    def scrape_html(self, source: dict) -> list[dict]:
        articles = []
        url = source.get("url")
        if not url:
            return articles
            
        try:
            article = Article(url, fetch_images=False, request_timeout=self.timeout)
            article.download()
            article.parse()
            
            extracted = {
                "title": article.title,
                "url": url,
                "published_date": str(article.publish_date) if article.publish_date else "",
                "summary": article.meta_description,
                "source_name": source.get("name", ""),
                "text": article.text
            }
            articles.append(extracted)
            logger.info(f"Scraped HTML article: {extracted['title']}")
        except ArticleException as e:
            logger.error(f"Error scraping HTML from {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error scraping HTML from {url}: {e}")
            
        return articles

    def scrape_all(self) -> list[dict]:
        all_articles = []
        sources = self.load_sources()
        for source in sources:
            source_type = source.get("type", "rss").lower()
            if source_type == "rss":
                articles = self.scrape_rss(source)
                all_articles.extend(articles)
            elif source_type == "html":
                articles = self.scrape_html(source)
                all_articles.extend(articles)
            time.sleep(self.rate_limit_delay)
        return all_articles
