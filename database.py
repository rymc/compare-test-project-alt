import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional

class TranscriptionDatabase:
    """Database manager for storing and retrieving speech transcriptions."""
    
    def __init__(self, db_path: str = "transcriptions.db"):
        """Initialize the database connection and create tables if needed."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the transcriptions table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration REAL,
                    audio_file_path TEXT,
                    confidence REAL
                )
            ''')
            conn.commit()
    
    def save_transcription(
        self, 
        text: str, 
        duration: Optional[float] = None,
        audio_file_path: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> int:
        """Save a transcription to the database and return the ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transcriptions (text, duration, audio_file_path, confidence)
                VALUES (?, ?, ?, ?)
            ''', (text, duration, audio_file_path, confidence))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_transcriptions(self) -> List[Tuple]:
        """Retrieve all transcriptions from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, text, timestamp, duration, audio_file_path, confidence
                FROM transcriptions
                ORDER BY timestamp DESC
            ''')
            return cursor.fetchall()
    
    def get_transcription_by_id(self, transcription_id: int) -> Optional[Tuple]:
        """Retrieve a specific transcription by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, text, timestamp, duration, audio_file_path, confidence
                FROM transcriptions
                WHERE id = ?
            ''', (transcription_id,))
            return cursor.fetchone()
    
    def search_transcriptions(self, search_term: str) -> List[Tuple]:
        """Search transcriptions by text content."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, text, timestamp, duration, audio_file_path, confidence
                FROM transcriptions
                WHERE text LIKE ?
                ORDER BY timestamp DESC
            ''', (f'%{search_term}%',))
            return cursor.fetchall()
    
    def delete_transcription(self, transcription_id: int) -> bool:
        """Delete a transcription by ID. Returns True if successful."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM transcriptions WHERE id = ?
            ''', (transcription_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total count
            cursor.execute('SELECT COUNT(*) FROM transcriptions')
            total_count = cursor.fetchone()[0]
            
            # Total duration
            cursor.execute('SELECT SUM(duration) FROM transcriptions WHERE duration IS NOT NULL')
            total_duration = cursor.fetchone()[0] or 0
            
            # Average confidence
            cursor.execute('SELECT AVG(confidence) FROM transcriptions WHERE confidence IS NOT NULL')
            avg_confidence = cursor.fetchone()[0] or 0
            
            return {
                'total_transcriptions': total_count,
                'total_duration_seconds': total_duration,
                'average_confidence': avg_confidence
            }
