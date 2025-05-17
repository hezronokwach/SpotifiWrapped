import spotipy
from spotipy.oauth2 import SpotifyOAuth
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
    top_tracks = sp_personal.current_user_top_tracks(limit=10, time_range='short_term')
    top_tracks_data = []
    for idx, track in enumerate(top_tracks['items'], 1):
        top_tracks_data.append({
            'track': track['name'],
            'artist': track['artists'][0]['name'],
            'rank': idx,
            'popularity': track['popularity']
        })
    top_tracks_df = pd.DataFrame(top_tracks_data)
    top_tracks_df.to_csv('data/top_tracks.csv', index=False)

    # Saved tracks
    saved_tracks = sp_personal.current_user_saved_tracks(limit=10)
    saved_tracks_data = []
    for idx, item in enumerate(saved_tracks['items'], 1):
        track = item['track']
        saved_tracks_data.append({
            'track': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'added_at': item['added_at']
        })
    saved_tracks_df = pd.DataFrame(saved_tracks_data)
    saved_tracks_df.to_csv('data/saved_tracks.csv', index=False)

    # Playlists
    playlists = sp_personal.current_user_playlists(limit=10)
    playlists_data = []
    for idx, playlist in enumerate(playlists['items'], 1):
        playlists_data.append({
            'playlist': playlist['name'],
            'total_tracks': playlist['tracks']['total'],
            'public': playlist['public'],
            'collaborative': playlist['collaborative']
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
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'progress_ms': current_track['progress_ms']
        })
    else:
        current_track_data.append({
            'track': 'None',
            'artist': 'None',
            'album': 'None',
            'duration_ms': 0,
            'progress_ms': 0
        })
    current_track_df = pd.DataFrame(current_track_data)
    current_track_df.to_csv('data/current_track.csv', index=False)

    # Get user profile info
    user_profile = sp_personal.current_user()
    user_data = {
        'display_name': user_profile.get('display_name', 'Unknown'),
        'id': user_profile.get('id', 'Unknown'),
        'followers': user_profile.get('followers', {}).get('total', 0),
        'image_url': user_profile.get('images', [{}])[0].get('url', '') if user_profile.get('images') else ''
    }
    user_df = pd.DataFrame([user_data])
    user_df.to_csv('data/user_profile.csv', index=False)

except Exception as e:
    print(f"Error fetching personal data: {e}")
    # Create empty dataframes if personal data fetch fails
    top_tracks_df = pd.DataFrame(columns=['track', 'artist', 'rank', 'popularity'])
    saved_tracks_df = pd.DataFrame(columns=['track', 'artist', 'album', 'added_at'])
    playlists_df = pd.DataFrame(columns=['playlist', 'total_tracks', 'public', 'collaborative'])
    current_track_df = pd.DataFrame([{'track': 'None', 'artist': 'None', 'album': 'None', 'duration_ms': 0, 'progress_ms': 0}])
    user_df = pd.DataFrame([{'display_name': 'Unknown', 'id': 'Unknown', 'followers': 0, 'image_url': ''}])
    
    # Save empty dataframes to CSV
    top_tracks_df.to_csv('data/top_tracks.csv', index=False)
    saved_tracks_df.to_csv('data/saved_tracks.csv', index=False)
    playlists_df.to_csv('data/playlists.csv', index=False)
    current_track_df.to_csv('data/current_track.csv', index=False)
    user_df.to_csv('data/user_profile.csv', index=False)

# --- Dash Dashboard ---
app = dash.Dash(__name__)

app.layout = html.Div([
    # Header with user profile
    html.Div([
        html.H1("My Spotify Personal Dashboard", style={'textAlign': 'center', 'color': '#1DB954'}),
        html.Div(id='user-profile', style={'textAlign': 'center', 'margin': '20px'})
    ]),
    
    # Error message div (hidden by default)
    html.Div(id='error-message', style={'color': '#FF5555', 'textAlign': 'center', 'margin': '10px', 'display': 'none'}),
    
    # Currently playing section
    html.Div([
        html.H2("Currently Playing", style={'color': '#1DB954', 'textAlign': 'center'}),
        html.Div(id='current-track-display', style={'textAlign': 'center', 'margin': '20px'})
    ], style={'backgroundColor': '#181818', 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
    
    # Top tracks section
    html.Div([
        html.H2("Your Top Tracks", style={'color': '#1DB954', 'textAlign': 'center'}),
        dcc.Graph(id='top-tracks-chart')
    ], style={'backgroundColor': '#181818', 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
    
    # Saved tracks section
    html.Div([
        html.H2("Recently Saved Tracks", style={'color': '#1DB954', 'textAlign': 'center'}),
        dcc.Graph(id='saved-tracks-chart')
    ], style={'backgroundColor': '#181818', 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
    
    # Playlists section
    html.Div([
        html.H2("Your Playlists", style={'color': '#1DB954', 'textAlign': 'center'}),
        dcc.Graph(id='playlists-chart')
    ], style={'backgroundColor': '#181818', 'padding': '20px', 'borderRadius': '10px', 'margin': '20px 0'}),
    
    # Auto-refresh component
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # in milliseconds (30 seconds)
        n_intervals=0
    )
], style={'backgroundColor': '#121212', 'padding': '20px', 'fontFamily': 'Helvetica, Arial, sans-serif'})

@app.callback(
    Output('user-profile', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_user_profile(_):
    try:
        user_data = pd.read_csv('data/user_profile.csv')
        if len(user_data) > 0:
            user = user_data.iloc[0]
            profile_content = [
                html.Img(src=user['image_url'], style={'borderRadius': '50%', 'width': '100px', 'height': '100px'}) 
                if user['image_url'] else None,
                html.H3(f"Welcome, {user['display_name']}", style={'color': '#FFFFFF', 'margin': '10px'}),
                html.P(f"Followers: {user['followers']}", style={'color': '#AAAAAA'})
            ]
            return [item for item in profile_content if item is not None]
        return html.P("User profile not available", style={'color': '#AAAAAA'})
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return html.P("User profile not available", style={'color': '#AAAAAA'})

@app.callback(
    Output('current-track-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_current_track(_):
    try:
        current_data = pd.read_csv('data/current_track.csv')
        if len(current_data) > 0 and current_data.iloc[0]['track'] != 'None':
            track = current_data.iloc[0]
            progress_percent = (track['progress_ms'] / track['duration_ms'] * 100) if track['duration_ms'] > 0 else 0
            
            return [
                html.H3(f"{track['track']}", style={'color': '#FFFFFF', 'margin': '5px'}),
                html.P(f"by {track['artist']}", style={'color': '#AAAAAA', 'margin': '5px'}),
                html.P(f"from {track['album']}", style={'color': '#AAAAAA', 'margin': '5px'}),
                html.Div([
                    html.Div(style={
                        'width': f'{progress_percent}%',
                        'backgroundColor': '#1DB954',
                        'height': '5px',
                        'borderRadius': '5px'
                    })
                ], style={
                    'width': '100%',
                    'backgroundColor': '#333333',
                    'height': '5px',
                    'borderRadius': '5px',
                    'margin': '10px 0'
                })
            ]
        return html.P("Not currently playing anything", style={'color': '#AAAAAA'})
    except Exception as e:
        print(f"Error updating current track: {e}")
        return html.P("Current track data not available", style={'color': '#AAAAAA'})

@app.callback(
    Output('top-tracks-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_top_tracks_chart(_):
    try:
        top_tracks_df = pd.read_csv('data/top_tracks.csv')
        if len(top_tracks_df) == 0:
            # Return empty figure with message if no data
            fig = px.bar(
                title='Your Top Tracks (No data available)'
            )
        else:
            # Sort by rank to ensure proper order
            top_tracks_df = top_tracks_df.sort_values('rank')
            fig = px.bar(
                top_tracks_df,
                x='track',
                y='popularity',
                color='artist',
                title='Your Top Tracks by Popularity',
                labels={'track': 'Track', 'popularity': 'Popularity Score', 'artist': 'Artist'}
            )
            fig.update_xaxes(tickangle=45)
        fig.update_layout(
            plot_bgcolor='#181818',
            paper_bgcolor='#181818',
            font_color='#FFFFFF',
            title_font_color='#1DB954',
            legend_title_font_color='#1DB954',
            height=500
        )
        return fig
    except Exception as e:
        print(f"Error updating top tracks chart: {e}")
        fig = px.bar(title='Your Top Tracks (Error loading data)')
        fig.update_layout(
            plot_bgcolor='#181818',
            paper_bgcolor='#181818',
            font_color='#FFFFFF',
            title_font_color='#FF5555'
        )
        return fig

@app.callback(
    Output('saved-tracks-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_saved_tracks_chart(_):
    try:
        saved_tracks_df = pd.read_csv('data/saved_tracks.csv')
        if len(saved_tracks_df) == 0:
            # Return empty figure with message if no data
            fig = px.bar(
                title='Your Saved Tracks (No data available)'
            )
        else:
            # Convert added_at to datetime and sort
            saved_tracks_df['added_at'] = pd.to_datetime(saved_tracks_df['added_at'])
            saved_tracks_df = saved_tracks_df.sort_values('added_at', ascending=False)
            
            fig = px.timeline(
                saved_tracks_df,
                x_start='added_at',
                y='track',
                color='artist',
                title='Recently Saved Tracks',
                labels={'added_at': 'Date Added', 'track': 'Track', 'artist': 'Artist'}
            )
            fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            plot_bgcolor='#181818',
            paper_bgcolor='#181818',
            font_color='#FFFFFF',
            title_font_color='#1DB954',
            legend_title_font_color='#1DB954',
            height=500
        )
        return fig
    except Exception as e:
        print(f"Error updating saved tracks chart: {e}")
        fig = px.bar(title='Your Saved Tracks (Error loading data)')
        fig.update_layout(
            plot_bgcolor='#181818',
            paper_bgcolor='#181818',
            font_color='#FFFFFF',
            title_font_color='#FF5555'
        )
        return fig

@app.callback(
    Output('playlists-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_playlists_chart(_):
    try:
        playlists_df = pd.read_csv('data/playlists.csv')
        if len(playlists_df) == 0:
            # Return empty figure with message if no data
            fig = px.bar(
                title='Your Playlists (No data available)'
            )
        else:
            # Sort by track count
            playlists_df = playlists_df.sort_values('total_tracks', ascending=False)
            
            # Create a color column based on playlist visibility
            playlists_df['visibility'] = playlists_df.apply(
                lambda x: 'Collaborative' if x['collaborative'] else ('Public' if x['public'] else 'Private'), 
                axis=1
            )
            
            fig = px.bar(
                playlists_df,
                x='playlist',
                y='total_tracks',
                color='visibility',
                title='Your Playlists by Track Count',
                labels={'playlist': 'Playlist', 'total_tracks': 'Number of Tracks', 'visibility': 'Visibility'}
            )
            fig.update_xaxes(tickangle=45)
        fig.update_layout(
            plot_bgcolor='#181818',
            paper_bgcolor='#181818',
            font_color='#FFFFFF',
            title_font_color='#1DB954',
            legend_title_font_color='#1DB954',
            height=500
        )
        return fig
    except Exception as e:
        print(f"Error updating playlists chart: {e}")
        fig = px.bar(title='Your Playlists (Error loading data)')
        fig.update_layout(
            plot_bgcolor='#181818',
            paper_bgcolor='#181818',
            font_color='#FFFFFF',
            title_font_color='#FF5555'
        )
        return fig

if __name__ == '__main__':
    app.run(debug=True)