import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
import pandas as pd
import time
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
            
            # Start historical data collection from Jan 1, 2025
            start_date = datetime(2025, 1, 1)
            data_collector.collect_historical_data(user_data['id'], start_date)
            
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
            db.save_track(current_track)
            db.save_listening_history(
                user_id=current_track['user_id'],
                track_id=current_track['id'],
                played_at=datetime.now().isoformat(),
                source='current'
            )
        
        return current_track
    return {}

# Update current track display
@app.callback(
    Output('current-track-container', 'children'),
    Input('current-track-store', 'data')
)
def update_current_track_display(current_track):
    """Update the currently playing track display."""
    if not current_track or 'track' not in current_track:
        return html.Div([
            html.H3("Not Currently Playing", style={'color': SPOTIFY_WHITE, 'textAlign': 'center'}),
            html.P("Play something on Spotify to see it here", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
        ])
    
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
        top_tracks_data = spotify_api.get_top_tracks(limit=10)
        data_processor.process_top_tracks(top_tracks_data)
    
    # Load data from file
    top_tracks_df = data_processor.load_data('top_tracks.csv')
    
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
        saved_tracks_data = spotify_api.get_saved_tracks(limit=10)
        data_processor.process_saved_tracks(saved_tracks_data)
    
    # Load data from file
    saved_tracks_df = data_processor.load_data('saved_tracks.csv')
    
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
        audio_features_data = spotify_api.get_audio_features_for_top_tracks(limit=5)
        data_processor.process_audio_features(audio_features_data)
    
    # Load data from file
    audio_features_df = data_processor.load_data('audio_features.csv')
    
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
        top_artists_data = spotify_api.get_top_artists(limit=10)
        data_processor.process_top_artists(top_artists_data)
    
    # Load data from file
    top_artists_df = data_processor.load_data('top_artists.csv')
    
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
            print("Fetching new top artists data for genre analysis...")
            top_artists_data = spotify_api.get_top_artists(limit=20)
            print(f"Retrieved {len(top_artists_data) if top_artists_data else 0} top artists")
            
            # Debug the top artists data
            if top_artists_data:
                for i, artist in enumerate(top_artists_data[:3]):  # Show first 3 for brevity
                    print(f"Artist {i+1}: {artist.get('name', 'Unknown')}")
                    print(f"  Genres: {artist.get('genres', [])}")
            else:
                print("WARNING: No top artists data retrieved from API")
            
            # Process the data
            print("Processing top artists data...")
            data_processor.process_top_artists(top_artists_data)
            print("Top artists data processed")
        
        # Load data from file
        print("Loading genre analysis data from file...")
        genre_df = data_processor.load_data('genre_analysis.csv')
        
        # Debug the loaded data
        print(f"Genre data loaded: {not genre_df.empty}")
        if not genre_df.empty:
            print(f"Genre columns: {genre_df.columns.tolist()}")
            print(f"Genre data rows: {len(genre_df)}")
            print(f"Genre data sample: {genre_df.head(3).to_dict('records')}")
        else:
            print("WARNING: Genre dataframe is empty!")
            
            # Check if the file exists
            import os
            if os.path.exists('data/genre_analysis.csv'):
                print("File exists but might be empty or corrupted")
                # Try to read raw file content
                with open('data/genre_analysis.csv', 'r') as f:
                    content = f.read()
                print(f"Raw file content (first 200 chars): {content[:200]}")
            else:
                print("File does not exist!")
                
                # Check if we need to create the genre data
                print("Attempting to create genre data...")
                # Get top artists
                top_artists_data = spotify_api.get_top_artists(limit=20)
                if top_artists_data:
                    # Extract genres
                    all_genres = []
                    for artist in top_artists_data:
                        genres = artist.get('genres', [])
                        for genre in genres:
                            all_genres.append(genre)
                    
                    # Count genres
                    from collections import Counter
                    genre_counts = Counter(all_genres)
                    
                    # Create dataframe
                    import pandas as pd
                    genre_df = pd.DataFrame({
                        'genre': list(genre_counts.keys()),
                        'count': list(genre_counts.values())
                    })
                    
                    # Save to file
                    genre_df.to_csv('data/genre_analysis.csv', index=False)
                    print(f"Created genre data with {len(genre_df)} genres")
        
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
    
    # Try database first
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            strftime('%w', played_at) as day_of_week,
            strftime('%H', played_at) as hour_of_day,
            COUNT(*) as play_count
        FROM listening_history
        WHERE user_id = ?
        AND played_at >= datetime('now', '-7 days')
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
    
    # Fallback to CSV data
    recently_played_df = data_processor.load_data('recently_played.csv')
    return visualizations.create_listening_patterns_heatmap(recently_played_df)

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
        cursor.execute('''
            WITH album_plays AS (
                SELECT 
                    t.album,
                    COUNT(*) as play_count,
                    COUNT(DISTINCT t.track_id) as unique_tracks,
                    SUM(CASE 
                        WHEN LAG(t.album) OVER (ORDER BY h.played_at) = t.album THEN 1 
                        ELSE 0 
                    END) as sequential_plays
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.user_id = ?
                GROUP BY t.album
            )
            SELECT 
                COUNT(CASE WHEN unique_tracks > 1 THEN 1 END) * 100.0 / COUNT(*) as album_completion_rate,
                SUM(sequential_plays) * 100.0 / SUM(play_count) as sequential_listening_score
            FROM album_plays
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
        summary = data_processor.generate_spotify_wrapped_summary()
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
        # Load data from files
        top_artists_df = data_processor.load_data('top_artists.csv')
        audio_features_df = data_processor.load_data('audio_features.csv')
        recently_played_df = data_processor.load_data('recently_played.csv')
        
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
    if not summary:
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
            "The dashboard will display sample data until connection is restored."
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
