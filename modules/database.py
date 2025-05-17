"""SQLite database implementation for storing Spotify listening history and related data."""
import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SpotifyDatabase:
    def __init__(self, db_path='data/spotify_data.db'):
        """Initialize database with schema."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # If database exists, delete it for fresh start
        if os.path.exists(db_path):
            os.remove(db_path)
            
        self.db_path = db_path
        self.initialize_db()
        
    def initialize_db(self):
        """Create all necessary database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Users table - minimal info as requested
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    followers INTEGER DEFAULT 0,
                    last_updated TIMESTAMP
                )
            ''')
            
            # Tracks table - store track information
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT,
                    duration_ms INTEGER,
                    popularity INTEGER,
                    preview_url TEXT,
                    image_url TEXT,
                    added_at TIMESTAMP,
                    last_seen TIMESTAMP
                )
            ''')
            
            # Listening history table - track play history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS listening_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    track_id TEXT NOT NULL,
                    played_at TIMESTAMP NOT NULL,
                    source TEXT NOT NULL,  -- 'saved', 'played', 'top_track'
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (track_id) REFERENCES tracks (track_id),
                    UNIQUE (user_id, track_id, played_at)  -- Prevent duplicates
                )
            ''')
            
            # Collection status table - track data collection progress
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collection_status (
                    user_id TEXT PRIMARY KEY,
                    last_collection_timestamp TIMESTAMP,
                    earliest_known_timestamp TIMESTAMP,
                    latest_known_timestamp TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_listening_history_user_time ON listening_history (user_id, played_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_listening_history_track ON listening_history (track_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks (artist)')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
            
    def save_user(self, user_data: dict):
        """Save basic user information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, display_name, followers, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_data.get('id'),
                user_data.get('display_name', 'Unknown'),
                user_data.get('followers', 0),
            ))
            
            # Initialize collection status for new user
            cursor.execute('''
                INSERT OR IGNORE INTO collection_status 
                (user_id, last_collection_timestamp)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (user_data.get('id'),))
            
            conn.commit()
            logger.info(f"Saved user data for {user_data.get('display_name')}")
            
        except sqlite3.Error as e:
            logger.error(f"Error saving user data: {e}")
            raise
        finally:
            conn.close()
            
    def save_track(self, track_data: dict):
        """Save track data and its timestamp."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO tracks (
                    track_id, name, artist, album,
                    duration_ms, popularity, preview_url,
                    image_url, added_at, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                track_data.get('id'),
                track_data.get('name'),
                track_data.get('artist'),
                track_data.get('album'),
                track_data.get('duration_ms'),
                track_data.get('popularity'),
                track_data.get('preview_url'),
                track_data.get('image_url'),
                track_data.get('added_at'),
            ))
            
            conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Error saving track data: {e}")
            raise
        finally:
            conn.close()
            
    def save_listening_history(self, user_id: str, track_id: str, played_at: str, source: str = 'played'):
        """Save a listening history entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO listening_history 
                (user_id, track_id, played_at, source)
                VALUES (?, ?, ?, ?)
            ''', (user_id, track_id, played_at, source))
            
            # Update collection status timestamps
            cursor.execute('''
                UPDATE collection_status 
                SET earliest_known_timestamp = MIN(COALESCE(earliest_known_timestamp, ?), ?),
                    latest_known_timestamp = MAX(COALESCE(latest_known_timestamp, ?), ?),
                    last_collection_timestamp = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (played_at, played_at, played_at, played_at, user_id))
            
            conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Error saving listening history: {e}")
            raise
        finally:
            conn.close()
            
    def get_collection_status(self, user_id: str) -> dict:
        """Get the current data collection status for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT last_collection_timestamp,
                       earliest_known_timestamp,
                       latest_known_timestamp
                FROM collection_status
                WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'last_collection': row[0],
                    'earliest_known': row[1],
                    'latest_known': row[2]
                }
            return None
            
        finally:
            conn.close()
            
    def get_listening_history(self, user_id: str, start_date: str = None, end_date: str = None) -> list:
        """Get listening history for a user within a date range."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT h.played_at, t.name, t.artist, t.album, h.source
            FROM listening_history h
            JOIN tracks t ON h.track_id = t.track_id
            WHERE h.user_id = ?
        '''
        params = [user_id]
        
        if start_date:
            query += ' AND h.played_at >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND h.played_at <= ?'
            params.append(end_date)
            
        query += ' ORDER BY h.played_at DESC'
        
        try:
            cursor.execute(query, params)
            return [dict(zip(['played_at', 'name', 'artist', 'album', 'source'], row))
                   for row in cursor.fetchall()]
        finally:
            conn.close()