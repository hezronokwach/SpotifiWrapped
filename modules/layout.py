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

        # Header with user profile - Enhanced futuristic styling
        return html.Div([
            # User profile section with enhanced styling
            html.Div([
                # User image with futuristic glow
                html.Div([
                    html.Img(
                        src=user_data.get('image_url', ''),
                        style={
                            'width': '120px',
                            'height': '120px',
                            'borderRadius': '50%',
                            'border': '3px solid rgba(29, 185, 84, 0.8)',
                            'boxShadow': '0 0 30px rgba(29, 185, 84, 0.4), 0 0 60px rgba(29, 185, 84, 0.2)',
                            'transition': 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                            'filter': 'brightness(1.1)'
                        },
                        className='futuristic-avatar'
                    ) if user_data.get('image_url') else html.Div([
                        # Enhanced stylish avatar with user's initials
                        html.Div(
                            user_data.get('display_name', 'S')[0].upper(),
                            style={
                                'width': '120px',
                                'height': '120px',
                                'borderRadius': '50%',
                                'background': 'linear-gradient(135deg, #1DB954, #00D4FF)',
                                'color': '#000000',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'fontSize': '48px',
                                'fontWeight': 'bold',
                                'fontFamily': "'Orbitron', monospace",
                                'border': '3px solid rgba(29, 185, 84, 0.8)',
                                'boxShadow': '0 0 30px rgba(29, 185, 84, 0.4), 0 0 60px rgba(29, 185, 84, 0.2)',
                                'transition': 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                                'textShadow': '0 0 10px rgba(0, 0, 0, 0.5)'
                            },
                            className='futuristic-avatar'
                        )
                    ])
                ], style={'display': 'inline-block', 'verticalAlign': 'middle'}),

                # Enhanced user info
                html.Div([
                    html.H1(f"Welcome, {user_data.get('display_name', 'Spotify User')}", style={
                        'color': 'rgba(255, 255, 255, 0.95)',
                        'margin': '0 0 15px 0',
                        'fontFamily': "'Orbitron', monospace",
                        'fontWeight': '700',
                        'fontSize': '2.5rem',
                        'textShadow': '0 0 20px rgba(29, 185, 84, 0.3)',
                        'background': 'linear-gradient(45deg, #FFFFFF, #1DB954)',
                        'backgroundClip': 'text',
                        'WebkitBackgroundClip': 'text',
                        'WebkitTextFillColor': 'transparent'
                    }),
                    html.Div([
                        # Enhanced followers and following stats
                        html.Div([
                            html.Div([
                                html.Strong(f"{user_data.get('followers', 0):,}", style={
                                    'fontSize': '1.8rem',
                                    'fontFamily': "'Orbitron', monospace",
                                    'fontWeight': '700',
                                    'color': '#1DB954',
                                    'textShadow': '0 0 10px rgba(29, 185, 84, 0.5)'
                                }),
                                html.Div("FOLLOWERS", style={
                                    'fontSize': '0.9rem',
                                    'fontFamily': "'Orbitron', monospace",
                                    'fontWeight': '500',
                                    'color': 'rgba(255, 255, 255, 0.7)',
                                    'letterSpacing': '1px',
                                    'marginTop': '2px'
                                })
                            ], style={
                                'textAlign': 'center',
                                'padding': '15px 25px',
                                'background': 'linear-gradient(135deg, rgba(29, 185, 84, 0.1), rgba(29, 185, 84, 0.05))',
                                'border': '1px solid rgba(29, 185, 84, 0.3)',
                                'borderRadius': '12px',
                                'marginRight': '20px',
                                'transition': 'all 0.3s ease',
                                'boxShadow': '0 4px 15px rgba(29, 185, 84, 0.1)'
                            }, className='futuristic-stat-box'),

                            html.Div([
                                html.Strong(f"{user_data.get('following', 0):,}", style={
                                    'fontSize': '1.8rem',
                                    'fontFamily': "'Orbitron', monospace",
                                    'fontWeight': '700',
                                    'color': '#00D4FF',
                                    'textShadow': '0 0 10px rgba(0, 212, 255, 0.5)'
                                }),
                                html.Div("FOLLOWING", style={
                                    'fontSize': '0.9rem',
                                    'fontFamily': "'Orbitron', monospace",
                                    'fontWeight': '500',
                                    'color': 'rgba(255, 255, 255, 0.7)',
                                    'letterSpacing': '1px',
                                    'marginTop': '2px'
                                })
                            ], style={
                                'textAlign': 'center',
                                'padding': '15px 25px',
                                'background': 'linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 212, 255, 0.05))',
                                'border': '1px solid rgba(0, 212, 255, 0.3)',
                                'borderRadius': '12px',
                                'transition': 'all 0.3s ease',
                                'boxShadow': '0 4px 15px rgba(0, 212, 255, 0.1)'
                            }, className='futuristic-stat-box')
                        ], style={
                            'display': 'flex',
                            'justifyContent': 'center',
                            'alignItems': 'center'
                        })
                    ], style={'marginTop': '10px'}),
                ], style={
                    'display': 'inline-block',
                    'verticalAlign': 'middle',
                    'marginLeft': '30px'
                })
            ], style={'textAlign': 'center', 'margin': '30px 0'}),

            # Dashboard title with futuristic styling
            html.H2("Your Personal Spotify Dashboard", style={
                'textAlign': 'center',
                'color': self.theme['accent_color'],
                'marginTop': '20px',
                'fontFamily': "'Orbitron', monospace",
                'fontWeight': '700',
                'fontSize': '2.2rem',
                'textTransform': 'uppercase',
                'letterSpacing': '2px',
                'textShadow': '0 0 20px rgba(29, 185, 84, 0.5)',
                'background': 'linear-gradient(45deg, #1DB954, #00D4FF)',
                'backgroundClip': 'text',
                'WebkitBackgroundClip': 'text',
                'WebkitTextFillColor': 'transparent'
            })
        ], style={'padding': '20px 0'}, className='futuristic-header')

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
        """Create the top tracks section with enhanced futuristic styling."""
        return create_spotify_card(
            title="Your Top Tracks",
            content=html.Div(
                id='top-tracks-chart',
                style={'minHeight': '400px'}
            ),
            icon="fa-music",
            card_type="neon",
            className="futuristic-chart-card"
        )

    def create_saved_tracks_section(self):
        """Create the saved tracks section."""
        return create_spotify_card(
            title="Recently Saved Tracks",
            content=html.Div(
                id='saved-tracks-chart',
                style={'minHeight': '300px'}
            ),
            icon="fa-heart",
            className="consistent-height-card"
        )

    def create_playlists_section(self):
        """Create the playlists section."""
        return create_spotify_card(
            title="Your Playlists",
            content=html.Div(
                id='playlists-container',
                style={
                    'minHeight': '300px',
                    'position': 'relative'
                }
            ),
            icon="fa-list",
            className="consistent-height-card"
        )

    def create_audio_features_section(self):
        """Create the audio features section with futuristic styling."""
        return create_spotify_card(
            title="Audio Features Analysis",
            content=dcc.Graph(
                id='audio-features-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-chart-radar",
            card_type="glass",
            className="consistent-height-card futuristic-chart-card"
        )

    def create_top_artists_section(self):
        """Create the top artists section with enhanced futuristic styling."""
        return create_spotify_card(
            title="Your Top Artists",
            content=html.Div(
                id='top-artists-chart',
                style={'minHeight': '400px'}
            ),
            icon="fa-user-music",
            card_type="glass",
            className="futuristic-chart-card"
        )

    def create_genre_analysis_section(self):
        """Create the genre analysis section with futuristic styling."""
        return create_spotify_card(
            title="Genre Analysis",
            content=dcc.Graph(
                id='genre-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-tag",
            card_type="neon",
            className="consistent-height-card futuristic-chart-card"
        )

    def create_listening_patterns_section(self):
        """Create the listening patterns section with futuristic styling."""
        return create_spotify_card(
            title="Listening Patterns",
            content=dcc.Graph(
                id='listening-patterns-chart',
                config={'displayModeBar': False}
            ),
            icon="fa-clock",
            card_type="neon",
            className="futuristic-chart-card futuristic-patterns-card"
        )

    def create_top_track_highlight_section(self):
        """Create the top track highlight section."""
        return create_spotify_card(
            title="Your #1 Track",
            content=html.Div(
                id='top-track-highlight-container',
                style={
                    'minHeight': '180px',
                    'position': 'relative'
                }
            ),
            icon="fa-music",
            card_type="neon"
        )

    def create_top_artist_highlight_section(self):
        """Create the top artist highlight section."""
        return create_spotify_card(
            title="Your Top Artist",
            content=html.Div(
                id='top-artist-highlight-container',
                style={
                    'minHeight': '180px',
                    'position': 'relative'
                }
            ),
            icon="fa-user-music",
            card_type="glass"
        )



    def create_wrapped_summary_section(self):
        """Create the Spotify Wrapped summary section with futuristic styling."""
        return create_spotify_card(
            title="Your Spotify Wrapped",
            content=html.Div(
                id='wrapped-summary-container',
                style={
                    'minHeight': '100px',
                    'position': 'relative'
                }
            ),
            icon="fa-star",
            card_type="glass"
        )

    def create_top_albums_section(self):
        """Create the top albums section."""
        return create_spotify_card(
            title="Your Top Albums",
            content=html.Div(
                id='top-albums-container'
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
                html.Div(id='listening-sessions-stat'),
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

                # Top highlights row (individual top track and artist)
                dbc.Row([
                    dbc.Col(self.create_top_track_highlight_section(), md=6),
                    dbc.Col(self.create_top_artist_highlight_section(), md=6)
                ], className='mb-4'),

                # Top content row (charts)
                dbc.Row([
                    dbc.Col(self.create_top_tracks_section(), md=6),
                    dbc.Col(self.create_top_artists_section(), md=6)
                ], className='mb-4'),

                # Top albums section
                self.create_top_albums_section(),

                # Your Spotify Wrapped (enhanced with Sound Story data)
                self.create_wrapped_summary_section(),

                # Album listening patterns section removed - now part of DNA section

                

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

                # Listening patterns (with date range)
                self.create_listening_patterns_section(),

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
