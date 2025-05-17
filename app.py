import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
import pandas as pd
import time

# Import custom modules
from modules.api import SpotifyAPI
from modules.data_processing import DataProcessor
from modules.layout import DashboardLayout
from modules.visualizations import (
    SpotifyVisualizations, SpotifyAnimations,
    SPOTIFY_GREEN, SPOTIFY_BLACK, SPOTIFY_WHITE, SPOTIFY_GRAY
)

# Load environment variables
load_dotenv()

# Initialize components
spotify_api = SpotifyAPI()
data_processor = DataProcessor()
dashboard_layout = DashboardLayout()
visualizations = SpotifyVisualizations()
animations = SpotifyAnimations()

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
    user_data = spotify_api.get_user_profile()
    if user_data:
        data_processor.save_data([user_data], 'user_profile.csv')
        return user_data
    return {}

# Update header with user data
@app.callback(
    Output('header-container', 'children'),
    Input('user-data-store', 'data')
)
def update_header(user_data):
    """Update the header with user profile data."""
    return dashboard_layout.create_header(user_data)

# Update current track
@app.callback(
    Output('current-track-store', 'data'),
    Input('interval-component', 'n_intervals')
)
def update_current_track(n_intervals):
    """Fetch and store currently playing track."""
    current_track = spotify_api.get_currently_playing()
    if current_track:
        data_processor.save_data([current_track], 'current_track.csv')
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
    return visualizations.create_saved_tracks_chart(saved_tracks_df)

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
    return visualizations.create_audio_features_chart(audio_features_df)

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
    # Load data from file
    genre_df = data_processor.load_data('genre_analysis.csv')
    
    # Create visualization
    return visualizations.create_genre_chart(genre_df)

# Update listening patterns chart
@app.callback(
    Output('listening-patterns-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_listening_patterns_chart(n_intervals, n_clicks):
    """Update the listening patterns chart."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        recently_played_data = spotify_api.get_recently_played(limit=50)
        data_processor.process_recently_played(recently_played_data)
    
    # Load data from file
    recently_played_df = data_processor.load_data('recently_played.csv')
    
    # Create visualization
    return visualizations.create_listening_patterns_chart(recently_played_df)

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
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_stat_cards(n_intervals, n_clicks):
    """Update the stat cards with user statistics."""
    # Load data
    top_tracks_df = data_processor.load_data('top_tracks.csv')
    recently_played_df = data_processor.load_data('recently_played.csv')
    playlists_df = data_processor.load_data('playlists.csv')
    
    # Calculate stats
    total_minutes = 0
    if not recently_played_df.empty and 'duration_ms' in recently_played_df.columns:
        total_minutes = int(recently_played_df['duration_ms'].sum() / 60000)
    
    unique_artists = 0
    if not top_tracks_df.empty and 'artist' in top_tracks_df.columns:
        unique_artists = len(top_tracks_df['artist'].unique())
    
    unique_tracks = len(top_tracks_df) if not top_tracks_df.empty else 0
    
    playlist_count = len(playlists_df) if not playlists_df.empty else 0
    
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
        "Top Tracks", 
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

# Main entry point
if __name__ == '__main__':
    # Initial data fetch
    try:
        # Fetch user profile
        user_data = spotify_api.get_user_profile()
        if user_data:
            data_processor.save_data([user_data], 'user_profile.csv')
        
        # Fetch top tracks
        top_tracks_data = spotify_api.get_top_tracks(limit=10)
        data_processor.process_top_tracks(top_tracks_data)
        
        # Fetch saved tracks
        saved_tracks_data = spotify_api.get_saved_tracks(limit=10)
        data_processor.process_saved_tracks(saved_tracks_data)
        
        # Fetch playlists
        playlists_data = spotify_api.get_playlists(limit=10)
        data_processor.save_data(playlists_data, 'playlists.csv')
        
        # Fetch audio features
        audio_features_data = spotify_api.get_audio_features_for_top_tracks(limit=5)
        data_processor.process_audio_features(audio_features_data)
        
        # Fetch top artists
        top_artists_data = spotify_api.get_top_artists(limit=10)
        data_processor.process_top_artists(top_artists_data)
        
        # Fetch recently played
        recently_played_data = spotify_api.get_recently_played(limit=50)
        data_processor.process_recently_played(recently_played_data)
        
        # Generate wrapped summary
        data_processor.generate_spotify_wrapped_summary()
        
        print("Initial data fetch completed successfully")
    except Exception as e:
        print(f"Error during initial data fetch: {e}")
        print("The dashboard will start with empty or cached data")
    
    # Run the app - Fixed method name from run_server to run
    app.run(debug=True)