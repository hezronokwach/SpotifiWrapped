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
from modules.data_processing import DataProcessor, normalize_timestamp, calculate_duration_minutes
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
    # Check if current_track is None or empty or if is_playing is False
    if not current_track or current_track.get('is_playing') is False:
        return html.Div([
            html.H3("Not Currently Playing", style={'color': SPOTIFY_WHITE, 'textAlign': 'center'}),
            html.P("Play something on Spotify to see it here", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
        ], style={
            'padding': '20px',
            'borderRadius': '10px',
            'backgroundColor': '#121212',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
            'margin': '20px 0',
            'textAlign': 'center'
        })

    # Check if we have the required fields
    if 'track' not in current_track:
        if 'name' in current_track:
            # Use name field instead
            current_track['track'] = current_track['name']
        else:
            return html.Div([
                html.H3("Track Information Unavailable", style={'color': SPOTIFY_WHITE, 'textAlign': 'center'}),
                html.P("Unable to retrieve track details", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
            ], style={
                'padding': '20px',
                'borderRadius': '10px',
                'backgroundColor': '#121212',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
                'margin': '20px 0',
                'textAlign': 'center'
            })

    # Set default values for missing fields
    if 'progress_ms' not in current_track:
        current_track['progress_ms'] = 0

    if 'duration_ms' not in current_track:
        current_track['duration_ms'] = 0

    # Calculate progress percentage - handle None values
    if current_track.get('duration_ms') is None:
        current_track['duration_ms'] = 0
    if current_track.get('progress_ms') is None:
        current_track['progress_ms'] = 0

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

    # Query for top tracks based on frequency in listening history - only count actual listening events
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            t.popularity,
            t.image_url,
            COUNT(h.history_id) as play_count,
            (COUNT(h.history_id) * 0.7 + (t.popularity / 100.0) * 0.3) as weighted_score
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
        GROUP BY t.track_id
        HAVING play_count >= 2  -- Minimum 2 plays to be considered
        ORDER BY weighted_score DESC
        LIMIT 10
    ''', (current_date,))

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

# Update saved tracks list
@app.callback(
    Output('saved-tracks-chart', 'children'),
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
                    # Use the improved timestamp normalization
                    timestamp = track.get('added_at')
                    played_at = normalize_timestamp(timestamp)
                    if not played_at:
                        # If normalization fails, use current time
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

    # Query for saved tracks with duration information - prevent duplicates
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            t.image_url,
            t.duration_ms,
            t.popularity,
            MAX(h.played_at) as added_at
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE h.source = 'saved'
        AND t.name IS NOT NULL
        AND t.artist IS NOT NULL
        GROUP BY t.track_id, t.name, t.artist, t.album, t.image_url, t.duration_ms, t.popularity
        ORDER BY added_at DESC
        LIMIT 20
    ''')

    saved_tracks_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Convert to DataFrame and process
    if saved_tracks_data:
        saved_tracks_df = pd.DataFrame(saved_tracks_data)

        # Calculate duration in minutes
        if 'duration_ms' in saved_tracks_df.columns:
            saved_tracks_df['duration_minutes'] = saved_tracks_df['duration_ms'].apply(calculate_duration_minutes)

        # Ensure added_at is properly formatted
        if 'added_at' in saved_tracks_df.columns:
            saved_tracks_df['added_at'] = saved_tracks_df['added_at'].apply(normalize_timestamp)
            saved_tracks_df['added_at'] = pd.to_datetime(saved_tracks_df['added_at'], errors='coerce')
            # Remove rows with invalid timestamps
            saved_tracks_df = saved_tracks_df.dropna(subset=['added_at'])

        print(f"Processed {len(saved_tracks_df)} saved tracks for visualization")
    else:
        # Create empty DataFrame with the right columns
        saved_tracks_df = pd.DataFrame(columns=['track', 'artist', 'album', 'added_at', 'duration_minutes'])

    # Create list visualization
    return visualizations.create_saved_tracks_list(saved_tracks_df)

# Update playlists list
@app.callback(
    Output('playlists-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_playlists_list(n_intervals, n_clicks):
    """Update the playlists fancy list."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        playlists_data = spotify_api.get_playlists(limit=10)
        data_processor.save_data(playlists_data, 'playlists.csv')

    # Load data from file
    playlists_df = data_processor.load_data('playlists.csv')

    # Create visualization - import the standalone function
    from modules.visualizations import create_playlists_fancy_list
    return create_playlists_fancy_list(playlists_df)

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

    # Query for top tracks using the same improved ranking system
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            COUNT(h.history_id) as play_count,
            (COUNT(h.history_id) * 0.7 + (t.popularity / 100.0) * 0.3) as weighted_score
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
        AND date(h.played_at) <= ?
        GROUP BY t.track_id
        HAVING play_count >= 2
        ORDER BY weighted_score DESC
        LIMIT 5
    ''', (current_date,))

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

    # Query for top artists - only count actual listening events
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT
            t.artist as artist,
            MAX(t.popularity) as popularity,
            MAX(t.image_url) as image_url,
            COUNT(h.history_id) as play_count,
            (COUNT(h.history_id) * 0.8 + (MAX(t.popularity) / 100.0) * 0.2) as weighted_score
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE t.artist IS NOT NULL AND t.artist != ''
        AND t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
        GROUP BY t.artist
        HAVING play_count >= 2  -- Minimum 2 plays to be considered
        ORDER BY weighted_score DESC
        LIMIT 10
    ''', (current_date,))

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

# Update top track highlight
@app.callback(
    Output('top-track-highlight-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_track_highlight(n_intervals, n_clicks):
    """Update the top track highlight card."""
    try:
        # Get top track from database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT t.name as track_name, t.artist as artist_name, t.album as album_name,
                   t.popularity, t.image_url, COUNT(h.history_id) as play_count
            FROM tracks t
            JOIN listening_history h ON t.track_id = h.track_id
            WHERE t.name IS NOT NULL AND t.name != ''
            AND t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
            GROUP BY t.track_id, t.name, t.artist, t.album, t.popularity, t.image_url
            ORDER BY play_count DESC, t.popularity DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        conn.close()

        if result:
            track_data = {
                'track': result[0],      # track_name
                'artist': result[1],     # artist_name
                'album': result[2] or 'Unknown Album',  # album_name
                'popularity': result[3] or 0,           # popularity
                'image_url': result[4] or '',           # image_url
                'play_count': result[5]                 # play_count
            }
            return visualizations.create_top_track_highlight_component(track_data)
        else:
            return html.Div([
                html.H3("Your #1 Track", style={'color': SPOTIFY_GREEN, 'textAlign': 'center'}),
                html.P("Start listening to discover your top track!", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
            ], style={'padding': '20px'})

    except Exception as e:
        print(f"Error updating top track highlight: {e}")
        return html.Div("Error loading top track", style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

# Update top artist highlight
@app.callback(
    Output('top-artist-highlight-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_artist_highlight(n_intervals, n_clicks):
    """Update the top artist highlight card."""
    try:
        # Get top artist from database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT t.artist as artist_name, COUNT(h.history_id) as play_count,
                   AVG(t.popularity) as avg_popularity, MAX(t.image_url) as image_url
            FROM tracks t
            JOIN listening_history h ON t.track_id = h.track_id
            WHERE t.artist IS NOT NULL AND t.artist != ''
            AND t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
            GROUP BY t.artist
            ORDER BY play_count DESC, avg_popularity DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        conn.close()

        if result:
            artist_data = {
                'artist': result[0],
                'play_count': result[1],
                'popularity': int(result[2]) if result[2] else 0,
                'image_url': result[3] or ''
            }
            return visualizations.create_top_artist_highlight_component(artist_data)
        else:
            return html.Div([
                html.H3("Your Top Artist", style={'color': SPOTIFY_GREEN, 'textAlign': 'center'}),
                html.P("Start listening to discover your top artist!", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
            ], style={'padding': '20px'})

    except Exception as e:
        print(f"Error updating top artist highlight: {e}")
        return html.Div("Error loading top artist", style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

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
                # We'll make up to 4 calls to get up to 200 tracks with better error handling
                max_batches = 4
                successful_batches = 0

                for i in range(max_batches):
                    try:
                        print(f"Fetching batch {i+1}/{max_batches}...")

                        # Get recently played tracks with retry logic
                        tracks = spotify_api.get_recently_played(limit=50, before=before_timestamp)

                        if not tracks or len(tracks) == 0:
                            print("No more tracks available")
                            break

                        print(f"Retrieved {len(tracks)} tracks in batch {i+1}")
                        all_tracks.extend(tracks)
                        successful_batches += 1

                        # Save tracks to database
                        for track in tracks:
                            db.save_track(track)

                            # Normalize the timestamp
                            played_at = normalize_timestamp(track.get('played_at'))
                            if not played_at:
                                # If normalization fails, use current time
                                played_at = datetime.now().replace(microsecond=0).isoformat()

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
                                # Use normalize_timestamp to parse consistently
                                normalized_timestamp = normalize_timestamp(played_at)
                                if normalized_timestamp:
                                    dt = datetime.fromisoformat(normalized_timestamp)
                                    # Convert to timestamp for the next request
                                    # Subtract 1 millisecond to avoid getting the same track again
                                    before_timestamp = int(dt.timestamp() * 1000) - 1
                                    print(f"Next request will fetch tracks before {dt}")
                                else:
                                    print(f"Failed to normalize timestamp: {played_at}")
                                    break
                            except ValueError as e:
                                print(f"Error parsing timestamp: {e}")
                                break
                        else:
                            print("Last track has no played_at timestamp")
                            break

                        # Progressive delay to avoid rate limiting
                        if i == 0:
                            time.sleep(1)  # Short delay after first batch
                        elif i == 1:
                            time.sleep(2)  # Longer delay after second batch
                        else:
                            time.sleep(3)  # Even longer delay for subsequent batches

                    except Exception as e:
                        print(f"Error fetching recently played tracks in batch {i+1}: {e}")

                        # Check if it's a rate limit error
                        if "429" in str(e) or "rate limit" in str(e).lower():
                            print("Rate limit detected, waiting longer before retry...")
                            time.sleep(10)  # Wait 10 seconds for rate limit

                            # Try one more time for this batch
                            try:
                                tracks = spotify_api.get_recently_played(limit=50, before=before_timestamp)
                                if tracks:
                                    print(f"Retry successful for batch {i+1}, retrieved {len(tracks)} tracks")
                                    all_tracks.extend(tracks)
                                    successful_batches += 1

                                    # Process tracks as before...
                                    for track in tracks:
                                        db.save_track(track)
                                        played_at = normalize_timestamp(track.get('played_at'))
                                        if not played_at:
                                            played_at = datetime.now().replace(microsecond=0).isoformat()
                                        db.save_listening_history(
                                            user_id=user_data['id'],
                                            track_id=track['id'],
                                            played_at=played_at,
                                            source='played'
                                        )

                                    # Update timestamp for next request
                                    last_track = tracks[-1]
                                    played_at = last_track.get('played_at')
                                    if played_at:
                                        normalized_timestamp = normalize_timestamp(played_at)
                                        if normalized_timestamp:
                                            dt = datetime.fromisoformat(normalized_timestamp)
                                            before_timestamp = int(dt.timestamp() * 1000) - 1
                                else:
                                    print(f"Retry failed for batch {i+1}")
                                    break
                            except Exception as retry_e:
                                print(f"Retry also failed for batch {i+1}: {retry_e}")
                                break
                        else:
                            import traceback
                            traceback.print_exc()
                            break

                print(f"Total tracks fetched: {len(all_tracks)} from {successful_batches}/{max_batches} successful batches")

                # Extract unique artists from the tracks
                artists = set()
                for track in all_tracks:
                    artist_name = track.get('artist')
                    if artist_name:
                        artists.add(artist_name)

                print(f"Found {len(artists)} unique artists in recently played tracks")

                # Process each artist to get their genres with improved rate limiting
                processed_count = 0
                for artist_name in artists:
                    print(f"Processing genres for artist: {artist_name} ({processed_count + 1}/{len(artists)})")

                    # Check if we already have genres for this artist
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM genres WHERE artist_name = ?", (artist_name,))
                    existing_genres = cursor.fetchone()[0]
                    conn.close()

                    if existing_genres > 0:
                        print(f"Already have {existing_genres} genres for artist: {artist_name}")
                        continue

                    # Use our new function to get genres
                    genres = spotify_api.get_artist_genres(artist_name)

                    if genres:
                        print(f"Found {len(genres)} genres for artist {artist_name}: {genres}")

                        # Save each genre to the database
                        for genre in genres:
                            if genre and genre.strip():  # Skip empty or whitespace-only genres
                                success = db.save_genre(genre.strip(), artist_name)
                                if success:
                                    print(f"Successfully saved genre '{genre}' for artist '{artist_name}'")
                                else:
                                    print(f"Failed to save genre '{genre}' to database")
                    else:
                        print(f"No genres found for artist {artist_name}")
                        # Save a placeholder to avoid repeated lookups
                        db.save_genre("unknown", artist_name)

                    processed_count += 1

                    # Improved rate limiting
                    if processed_count % 5 == 0:
                        print(f"Taking a longer break after processing {processed_count} artists...")
                        time.sleep(3)  # Longer break every 5 artists
                    else:
                        time.sleep(1)  # Standard delay

        # Process all artists in the database to ensure we have genres for all of them
        print("Processing genres for all artists in the database...")

        # Get all artists from the database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT artist FROM tracks")
        all_artists = [row[0] for row in cursor.fetchall()]
        conn.close()

        print(f"Found {len(all_artists)} unique artists in the database")

        # Process each artist to get their genres with better batching
        processed_artists = 0
        max_artists_per_session = 50  # Limit processing to avoid long delays

        for artist_name in all_artists[:max_artists_per_session]:  # Limit to first 50 artists
            # Check if we already have genres for this artist
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM genres WHERE artist_name = ?", (artist_name,))
            genre_count = cursor.fetchone()[0]
            conn.close()

            # If we don't have genres for this artist, get them
            if genre_count == 0:
                print(f"Getting genres for artist: {artist_name} ({processed_artists + 1}/{min(len(all_artists), max_artists_per_session)})")

                # Get genres for this artist
                genres = spotify_api.get_artist_genres(artist_name)

                # Save each genre to the database
                if genres:
                    for genre in genres:
                        if genre and genre.strip():  # Skip empty or whitespace-only genres
                            success = db.save_genre(genre.strip(), artist_name)
                            if success:
                                print(f"Successfully saved genre '{genre}' for artist '{artist_name}'")
                else:
                    # If no genres found, save a placeholder to avoid repeated lookups
                    print(f"No genres found for artist {artist_name}, saving placeholder")
                    db.save_genre("unknown", artist_name)

                processed_artists += 1

                # Improved rate limiting
                if processed_artists % 10 == 0:
                    print(f"Taking an extended break after processing {processed_artists} artists...")
                    time.sleep(5)  # Extended break every 10 artists
                elif processed_artists % 5 == 0:
                    print(f"Taking a longer break after processing {processed_artists} artists...")
                    time.sleep(2)  # Longer break every 5 artists
                else:
                    time.sleep(1)  # Standard delay
            else:
                print(f"Already have {genre_count} genres for artist: {artist_name}")

        if len(all_artists) > max_artists_per_session:
            print(f"Processed {max_artists_per_session} artists this session. {len(all_artists) - max_artists_per_session} remaining for next refresh.")

        # Get user data if not already available
        if 'user_data' not in locals() or user_data is None:
            user_data = spotify_api.get_user_profile()

        # Get genre data from the genres table with categorization
        genre_data = db.get_top_genres(limit=10, exclude_unknown=True, categorize=True)

        # Convert to DataFrame
        if genre_data:
            genre_df = pd.DataFrame(genre_data)
            print(f"Genre data loaded from database: {len(genre_df)} genres")
            print(f"Top genres: {genre_df['genre'].tolist()}")
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

    # First, clean up any problematic data in the database
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        # 1. Update any future timestamps to current time
        cursor.execute('''
            UPDATE listening_history
            SET played_at = datetime('now')
            WHERE date(played_at) > ?
        ''', (current_date,))

        if cursor.rowcount > 0:
            print(f"Fixed {cursor.rowcount} future timestamps in the database")

        # 2. Remove duplicate entries with the same timestamp and track_id
        # First identify duplicates
        cursor.execute('''
            WITH duplicates AS (
                SELECT history_id, user_id, track_id, played_at, source,
                       ROW_NUMBER() OVER (PARTITION BY user_id, track_id, played_at ORDER BY history_id) as row_num
                FROM listening_history
                WHERE user_id = ?
            )
            DELETE FROM listening_history
            WHERE history_id IN (
                SELECT history_id FROM duplicates WHERE row_num > 1
            )
        ''', (user_data['id'],))

        if cursor.rowcount > 0:
            print(f"Removed {cursor.rowcount} duplicate entries from the database")

        conn.commit()
    except Exception as e:
        print(f"Error cleaning up database: {e}")
    finally:
        conn.close()

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for listening patterns with proper filtering
    # Only include actual listening events (not top tracks) and ensure dates are valid
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Use localtime for user-friendly display
    # SQLite datetime() function with 'localtime' modifier automatically adjusts to local timezone
    print(f"TIMEZONE DEBUG: Current local time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"TIMEZONE DEBUG: Current UTC time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

    cursor.execute('''
        SELECT
            strftime('%w', datetime(played_at, 'localtime')) as day_of_week,
            strftime('%H', datetime(played_at, 'localtime')) as hour_of_day,
            COUNT(*) as play_count,
            SUM(CASE WHEN t.duration_ms IS NOT NULL THEN t.duration_ms ELSE 0 END) as total_duration_ms
        FROM listening_history h
        JOIN tracks t ON h.track_id = t.track_id
        WHERE h.user_id = ?
        AND h.played_at IS NOT NULL
        AND h.source IN ('played', 'recently_played', 'current')  -- Only include actual listening events
        AND datetime(h.played_at) <= datetime('now')  -- Ensure dates are not in the future
        AND datetime(h.played_at) >= datetime('now', '-7 days')  -- Only last 7 days
        GROUP BY day_of_week, hour_of_day
        ORDER BY day_of_week, hour_of_day
    ''', (user_data['id'],))

    patterns_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if patterns_data:
        # Convert numeric day of week to name and calculate minutes
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        patterns_df = pd.DataFrame(patterns_data)
        patterns_df['day_name'] = patterns_df['day_of_week'].astype(int).map(lambda x: day_names[x])

        # Calculate minutes played
        patterns_df['minutes_played'] = patterns_df['total_duration_ms'].apply(calculate_duration_minutes)

        print(f"Listening patterns data: {len(patterns_df)} time slots with total {patterns_df['minutes_played'].sum():.1f} minutes")
        return visualizations.create_listening_patterns_heatmap(patterns_df, date_range_days=7)

    # If no data in database, try to fetch recent data from API and save to database
    recently_played = spotify_api.get_recently_played(limit=50)
    if recently_played and user_data:
        # Save to database
        for track in recently_played:
            db.save_track(track)
            # Normalize the timestamp using our utility function
            played_at = normalize_timestamp(track.get('played_at'))
            if not played_at:
                # If normalization fails, use current time
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

        print(f"TIMEZONE DEBUG (retry): Current local time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"TIMEZONE DEBUG (retry): Current UTC time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

        cursor.execute('''
            SELECT
                strftime('%w', datetime(played_at, 'localtime')) as day_of_week,
                strftime('%H', datetime(played_at, 'localtime')) as hour_of_day,
                COUNT(*) as play_count,
                SUM(CASE WHEN t.duration_ms IS NOT NULL THEN t.duration_ms ELSE 0 END) as total_duration_ms
            FROM listening_history h
            JOIN tracks t ON h.track_id = t.track_id
            WHERE h.user_id = ?
            AND h.played_at IS NOT NULL
            AND h.source IN ('played', 'recently_played', 'current')  -- Only include actual listening events
            AND datetime(h.played_at) <= datetime('now')  -- Ensure dates are not in the future
            AND datetime(h.played_at) >= datetime('now', '-7 days')  -- Only last 7 days
            GROUP BY day_of_week, hour_of_day
            ORDER BY day_of_week, hour_of_day
        ''', (user_data['id'],))

        patterns_data = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if patterns_data:
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            patterns_df = pd.DataFrame(patterns_data)
            patterns_df['day_name'] = patterns_df['day_of_week'].astype(int).map(lambda x: day_names[x])

            # Calculate minutes played
            patterns_df['minutes_played'] = patterns_df['total_duration_ms'].apply(calculate_duration_minutes)

            print(f"Listening patterns data (retry): {len(patterns_df)} time slots with total {patterns_df['minutes_played'].sum():.1f} minutes")
            return visualizations.create_listening_patterns_heatmap(patterns_df, date_range_days=7)

    # Create empty DataFrame with the right columns
    patterns_df = pd.DataFrame(columns=['day_of_week', 'hour_of_day', 'play_count', 'day_name'])
    return visualizations.create_listening_patterns_heatmap(patterns_df, date_range_days=7)

# New callback for top albums section
@app.callback(
    Output('top-albums-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_albums(n_intervals, n_clicks):
    """Update the top albums section."""
    try:
        # Get user data first to ensure we have a valid user
        user_data = spotify_api.get_user_profile()
        if not user_data:
            return html.Div("Log in to see your top albums",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        # Fetch new data if refresh button clicked
        if n_clicks is not None and n_clicks > 0:
            top_albums_data = get_top_albums(spotify_api, limit=10)
            data_processor.save_data(top_albums_data.to_dict('records'), 'top_albums.csv')

        # Load data from file
        top_albums_df = data_processor.load_data('top_albums.csv')

        if top_albums_df.empty:
            # Try to get fresh data if CSV is empty
            top_albums_data = get_top_albums(spotify_api, limit=10)
            if not top_albums_data.empty:
                data_processor.save_data(top_albums_data.to_dict('records'), 'top_albums.csv')
                top_albums_df = top_albums_data
            else:
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
                CASE WHEN COUNT(*) > 0
                     THEN COUNT(CASE WHEN track_count > 1 THEN 1 END) * 100.0 / COUNT(*)
                     ELSE 0 END as album_completion_rate,
                CASE WHEN COUNT(*) > 0 THEN 50.0 ELSE 0 END as sequential_listening_score
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

            # Recommendations - Side by Side Layout
            html.Div([
                html.H3("🎯 Personalized Recommendations",
                    style={
                        'color': SPOTIFY_WHITE,
                        'textAlign': 'center',
                        'marginBottom': '20px',
                        'fontSize': '1.5rem'
                    }
                ),
                html.Div([
                    # Left column
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-lightbulb",
                                style={
                                    'color': SPOTIFY_GREEN,
                                    'fontSize': '1rem',
                                    'marginRight': '8px'
                                }
                            ),
                            html.Span(recommendation, style={'fontSize': '0.9rem'})
                        ], style={
                            'color': SPOTIFY_WHITE,
                            'backgroundColor': '#1a1a1a',
                            'padding': '15px',
                            'borderRadius': '8px',
                            'marginBottom': '10px',
                            'border': f'1px solid {["#1DB954", "#FF6B35", "#1E90FF", "#FFD700", "#FF69B4"][i % 5]}',
                            'display': 'flex',
                            'alignItems': 'flex-start'
                        }) for i, recommendation in enumerate(personality_data.get('recommendations', [])[::2])  # Even indices
                    ], className="col-md-6"),

                    # Right column
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-lightbulb",
                                style={
                                    'color': SPOTIFY_GREEN,
                                    'fontSize': '1rem',
                                    'marginRight': '8px'
                                }
                            ),
                            html.Span(recommendation, style={'fontSize': '0.9rem'})
                        ], style={
                            'color': SPOTIFY_WHITE,
                            'backgroundColor': '#1a1a1a',
                            'padding': '15px',
                            'borderRadius': '8px',
                            'marginBottom': '10px',
                            'border': f'1px solid {["#1DB954", "#FF6B35", "#1E90FF", "#FFD700", "#FF69B4"][(i*2+1) % 5]}',
                            'display': 'flex',
                            'alignItems': 'flex-start'
                        }) for i, recommendation in enumerate(personality_data.get('recommendations', [])[1::2])  # Odd indices
                    ], className="col-md-6")
                ], className="row")
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
        user_data = spotify_api.get_user_profile()
        if not user_data:
            return html.Div("Log in to see your DJ mode statistics",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        # Get data from database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Calculate DJ mode usage based on track data - only count actual listening events
        current_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT
                COUNT(*) as total_tracks,
                SUM(t.duration_ms) / 60000 as total_minutes
            FROM listening_history h
            JOIN tracks t ON h.track_id = t.track_id
            WHERE h.user_id = ?
            AND h.source NOT LIKE 'top_%'  -- Exclude top tracks data
            AND date(h.played_at) <= ?     -- Ensure dates are not in the future
        ''', (user_data['id'], current_date))

        result = cursor.fetchone()
        conn.close()

        if result and result[0] > 0:
            total_tracks = result[0]
            total_minutes = result[1] or 0

            # Spotify DJ is a premium-only feature, so we need to check if the user is premium
            # Try to get the user's subscription status from the Spotify API
            is_premium = False  # Default to not premium

            # Try to get the user's subscription type from the API
            try:
                user_profile = spotify_api.sp.current_user()
                product_type = user_profile.get('product', 'free')
                is_premium = product_type == 'premium'
                print(f"DEBUG: User subscription type: {product_type}, is_premium: {is_premium}")
            except Exception as e:
                print(f"DEBUG: Error getting user subscription type: {e}")
                is_premium = False

            # If the user is premium, calculate DJ mode usage
            if is_premium:
                # Estimate DJ mode usage (simplified for limited data)
                estimated_minutes = max(1, int(total_minutes * 0.15))  # Assume 15% of listening is DJ mode
                percentage_of_listening = min(100, max(5, int((estimated_minutes / max(1, total_minutes)) * 100)))
                dj_mode_user = True  # Premium users can use DJ mode
            else:
                # For non-premium users, set default values
                estimated_minutes = 0
                percentage_of_listening = 0
                dj_mode_user = False  # Not a DJ mode user since it's premium-only

            dj_stats = {
                'estimated_minutes': estimated_minutes,
                'percentage_of_listening': percentage_of_listening,
                'dj_mode_user': dj_mode_user,
                'is_premium': is_premium
            }
        else:
            # Default values for very limited data
            # Try to get the user's subscription type from the API
            is_premium = False
            try:
                user_profile = spotify_api.sp.current_user()
                product_type = user_profile.get('product', 'free')
                is_premium = product_type == 'premium'
                print(f"DEBUG: User subscription type (no data): {product_type}, is_premium: {is_premium}")
            except Exception as e:
                print(f"DEBUG: Error getting user subscription type (no data): {e}")
                is_premium = False

            dj_stats = {
                'estimated_minutes': 5 if is_premium else 0,
                'percentage_of_listening': 10 if is_premium else 0,
                'dj_mode_user': is_premium,  # Only premium users can use DJ mode
                'is_premium': is_premium
            }

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
                "Active User" if dj_stats.get('dj_mode_user', False) else ("Not Available" if not dj_stats.get('is_premium', False) else "Occasional User"),
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
    """Generate and store Spotify Wrapped style summary using only database data."""
    try:
        # Generate summary from database
        if n_clicks is not None and n_clicks > 0:
            return generate_wrapped_summary_from_db()

        # For non-refresh updates, still use database
        return generate_wrapped_summary_from_db()
    except Exception as e:
        print(f"Error updating wrapped summary: {e}")
        return {}



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

    # Create visualizations instance to use the new components
    vis = visualizations

    # Create the enhanced wrapped summary component
    wrapped_summary = vis.create_wrapped_summary_component(summary)

    # Return only the wrapped summary component
    return wrapped_summary

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

    # Calculate total minutes from database - only count actual listening events
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT SUM(t.duration_ms) / 60000 as total_minutes,
               COUNT(DISTINCT t.artist) as unique_artists,
               COUNT(DISTINCT h.track_id) as unique_tracks
        FROM listening_history h
        JOIN tracks t ON h.track_id = t.track_id
        WHERE h.user_id = ?
        AND h.source NOT LIKE 'top_%'  -- Exclude top tracks data
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
    ''', (user_data['id'], current_date))

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

    # Get top track - only count actual listening events
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            COUNT(h.history_id) as play_count
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
        AND h.source NOT LIKE 'top_%'  -- Exclude top tracks data
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
        GROUP BY t.track_id
        ORDER BY play_count DESC
        LIMIT 1
    ''', (current_date,))

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

    # Get top artist - only count actual listening events
    cursor.execute('''
        SELECT
            t.artist as artist,
            COUNT(h.history_id) as play_count
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE t.artist IS NOT NULL AND t.artist != ''
        AND h.source NOT LIKE 'top_%'  -- Exclude top tracks data
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
        GROUP BY t.artist
        ORDER BY play_count DESC
        LIMIT 1
    ''', (current_date,))

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

    # Get audio features for mood - handle case with limited data
    cursor.execute('''
        SELECT
            AVG(CASE WHEN t.danceability IS NULL THEN 0.5 ELSE t.danceability END) as avg_danceability,
            AVG(CASE WHEN t.energy IS NULL THEN 0.5 ELSE t.energy END) as avg_energy,
            AVG(CASE WHEN t.valence IS NULL THEN 0.5 ELSE t.valence END) as avg_valence,
            AVG(CASE WHEN t.tempo IS NULL THEN 120 ELSE t.tempo END) as avg_tempo,
            COUNT(*) as track_count
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE h.source NOT LIKE 'top_%'  -- Exclude top tracks data
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
    ''', (current_date,))

    audio_features_row = cursor.fetchone()
    if audio_features_row and audio_features_row['track_count'] > 0:
        features = dict(audio_features_row)
        avg_valence = features.get('avg_valence', 0.5) or 0.5
        avg_energy = features.get('avg_energy', 0.5) or 0.5
        avg_tempo = features.get('avg_tempo', 120) or 120

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

        # Add tempo to the summary
        summary['tempo'] = avg_tempo
    else:
        # Default mood if no audio features found
        summary['music_mood'] = {
            'mood': "Discovering Your Sound",
            'valence': 0.5,
            'energy': 0.5
        }

    # Get top genre from the dedicated genres table, excluding "unknown" placeholder
    # Since the genres table doesn't have track_id in our schema, we need a different approach
    cursor.execute('''
        SELECT
            genre_name as genre,
            SUM(count) as count
        FROM genres
        WHERE genre_name != 'unknown'
        AND genre_name != ''
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
