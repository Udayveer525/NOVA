import sqlite3
from datetime import datetime

from core.config import DB_PATH


class MemoryManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with memory tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                speaker TEXT NOT NULL,
                message TEXT NOT NULL,
                session_id TEXT,
                metadata TEXT
            )
        ''')
        
        # User facts/preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        ''')
        
        # Project/file context table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                file_path TEXT,
                description TEXT,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_exchange(self, speaker: str, message: str, session_id: str = "default"):
        """Save a conversation exchange to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (speaker, message, session_id) VALUES (?, ?, ?)",
            (speaker, message, session_id)
        )
        conn.commit()
        conn.close()
    
    def get_recent_conversation(self, limit: int = 50) -> list:
        """Get recent conversation history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT speaker, message FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        results = cursor.fetchall()
        conn.close()
        
        # Reverse to chronological order
        return [f"{speaker}: {msg}" for speaker, msg in reversed(results)]
    
    def save_user_fact(self, category: str, key: str, value: str):
        """Save or update a user fact/preference."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO user_facts (category, key, value) 
               VALUES (?, ?, ?)
               ON CONFLICT(category, key) 
               DO UPDATE SET value=?, last_updated=CURRENT_TIMESTAMP""",
            (category, key, value, value)
        )
        conn.commit()
        conn.close()
    
    def get_user_facts(self, category: str = None) -> dict:
        """Get user facts, optionally filtered by category."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute(
                "SELECT key, value FROM user_facts WHERE category = ?",
                (category,)
            )
        else:
            cursor.execute("SELECT category, key, value FROM user_facts")
        
        results = cursor.fetchall()
        conn.close()
        
        if category:
            return {key: value for key, value in results}
        else:
            facts = {}
            for cat, key, value in results:
                if cat not in facts:
                    facts[cat] = {}
                facts[cat][key] = value
            return facts
    
    def search_conversation_history(self, keyword: str, limit: int = 10) -> list:
        """Search past conversations for a keyword."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT speaker, message, timestamp FROM conversations 
               WHERE message LIKE ? 
               ORDER BY id DESC LIMIT ?""",
            (f"%{keyword}%", limit)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [
            f"[{timestamp}] {speaker}: {msg}" 
            for speaker, msg, timestamp in results
        ]
