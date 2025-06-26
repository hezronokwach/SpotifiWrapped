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

        # Don't delete the database if it exists - we want to keep our data
        self.db_path = db_path

        # Initialize the database if it doesn't exist
        if not os.path.exists(db_path):
            self.initialize_db()
        else:
            # Make sure all tables exist
            self.ensure_tables_exist()

    def ensure_tables_exist(self):
        """Make sure all necessary tables exist in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if the genres table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='genres'")
            if cursor.fetchone() is None:
                # Create the genres table if it doesn't exist
                self._create_tables(conn)
                logger.info("Created missing tables in database")
            else:
                logger.info("All tables exist in database")

            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error ensuring tables exist: {e}")
            raise
        finally:
            conn.close()

    def _create_tables(self, conn):
        """Create all database tables."""
        cursor = conn.cursor()

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
                last_seen TIMESTAMP,
                danceability REAL,
                energy REAL,
                key INTEGER,
                loudness REAL,
                mode INTEGER,
                speechiness REAL,
                acousticness REAL,
                instrumentalness REAL,
                liveness REAL,
                valence REAL,
                tempo REAL
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

        # Genres table - simplified with no user dependency
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genres (
                genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
                genre_name TEXT NOT NULL,
                artist_name TEXT,
                count INTEGER DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(genre_name, artist_name)
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_genres_name ON genres (genre_name)')

        logger.info("Created all database tables")

    def initialize_db(self):
        """Create all necessary database tables."""
        conn = sqlite3.connect(self.db_path)

        try:
            self._create_tables(conn)
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
            # Check for required fields and provide defaults if missing
            track_id = track_data.get('id')
            if not track_id:
                logger.warning("Cannot save track without ID")
                return

            # Get name from either 'name' or 'track' field
            name = track_data.get('name') or track_data.get('track')
            if not name:
                name = f"Unknown Track ({track_id})"

            # Get artist with default and validation
            artist = track_data.get('artist')
            if not artist or not str(artist).strip():
                artist = "Unknown Artist"
            else:
                artist = str(artist).strip()

            # Validate and clean other string fields
            album = track_data.get('album')
            if album:
                album = str(album).strip()
                if not album:
                    album = None

            # Validate numeric fields
            duration_ms = track_data.get('duration_ms')
            if duration_ms is not None:
                try:
                    duration_ms = int(duration_ms)
                    if duration_ms < 0:
                        duration_ms = None
                except (ValueError, TypeError):
                    duration_ms = None

            popularity = track_data.get('popularity')
            if popularity is not None:
                try:
                    popularity = int(popularity)
                    if not (0 <= popularity <= 100):
                        popularity = None
                except (ValueError, TypeError):
                    popularity = None

            # Special logging for genre tracks
            if track_id.startswith('genre-'):
                print(f"DATABASE: Saving genre track: {track_id}, name: {name}, artist: {artist}")

            cursor.execute('''
                INSERT OR REPLACE INTO tracks (
                    track_id, name, artist, album,
                    duration_ms, popularity, preview_url,
                    image_url, added_at, last_seen,
                    danceability, energy, key, loudness, mode,
                    speechiness, acousticness, instrumentalness,
                    liveness, valence, tempo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP,
                          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                track_id,
                name,
                artist,
                album,
                duration_ms,
                popularity,
                str(track_data.get('preview_url', '')).strip() if track_data.get('preview_url') else None,
                str(track_data.get('image_url', '')).strip() if track_data.get('image_url') else None,
                track_data.get('added_at'),
                track_data.get('danceability'),
                track_data.get('energy'),
                track_data.get('key'),
                track_data.get('loudness'),
                track_data.get('mode'),
                track_data.get('speechiness'),
                track_data.get('acousticness'),
                track_data.get('instrumentalness'),
                track_data.get('liveness'),
                track_data.get('valence'),
                track_data.get('tempo'),
            ))

            conn.commit()

            # Verify the track was saved
            if track_id.startswith('genre-'):
                cursor.execute("SELECT track_id FROM tracks WHERE track_id = ?", (track_id,))
                track_exists = cursor.fetchone() is not None
                if track_exists:
                    print(f"DATABASE: Successfully saved genre track: {track_id}")
                else:
                    print(f"DATABASE: WARNING - Genre track {track_id} was not found after save attempt")

        except sqlite3.Error as e:
            logger.error(f"Error saving track data: {e}")
            if track_id and track_id.startswith('genre-'):
                print(f"DATABASE ERROR saving genre track {track_id}: {e}")
            raise
        finally:
            conn.close()

    def save_listening_history(self, user_id: str, track_id: str, played_at: str, source: str = 'played'):
        """Save a listening history entry with validation."""
        # Validate required parameters
        if not user_id or not isinstance(user_id, str):
            logger.error("Invalid user_id: must be a non-empty string")
            return False

        if not track_id or not isinstance(track_id, str):
            logger.error("Invalid track_id: must be a non-empty string")
            return False

        if not played_at or not isinstance(played_at, str):
            logger.error("Invalid played_at: must be a non-empty string")
            return False

        if not source or not isinstance(source, str):
            logger.error("Invalid source: must be a non-empty string")
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Validate timestamp - ensure it's not in the future
            try:
                # Parse the timestamp
                if 'Z' in played_at:
                    dt = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
                elif 'T' in played_at and ('+' in played_at or '-' in played_at.split('T')[1]):
                    dt = datetime.fromisoformat(played_at)
                else:
                    dt = datetime.fromisoformat(played_at)

                # Remove timezone info for comparison
                dt = dt.replace(tzinfo=None)

                # Check if timestamp is in the future
                current_time = datetime.now()
                if dt > current_time:
                    # If in the future, use current time instead
                    played_at = current_time.isoformat()
                    logger.warning(f"Future timestamp detected ({dt}), using current time instead")
            except ValueError:
                # If parsing fails, use current time
                played_at = datetime.now().isoformat()
                logger.warning(f"Invalid timestamp format ({played_at}), using current time instead")

            # Special logging for genre tracks
            if track_id.startswith('genre-') or source == 'genre':
                print(f"DATABASE: Saving listening history for genre: track_id={track_id}, user_id={user_id}, source={source}")

                # Check if the track exists in the tracks table
                cursor.execute("SELECT track_id FROM tracks WHERE track_id = ?", (track_id,))
                track_exists = cursor.fetchone() is not None
                if not track_exists:
                    print(f"DATABASE WARNING: Track {track_id} does not exist in tracks table")

                # Check if the user exists in the users table
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                user_exists = cursor.fetchone() is not None
                if not user_exists:
                    print(f"DATABASE WARNING: User {user_id} does not exist in users table")

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

            # Verify the listening history entry was saved
            if track_id.startswith('genre-') or source == 'genre':
                cursor.execute(
                    "SELECT history_id FROM listening_history WHERE user_id = ? AND track_id = ? AND source = ?",
                    (user_id, track_id, source)
                )
                history_exists = cursor.fetchone() is not None
                if history_exists:
                    print(f"DATABASE: Successfully saved listening history for genre: {track_id}")
                else:
                    print(f"DATABASE WARNING: Listening history for genre {track_id} was not found after save attempt")

            return True

        except sqlite3.Error as e:
            logger.error(f"Error saving listening history: {e}")
            if track_id.startswith('genre-') or source == 'genre':
                print(f"DATABASE ERROR saving listening history for genre {track_id}: {e}")
            return False
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

    def save_genre(self, genre_name: str, artist_name: str = None):
        """Save a genre to the database, incrementing count if it already exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if this genre already exists for this artist
            cursor.execute('''
                SELECT genre_id, count FROM genres
                WHERE genre_name = ? AND (artist_name = ? OR (artist_name IS NULL AND ? IS NULL))
            ''', (genre_name, artist_name, artist_name))

            existing = cursor.fetchone()

            if existing:
                # Increment count for existing genre
                genre_id, count = existing
                cursor.execute('''
                    UPDATE genres
                    SET count = count + 1, added_at = CURRENT_TIMESTAMP
                    WHERE genre_id = ?
                ''', (genre_id,))
                print(f"DATABASE: Incremented count for genre '{genre_name}' to {count + 1}")
            else:
                # Insert new genre
                cursor.execute('''
                    INSERT INTO genres (genre_name, artist_name, count)
                    VALUES (?, ?, 1)
                ''', (genre_name, artist_name))
                print(f"DATABASE: Added new genre '{genre_name}'")

            conn.commit()
            return True

        except sqlite3.Error as e:
            logger.error(f"Error saving genre data: {e}")
            print(f"DATABASE ERROR saving genre '{genre_name}': {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_top_genres(self, limit: int = 10, exclude_unknown: bool = True, categorize: bool = True):
        """
        Get top genres from the database with optional categorization.

        Args:
            limit: Maximum number of genres to return
            exclude_unknown: Whether to exclude the 'unknown' placeholder genre
            categorize: Whether to group similar genres together

        Returns:
            List of genre dictionaries with genre and count
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            if exclude_unknown:
                cursor.execute('''
                    SELECT genre_name as genre, SUM(count) as count
                    FROM genres
                    WHERE genre_name != 'unknown' AND genre_name IS NOT NULL AND genre_name != ''
                    GROUP BY genre_name
                    ORDER BY count DESC
                ''')
            else:
                cursor.execute('''
                    SELECT genre_name as genre, SUM(count) as count
                    FROM genres
                    WHERE genre_name IS NOT NULL AND genre_name != ''
                    GROUP BY genre_name
                    ORDER BY count DESC
                ''')

            raw_genres = [dict(row) for row in cursor.fetchall()]

            if categorize and raw_genres:
                # Group similar genres together
                categorized_genres = self._categorize_genres(raw_genres)
                return categorized_genres[:limit]
            else:
                return raw_genres[:limit]

        except sqlite3.Error as e:
            logger.error(f"Error getting top genres: {e}")
            return []
        finally:
            conn.close()

    def _categorize_genres(self, genres):
        """
        Categorize and group similar genres together.

        Args:
            genres: List of genre dictionaries with 'genre' and 'count' keys

        Returns:
            List of categorized genre dictionaries
        """
        # Define genre categories and their keywords
        genre_categories = {
            'Pop': ['pop', 'mainstream', 'top 40'],
            'Rock': ['rock', 'alternative', 'indie rock', 'classic rock', 'hard rock'],
            'Hip Hop': ['hip hop', 'rap', 'trap', 'hip-hop'],
            'Electronic': ['electronic', 'edm', 'house', 'techno', 'dubstep', 'electro'],
            'R&B': ['r&b', 'soul', 'neo soul', 'contemporary r&b'],
            'Country': ['country', 'folk', 'americana', 'bluegrass'],
            'Jazz': ['jazz', 'smooth jazz', 'bebop', 'swing'],
            'Classical': ['classical', 'orchestral', 'symphony', 'opera'],
            'Reggae': ['reggae', 'dancehall', 'ska'],
            'Latin': ['latin', 'salsa', 'reggaeton', 'bachata', 'merengue'],
            'Blues': ['blues', 'delta blues', 'chicago blues'],
            'Punk': ['punk', 'hardcore', 'post-punk'],
            'Metal': ['metal', 'heavy metal', 'death metal', 'black metal'],
            'Funk': ['funk', 'disco', 'groove']
        }

        # Initialize category counts
        category_counts = {category: 0 for category in genre_categories.keys()}
        uncategorized = []

        # Categorize each genre
        for genre_data in genres:
            genre_name = genre_data['genre'].lower()
            count = genre_data['count']
            categorized = False

            # Check if genre matches any category
            for category, keywords in genre_categories.items():
                if any(keyword in genre_name for keyword in keywords):
                    category_counts[category] += count
                    categorized = True
                    break

            # If not categorized, keep as individual genre
            if not categorized:
                uncategorized.append(genre_data)

        # Create final list with categories and uncategorized genres
        result = []

        # Add categories with counts > 0
        for category, count in category_counts.items():
            if count > 0:
                result.append({'genre': category, 'count': count})

        # Add uncategorized genres
        result.extend(uncategorized)

        # Sort by count descending
        result.sort(key=lambda x: x['count'], reverse=True)

        return result

    def get_all_listening_history_artists(self):
        """Get all unique artists from the listening history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT DISTINCT t.artist
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
            ''')

            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting listening history artists: {e}")
            return []
        finally:
            conn.close()

    def get_listening_statistics(self, user_id: str):
        """
        Get comprehensive listening statistics for a user.

        Args:
            user_id: User ID to get statistics for

        Returns:
            Dictionary with listening statistics
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Get total listening time and track count
            cursor.execute('''
                SELECT
                    COUNT(DISTINCT h.history_id) as total_plays,
                    COUNT(DISTINCT t.track_id) as unique_tracks,
                    COUNT(DISTINCT t.artist) as unique_artists,
                    SUM(t.duration_ms) as total_duration_ms,
                    AVG(t.duration_ms) as avg_track_duration_ms
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.user_id = ?
                AND h.source IN ('played', 'recently_played', 'current')
                AND t.duration_ms IS NOT NULL
                AND t.duration_ms > 0
            ''', (user_id,))

            stats = dict(cursor.fetchone())

            # Calculate derived statistics
            total_minutes = round((stats['total_duration_ms'] or 0) / 60000, 2)
            total_hours = round(total_minutes / 60, 2)
            avg_track_minutes = round((stats['avg_track_duration_ms'] or 0) / 60000, 2)

            return {
                'total_plays': stats['total_plays'] or 0,
                'unique_tracks': stats['unique_tracks'] or 0,
                'unique_artists': stats['unique_artists'] or 0,
                'total_minutes': total_minutes,
                'total_hours': total_hours,
                'average_track_minutes': avg_track_minutes
            }

        except sqlite3.Error as e:
            logger.error(f"Error getting listening statistics: {e}")
            return {
                'total_plays': 0,
                'unique_tracks': 0,
                'unique_artists': 0,
                'total_minutes': 0,
                'total_hours': 0,
                'average_track_minutes': 0
            }
        finally:
            conn.close()