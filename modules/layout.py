import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from modules.visualizations import (
    create_spotify_card, create_track_list_item, 
    create_artist_list_item, create_stat_card,
    create_progress_bar, create_spotify_button,
    create_album_card, create_personality_card,
    create_dj_mode_card, create_album_listening_style_card,
    SPOTIFY_GREEN, SPOTIFY_BLACK, SPOTIFY_WHITE, SPOTIFY_GRAY
)

class DashboardLayout:
    """Class for creating and managing the dashboard layout."""
    
    def __init__(self):
        """Initialize the dashboard layout."""
        self.theme = {
            'background_color': SPOTIFY_BLACK,
            'text_color': SPOTIFY_WHITE,
            'accent_color': SPOTIFY_GREEN,
            'secondary_color': SPOTIFY_GRAY,
            'font_family': 'Gotham, Helvetica Neue, Helvetica, Arial, sans-serif'
        }
    
    def create_header(self, user_data=None):
        """Create the dashboard header with user profile."""
        if not user_data:
            # Default header without user data
            return html.Div([
                html.H1("Spotify Wrapped Remix", style={
                    'textAlign': 'center',
                    'color': self.theme['accent_color'],
                    'marginBottom': '20px',
                    'fontFamily': self.theme['font_family']
                }),
                html.P("Connect your Spotify account to see your personalized dashboard", style={
                    'textAlign': 'center',
                    'color': self.theme['secondary_color']
                })
            ], style={'padding': '20px 0'})
        
        # Header with user profile
        return html.Div([
            # User profile section
            html.Div([
                # User image
                html.Div([
                    html.Img(
                        src=user_data.get('image_url', ''),
                        style={
                            'width': '100px',
                            'height': '100px',
                            'borderRadius': '50%',
                            'border': f'3px solid {self.theme["accent_color"]}'
                        }
                    ) if user_data.get('image_url') else html.Div(
                        style={
                            'width': '100px',
                            'height': '100px',
                            'borderRadius': '50%',
                            'backgroundColor': self.theme['secondary_color'],
                            'border': f'3px solid {self.theme["accent_color"]}'
                        }
                    )
                ], style={'display': 'inline-block', 'verticalAlign': 'middle'}),
                
                # User info
                html.Div([
                    html.H1(f"Welcome, {user_data.get('display_name', 'Spotify User')}", style={
                        'color': self.theme['text_color'],
                        'margin': '0 0 10px 0'
                    }),
                    html.P([
                        f"{user_data.get('followers', 0)} followers"
                    ], style={
                        'color': self.theme['secondary_color'],
                        'fontSize': '1.1rem',
                        'fontWeight': '500'
                    })
                ], style={
                    'display': 'inline-block',
                    'verticalAlign': 'middle',
                    'marginLeft': '20px'
                })
            ], style={'textAlign': 'center', 'margin': '20px 0'}),
            
            # Dashboard title
            html.H2("Your Personal Spotify Dashboard", style={
                'textAlign': 'center',
                'color': self.theme['accent_color'],
                'marginTop': '20px',
                'fontFamily': self.theme['font_family']
            })
        ], style={'padding': '20px 0'})
    
    def create_currently_playing_section(self):
        """Create the currently playing section."""
        return html.Div(
            id='current-track-container',
            style={
                'margin': '20px 0',
                'padding': '20px',
                'borderRadius': '10px',
                'backgroundColor': '#121212'
            }
        )
    
    def create_top_tracks_section(self):
        """Create the top tracks section."""
        return create_spotify_card(
            title="Your Top Tracks",
            content=dcc.Graph(
                id='top-tracks-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-music"
        )
    
    def create_saved_tracks_section(self):
        """Create the saved tracks section."""
        return create_spotify_card(
            title="Recently Saved Tracks",
            content=dcc.Graph(
                id='saved-tracks-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-heart"
        )
    
    def create_playlists_section(self):
        """Create the playlists section."""
        return create_spotify_card(
            title="Your Playlists",
            content=dcc.Graph(
                id='playlists-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-list"
        )
    
    def create_audio_features_section(self):
        """Create the audio features section."""
        return create_spotify_card(
            title="Audio Features Analysis",
            content=dcc.Graph(
                id='audio-features-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-chart-radar"
        )
    
    def create_top_artists_section(self):
        """Create the top artists section."""
        return create_spotify_card(
            title="Your Top Artists",
            content=dcc.Graph(
                id='top-artists-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-user"
        )
    
    def create_genre_analysis_section(self):
        """Create the genre analysis section."""
        return create_spotify_card(
            title="Genre Analysis",
            content=dcc.Graph(
                id='genre-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-tag"
        )
    
    def create_listening_patterns_section(self):
        """Create the listening patterns section."""
        return create_spotify_card(
            title="Listening Patterns",
            content=dcc.Graph(
                id='listening-patterns-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-clock"
        )
    
    def create_wrapped_summary_section(self):
        """Create the Spotify Wrapped summary section."""
        return html.Div(
            id='wrapped-summary-container',
            style={
                'margin': '30px 0'
            }
        )
    
    def create_top_albums_section(self):
        """Create the top albums section."""
        return create_spotify_card(
            title="Your Top Albums",
            content=html.Div(
                id='top-albums-container',
                className="album-grid-container"
            ),
            icon="fa-compact-disc"
        )
    
    def create_personality_section(self):
        """Create the personality analysis section."""
        return html.Div(
            id='personality-container',
            style={
                'margin': '30px 0'
            }
        )
    
    def create_dj_mode_section(self):
        """Create the DJ mode stats section."""
        return html.Div(
            id='dj-mode-container',
            style={
                'margin': '30px 0'
            }
        )
    
    def create_album_listening_patterns_section(self):
        """Create the album listening patterns section."""
        return html.Div(
            id='album-listening-patterns-container',
            style={
                'margin': '30px 0'
            }
        )
    
    def create_music_analysis_section(self):
        """Create the music analysis section."""
        return create_spotify_card(
            title="Your Musical Universe",
            content=html.Div(
                id='music-analysis-container',
                style={
                    'backgroundColor': '#181818',
                    'borderRadius': '15px',
                    'padding': '30px',
                    'boxShadow': '0 8px 16px rgba(0,0,0,0.4)',
                    'margin': '20px 0'
                }
            ),
            icon="fa-music"
        )
    
    def create_stats_row(self):
        """Create a row of stat cards."""
        return dbc.Row([
            dbc.Col(
                html.Div(id='total-minutes-stat'),
                width=3
            ),
            dbc.Col(
                html.Div(id='unique-artists-stat'),
                width=3
            ),
            dbc.Col(
                html.Div(id='unique-tracks-stat'),
                width=3
            ),
            dbc.Col(
                html.Div(id='playlist-count-stat'),
                width=3
            )
        ], className='mb-4')
    
    def create_error_message(self):
        """Create an error message component."""
        return html.Div(
            id='error-message',
            style={
                'color': '#FF5555',
                'textAlign': 'center',
                'margin': '10px',
                'padding': '10px',
                'backgroundColor': '#2A0A0A',
                'borderRadius': '5px',
                'display': 'none'
            }
        )
    
    def create_refresh_button(self):
        """Create a refresh button."""
        return html.Div([
            create_spotify_button(
                "Refresh Data",
                id='refresh-button'
            )
        ], style={
            'textAlign': 'center',
            'margin': '20px 0'
        })
    
    def create_footer(self):
        """Create the dashboard footer."""
        return html.Footer([
            html.P([
                "Powered by ",
                html.A("Spotify API", href="https://developer.spotify.com/documentation/web-api/", target="_blank"),
                " | Created with Dash and Plotly"
            ], style={'color': self.theme['secondary_color']})
        ], style={
            'textAlign': 'center',
            'padding': '20px',
            'marginTop': '40px',
            'borderTop': f'1px solid {self.theme["secondary_color"]}'
        })
    
    def create_layout(self):
        """Create the complete dashboard layout."""
        layout = html.Div([
            # Auto-refresh component
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # in milliseconds (30 seconds)
                n_intervals=0
            ),
            
            # Store components for data
            dcc.Store(id='user-data-store'),
            dcc.Store(id='current-track-store'),
            dcc.Store(id='wrapped-summary-store'),
            dcc.Store(id='personality-data-store'),
            
            # Error message
            self.create_error_message(),
            
            # Collection status
            html.Div(id='collection-status', className='mb-3'),
            
            # Header (will be populated with user data)
            html.Div(id='header-container'),
            
            # Main content container
            dbc.Container([
                # Stats row
                self.create_stats_row(),
                
                # Currently playing section
                self.create_currently_playing_section(),
                
                # Personality analysis section
                self.create_personality_section(),
                
                # Top content row
                dbc.Row([
                    dbc.Col(self.create_top_tracks_section(), md=6),
                    dbc.Col(self.create_top_artists_section(), md=6)
                ], className='mb-4'),
                
                # Top albums section
                self.create_top_albums_section(),
                
                # Album listening patterns and DJ mode row
                dbc.Row([
                    dbc.Col(self.create_album_listening_patterns_section(), md=6),
                    dbc.Col(self.create_dj_mode_section(), md=6)
                ], className='mb-4'),
                
                # Music analysis section
                self.create_music_analysis_section(),

                # Audio analysis row
                dbc.Row([
                    dbc.Col(self.create_audio_features_section(), md=6),
                    dbc.Col(self.create_genre_analysis_section(), md=6)
                ], className='mb-4'),
                
                # Library content row
                dbc.Row([
                    dbc.Col(self.create_saved_tracks_section(), md=6),
                    dbc.Col(self.create_playlists_section(), md=6)
                ], className='mb-4'),
                
                # Listening patterns
                self.create_listening_patterns_section(),
                
                # Wrapped summary section
                self.create_wrapped_summary_section(),
                
                # Refresh button
                self.create_refresh_button(),
                
                # Footer
                self.create_footer()
            ], fluid=True)
        ], style={
            'backgroundColor': self.theme['background_color'],
            'color': self.theme['text_color'],
            'fontFamily': self.theme['font_family'],
            'minHeight': '100vh',
            'padding': '20px'
        })
        
        # Add custom CSS
        return html.Div([
            self.add_custom_css(),
            layout
        ])
    
    def add_custom_css(self):
        """Add custom CSS to the dashboard."""
        # Since we're using the assets folder for CSS, we don't need to add inline styles
        # This is just a placeholder that returns an empty div
        return html.Div(id="css-container", style={"display": "none"})
