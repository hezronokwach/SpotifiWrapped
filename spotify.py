import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials from .env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# --- Fetch Personal Data ---
scopes = 'user-top-read user-library-read playlist-read-private user-read-currently-playing'
try:
    sp_personal = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scopes,
        open_browser=False
    ))

    # Top tracks
    top_tracks = sp_personal.current_user_top_tracks(limit=5, time_range='short_term')
    top_tracks_data = []
    for idx, track in enumerate(top_tracks['items'], 1):
        top_tracks_data.append({
            'track': track['name'],
            'artist': track['artists'][0]['name']
        })
    top_tracks_df = pd.DataFrame(top_tracks_data)
    top_tracks_df.to_csv('data/top_tracks.csv', index=False)

    # Saved tracks
    saved_tracks = sp_personal.current_user_saved_tracks(limit=5)
    saved_tracks_data = []
    for idx, item in enumerate(saved_tracks['items'], 1):
        track = item['track']
        saved_tracks_data.append({
            'track': track['name'],
            'artist': track['artists'][0]['name']
        })
    saved_tracks_df = pd.DataFrame(saved_tracks_data)
    saved_tracks_df.to_csv('data/saved_tracks.csv', index=False)

    # Playlists
    playlists = sp_personal.current_user_playlists(limit=5)
    playlists_data = []
    for idx, playlist in enumerate(playlists['items'], 1):
        playlists_data.append({
            'playlist': playlist['name'],
            'total_tracks': playlist['tracks']['total']
        })
    playlists_df = pd.DataFrame(playlists_data)
    playlists_df.to_csv('data/playlists.csv', index=False)

    # Currently playing
    current_track = sp_personal.currently_playing()
    current_track_data = []
    if current_track and current_track.get('is_playing', False):
        track = current_track['item']
        current_track_data.append({
            'track': track['name'],
            'artist': track['artists'][0]['name']
        })
    else:
        current_track_data.append({
            'track': 'None',
            'artist': 'None'
        })
    current_track_df = pd.DataFrame(current_track_data)
    current_track_df.to_csv('data/current_track.csv', index=False)

except Exception as e:
    print(f"Error fetching personal data: {e}")
    # Create empty dataframes if personal data fetch fails
    top_tracks_df = pd.DataFrame(columns=['track', 'artist'])
    saved_tracks_df = pd.DataFrame(columns=['track', 'artist'])
    playlists_df = pd.DataFrame(columns=['playlist', 'total_tracks'])
    current_track_df = pd.DataFrame([{'track': 'None', 'artist': 'None'}])
    
    # Save empty dataframes to CSV
    top_tracks_df.to_csv('data/top_tracks.csv', index=False)
    saved_tracks_df.to_csv('data/saved_tracks.csv', index=False)
    playlists_df.to_csv('data/playlists.csv', index=False)
    current_track_df.to_csv('data/current_track.csv', index=False)

# --- Fetch General Data ---
try:
    sp_general = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ))
    
    # Using Today's Top Hits playlist instead (more stable and popular)
    playlist_id = '37i9dQZF1DXcBWIGoYBM5M'  # Today's Top Hits
    
    # Add retry mechanism for API calls
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            playlist_tracks = sp_general.playlist_tracks(playlist_id, limit=5)
            trending_data = []
            for idx, item in enumerate(playlist_tracks['items'], 1):
                if item['track']:  # Check if track exists
                    track = item['track']
                    trending_data.append({
                        'track': track['name'],
                        'artist': track['artists'][0]['name']
                    })
            trending_df = pd.DataFrame(trending_data)
            trending_df.to_csv('data/trending_tracks.csv', index=False)
            break  # Success, exit the retry loop
        except Exception as e:
            retry_count += 1
            print(f"Retry {retry_count}/{max_retries} - Error: {e}")
            if retry_count < max_retries:
                time.sleep(2)  # Wait before retrying
            else:
                raise  # Re-raise the exception if all retries failed

except Exception as e:
    print(f"Error fetching general data: {e}")
    # Create empty trending dataframe if general data fetch fails
    trending_df = pd.DataFrame(columns=['track', 'artist'])
    trending_df.to_csv('data/trending_tracks.csv', index=False)

# --- Dash Dashboard ---
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Spotify Wrapped Remix", style={'textAlign': 'center', 'color': '#1DB954'}),
    
    # Error message div (hidden by default)
    html.Div(id='error-message', style={'color': '#FF5555', 'textAlign': 'center', 'margin': '10px', 'display': 'none'}),
    
    dcc.Graph(id='top-tracks-chart'),
    dcc.Graph(id='saved-tracks-chart'),
    dcc.Graph(id='playlists-chart'),
    
    html.H3("Currently Playing", style={'color': '#FFFFFF'}),
    html.Div(id='current-track-text', style={'color': '#FFFFFF'}),
    
    html.H3("Trending Tracks", style={'color': '#FFFFFF'}),
    html.Div(id='trending-tracks', style={'color': '#FFFFFF'})
], style={'backgroundColor': '#121212', 'padding': '20px'})

@app.callback(
    Output('top-tracks-chart', 'figure'),
    Input('top-tracks-chart', 'id')
)
def update_top_tracks_chart(_):
    if len(top_tracks_df) == 0:
        # Return empty figure with message if no data
        fig = px.bar(
            title='Your Top Tracks (No data available)'
        )
    else:
        fig = px.bar(
            top_tracks_df,
            x='track',
            y=[1]*len(top_tracks_df),
            color='artist',
            title='Your Top Tracks',
            labels={'track': 'Track', 'y': 'Rank'}
        )
    fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font_color='#FFFFFF',
        title_font_color='#1DB954'
    )
    return fig

@app.callback(
    Output('saved-tracks-chart', 'figure'),
    Input('saved-tracks-chart', 'id')
)
def update_saved_tracks_chart(_):
    if len(saved_tracks_df) == 0:
        # Return empty figure with message if no data
        fig = px.bar(
            title='Your Saved Tracks (No data available)'
        )
    else:
        fig = px.bar(
            saved_tracks_df,
            x='track',
            y=[1]*len(saved_tracks_df),
            color='artist',
            title='Your Saved Tracks',
            labels={'track': 'Track', 'y': 'Rank'}
        )
    fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font_color='#FFFFFF',
        title_font_color='#1DB954'
    )
    return fig

@app.callback(
    Output('playlists-chart', 'figure'),
    Input('playlists-chart', 'id')
)
def update_playlists_chart(_):
    if len(playlists_df) == 0:
        # Return empty figure with message if no data
        fig = px.bar(
            title='Your Playlists (No data available)'
        )
    else:
        fig = px.bar(
            playlists_df,
            x='playlist',
            y='total_tracks',
            title='Your Playlists',
            labels={'playlist': 'Playlist', 'total_tracks': 'Total Tracks'}
        )
    fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font_color='#FFFFFF',
        title_font_color='#1DB954'
    )
    return fig

@app.callback(
    Output('current-track-text', 'children'),
    Input('current-track-text', 'id')
)
def update_current_track(_):
    if len(current_track_df) == 0:
        return "Not currently playing anything"
    
    track = current_track_df.iloc[0]['track']
    artist = current_track_df.iloc[0]['artist']
    
    if track == 'None' and artist == 'None':
        return "Not currently playing anything"
    return f"Now Playing: {track} by {artist}"

@app.callback(
    Output('trending-tracks', 'children'),
    Input('trending-tracks', 'id')
)
def update_trending_tracks(_):
    if len(trending_df) == 0:
        return "No trending tracks data available"
    
    tracks_list = [html.Li(f"{row['track']} by {row['artist']}") for _, row in trending_df.iterrows()]
    return html.Ul(tracks_list)

if __name__ == '__main__':
    app.run(debug=True)