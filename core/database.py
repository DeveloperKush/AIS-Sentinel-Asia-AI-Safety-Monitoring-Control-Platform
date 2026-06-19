import sqlite3
import contextlib
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "ais_sentinel.db"

@contextlib.contextmanager
def get_db_connection():
    """Context manager for SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    """Initializes the database and creates tables if they do not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                source_url TEXT,
                source_country TEXT,
                language TEXT,
                original_text TEXT,
                translated_text TEXT,
                threat_detected BOOLEAN,
                confidence_score REAL,
                risk_category TEXT,
                justification TEXT,
                created_at TEXT
            )
        """)
        
        # Create benchmark_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                language TEXT,
                test_type TEXT,
                prompt TEXT,
                model_response TEXT,
                passed BOOLEAN,
                created_at TEXT
            )
        """)
        
        # Create agent_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_description TEXT,
                attack_type TEXT,
                slide_json TEXT,
                monitor_suspicion_score REAL,
                detected BOOLEAN,
                created_at TEXT
            )
        """)
        
        conn.commit()

def insert_article(data: dict) -> int:
    """Inserts a new article into the database.
    
    Args:
        data: A dictionary containing the article fields.
        
    Returns:
        The ID of the inserted row.
    """
    created_at = data.get("created_at") or datetime.now().isoformat()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO articles (
                title, source_url, source_country, language, original_text,
                translated_text, threat_detected, confidence_score,
                risk_category, justification, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("title"),
                data.get("source_url"),
                data.get("source_country"),
                data.get("language"),
                data.get("original_text"),
                data.get("translated_text"),
                data.get("threat_detected"),
                data.get("confidence_score"),
                data.get("risk_category"),
                data.get("justification"),
                created_at,
            ),
        )
        conn.commit()
        return cursor.lastrowid

def get_articles(threat_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves articles from the database.
    
    Args:
        threat_only: If True, filters to only retrieve articles where threat_detected is True.
        limit: The maximum number of articles to retrieve.
        
    Returns:
        A list of dictionaries representing the articles.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if threat_only:
            cursor.execute(
                "SELECT * FROM articles WHERE threat_detected = 1 ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
        else:
            cursor.execute(
                "SELECT * FROM articles ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def insert_benchmark_result(data: dict) -> int:
    """Inserts a benchmark result into the database.
    
    Args:
        data: A dictionary containing the benchmark result fields.
        
    Returns:
        The ID of the inserted row.
    """
    created_at = data.get("created_at") or datetime.now().isoformat()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO benchmark_results (
                model_name, language, test_type, prompt, model_response, passed, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("model_name"),
                data.get("language"),
                data.get("test_type"),
                data.get("prompt"),
                data.get("model_response"),
                data.get("passed"),
                created_at,
            ),
        )
        conn.commit()
        return cursor.lastrowid

def get_benchmark_results(
    model_name: Optional[str] = None, language: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves benchmark results, optionally filtered by model_name and/or language.
    
    Args:
        model_name: Optional model name to filter by.
        language: Optional language to filter by.
        
    Returns:
        A list of dictionaries representing the benchmark results.
    """
    query = "SELECT * FROM benchmark_results"
    params = []
    conditions = []
    
    if model_name is not None:
        conditions.append("model_name = ?")
        params.append(model_name)
    if language is not None:
        conditions.append("language = ?")
        params.append(language)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def insert_agent_log(data: dict) -> int:
    """Inserts an agent log into the database.
    
    Args:
        data: A dictionary containing the agent log fields.
        
    Returns:
        The ID of the inserted row.
    """
    created_at = data.get("created_at") or datetime.now().isoformat()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO agent_logs (
                task_description, attack_type, slide_json,
                monitor_suspicion_score, detected, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("task_description"),
                data.get("attack_type"),
                data.get("slide_json"),
                data.get("monitor_suspicion_score"),
                data.get("detected"),
                created_at,
            ),
        )
        conn.commit()
        return cursor.lastrowid

def get_agent_logs(detected_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieves agent logs from the database.
    
    Args:
        detected_only: If True, filters to only retrieve logs where detected is True.
        
    Returns:
        A list of dictionaries representing the agent logs.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if detected_only:
            cursor.execute("SELECT * FROM agent_logs WHERE detected = 1 ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM agent_logs ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
