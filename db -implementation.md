ow a Database Would Solve the Listening Trends Limitation
With a database implementation, you could:

Store historical listening data over time, not just the most recent 50 tracks
Build comprehensive listening patterns across days, weeks, months, or even years
Provide true time-range filtering for all visualizations, not just the ones Spotify's API directly supports
Implementation Requirements
To implement this database-driven approach, you would need:

1. Database Infrastructure
Database type: PostgreSQL, MongoDB, or even SQLite for simpler implementations
Schema design: Tables/collections for users, tracks, listening history, etc.
Example schema:
users (user_id, spotify_id, display_name, ...)
tracks (track_id, name, artist, album, duration, ...)
listening_history (id, user_id, track_id, played_at, ...)

Copy

Insert

2. Data Collection Process
Scheduled jobs: A background process that runs periodically (e.g., every hour)
API polling: Regularly fetch recently played tracks for each user
Deduplication logic: Ensure you don't store duplicate entries
Example approach:
def update_listening_history(user_id):
    # Get last timestamp we collected for this user
    last_timestamp = db.get_last_timestamp(user_id)
    
    # Fetch recently played tracks since that timestamp
    new_tracks = spotify_api.get_recently_played(after=last_timestamp)
    
    # Store new tracks in database
    db.save_tracks(new_tracks)

Copy

Insert

3. Enhanced API Layer
Custom endpoints: Create your own API endpoints that query your database
Aggregation functions: Methods to summarize listening data by time periods
Example query:
def get_listening_patterns(user_id, time_range='week'):
    # Define date range based on time_range parameter
    if time_range == 'week':
        start_date = datetime.now() - timedelta(days=7)
    elif time_range == 'month':
        start_date = datetime.now() - timedelta(days=30)
    # ...
    
    # Query database for listening history in that range
    history = db.query(
        "SELECT day_of_week, hour_of_day, COUNT(*) as count " +
        "FROM listening_history " +
        "WHERE user_id = ? AND played_at >= ? " +
        "GROUP BY day_of_week, hour_of_day",
        [user_id, start_date]
    )
    
    return history

Copy

Insert

4. UI Components
Time range selectors: Dropdowns or toggle buttons for different time periods
Loading states: Indicators for when data is being fetched/processed
Callback structure:
@app.callback(
    Output('listening-patterns-chart', 'figure'),
    [Input('time-range-dropdown', 'value')]
)
def update_listening_patterns(time_range):
    # Get data for selected time range
    patterns_data = get_listening_patterns(current_user_id, time_range)
    
    # Create visualization
    return create_listening_patterns_heatmap(patterns_data)

Copy

Insert

Practical Considerations
Data Privacy: You'll need to handle user data responsibly and consider privacy regulations
Authentication: Maintain Spotify authentication tokens for background data collection
Scaling: As your user base grows, your data collection process needs to scale
Storage Requirements: Listening history can grow large over time, so plan accordingly
Potential Challenges
API Rate Limits: Spotify limits how often you can call their API
Token Expiration: Handling refreshing of access tokens for background processes
Data Gaps: If your collection process fails or users don't use your app for periods of time
Initial Data Sparsity: New users won't have historical data until it's collected over time
Phased Implementation Approach
You could implement this in phases:

Phase 1: Set up basic database schema and initial data collection
Phase 2: Implement time-range filtering for top tracks/artists (using Spotify's API)
Phase 3: Build custom listening patterns visualization with your collected data
Phase 4: Add more sophisticated analysis and visualizations based on historical data
This approach would allow you to gradually enhance your application while providing immediate value to users.


Best Database Options (Free)
SQLite
Pros: Zero setup, file-based, no server required, perfect for single-user applications
Cons: Not ideal for concurrent access if you plan to scale to many users
Recommendation: Excellent choice for your educational project where each user has their own database
PostgreSQL (Free Tier)
Pros: More robust, supports complex queries, good for time-series data
Cons: Requires more setup than SQLite
Free Options: Render, Supabase, or ElephantSQL offer free tiers
MongoDB (Free Tier)
Pros: Flexible schema, good for storing JSON-like data
Cons: Less efficient for relational queries
Free Options: MongoDB Atlas has a free tier
Recommended Approach: SQLite
For your specific needs (educational project, storing limited data from the start of the year), SQLite is likely the best option:

Simple Schema Design:
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    display_name TEXT,
    country TEXT,
    product TEXT
);

CREATE TABLE tracks (
    track_id TEXT PRIMARY KEY,
    name TEXT,
    artist TEXT,
    album TEXT,
    duration_ms INTEGER
);

CREATE TABLE listening_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    track_id TEXT,
    played_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);

CREATE INDEX idx_listening_history_user_id ON listening_history(user_id);
CREATE INDEX idx_listening_history_played_at ON listening_history(played_at);

Copy

Insert

Data Collection Strategy:
Keep the "currently playing" feature
Add a background task that runs every 15-30 minutes to fetch recently played tracks
Store only the data you need (track ID, timestamp, etc.)
Implement deduplication to avoid storing the same play multiple times
Storage Requirements:
Very minimal - a full year of listening history for one user might be only a few MB
Each listening event is just a few bytes (IDs and timestamps)
Regarding the "Currently Playing" Feature
You can absolutely keep the currently playing feature! In fact, it complements your data collection strategy:

Keep the real-time feature: The "currently playing" display is a nice interactive element
Add background collection: Separately collect listening history in the background
How they work together:
Currently playing: Shows what's happening right now (real-time)
Listening history database: Builds up your historical data over time
Implementation Approach
Add SQLite Integration:
import sqlite3
import os

class SpotifyDatabase:
    def __init__(self, db_path='spotify_data.db'):
        self.db_path = db_path
        self.initialize_db()
        
    def initialize_db(self):
        """Create database tables if they don't exist."""
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT,
                    country TEXT,
                    product TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    name TEXT,
                    artist TEXT,
                    album TEXT,
                    duration_ms INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS listening_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    track_id TEXT,
                    played_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (track_id) REFERENCES tracks(track_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_listening_history_user_id ON listening_history(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_listening_history_played_at ON listening_history(played_at)')
            
            conn.commit()
            conn.close()
    
    def save_user(self, user_data):
        """Save user profile data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, display_name, country, product)
            VALUES (?, ?, ?, ?)
        ''', (
            user_data['id'],
            user_data['display_name'],
            user_data.get('country', 'Unknown'),
            user_data.get('product', 'Unknown')
        ))
        
        conn.commit()
        conn.close()
    
    def save_track(self, track_data):
        """Save track data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tracks (track_id, name, artist, album, duration_ms)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            track_data['id'],
            track_data['track'],
            track_data['artist'],
            track_data.get('album', 'Unknown'),
            track_data.get('duration_ms', 0)
        ))
        
        conn.commit()
        conn.close()
        
    def save_listening_event(self, user_id, track_id, played_at):
        """Save a listening event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if this exact event already exists
        cursor.execute('''
            SELECT id FROM listening_history 
            WHERE user_id = ? AND track_id = ? AND played_at = ?
        ''', (user_id, track_id, played_at))
        
        if cursor.fetchone() is None:
            # Only insert if it doesn't exist
            cursor.execute('''
                INSERT INTO listening_history (user_id, track_id, played_at)
                VALUES (?, ?, ?)
            ''', (user_id, track_id, played_at))
        
        conn.commit()
        conn.close()
    
    def get_listening_history(self, user_id, start_date=None, end_date=None):
        """Get listening history for a user within a date range."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        query = '''
            SELECT h.played_at, t.name as track, t.artist, t.album, t.duration_ms
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
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results

Copy

Insert

Add Background Data Collection:
import threading
import time
import datetime

def background_data_collector(spotify_api, db, user_id, interval=1800):
    """
    Background thread to collect listening history.
    Runs every 'interval' seconds (default 30 minutes).
    """
    while True:
        try:
            # Get recently played tracks
            recently_played = spotify_api.get_recently_played(limit=50)
            
            # Process and save each track
            for item in recently_played:
                # Save track data
                db.save_track({
                    'id': item['id'],
                    'track': item['track'],
                    'artist': item['artist'],
                    'album': item.get('album', 'Unknown'),
                    'duration_ms': item.get('duration_ms', 0)
                })
                
                # Save listening event
                db.save_listening_event(
                    user_id=user_id,
                    track_id=item['id'],
                    played_at=item['played_at']
                )
            
            print(f"[{datetime.datetime.now()}] Collected {len(recently_played)} recently played tracks")
        except Exception as e:
            print(f"Error in background collector: {e}")
        
        # Sleep for the specified interval
        time.sleep(interval)

# Start the background collector
def start_background_collector(spotify_api, db, user_id):
    collector_thread = threading.Thread(
        target=background_data_collector,
        args=(spotify_api, db, user_id),
        daemon=True  # This makes the thread exit when the main program exits
    )
    collector_thread.start()
    return collector_thread

Copy

Insert

Initialize in your main app:
# In app.py
from modules.database import SpotifyDatabase

# Initialize database
db = SpotifyDatabase()

# After user authentication
user_data = spotify_api.get_user_profile()
if user_data:
    db.save_user(user_data)
    # Start background collector
    start_background_collector(spotify_api, db, user_data['id'])

Copy

Insert

This approach gives you the best of both worlds - real-time "currently playing" information and a growing database of listening history that you can use for more comprehensive visualizations over time.