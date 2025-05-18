import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
import pandas as pd
import time
import json
from datetime import datetime, timedelta

# Import custom modules
import sqlite3
from modules.api import SpotifyAPI
from modules.data_processing import DataProcessor
from modules.layout import DashboardLayout
from modules.visualizations import (
    SpotifyVisualizations, SpotifyAnimations,
    SPOTIFY_GREEN, SPOTIFY_BLACK, SPOTIFY_WHITE, SPOTIFY_GRAY,
    create_album_card, create_personality_card
)

# Import data storage modules
from modules.database import SpotifyDatabase
from modules.data_collector import SpotifyDataCollector

# Import new modules
from modules.top_albums import get_top_albums, get_album_listening_patterns
from modules.analyzer import ListeningPersonalityAnalyzer
from modules.recent_tracks_collector import RecentTracksCollector
from modules.genre_extractor import GenreExtractor

# Load environment variables
load_dotenv()

# Initialize components
spotify_api = SpotifyAPI()
data_processor = DataProcessor()
dashboard_layout = DashboardLayout()
visualizations = SpotifyVisualizations()
animations = SpotifyAnimations()

# Initialize database and data collector
db = SpotifyDatabase()  # This will create tables if they don't exist
data_collector = SpotifyDataCollector(spotify_api, db)

# Initialize personality analyzer
personality_analyzer = ListeningPersonalityAnalyzer(spotify_api)

# Initialize recent tracks collector and genre extractor
recent_tracks_collector = RecentTracksCollector(spotify_api, db)
genre_extractor = GenreExtractor(spotify_api, db)

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

app.title = "Spotify Wrapped Remix"
app.layout = dashboard_layout.create_layout()

# --- Callbacks ---

# Update user data
@app.callback(
    Output('user-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_user_data(n_intervals, n_clicks):
    """Fetch and store user profile data."""
    print("Fetching user profile data...")  # Debug log
    try:
        # Try to read from CSV first
        try:
            stored_data = data_processor.load_data('user_profile.csv')
            if not stored_data.empty:
                user_data = stored_data.iloc[0].to_dict()
                print(f"Loaded user data from CSV: {user_data}")
                return user_data
        except Exception as e:
            print(f"Error loading from CSV: {e}")

        # If CSV fails or is empty, try to fetch from API
        user_data = spotify_api.get_user_profile()
        if user_data:
            print(f"Got user data from API: {user_data}")
            # Save user data both to CSV and database
            data_processor.save_data([user_data], 'user_profile.csv')
            db.save_user(user_data)

            # Start historical data collection for the past two weeks
            # This will automatically use the default two-week timeframe
            data_collector.collect_historical_data(user_data['id'])

            return user_data

        print("No user data received")
        return {}
    except Exception as e:
        print(f"Error in update_user_data: {e}")
        return {}

# Update header with user data
@app.callback(
    Output('header-container', 'children'),
    Input('user-data-store', 'data')
)
def update_header(user_data):
    """Update the header with user profile data."""
    print(f"Updating header with user data: {user_data}")  # Debug log
    header = dashboard_layout.create_header(user_data)
    print(f"Created header: {header}")  # Debug log
    return header

# Update current track
@app.callback(
    Output('current-track-store', 'data'),
    Input('interval-component', 'n_intervals')
)
def update_current_track(n_intervals):
    """Fetch and store currently playing track."""
    try:
        current_track = spotify_api.get_currently_playing()
        if current_track and 'track' in current_track:
            # Get user profile to get user_id
            user_data = spotify_api.get_user_profile()
            if user_data:
                current_track['user_id'] = user_data['id']

            # Save to CSV for backward compatibility
            data_processor.save_data([current_track], 'current_track.csv')

            # Save to database if we have user_id
            if 'user_id' in current_track:
                # Make sure we have all required fields
                if 'id' not in current_track:
                    current_track['id'] = f"current-{datetime.now().timestamp()}"

                # Ensure track has all required fields
                track_data = {
                    'id': current_track['id'],
                    'name': current_track.get('track', 'Unknown Track'),
                    'artist': current_track.get('artist', 'Unknown Artist'),
                    'album': current_track.get('album', 'Unknown Album'),
                    'duration_ms': current_track.get('duration_ms', 0),
                    'popularity': current_track.get('popularity', 0),
                    'preview_url': current_track.get('preview_url', ''),
                    'image_url': current_track.get('image_url', ''),
                    'added_at': datetime.now().replace(microsecond=0).isoformat()
                }

                db.save_track(track_data)
                db.save_listening_history(
                    user_id=current_track['user_id'],
                    track_id=track_data['id'],
                    played_at=datetime.now().replace(microsecond=0).isoformat(),
                    source='current'
                )

            return current_track

        # If no current track, try to get the most recent one from the database
        user_data = spotify_api.get_user_profile()
        if user_data:
            conn = sqlite3.connect(db.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get the most recent track
            cursor.execute('''
                SELECT
                    t.track_id as id,
                    t.name as track,
                    t.artist,
                    t.album,
                    t.duration_ms,
                    t.image_url,
                    h.played_at
                FROM tracks t
                JOIN listening_history h ON t.track_id = h.track_id
                WHERE h.user_id = ?
                ORDER BY h.played_at DESC
                LIMIT 1
            ''', (user_data['id'],))

            row = cursor.fetchone()
            conn.close()

            if row:
                # Create a "not currently playing" track object
                track_data = dict(row)
                track_data['is_playing'] = False
                track_data['progress_ms'] = 0
                return track_data

        return {}
    except Exception as e:
        print(f"Error updating current track: {e}")
        return {}

# Update current track display
@app.callback(
    Output('current-track-container', 'children'),
    Input('current-track-store', 'data')
)
def update_current_track_display(current_track):
    """Update the currently playing track display."""
    if not current_track:
        return html.Div([
            html.H3("Not Currently Playing", style={'color': SPOTIFY_WHITE, 'textAlign': 'center'}),
            html.P("Play something on Spotify to see it here", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
        ])

    # Check if we have the required fields
    if 'track' not in current_track:
        if 'name' in current_track:
            # Use name field instead
            current_track['track'] = current_track['name']
        else:
            return html.Div([
                html.H3("Track Information Unavailable", style={'color': SPOTIFY_WHITE, 'textAlign': 'center'}),
                html.P("Unable to retrieve track details", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
            ])

    # Set default values for missing fields
    if 'progress_ms' not in current_track:
        current_track['progress_ms'] = 0

    if 'duration_ms' not in current_track:
        current_track['duration_ms'] = 0

    # Calculate progress percentage
    progress_percent = (current_track['progress_ms'] / current_track['duration_ms'] * 100) if current_track['duration_ms'] > 0 else 0

    # Format duration
    duration_sec = current_track['duration_ms'] / 1000
    progress_sec = current_track['progress_ms'] / 1000
    duration_str = f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}"
    progress_str = f"{int(progress_sec // 60)}:{int(progress_sec % 60):02d}"

    return html.Div([
        html.H3("Currently Playing", style={'color': SPOTIFY_GREEN, 'textAlign': 'center', 'marginBottom': '20px'}),

        # Track info with album art
        html.Div([
            # Album art
            html.Div([
                html.Img(
                    src=current_track.get('image_url', ''),
                    style={'width': '100%', 'borderRadius': '8px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}
                ) if current_track.get('image_url') else html.Div(
                    style={'width': '100%', 'paddingBottom': '100%', 'backgroundColor': SPOTIFY_GRAY, 'borderRadius': '8px'}
                )
            ], style={'width': '150px', 'display': 'inline-block', 'verticalAlign': 'top'}),

            # Track details
            html.Div([
                html.H4(current_track['track'], style={'color': SPOTIFY_WHITE, 'marginBottom': '5px'}),
                html.P(f"by {current_track['artist']}", style={'color': SPOTIFY_GRAY, 'marginBottom': '5px'}),
                html.P(f"from {current_track['album']}", style={'color': SPOTIFY_GRAY, 'marginBottom': '15px'}),

                # Progress bar
                html.Div([
                    html.Div(style={
                        'width': f'{progress_percent}%',
                        'backgroundColor': SPOTIFY_GREEN,
                        'height': '4px',
                        'borderRadius': '2px'
                    })
                ], style={
                    'width': '100%',
                    'backgroundColor': '#333333',
                    'height': '4px',
                    'borderRadius': '2px',
                    'marginBottom': '5px'
                }),

                # Time indicators
                html.Div([
                    html.Span(progress_str, style={'color': SPOTIFY_GRAY, 'fontSize': '0.8em'}),
                    html.Span(duration_str, style={'color': SPOTIFY_GRAY, 'fontSize': '0.8em', 'float': 'right'})
                ])
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '20px', 'width': 'calc(100% - 180px)'})
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
    ], style={
        'padding': '20px',
        'borderRadius': '10px',
        'backgroundColor': '#121212',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
        'margin': '20px 0'
    })

# Update top tracks chart
@app.callback(
    Output('top-tracks-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_tracks_chart(n_intervals, n_clicks):
    """Update the top tracks chart."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        user_data = spotify_api.get_user_profile()
        if user_data:
            # Fetch top tracks and save to database
            top_tracks_data = spotify_api.get_top_tracks(limit=10)
            if top_tracks_data:
                # Save to database
                for track in top_tracks_data:
                    db.save_track(track)
                    # Use a consistent datetime format
                    db.save_listening_history(
                        user_id=user_data['id'],
                        track_id=track['id'],
                        played_at=datetime.now().replace(microsecond=0).isoformat(),
                        source='top_short_term'
                    )

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for top tracks based on frequency in listening history
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            t.popularity,
            t.image_url,
            COUNT(h.history_id) as play_count
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE h.source LIKE 'top_%'
        GROUP BY t.track_id
        ORDER BY play_count DESC
        LIMIT 10
    ''')

    top_tracks_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Convert to DataFrame
    if top_tracks_data:
        top_tracks_df = pd.DataFrame(top_tracks_data)
        # Add rank column
        top_tracks_df['rank'] = range(1, len(top_tracks_df) + 1)
    else:
        # Create empty DataFrame with the right columns
        top_tracks_df = pd.DataFrame(columns=['track', 'artist', 'album', 'popularity', 'rank'])

    # Create visualization
    return visualizations.create_top_tracks_chart(top_tracks_df)

# Update saved tracks chart
@app.callback(
    Output('saved-tracks-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_saved_tracks_chart(n_intervals, n_clicks):
    """Update the saved tracks chart."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        user_data = spotify_api.get_user_profile()
        if user_data:
            # Fetch saved tracks and save to database
            saved_tracks_data = spotify_api.get_saved_tracks(limit=10)
            if saved_tracks_data:
                # Save to database
                for track in saved_tracks_data:
                    db.save_track(track)
                    # Use a consistent datetime format
                    timestamp = track.get('added_at')
                    if timestamp:
                        # Try to parse and normalize the timestamp
                        try:
                            if 'Z' in timestamp:
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            elif 'T' in timestamp and ('+' in timestamp or '-' in timestamp.split('T')[1]):
                                dt = datetime.fromisoformat(timestamp)
                            else:
                                dt = datetime.fromisoformat(timestamp)

                            # Convert to naive datetime in ISO format
                            played_at = dt.replace(tzinfo=None, microsecond=0).isoformat()
                        except ValueError:
                            # If parsing fails, use current time
                            played_at = datetime.now().replace(microsecond=0).isoformat()
                    else:
                        # If no timestamp, use current time
                        played_at = datetime.now().replace(microsecond=0).isoformat()

                    db.save_listening_history(
                        user_id=user_data['id'],
                        track_id=track['id'],
                        played_at=played_at,
                        source='saved'
                    )

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for saved tracks
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            t.image_url,
            h.played_at as added_at
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE h.source = 'saved'
        ORDER BY h.played_at DESC
        LIMIT 10
    ''')

    saved_tracks_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Convert to DataFrame
    if saved_tracks_data:
        saved_tracks_df = pd.DataFrame(saved_tracks_data)
    else:
        # Create empty DataFrame with the right columns
        saved_tracks_df = pd.DataFrame(columns=['track', 'artist', 'album', 'added_at'])

    # Create visualization
    return visualizations.create_saved_tracks_timeline(saved_tracks_df)

# Update playlists chart
@app.callback(
    Output('playlists-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_playlists_chart(n_intervals, n_clicks):
    """Update the playlists chart."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        playlists_data = spotify_api.get_playlists(limit=10)
        data_processor.save_data(playlists_data, 'playlists.csv')

    # Load data from file
    playlists_df = data_processor.load_data('playlists.csv')

    # Create visualization
    return visualizations.create_playlists_chart(playlists_df)

# Update audio features chart
@app.callback(
    Output('audio-features-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_audio_features_chart(n_intervals, n_clicks):
    """Update the audio features chart."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        user_data = spotify_api.get_user_profile()
        if user_data:
            # Get audio features for top tracks
            audio_features_data = spotify_api.get_audio_features_for_top_tracks(limit=5)
            if audio_features_data:
                # Save to database
                for track in audio_features_data:
                    # Save track with audio features
                    db.save_track({
                        'id': track['id'],
                        'name': track['track'],
                        'artist': track['artist'],
                        'duration_ms': track.get('duration_ms', 0),
                        'popularity': 0,  # Not available in this context
                        'preview_url': '',  # Not available in this context
                        'image_url': '',  # Not available in this context
                        'added_at': datetime.now().replace(microsecond=0).isoformat(),
                        # Audio features
                        'danceability': track.get('danceability', 0),
                        'energy': track.get('energy', 0),
                        'key': track.get('key', 0),
                        'loudness': track.get('loudness', 0),
                        'mode': track.get('mode', 0),
                        'speechiness': track.get('speechiness', 0),
                        'acousticness': track.get('acousticness', 0),
                        'instrumentalness': track.get('instrumentalness', 0),
                        'liveness': track.get('liveness', 0),
                        'valence': track.get('valence', 0),
                        'tempo': track.get('tempo', 0)
                    })

                    # Save listening history entry with consistent datetime format
                    db.save_listening_history(
                        user_id=user_data['id'],
                        track_id=track['id'],
                        played_at=datetime.now().replace(microsecond=0).isoformat(),
                        source='audio_features'
                    )

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for tracks with audio features
    cursor.execute('''
        SELECT DISTINCT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            h.played_at
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE h.source = 'audio_features' OR h.source LIKE 'top_%'
        ORDER BY h.played_at DESC
        LIMIT 5
    ''')

    tracks_data = [dict(row) for row in cursor.fetchall()]

    # Get audio features for these tracks
    audio_features_data = []
    for track in tracks_data:
        # Get audio features from API
        features = spotify_api.get_audio_features_safely(track['id'])

        # Combine track info with audio features
        audio_features_data.append({
            'track': track['track'],
            'artist': track['artist'],
            'id': track['id'],
            'danceability': features.get('danceability', 0),
            'energy': features.get('energy', 0),
            'key': features.get('key', 0),
            'loudness': features.get('loudness', 0),
            'mode': features.get('mode', 0),
            'speechiness': features.get('speechiness', 0),
            'acousticness': features.get('acousticness', 0),
            'instrumentalness': features.get('instrumentalness', 0),
            'liveness': features.get('liveness', 0),
            'valence': features.get('valence', 0),
            'tempo': features.get('tempo', 0)
        })

    conn.close()

    # Convert to DataFrame
    if audio_features_data:
        audio_features_df = pd.DataFrame(audio_features_data)
    else:
        # Create empty DataFrame with the right columns
        audio_features_df = pd.DataFrame(columns=[
            'track', 'artist', 'id', 'danceability', 'energy', 'key', 'loudness',
            'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
            'valence', 'tempo'
        ])

    # Create visualization
    return visualizations.create_audio_features_radar(audio_features_df)

# Update top artists chart
@app.callback(
    Output('top-artists-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_artists_chart(n_intervals, n_clicks):
    """Update the top artists chart."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        user_data = spotify_api.get_user_profile()
        if user_data:
            # Fetch top artists and save to database
            top_artists_data = spotify_api.get_top_artists(limit=10)
            if top_artists_data:
                # Save to database
                for artist in top_artists_data:
                    # Create a track-like entry for the artist
                    artist_data = {
                        'id': f"artist-{artist.get('id', '').replace(' ', '-')}",
                        'name': artist.get('name', 'Unknown Artist'),
                        'artist': artist.get('name', 'Unknown Artist'),  # Artist is their own artist
                        'popularity': artist.get('popularity', 0),
                        'image_url': artist.get('image_url', ''),
                        'added_at': datetime.now().replace(microsecond=0).isoformat()
                    }

                    # Save to database
                    try:
                        db.save_track(artist_data)
                        db.save_listening_history(
                            user_id=user_data['id'],
                            track_id=artist_data['id'],
                            played_at=datetime.now().replace(microsecond=0).isoformat(),
                            source='top_artist'
                        )
                    except Exception as e:
                        print(f"Error saving artist {artist.get('name')}: {e}")

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for top artists
    cursor.execute('''
        SELECT
            t.name as artist,
            t.popularity,
            t.image_url,
            COUNT(h.history_id) as play_count
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE h.source = 'top_artist'
        GROUP BY t.name
        ORDER BY play_count DESC
        LIMIT 10
    ''')

    artists_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Convert to DataFrame
    if artists_data:
        top_artists_df = pd.DataFrame(artists_data)
        # Add rank column
        top_artists_df['rank'] = range(1, len(top_artists_df) + 1)
    else:
        # Create empty DataFrame with the right columns
        top_artists_df = pd.DataFrame(columns=['artist', 'popularity', 'image_url', 'rank'])

    # Create visualization
    return visualizations.create_top_artists_chart(top_artists_df)

# Update genre chart
@app.callback(
    Output('genre-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_genre_chart(n_intervals, n_clicks):
    """Update the genre chart."""
    try:
        print("=== Genre Chart Update Started ===")

        # Fetch new data if refresh button clicked
        if n_clicks is not None and n_clicks > 0:
            print("Fetching genre data from recently played tracks...")
            user_data = spotify_api.get_user_profile()
            if user_data:
                print(f"User ID: {user_data['id']}")

                # IMPORTANT: Save user to database first to ensure user exists
                try:
                    print(f"Saving user {user_data['display_name']} to database")
                    db.save_user(user_data)
                    print(f"User saved successfully")
                except Exception as e:
                    print(f"ERROR saving user to database: {e}")
                    import traceback
                    traceback.print_exc()

                # Verify user exists in database
                conn = sqlite3.connect(db.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_data['id'],))
                user_exists = cursor.fetchone() is not None
                conn.close()

                if not user_exists:
                    print(f"WARNING: User {user_data['id']} not found in database after save attempt")
                    print("Creating user record again")
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO users (user_id, display_name, followers, last_updated)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (user_data['id'], user_data.get('display_name', 'Unknown'), user_data.get('followers', 0)))
                    conn.commit()
                    conn.close()
                    print(f"User {user_data['id']} created manually")

                # Fetch up to 200 recently played tracks using pagination
                print("Fetching up to 200 recently played tracks...")
                all_tracks = []
                before_timestamp = None

                # Spotify API has a limit of 50 tracks per call, so we need to paginate
                # We'll make up to 4 calls to get up to 200 tracks
                for i in range(4):  # 4 calls * 50 tracks = 200 tracks max
                    try:
                        # Get recently played tracks
                        tracks = spotify_api.get_recently_played(limit=50, before=before_timestamp)

                        if not tracks or len(tracks) == 0:
                            print("No more tracks available")
                            break

                        print(f"Retrieved {len(tracks)} tracks in batch {i+1}")
                        all_tracks.extend(tracks)

                        # Save tracks to database
                        for track in tracks:
                            db.save_track(track)

                            # Normalize the timestamp
                            played_at = track.get('played_at')
                            if played_at:
                                try:
                                    # Parse the timestamp
                                    if 'Z' in played_at:
                                        dt = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
                                    elif 'T' in played_at and ('+' in played_at or '-' in played_at.split('T')[1]):
                                        dt = datetime.fromisoformat(played_at)
                                    else:
                                        dt = datetime.fromisoformat(played_at)

                                    # Convert to naive datetime in ISO format
                                    played_at = dt.replace(tzinfo=None).isoformat()
                                except ValueError:
                                    # If parsing fails, use the original timestamp
                                    pass
                            else:
                                # If no timestamp, use current time
                                played_at = datetime.now().isoformat()

                            # Save listening history
                            db.save_listening_history(
                                user_id=user_data['id'],
                                track_id=track['id'],
                                played_at=played_at,
                                source='played'
                            )

                        # Update the timestamp for the next request
                        # We use the played_at time of the last track as the 'before' parameter
                        last_track = tracks[-1]
                        played_at = last_track.get('played_at')

                        if played_at:
                            try:
                                # Parse the timestamp
                                if 'Z' in played_at:
                                    dt = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
                                elif 'T' in played_at and ('+' in played_at or '-' in played_at.split('T')[1]):
                                    dt = datetime.fromisoformat(played_at)
                                else:
                                    dt = datetime.fromisoformat(played_at)

                                # Convert to timestamp for the next request
                                # Subtract 1 millisecond to avoid getting the same track again
                                before_timestamp = int(dt.timestamp() * 1000) - 1
                                print(f"Next request will fetch tracks before {dt}")
                            except ValueError as e:
                                print(f"Error parsing timestamp: {e}")
                                break
                        else:
                            print("Last track has no played_at timestamp")
                            break

                        # Add a delay to avoid rate limiting
                        time.sleep(1)

                    except Exception as e:
                        print(f"Error fetching recently played tracks: {e}")
                        import traceback
                        traceback.print_exc()
                        break

                print(f"Total tracks fetched: {len(all_tracks)}")

                # Extract unique artists from the tracks
                artists = set()
                for track in all_tracks:
                    artist_name = track.get('artist')
                    if artist_name:
                        artists.add(artist_name)

                print(f"Found {len(artists)} unique artists in recently played tracks")

                # Process each artist to get their genres
                for artist_name in artists:
                    print(f"Processing genres for artist: {artist_name}")

                    # Use our new function to get genres
                    genres = spotify_api.get_artist_genres(artist_name)

                    if genres:
                        print(f"Found {len(genres)} genres for artist {artist_name}: {genres}")

                        # Save each genre to the database
                        for genre in genres:
                            if genre:  # Skip empty genres
                                success = db.save_genre(genre, artist_name)
                                if success:
                                    print(f"Successfully saved genre '{genre}' for artist '{artist_name}'")
                                else:
                                    print(f"Failed to save genre '{genre}' to database")
                    else:
                        print(f"No genres found for artist {artist_name}")

                    # Add a small delay to avoid rate limiting
                    time.sleep(0.5)

        # Process all artists in the database to ensure we have genres for all of them
        print("Processing genres for all artists in the database...")

        # Get all artists from the database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT artist FROM tracks")
        all_artists = [row[0] for row in cursor.fetchall()]
        conn.close()

        print(f"Found {len(all_artists)} unique artists in the database")

        # Process each artist to get their genres
        for artist_name in all_artists:
            # Check if we already have genres for this artist
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM genres WHERE artist_name = ?", (artist_name,))
            genre_count = cursor.fetchone()[0]
            conn.close()

            # If we don't have genres for this artist, get them
            if genre_count == 0:
                print(f"Getting genres for artist: {artist_name}")

                # Get genres for this artist
                genres = spotify_api.get_artist_genres(artist_name)

                # Save each genre to the database
                for genre in genres:
                    if genre:  # Skip empty genres
                        success = db.save_genre(genre, artist_name)
                        if success:
                            print(f"Successfully saved genre '{genre}' for artist '{artist_name}'")

                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
            else:
                print(f"Already have {genre_count} genres for artist: {artist_name}")

        # Get user data if not already available
        if 'user_data' not in locals() or user_data is None:
            user_data = spotify_api.get_user_profile()

        # Get genre data from the genres table
        genre_data = db.get_top_genres(limit=10)

        # Convert to DataFrame
        if genre_data:
            genre_df = pd.DataFrame(genre_data)
            print(f"Genre data loaded from database: {len(genre_df)} genres")
        else:
            print("No genre data in database")
            # Create an empty DataFrame
            genre_df = pd.DataFrame(columns=['genre', 'count'])

        # Create visualization
        print("Creating genre pie chart...")
        fig = visualizations.create_genre_pie_chart(genre_df)
        print("Genre pie chart created")

        print("=== Genre Chart Update Completed ===")
        return fig
    except Exception as e:
        print(f"Error updating genre chart: {e}")
        import traceback
        traceback.print_exc()

        # Return empty figure with error message
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text="Error loading genre data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=SPOTIFY_GRAY, size=16)
        )
        fig.update_layout(
            paper_bgcolor='#121212',
            plot_bgcolor='#121212',
            margin=dict(t=0, b=0, l=0, r=0)
        )
        return fig

# Update listening patterns chart
@app.callback(
    Output('listening-patterns-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_listening_patterns_chart(n_intervals):
    """Update the listening patterns chart."""
    user_data = spotify_api.get_user_profile()
    if not user_data:
        return visualizations.create_empty_chart("Log in to see your listening patterns")

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for listening patterns in the past two weeks
    cursor.execute('''
        SELECT
            strftime('%w', played_at) as day_of_week,
            strftime('%H', played_at) as hour_of_day,
            COUNT(*) as play_count
        FROM listening_history
        WHERE user_id = ?
        AND played_at IS NOT NULL
        GROUP BY day_of_week, hour_of_day
        ORDER BY day_of_week, hour_of_day
    ''', (user_data['id'],))

    patterns_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if patterns_data:
        # Convert numeric day of week to name
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        patterns_df = pd.DataFrame(patterns_data)
        patterns_df['day_name'] = patterns_df['day_of_week'].astype(int).map(lambda x: day_names[x])
        return visualizations.create_listening_patterns_heatmap(patterns_df)

    # If no data in database, try to fetch recent data from API and save to database
    recently_played = spotify_api.get_recently_played(limit=50)
    if recently_played and user_data:
        # Save to database
        for track in recently_played:
            db.save_track(track)
            # Normalize the timestamp
            played_at = track.get('played_at')
            if played_at:
                try:
                    # Parse the timestamp
                    if 'Z' in played_at:
                        dt = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
                    elif 'T' in played_at and ('+' in played_at or '-' in played_at.split('T')[1]):
                        dt = datetime.fromisoformat(played_at)
                    else:
                        dt = datetime.fromisoformat(played_at)

                    # Convert to naive datetime in ISO format
                    played_at = dt.replace(tzinfo=None, microsecond=0).isoformat()
                except ValueError:
                    # If parsing fails, use current time
                    played_at = datetime.now().replace(microsecond=0).isoformat()
            else:
                # If no timestamp, use current time
                played_at = datetime.now().replace(microsecond=0).isoformat()

            db.save_listening_history(
                user_id=user_data['id'],
                track_id=track['id'],
                played_at=played_at,
                source='recently_played'
            )

        # Try database query again
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                strftime('%w', played_at) as day_of_week,
                strftime('%H', played_at) as hour_of_day,
                COUNT(*) as play_count
            FROM listening_history
            WHERE user_id = ? AND played_at IS NOT NULL
            GROUP BY day_of_week, hour_of_day
            ORDER BY day_of_week, hour_of_day
        ''', (user_data['id'],))

        patterns_data = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if patterns_data:
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            patterns_df = pd.DataFrame(patterns_data)
            patterns_df['day_name'] = patterns_df['day_of_week'].astype(int).map(lambda x: day_names[x])
            return visualizations.create_listening_patterns_heatmap(patterns_df)

    # Create empty DataFrame with the right columns
    patterns_df = pd.DataFrame(columns=['day_of_week', 'hour_of_day', 'play_count', 'day_name'])
    return visualizations.create_listening_patterns_heatmap(patterns_df)

# New callback for top albums section
@app.callback(
    Output('top-albums-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_albums(n_intervals, n_clicks):
    """Update the top albums section."""
    try:
        # Fetch new data if refresh button clicked
        if n_clicks is not None and n_clicks > 0:
            top_albums_data = get_top_albums(spotify_api, limit=10)
            data_processor.save_data(top_albums_data.to_dict('records'), 'top_albums.csv')

        # Load data from file
        top_albums_df = data_processor.load_data('top_albums.csv')

        if top_albums_df.empty:
            return html.Div("No album data available",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        # Create album cards
        album_cards = []
        for i, (_, album) in enumerate(top_albums_df.iterrows()):
            album_card = create_album_card(
                album_name=album.get('album', 'Unknown Album'),
                artist_name=album.get('artist', 'Unknown Artist'),
                rank=i+1,
                image_url=album.get('image_url', ''),
                score=album.get('total_count', 0)
            )
            album_cards.append(album_card)

        return html.Div(album_cards, style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fill, minmax(200px, 1fr))',
            'gap': '20px',
            'padding': '20px'
        })

    except Exception as e:
        print(f"Error updating top albums: {e}")
        return html.Div("Error loading album data",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

# Callback for album listening patterns
@app.callback(
    Output('album-listening-patterns-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_album_listening_patterns(n_intervals):
    """Update the album listening patterns section."""
    user_data = spotify_api.get_user_profile()
    if not user_data:
        return html.Div("Log in to see your album listening patterns",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

    try:
        # Get patterns from database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Calculate album completion rate and sequential listening
        # Use a simpler query that doesn't rely on window functions
        cursor.execute('''
            SELECT
                COUNT(CASE WHEN track_count > 1 THEN 1 END) * 100.0 / COUNT(*) as album_completion_rate,
                50.0 as sequential_listening_score
            FROM (
                SELECT
                    t.album,
                    COUNT(DISTINCT t.track_id) as track_count
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.user_id = ? AND t.album IS NOT NULL AND t.album != ''
                GROUP BY t.album
            )
        ''', (user_data['id'],))

        result = cursor.fetchone()
        conn.close()

        if result and result[0] is not None:
            patterns = {
                'album_completion_rate': round(result[0], 2),
                'sequential_listening_score': round(result[1], 2),
                'album_focused': result[1] > 40 or result[0] > 30,
                'listening_style': get_listening_style(result[0], result[1])
            }
        else:
            # Fallback to CSV data
            patterns_df = data_processor.load_data('album_patterns.csv')
            if patterns_df.empty:
                return html.Div("No album patterns available",
                              style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})
            patterns = patterns_df.iloc[0].to_dict()

        # Create stats cards
        from modules.visualizations import create_stat_card

        stats_cards = [
            create_stat_card(
                "Album Completion",
                f"{patterns.get('album_completion_rate', 0)}%",
                icon="fa-compact-disc",
                color=SPOTIFY_GREEN
            ),
            create_stat_card(
                "Sequential Listening",
                f"{patterns.get('sequential_listening_score', 0)}%",
                icon="fa-list-ol",
                color="#1ED760"
            ),
            create_stat_card(
                "Listening Style",
                patterns.get('listening_style', 'Unknown'),
                icon="fa-headphones",
                color="#2D46B9"
            )
        ]

        return html.Div(stats_cards, style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'space-around',
            'padding': '20px'
        })

    except Exception as e:
        print(f"Error updating album listening patterns: {e}")
        return html.Div("Error loading album listening patterns",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

def get_listening_style(completion_rate, sequential_score):
    """Determine listening style based on metrics."""
    album_focused = sequential_score > 40 or completion_rate > 30

    if album_focused:
        if sequential_score > 70:
            return "Album Purist"
        return "Album Explorer"

    if sequential_score < 20:
        return "Track Hopper"
    return "Mood Curator"

# New callback for personality analysis
@app.callback(
    Output('personality-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)

def update_personality_analysis(n_intervals, n_clicks):
    """Update the personality analysis section."""
    try:
        # Fetch new data if refresh button clicked
        if n_clicks is not None and n_clicks > 0:
            personality_data = personality_analyzer.analyze()

            # Convert NumPy types to Python native types before saving
            if 'metrics' in personality_data and isinstance(personality_data['metrics'], dict):
                for key, value in personality_data['metrics'].items():
                    if hasattr(value, 'item'):  # Check if it's a NumPy type
                        personality_data['metrics'][key] = value.item()  # Convert to Python native type

            data_processor.save_data([personality_data], 'personality.csv')

        # Load data from file
        personality_df = data_processor.load_data('personality.csv')

        if personality_df.empty:
            return html.Div("No personality analysis available",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        personality_data = personality_df.iloc[0].to_dict()

        # Ensure recommendations is a list
        if 'recommendations' in personality_data and isinstance(personality_data['recommendations'], str):
            try:
                # Try to safely evaluate the string representation of the list
                import ast
                personality_data['recommendations'] = ast.literal_eval(personality_data['recommendations'])
            except:
                # Fallback to empty list if parsing fails
                personality_data['recommendations'] = []

        # Ensure metrics is a dictionary
        if 'metrics' in personality_data and isinstance(personality_data['metrics'], str):
            try:
                # Try to safely evaluate the string representation of the dictionary
                import ast
                personality_data['metrics'] = ast.literal_eval(personality_data['metrics'])
            except:
                # Fallback to empty dict if parsing fails
                personality_data['metrics'] = {}

        # Load DJ mode stats to include in metrics
        dj_stats_df = data_processor.load_data('dj_stats.csv')
        if not dj_stats_df.empty:
            dj_stats = dj_stats_df.iloc[0].to_dict()
            # Add DJ stats to metrics
            if 'metrics' in personality_data and isinstance(personality_data['metrics'], dict):
                personality_data['metrics']['estimated_minutes'] = dj_stats.get('estimated_minutes', 0)
                personality_data['metrics']['percentage_of_listening'] = dj_stats.get('percentage_of_listening', 0)
                personality_data['metrics']['dj_mode_user'] = dj_stats.get('dj_mode_user', False)

        # Load album patterns to include in metrics
        album_patterns_df = data_processor.load_data('album_patterns.csv')
        if not album_patterns_df.empty:
            album_patterns = album_patterns_df.iloc[0].to_dict()
            # Add album patterns to metrics if not already present
            if 'metrics' in personality_data and isinstance(personality_data['metrics'], dict):
                if 'album_completion_rate' not in personality_data['metrics'] or personality_data['metrics']['album_completion_rate'] == 0:
                    personality_data['metrics']['album_completion_rate'] = album_patterns.get('album_completion_rate', 0)
                if 'sequential_listening_score' not in personality_data['metrics'] or personality_data['metrics']['sequential_listening_score'] == 0:
                    personality_data['metrics']['sequential_listening_score'] = album_patterns.get('sequential_listening_score', 0)
                if 'listening_style' not in personality_data['metrics'] or personality_data['metrics']['listening_style'] == 'Unknown':
                    personality_data['metrics']['listening_style'] = album_patterns.get('listening_style', 'Unknown')

        # Create a modern, visually appealing personality section
        return html.Div([
            # Header section
            html.Div([
                html.H2("Your Music Personality",
                    style={
                        'color': SPOTIFY_GREEN,
                        'textAlign': 'center',
                        'fontSize': '3rem',
                        'fontWeight': 'bold',
                        'marginBottom': '20px',
                        'letterSpacing': '1px',
                        'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
                    }
                ),
                html.Div([
                    html.Span(personality_data.get('primary_type', 'Unknown'),
                        style={
                            'color': SPOTIFY_WHITE,
                            'fontSize': '1.8rem',
                            'fontWeight': 'bold'
                        }
                    ),
                    html.Span(" × ",
                        style={
                            'color': SPOTIFY_GRAY,
                            'fontSize': '1.8rem',
                            'margin': '0 10px'
                        }
                    ),
                    html.Span(personality_data.get('secondary_type', 'Unknown'),
                        style={
                            'color': SPOTIFY_WHITE,
                            'fontSize': '1.8rem',
                            'fontWeight': 'bold'
                        }
                    )
                ], style={
                    'textAlign': 'center',
                    'marginBottom': '30px'
                })
            ]),

            # Description card
            html.Div([
                html.P(personality_data.get('description', 'No description available'),
                    style={
                        'color': SPOTIFY_WHITE,
                        'fontSize': '1.2rem',
                        'lineHeight': '1.6',
                        'textAlign': 'center',
                        'margin': '0 auto',
                        'maxWidth': '800px'
                    }
                )
            ], style={
                'backgroundColor': '#181818',
                'padding': '30px',
                'borderRadius': '15px',
                'marginBottom': '30px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.3)'
            }),

            # Recommendations
            html.Div([
                html.H3("Personalized Recommendations",
                    style={
                        'color': SPOTIFY_WHITE,
                        'textAlign': 'center',
                        'marginBottom': '20px',
                        'fontSize': '1.5rem'
                    }
                ),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-lightbulb",
                            style={
                                'color': SPOTIFY_GREEN,
                                'fontSize': '1.2rem',
                                'marginRight': '10px'
                            }
                        ),
                        html.Span(recommendation)
                    ], style={
                        'color': SPOTIFY_WHITE,
                        'backgroundColor': '#242424',
                        'padding': '15px 20px',
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                        'fontSize': '1.1rem'
                    }) for recommendation in personality_data.get('recommendations', [])
                ])
            ], style={
                'backgroundColor': '#181818',
                'padding': '30px',
                'borderRadius': '15px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.3)'
            })
        ], style={
            'padding': '40px',
            'backgroundColor': '#121212',
            'borderRadius': '20px',
            'margin': '20px 0',
            'boxShadow': '0 8px 16px rgba(0,0,0,0.4)'
        })

    except Exception as e:
        print(f"Error updating personality analysis: {e}")
        return html.Div("Error loading personality analysis",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})


# New callback for DJ mode stats
@app.callback(
    Output('dj-mode-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_dj_mode_stats(n_intervals, n_clicks):
    """Update the DJ mode stats section."""
    try:
        # Fetch new data if refresh button clicked
        if n_clicks is not None and n_clicks > 0:
            recently_played = spotify_api.get_recently_played(limit=50)
            dj_stats = personality_analyzer._estimate_dj_mode_usage(recently_played)
            data_processor.save_data([dj_stats], 'dj_stats.csv')

        # Load data from file
        dj_stats_df = data_processor.load_data('dj_stats.csv')

        if dj_stats_df.empty:
            return html.Div("No DJ mode statistics available",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        dj_stats = dj_stats_df.iloc[0].to_dict()

        # Create stats cards
        from modules.visualizations import create_stat_card

        stats_cards = [
            create_stat_card(
                "DJ Mode Minutes",
                f"{dj_stats.get('estimated_minutes', 0)}",
                icon="fa-robot",
                color=SPOTIFY_GREEN
            ),
            create_stat_card(
                "DJ Mode Usage",
                f"{dj_stats.get('percentage_of_listening', 0)}%",
                icon="fa-percentage",
                color="#1ED760"
            ),
            create_stat_card(
                "DJ Mode Status",
                "Active User" if dj_stats.get('dj_mode_user', False) else "Occasional User",
                icon="fa-user-check",
                color="#2D46B9"
            )
        ]

        return html.Div(stats_cards, style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'space-around',
            'padding': '20px'
        })

    except Exception as e:
        print(f"Error updating DJ mode stats: {e}")
        return html.Div("Error loading DJ mode statistics",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

# Update wrapped summary
@app.callback(
    Output('wrapped-summary-store', 'data'),
    Input('refresh-button', 'n_clicks')
)
def update_wrapped_summary(n_clicks):
    """Generate and store Spotify Wrapped style summary."""
    if n_clicks is not None and n_clicks > 0:
        # Get user data
        user_data = spotify_api.get_user_profile()
        if user_data:
            print(f"Generating wrapped summary for user: {user_data['id']}")

            # IMPORTANT: Save user to database first to ensure user exists
            try:
                print(f"Saving user {user_data['display_name']} to database")
                db.save_user(user_data)
                print(f"User saved successfully")
            except Exception as e:
                print(f"ERROR saving user to database: {e}")
                import traceback
                traceback.print_exc()

            # Verify user exists in database
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_data['id'],))
            user_exists = cursor.fetchone() is not None
            conn.close()

            if not user_exists:
                print(f"WARNING: User {user_data['id']} not found in database after save attempt")
                print("Creating user record again")
                conn = sqlite3.connect(db.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, display_name, followers, last_updated)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_data['id'], user_data.get('display_name', 'Unknown'), user_data.get('followers', 0)))
                conn.commit()
                conn.close()
                print(f"User {user_data['id']} created manually")

            # Get top artists and their genres
            top_artists_data = spotify_api.get_top_artists(limit=20)
            if top_artists_data:
                print(f"Processing {len(top_artists_data)} artists for genre analysis")

                # Process and save genres to database
                for artist in top_artists_data:
                    artist_name = artist.get('name', 'Unknown Artist')
                    print(f"Processing genres for artist: {artist_name}")

                    # Extract genres
                    genres = artist.get('genres', [])
                    print(f"Raw genres data: {genres} (type: {type(genres)})")

                    if isinstance(genres, str):
                        # If genres is a string (comma-separated), convert to list
                        genres = [g.strip() for g in genres.split(',') if g.strip()]
                        print(f"Converted string genres to list: {genres}")

                    # Save each genre to the genres table
                    if genres:
                        print(f"Found {len(genres)} genres for {artist_name}")
                        for genre in genres:
                            if genre:  # Skip empty genres
                                print(f"Saving genre '{genre}' for artist '{artist_name}'")

                                # Save to the simplified genres table
                                success = db.save_genre(genre, artist_name)

                                if success:
                                    print(f"Successfully saved genre '{genre}' to database")
                                else:
                                    print(f"Failed to save genre '{genre}' to database")
                    else:
                        print(f"No genres found for artist: {artist_name}")

                # Also save to CSV for backward compatibility
                # Extract and count all genres
                all_genres = []
                for artist in top_artists_data:
                    genres = artist.get('genres', [])
                    if isinstance(genres, str):
                        genres = [g.strip() for g in genres.split(',') if g.strip()]

                    for genre in genres:
                        if genre:  # Skip empty genres
                            all_genres.append({
                                'genre': genre,
                                'count': 1
                            })

                if all_genres:
                    # Aggregate by genre
                    genre_counts = pd.DataFrame(all_genres).groupby('genre')['count'].sum().reset_index()
                    genre_counts = genre_counts.sort_values('count', ascending=False)
                    genre_counts.to_csv(os.path.join('data', 'genre_analysis.csv'), index=False)
                    print(f"Saved {len(genre_counts)} genres to genre_analysis.csv")
            else:
                print("No top artists data available for genre analysis")

        # Generate summary from database
        summary = generate_wrapped_summary_from_db()
        return summary

    try:
        # Try to load existing summary
        with open(os.path.join('data', 'wrapped_summary.json'), 'r') as f:
            import json
            return json.load(f)
    except:
        return {}

# New callback for music analysis section
@app.callback(
    Output('music-analysis-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_music_analysis(n_intervals, n_clicks):
    """Update the music analysis section."""
    try:
        # Get audio features from database
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query for tracks with audio features
        cursor.execute('''
            SELECT
                AVG(danceability) as energy,
                AVG(energy) as energy,
                AVG(valence) as valence,
                AVG(tempo) as tempo
            FROM tracks
            WHERE danceability IS NOT NULL
        ''')

        result = cursor.fetchone()
        conn.close()

        if result:
            # Create a DataFrame with the average values
            audio_features_df = pd.DataFrame([{
                'energy': result['energy'] or 0.5,
                'valence': result['valence'] or 0.5,
                'tempo': result['tempo'] or 120
            }])
        else:
            # Create default values if no data
            audio_features_df = pd.DataFrame([{
                'energy': 0.5,
                'valence': 0.5,
                'tempo': 120
            }])

        # Create a modern, visually appealing layout
        return html.Div([
            # Main title and subtitle
            html.H2("Your Sound Story",
                style={
                    'color': SPOTIFY_GREEN,
                    'textAlign': 'center',
                    'fontSize': '3rem',
                    'fontWeight': 'bold',
                    'marginBottom': '20px',
                    'letterSpacing': '1px',
                    'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
                }
            ),
            html.P("Discover the unique elements that make up your musical identity",
                style={
                    'color': SPOTIFY_WHITE,
                    'textAlign': 'center',
                    'fontSize': '1.2rem',
                    'marginBottom': '40px',
                    'opacity': '0.9'
                }
            ),

            # Stats Grid
            html.Div([
                # Energy Level
                html.Div([
                    html.I(className="fas fa-bolt", style={
                        'fontSize': '2rem',
                        'color': SPOTIFY_GREEN,
                        'marginBottom': '15px'
                    }),
                    html.H3("Energy Level", style={'color': SPOTIFY_WHITE, 'marginBottom': '10px'}),
                    html.H4(f"{int(audio_features_df['energy'].mean() * 100)}%",
                        style={'color': SPOTIFY_GREEN, 'fontSize': '2.5rem', 'marginBottom': '5px'}),
                ], style={'textAlign': 'center', 'padding': '20px'}),

                # Mood
                html.Div([
                    html.I(className="fas fa-smile", style={
                        'fontSize': '2rem',
                        'color': SPOTIFY_GREEN,
                        'marginBottom': '15px'
                    }),
                    html.H3("Mood", style={'color': SPOTIFY_WHITE, 'marginBottom': '10px'}),
                    html.H4(f"{int(audio_features_df['valence'].mean() * 100)}% Positive",
                        style={'color': SPOTIFY_GREEN, 'fontSize': '2.5rem', 'marginBottom': '5px'}),
                ], style={'textAlign': 'center', 'padding': '20px'}),

                # Tempo
                html.Div([
                    html.I(className="fas fa-running", style={
                        'fontSize': '2rem',
                        'color': SPOTIFY_GREEN,
                        'marginBottom': '15px'
                    }),
                    html.H3("Average Tempo", style={'color': SPOTIFY_WHITE, 'marginBottom': '10px'}),
                    html.H4(f"{int(audio_features_df['tempo'].mean())} BPM",
                        style={'color': SPOTIFY_GREEN, 'fontSize': '2.5rem', 'marginBottom': '5px'}),
                ], style={'textAlign': 'center', 'padding': '20px'})
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                'gap': '20px',
                'marginBottom': '40px',
                'backgroundColor': '#242424',
                'borderRadius': '15px',
                'padding': '20px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.2)'
            })
        ])

    except Exception as e:
        print(f"Error updating music analysis: {e}")
        return html.Div("Error loading music analysis",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

# Update wrapped summary display
@app.callback(
    Output('wrapped-summary-container', 'children'),
    Input('wrapped-summary-store', 'data')
)
def update_wrapped_summary_display(summary):
    """Update the Wrapped summary display."""
    # Handle the case when summary is None or empty
    if summary is None or not summary:
        return html.Div([
            html.H3("Your Spotify Wrapped", style={'color': SPOTIFY_GREEN, 'textAlign': 'center'}),
            html.P("Click 'Refresh Data' to generate your Spotify Wrapped summary",
                  style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
        ], style={
            'padding': '30px',
            'borderRadius': '10px',
            'backgroundColor': '#121212',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
            'margin': '20px 0',
            'textAlign': 'center'
        })

    # Initialize default values for all required fields to prevent NoneType errors
    if 'top_track' not in summary or summary['top_track'] is None:
        summary['top_track'] = {'name': 'Start listening to discover your top track', 'artist': 'Unknown'}

    if 'top_artist' not in summary or summary['top_artist'] is None:
        summary['top_artist'] = {'name': 'Start listening to discover your top artist', 'genres': 'Exploring genres'}

    if 'music_mood' not in summary or summary['music_mood'] is None:
        summary['music_mood'] = {'mood': 'Discovering Your Sound', 'valence': 0.5, 'energy': 0.5}

    if 'genre_highlight' not in summary or summary['genre_highlight'] is None:
        summary['genre_highlight'] = {'name': 'Exploring New Genres', 'count': 0}

    # Create a Wrapped-style summary display
    return html.Div([
        html.H2("Your Spotify Wrapped", style={
            'color': SPOTIFY_GREEN,
            'textAlign': 'center',
            'fontSize': '2.5rem',
            'fontWeight': 'bold',
            'marginBottom': '30px'
        }),

        # Top track and artist
        html.Div([
            # Top track section
            html.Div([
                html.H3("Your Top Track", style={'color': SPOTIFY_WHITE, 'marginBottom': '15px'}),
                html.Div([
                    html.H4(summary.get('top_track', {}).get('name', 'Unknown'),
                           style={'color': SPOTIFY_GREEN, 'fontSize': '1.8rem', 'marginBottom': '5px'}),
                    html.P(f"by {summary.get('top_track', {}).get('artist', 'Unknown')}",
                          style={'color': SPOTIFY_GRAY})
                ], style={
                    'backgroundColor': '#181818',
                    'padding': '20px',
                    'borderRadius': '10px'
                })
            ], style={'width': '48%', 'display': 'inline-block'}),

            # Top artist section
            html.Div([
                html.H3("Your Top Artist", style={'color': SPOTIFY_WHITE, 'marginBottom': '15px'}),
                html.Div([
                    html.H4(summary.get('top_artist', {}).get('name', 'Unknown'),
                           style={'color': SPOTIFY_GREEN, 'fontSize': '1.8rem', 'marginBottom': '5px'}),
                    html.P(f"Genres: {summary.get('top_artist', {}).get('genres', 'Unknown')}",
                          style={'color': SPOTIFY_GRAY})
                ], style={
                    'backgroundColor': '#181818',
                    'padding': '20px',
                    'borderRadius': '10px'
                })
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ], style={'marginBottom': '30px'}),

        # Music mood
        html.Div([
            html.H3("Your Music Mood", style={'color': SPOTIFY_WHITE, 'marginBottom': '15px', 'textAlign': 'center'}),
            html.Div([
                html.H4(summary.get('music_mood', {}).get('mood', 'Unknown'),
                       style={'color': SPOTIFY_GREEN, 'fontSize': '2rem', 'textAlign': 'center', 'marginBottom': '15px'}),

                # Mood visualization
                html.Div([
                    html.Div(style={
                        'width': f"{int(summary.get('music_mood', {}).get('valence', 0) * 100)}%",
                        'backgroundColor': SPOTIFY_GREEN,
                        'height': '8px',
                        'borderRadius': '4px'
                    })
                ], style={
                    'width': '100%',
                    'backgroundColor': '#333333',
                    'height': '8px',
                    'borderRadius': '4px',
                    'marginBottom': '10px'
                }),
                html.P("Happiness", style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'marginBottom': '15px'}),

                html.Div([
                    html.Div(style={
                        'width': f"{int(summary.get('music_mood', {}).get('energy', 0) * 100)}%",
                        'backgroundColor': SPOTIFY_GREEN,
                        'height': '8px',
                        'borderRadius': '4px'
                    })
                ], style={
                    'width': '100%',
                    'backgroundColor': '#333333',
                    'height': '8px',
                    'borderRadius': '4px',
                    'marginBottom': '10px'
                }),
                html.P("Energy", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
            ], style={
                'backgroundColor': '#181818',
                'padding': '20px',
                'borderRadius': '10px'
            })
        ], style={'marginBottom': '30px'}),

        # Genre highlight
        html.Div([
            html.H3("Your Top Genre", style={'color': SPOTIFY_WHITE, 'marginBottom': '15px', 'textAlign': 'center'}),
            html.Div([
                html.H4(summary.get('genre_highlight', {}).get('name', 'Unknown'),
                       style={'color': SPOTIFY_GREEN, 'fontSize': '2rem', 'textAlign': 'center'})
            ], style={
                'backgroundColor': '#181818',
                'padding': '20px',
                'borderRadius': '10px'
            })
        ])
    ], style={
        'padding': '30px',
        'borderRadius': '10px',
        'backgroundColor': '#121212',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
        'margin': '20px 0'
    })

# Update stat cards
@app.callback(
    [
        Output('total-minutes-stat', 'children'),
        Output('unique-artists-stat', 'children'),
        Output('unique-tracks-stat', 'children'),
        Output('playlist-count-stat', 'children')
    ],
    Input('interval-component', 'n_intervals')
)
def update_stat_cards(n_intervals):
    """Update the stat cards with user statistics."""
    user_data = spotify_api.get_user_profile()
    if not user_data:
        return create_empty_stats()

    # Get stats from database first
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    # Calculate total minutes from database
    cursor.execute('''
        SELECT SUM(t.duration_ms) / 60000 as total_minutes,
               COUNT(DISTINCT t.artist) as unique_artists,
               COUNT(DISTINCT h.track_id) as unique_tracks
        FROM listening_history h
        JOIN tracks t ON h.track_id = t.track_id
        WHERE h.user_id = ?
    ''', (user_data['id'],))

    db_stats = cursor.fetchone()
    conn.close()

    # Fallback to CSV data if database is empty
    total_minutes = int(db_stats[0] or 0) if db_stats[0] else 0
    unique_artists = db_stats[1] or 0
    unique_tracks = db_stats[2] or 0

    if total_minutes == 0:
        # Fallback to CSV data
        recently_played_df = data_processor.load_data('recently_played.csv')
        if not recently_played_df.empty and 'duration_ms' in recently_played_df.columns:
            total_minutes = int(recently_played_df['duration_ms'].sum() / 60000)

    # Get playlist count from Spotify API directly
    playlists_data = spotify_api.get_playlists()
    playlist_count = len(playlists_data) if playlists_data else 0

    # Create stat cards
    from modules.visualizations import create_stat_card

    total_minutes_card = create_stat_card(
        "Minutes Listened",
        f"{total_minutes:,}",
        icon="fa-clock",
        color=SPOTIFY_GREEN
    )

    unique_artists_card = create_stat_card(
        "Unique Artists",
        str(unique_artists),
        icon="fa-user",
        color="#1ED760"
    )

    unique_tracks_card = create_stat_card(
        "Unique Tracks",
        str(unique_tracks),
        icon="fa-music",
        color="#2D46B9"
    )

    playlist_count_card = create_stat_card(
        "Your Playlists",
        str(playlist_count),
        icon="fa-list",
        color="#F037A5"
    )

    return total_minutes_card, unique_artists_card, unique_tracks_card, playlist_count_card

def create_empty_stats():
    """Create empty stat cards when no user data is available."""
    from modules.visualizations import create_stat_card
    return [
        create_stat_card("Minutes Listened", "0", icon="fa-clock", color=SPOTIFY_GREEN),
        create_stat_card("Unique Artists", "0", icon="fa-user", color="#1ED760"),
        create_stat_card("Unique Tracks", "0", icon="fa-music", color="#2D46B9"),
        create_stat_card("Your Playlists", "0", icon="fa-list", color="#F037A5")
    ]

def generate_wrapped_summary_from_db():
    """Generate a Spotify Wrapped style summary using database data."""
    user_data = spotify_api.get_user_profile()
    if not user_data:
        return {}

    summary = {
        'timestamp': datetime.now().isoformat(),
        'top_track': None,
        'top_artist': None,
        'total_minutes': 0,
        'music_mood': None,
        'genre_highlight': None
    }

    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get top track
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            COUNT(h.history_id) as play_count
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        GROUP BY t.track_id
        ORDER BY play_count DESC
        LIMIT 1
    ''')

    top_track_row = cursor.fetchone()
    if top_track_row:
        top_track = dict(top_track_row)
        summary['top_track'] = {
            'name': top_track['track'],
            'artist': top_track['artist']
        }
    else:
        # Default top track if none found
        summary['top_track'] = {
            'name': 'Start listening to discover your top track',
            'artist': 'Unknown'
        }

    # Get top artist
    cursor.execute('''
        SELECT
            t.artist as artist,
            COUNT(h.history_id) as play_count
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        GROUP BY t.artist
        ORDER BY play_count DESC
        LIMIT 1
    ''')

    top_artist_row = cursor.fetchone()
    if top_artist_row:
        top_artist = dict(top_artist_row)

        # Get genres for this artist from the dedicated genres table
        cursor.execute('''
            SELECT
                genre_name as genre
            FROM genres
            WHERE artist_name = ?
            GROUP BY genre_name
            ORDER BY count DESC
            LIMIT 5
        ''', (top_artist['artist'],))

        genres = [dict(row)['genre'] for row in cursor.fetchall()]

        summary['top_artist'] = {
            'name': top_artist['artist'],
            'genres': ', '.join(genres) if genres else 'Exploring genres'
        }
    else:
        # Default top artist if none found
        summary['top_artist'] = {
            'name': 'Start listening to discover your top artist',
            'genres': 'Exploring genres'
        }

    # Get audio features for mood
    cursor.execute('''
        SELECT
            AVG(t.danceability) as avg_danceability,
            AVG(t.energy) as avg_energy,
            AVG(t.valence) as avg_valence
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE t.danceability IS NOT NULL
    ''')

    audio_features_row = cursor.fetchone()
    if audio_features_row:
        features = dict(audio_features_row)
        avg_valence = features.get('avg_valence', 0) or 0
        avg_energy = features.get('avg_energy', 0) or 0

        # Determine mood quadrant
        if avg_valence > 0.5 and avg_energy > 0.5:
            mood = "Happy & Energetic"
        elif avg_valence > 0.5 and avg_energy <= 0.5:
            mood = "Peaceful & Positive"
        elif avg_valence <= 0.5 and avg_energy > 0.5:
            mood = "Angry & Intense"
        else:
            mood = "Sad & Chill"

        summary['music_mood'] = {
            'mood': mood,
            'valence': avg_valence,
            'energy': avg_energy
        }
    else:
        # Default mood if no audio features found
        summary['music_mood'] = {
            'mood': "Discovering Your Sound",
            'valence': 0.5,
            'energy': 0.5
        }

    # Get top genre from the dedicated genres table
    cursor.execute('''
        SELECT
            genre_name as genre,
            SUM(count) as count
        FROM genres
        GROUP BY genre_name
        ORDER BY count DESC
        LIMIT 1
    ''')

    top_genre_row = cursor.fetchone()
    if top_genre_row:
        top_genre = dict(top_genre_row)
        summary['genre_highlight'] = {
            'name': top_genre['genre'],
            'count': top_genre['count']
        }
    else:
        # Default genre highlight if none found
        summary['genre_highlight'] = {
            'name': 'Exploring New Genres',
            'count': 0
        }

    conn.close()

    # Save summary to JSON
    with open(os.path.join('data', 'wrapped_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    return summary

# Error handling callback
@app.callback(
    Output('error-message', 'children'),
    Output('error-message', 'style'),
    Input('interval-component', 'n_intervals')
)
def update_error_message(n_intervals):
    """Update error message if API connection fails."""
    if spotify_api.sp is None:
        error_style = {
            'color': '#FF5555',
            'textAlign': 'center',
            'margin': '10px',
            'padding': '10px',
            'backgroundColor': '#2A0A0A',
            'borderRadius': '5px',
            'display': 'block'
        }
        return [
            "Error connecting to Spotify API. Please check your credentials and internet connection.",
            html.Br(),
            "The dashboard will display limited data until connection is restored."
        ], error_style

    # No error, hide the message
    error_style = {
        'display': 'none'
    }
    return "", error_style

# New callback for data collection status
@app.callback(
    Output('collection-status', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_collection_status(n_intervals):
    """Update the collection status display."""
    user_data = spotify_api.get_user_profile()
    if not user_data:
        return html.Div("Please log in to see your data", className="alert alert-info")

    # Get collection status from database
    status = db.get_collection_status(user_data['id'])
    if not status:
        return html.Div("Starting data collection...", className="alert alert-info")

    # Get track count
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as track_count
        FROM listening_history
        WHERE user_id = ?
    ''', (user_data['id'],))
    track_count = cursor.fetchone()[0]
    conn.close()

    # Calculate collection period
    if status['earliest_known'] and status['latest_known']:
        earliest = datetime.fromisoformat(status['earliest_known'])
        latest = datetime.fromisoformat(status['latest_known'])
        days = (latest - earliest).days

        return html.Div([
            html.P([
                f"Collected {track_count} tracks over {days} days. ",
                html.Small("Data collection is running in the background.")
            ], className="alert alert-success mb-0")
        ])

    return html.Div("Data collection in progress...", className="alert alert-info")

# Main entry point
if __name__ == '__main__':
    # Initial data fetch
    try:
        # Fetch user profile
        user_data = spotify_api.get_user_profile()
        if user_data:
            data_processor.save_data([user_data], 'user_profile.csv')

        # Fetch top tracks
        top_tracks_data = spotify_api.get_top_tracks(limit=50)
        data_processor.process_top_tracks(top_tracks_data)

        # Fetch saved tracks
        saved_tracks_data = spotify_api.get_saved_tracks(limit=50)
        data_processor.process_saved_tracks(saved_tracks_data)

        # Fetch playlists
        playlists_data = spotify_api.get_playlists(limit=20)
        data_processor.save_data(playlists_data, 'playlists.csv')

        # Fetch audio features
        audio_features_data = spotify_api.get_audio_features_for_top_tracks(limit=50)
        data_processor.process_audio_features(audio_features_data)

        # Fetch top artists
        top_artists_data = spotify_api.get_top_artists(limit=20)
        data_processor.process_top_artists(top_artists_data)

        # Fetch recently played - respect the 50 track limit
        recently_played_data = spotify_api.get_recently_played(limit=50)
        data_processor.process_recently_played(recently_played_data)

        # Fetch top albums (new)
        top_albums_data = get_top_albums(spotify_api, limit=10)
        data_processor.save_data(top_albums_data.to_dict('records'), 'top_albums.csv')

        # Get album listening patterns (new)
        album_patterns = get_album_listening_patterns(spotify_api)
        data_processor.save_data([album_patterns], 'album_patterns.csv')

        # Generate personality analysis (new)
        personality_data = personality_analyzer.analyze()
        data_processor.save_data([personality_data], 'personality.csv')

        # Get DJ mode stats (new) - respect the 50 track limit
        recently_played = spotify_api.get_recently_played(limit=50)
        dj_stats = personality_analyzer._estimate_dj_mode_usage(recently_played)
        data_processor.save_data([dj_stats], 'dj_stats.csv')

        # Generate wrapped summary
        data_processor.generate_spotify_wrapped_summary()

        print("Initial data fetch completed successfully")
    except Exception as e:
        print(f"Error during initial data fetch: {e}")
        print("The dashboard will start with empty or cached data")

    def background_data_collector():
        """Background thread to periodically collect data."""
        while True:
            try:
                # Get current user
                user_data = spotify_api.get_user_profile()
                if user_data:
                    # Update database with latest data
                    data_collector.collect_historical_data(
                        user_data['id'],
                        datetime.now() - timedelta(hours=24)  # Last 24 hours
                    )

                # Wait for 30 minutes before next collection
                time.sleep(1800)

            except Exception as e:
                print(f"Error in background collector: {e}")
                time.sleep(300)  # Wait 5 minutes on error

    # Start background collector thread
    import threading
    collector_thread = threading.Thread(target=background_data_collector, daemon=True)
    collector_thread.start()

    # Run the app
    app.run(debug=True)
