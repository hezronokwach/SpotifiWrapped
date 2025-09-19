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
                html.H1("Spotifi Wrapped", style={
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
        return html.Div(
            id='wrapped-summary-container',
            style={
                'minHeight': '100px',
                'position': 'relative',
                'margin': '20px 0'
            }
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
                id='visible-refresh-button'
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

def create_onboarding_page():
    """Create the layout for the onboarding page with futuristic cyberpunk styling."""
    return html.Div([
        # Animated background particles
        html.Div([
            html.Div(className="particle", style={
                'position': 'absolute',
                'width': '2px',
                'height': '2px',
                'backgroundColor': SPOTIFY_GREEN,
                'borderRadius': '50%',
                'animation': f'float 6s ease-in-out infinite, glow 2s ease-in-out infinite alternate',
                'top': f'{i*15}%',
                'left': f'{(i*23) % 100}%',
                'animationDelay': f'{i*0.5}s'
            }) for i in range(8)
        ], style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'height': '100%',
            'pointerEvents': 'none',
            'zIndex': '1'
        }),
        
        # Main content container
        html.Div([
            # Hero section with animated title
            html.Div([
                html.Div([
                    html.H1([
                        html.Span("SPOTIFI", className="title-part", style={
                            'fontFamily': 'Orbitron, monospace',
                            'fontWeight': '900',
                            'fontSize': '3.5rem',
                            'background': 'linear-gradient(45deg, #1DB954, #1ED760, #00d4ff)',
                            'backgroundClip': 'text',
                            'WebkitBackgroundClip': 'text',
                            'WebkitTextFillColor': 'transparent',
                            'textShadow': '0 0 30px rgba(29, 185, 84, 0.5)',
                            'animation': 'shimmer 3s ease-in-out infinite',
                            'display': 'inline-block',
                            'marginRight': '20px'
                        }),
                        html.Span("WRAPPED", className="title-part", style={
                            'fontFamily': 'Orbitron, monospace',
                            'fontWeight': '900',
                            'fontSize': '3.5rem',
                            'background': 'linear-gradient(45deg, #00d4ff, #8b5cf6, #f472b6)',
                            'backgroundClip': 'text',
                            'WebkitBackgroundClip': 'text',
                            'WebkitTextFillColor': 'transparent',
                            'textShadow': '0 0 30px rgba(0, 212, 255, 0.5)',
                            'animation': 'shimmer 3s ease-in-out infinite 1.5s',
                            'display': 'inline-block'
                        })
                    ], style={
                        'textAlign': 'center',
                        'marginBottom': '20px',
                        'animation': 'fadeIn 2s ease-out'
                    }),
                    
                    html.P([
                        "Initialize your ",
                        html.Span("neural connection", style={
                            'color': '#00d4ff',
                            'fontWeight': 'bold',
                            'textShadow': '0 0 10px rgba(0, 212, 255, 0.5)'
                        }),
                        " to the Spotifi matrix or explore with ",
                        html.Span("synthetic data", style={
                            'color': '#8b5cf6',
                            'fontWeight': 'bold',
                            'textShadow': '0 0 10px rgba(139, 92, 246, 0.5)'
                        })
                    ], style={
                        'color': SPOTIFY_WHITE,
                        'textAlign': 'center',
                        'fontSize': '1.2rem',
                        'marginBottom': '40px',
                        'fontFamily': 'Montserrat, sans-serif',
                        'animation': 'slideUp 1.5s ease-out 0.5s both'
                    })
                ], className="hero-content")
            ], style={
                'marginBottom': '50px',
                'position': 'relative',
                'zIndex': '2'
            }),

            # Connection cards container
            html.Div([
                # Spotify API Connection Card
                html.Div([
                    html.Div([
                        # Card header with animated icon
                        html.Div([
                            html.Div([
                                html.I(className="fab fa-spotify", style={
                                    'fontSize': '2.5rem',
                                    'color': SPOTIFY_GREEN,
                                    'animation': 'spin 10s linear infinite, glow 2s ease-in-out infinite alternate',
                                    'marginRight': '15px'
                                }),
                                html.H3("NEURAL LINK", style={
                                    'fontFamily': 'Orbitron, monospace',
                                    'fontWeight': '700',
                                    'color': SPOTIFY_GREEN,
                                    'margin': '0',
                                    'textShadow': '0 0 15px rgba(29, 185, 84, 0.5)',
                                    'letterSpacing': '2px'
                                })
                            ], style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'marginBottom': '10px'
                            }),
                            html.P("Establish direct connection to Spotifi mainframe", style={
                                'color': '#b3b3b3',
                                'margin': '0',
                                'fontSize': '0.9rem',
                                'fontFamily': 'Montserrat, sans-serif'
                            })
                        ], style={'marginBottom': '25px'}),

                        # Setup instructions with cyberpunk styling
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-terminal", style={
                                    'color': '#00d4ff',
                                    'marginRight': '10px',
                                    'fontSize': '1.2rem'
                                }),
                                html.Strong("INITIALIZATION PROTOCOL:", style={
                                    'color': '#00d4ff',
                                    'fontFamily': 'Orbitron, monospace',
                                    'fontSize': '0.9rem',
                                    'letterSpacing': '1px'
                                })
                            ], style={'marginBottom': '15px'}),
                            
                            html.Div([
                                html.Div([
                                    html.Span("01", style={
                                        'color': SPOTIFY_GREEN,
                                        'fontFamily': 'Orbitron, monospace',
                                        'fontWeight': 'bold',
                                        'marginRight': '10px',
                                        'fontSize': '0.8rem'
                                    }),
                                    "Access ", 
                                    html.A("Spotify Developer Matrix", 
                                           href="https://developer.spotify.com/dashboard", 
                                           target="_blank", 
                                           style={
                                               'color': SPOTIFY_GREEN,
                                               'textDecoration': 'none',
                                               'borderBottom': f'1px solid {SPOTIFY_GREEN}',
                                               'transition': 'all 0.3s ease',
                                               'textShadow': '0 0 5px rgba(29, 185, 84, 0.3)'
                                           })
                                ], style={'marginBottom': '8px', 'fontSize': '0.9rem'}),
                                
                                html.Div([
                                    html.Span("02", style={
                                        'color': SPOTIFY_GREEN,
                                        'fontFamily': 'Orbitron, monospace',
                                        'fontWeight': 'bold',
                                        'marginRight': '10px',
                                        'fontSize': '0.8rem'
                                    }),
                                    "Configure application settings"
                                ], style={'marginBottom': '8px', 'fontSize': '0.9rem'}),
                                
                                html.Div([
                                    html.Span("03", style={
                                        'color': SPOTIFY_GREEN,
                                        'fontFamily': 'Orbitron, monospace',
                                        'fontWeight': 'bold',
                                        'marginRight': '10px',
                                        'fontSize': '0.8rem'
                                    }),
                                    "Install redirect endpoint (choose one):"
                                ], style={'marginBottom': '10px', 'fontSize': '0.9rem'}),

                                # Local development option
                                html.Div([
                                    html.Span("• Local development: ", style={'fontWeight': 'bold'}),
                                    html.Code("http://127.0.0.1:8080/callback", style={
                                        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                        'color': '#00d4ff',
                                        'padding': '4px 8px',
                                        'borderRadius': '4px',
                                        'border': '1px solid rgba(0, 212, 255, 0.3)',
                                        'fontFamily': 'Orbitron, monospace',
                                        'fontSize': '0.8rem',
                                        'textShadow': '0 0 5px rgba(0, 212, 255, 0.3)'
                                    })
                                ], style={'marginBottom': '8px', 'fontSize': '0.9rem'}),

                                # Deployed version option
                                html.Div([
                                    html.Span("• Deployed version: ", style={'fontWeight': 'bold'}),
                                    html.Code("https://spotifiwrapped.onrender.com/callback", style={
                                        'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                                        'color': '#00d4ff',
                                        'padding': '4px 8px',
                                        'borderRadius': '4px',
                                        'border': '1px solid rgba(0, 212, 255, 0.3)',
                                        'fontFamily': 'Orbitron, monospace',
                                        'fontSize': '0.8rem',
                                        'textShadow': '0 0 5px rgba(0, 212, 255, 0.3)'
                                    })
                                ], style={'marginBottom': '15px', 'fontSize': '0.9rem'})
                            ], style={
                                'backgroundColor': 'rgba(0, 212, 255, 0.05)',
                                'border': '1px solid rgba(0, 212, 255, 0.2)',
                                'borderRadius': '8px',
                                'padding': '15px',
                                'marginBottom': '25px'
                            })
                        ]),

                        # Input fields with futuristic styling
                        html.Div([
                            html.Label([
                                html.I(className="fas fa-key", style={
                                    'color': SPOTIFY_GREEN,
                                    'marginRight': '8px'
                                }),
                                "CLIENT ID"
                            ], style={
                                'color': SPOTIFY_WHITE,
                                'fontFamily': 'Orbitron, monospace',
                                'fontWeight': 'bold',
                                'fontSize': '0.9rem',
                                'letterSpacing': '1px',
                                'marginBottom': '8px',
                                'display': 'block'
                            }),
                            dbc.Input(
                                id="client-id-input",
                                placeholder="Enter neural access key...",
                                type="text",
                                className="cyberpunk-input",
                                style={
                                    'backgroundColor': 'rgba(0, 0, 0, 0.7)',
                                    'color': SPOTIFY_WHITE,
                                    'border': '2px solid rgba(29, 185, 84, 0.3)',
                                    'borderRadius': '8px',
                                    'padding': '12px',
                                    'fontFamily': 'Orbitron, monospace',
                                    'fontSize': '0.9rem',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': 'inset 0 0 10px rgba(0, 0, 0, 0.5)',
                                    'marginBottom': '20px'
                                }
                            )
                        ]),

                        html.Div([
                            html.Label([
                                html.I(className="fas fa-lock", style={
                                    'color': SPOTIFY_GREEN,
                                    'marginRight': '8px'
                                }),
                                "CLIENT SECRET"
                            ], style={
                                'color': SPOTIFY_WHITE,
                                'fontFamily': 'Orbitron, monospace',
                                'fontWeight': 'bold',
                                'fontSize': '0.9rem',
                                'letterSpacing': '1px',
                                'marginBottom': '8px',
                                'display': 'block'
                            }),
                            dbc.Input(
                                id="client-secret-input",
                                placeholder="Enter encryption cipher...",
                                type="password",
                                className="cyberpunk-input",
                                style={
                                    'backgroundColor': 'rgba(0, 0, 0, 0.7)',
                                    'color': SPOTIFY_WHITE,
                                    'border': '2px solid rgba(29, 185, 84, 0.3)',
                                    'borderRadius': '8px',
                                    'padding': '12px',
                                    'fontFamily': 'Orbitron, monospace',
                                    'fontSize': '0.9rem',
                                    'transition': 'all 0.3s ease',
                                    'boxShadow': 'inset 0 0 10px rgba(0, 0, 0, 0.5)',
                                    'marginBottom': '25px'
                                }
                            )
                        ]),

                        # Connect button with advanced styling
                        dbc.Button([
                            html.I(className="fas fa-plug", style={'marginRight': '10px'}),
                            "INITIATE CONNECTION"
                        ],
                            id="connect-button",
                            className="cyberpunk-button",
                            style={
                                'background': f'linear-gradient(45deg, {SPOTIFY_GREEN}, #1ED760)',
                                'border': 'none',
                                'borderRadius': '25px',
                                'color': SPOTIFY_BLACK,
                                'fontFamily': 'Orbitron, monospace',
                                'fontWeight': 'bold',
                                'fontSize': '1rem',
                                'letterSpacing': '2px',
                                'padding': '15px 30px',
                                'width': '100%',
                                'position': 'relative',
                                'overflow': 'hidden',
                                'transition': 'all 0.3s ease',
                                'textShadow': 'none',
                                'boxShadow': f'0 0 20px rgba(29, 185, 84, 0.3), inset 0 0 20px rgba(255, 255, 255, 0.1)'
                            }
                        ),
                        html.Div(id='connect-status', className='mt-3', style={'color': SPOTIFY_WHITE})
                    ])
                ], className="connection-card", style={
                    'background': 'linear-gradient(135deg, rgba(29, 185, 84, 0.1) 0%, rgba(0, 0, 0, 0.8) 100%)',
                    'border': '2px solid rgba(29, 185, 84, 0.3)',
                    'borderRadius': '15px',
                    'padding': '30px',
                    'marginBottom': '30px',
                    'position': 'relative',
                    'overflow': 'hidden',
                    'backdropFilter': 'blur(10px)',
                    'boxShadow': '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 0 20px rgba(29, 185, 84, 0.05)',
                    'animation': 'slideUp 1s ease-out 1s both',
                    'transition': 'all 0.3s ease'
                }),

                # Sample Data Card
                html.Div([
                    html.Div([
                        # Card header
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-database", style={
                                    'fontSize': '2.5rem',
                                    'color': '#8b5cf6',
                                    'animation': 'pulse 2s ease-in-out infinite, glow 2s ease-in-out infinite alternate',
                                    'marginRight': '15px'
                                }),
                                html.H3("DEMO MATRIX", style={
                                    'fontFamily': 'Orbitron, monospace',
                                    'fontWeight': '700',
                                    'color': '#8b5cf6',
                                    'margin': '0',
                                    'textShadow': '0 0 15px rgba(139, 92, 246, 0.5)',
                                    'letterSpacing': '2px'
                                })
                            ], style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'marginBottom': '10px'
                            }),
                            html.P("Experience the full system with synthetic data streams", style={
                                'color': '#b3b3b3',
                                'margin': '0',
                                'fontSize': '0.9rem',
                                'fontFamily': 'Montserrat, sans-serif'
                            })
                        ], style={'marginBottom': '25px'}),

                        html.P([
                            "Explore the complete ",
                            html.Span("neural interface", style={
                                'color': '#f472b6',
                                'fontWeight': 'bold',
                                'textShadow': '0 0 10px rgba(244, 114, 182, 0.5)'
                            }),
                            " without establishing a live connection. ",
                            html.Br(),
                            "All systems operational with ",
                            html.Span("realistic data simulation", style={
                                'color': '#00d4ff',
                                'fontWeight': 'bold',
                                'textShadow': '0 0 10px rgba(0, 212, 255, 0.5)'
                            }),
                            "."
                        ], style={
                            'color': SPOTIFY_WHITE,
                            'marginBottom': '25px',
                            'fontSize': '1rem',
                            'lineHeight': '1.6'
                        }),

                        # Features list
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-check-circle", style={
                                    'color': '#1ED760',
                                    'marginRight': '10px'
                                }),
                                html.Span("Synthetic listening patterns & AI analysis", style={
                                    'color': '#b3b3b3',
                                    'fontSize': '0.9rem'
                                })
                            ], style={'marginBottom': '8px'}),
                            html.Div([
                                html.I(className="fas fa-check-circle", style={
                                    'color': '#1ED760',
                                    'marginRight': '10px'
                                }),
                                html.Span("Simulated top tracks, artists & playlists", style={
                                    'color': '#b3b3b3',
                                    'fontSize': '0.9rem'
                                })
                            ], style={'marginBottom': '8px'}),
                            html.Div([
                                html.I(className="fas fa-check-circle", style={
                                    'color': '#1ED760',
                                    'marginRight': '10px'
                                }),
                                html.Span("Full dashboard experience preview", style={
                                    'color': '#b3b3b3',
                                    'fontSize': '0.9rem'
                                })
                            ], style={'marginBottom': '25px'})
                        ]),

                        # Demo button
                        dbc.Button([
                            html.I(className="fas fa-rocket", style={'marginRight': '10px'}),
                            "ENTER DEMO MATRIX"
                        ],
                            id="sample-data-button",
                            className="demo-button",
                            style={
                                'background': 'linear-gradient(45deg, #8b5cf6, #f472b6)',
                                'border': 'none',
                                'borderRadius': '25px',
                                'color': SPOTIFY_WHITE,
                                'fontFamily': 'Orbitron, monospace',
                                'fontWeight': 'bold',
                                'fontSize': '1rem',
                                'letterSpacing': '2px',
                                'padding': '15px 30px',
                                'width': '100%',
                                'position': 'relative',
                                'overflow': 'hidden',
                                'transition': 'all 0.3s ease',
                                'boxShadow': '0 0 20px rgba(139, 92, 246, 0.3), inset 0 0 20px rgba(255, 255, 255, 0.1)'
                            }
                        ),
                        html.Div(id='sample-data-status', className='mt-3', style={'color': SPOTIFY_WHITE})
                    ])
                ], className="demo-card", style={
                    'background': 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(0, 0, 0, 0.8) 100%)',
                    'border': '2px solid rgba(139, 92, 246, 0.3)',
                    'borderRadius': '15px',
                    'padding': '30px',
                    'marginBottom': '30px',
                    'position': 'relative',
                    'overflow': 'hidden',
                    'backdropFilter': 'blur(10px)',
                    'boxShadow': '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 0 20px rgba(139, 92, 246, 0.05)',
                    'animation': 'slideUp 1s ease-out 1.5s both',
                    'transition': 'all 0.3s ease'
                })
            ], className="cards-container", style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(400px, 1fr))',
                'gap': '30px',
                'marginBottom': '40px'
            }),

            # Footer with help link
            html.Div([
                html.P([
                    "Need assistance accessing the developer matrix? Visit the ",
                    html.A("Spotifi Developer Portal", 
                           href="https://developer.spotify.com/dashboard/", 
                           target="_blank", 
                           style={
                               'color': SPOTIFY_GREEN,
                               'textDecoration': 'none',
                               'borderBottom': f'1px solid {SPOTIFY_GREEN}',
                               'transition': 'all 0.3s ease'
                           }),
                    "."
                ], style={
                    'color': SPOTIFY_GRAY,
                    'textAlign': 'center',
                    'fontSize': '0.9rem',
                    'animation': 'fadeIn 2s ease-out 2s both'
                })
            ])

        ], style={
            'maxWidth': '1000px',
            'margin': '0 auto',
            'padding': '40px 20px',
            'position': 'relative',
            'zIndex': '2'
        })
    ], style={
        'backgroundColor': '#0a0a0a',
        'backgroundImage': '''
            radial-gradient(circle at 20% 80%, rgba(29, 185, 84, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(139, 92, 246, 0.05) 0%, transparent 50%)
        ''',
        'minHeight': '100vh',
        'position': 'relative',
        'overflow': 'hidden'
    })

def create_settings_page():
    """Create the layout for the settings page."""
    return html.Div([
        html.Div([
            html.H2("⚙️ Settings", style={'color': SPOTIFY_GREEN, 'textAlign': 'center', 'marginBottom': '20px'}),
            html.P("Manage your application settings and data preferences.", style={'color': SPOTIFY_WHITE, 'textAlign': 'center', 'marginBottom': '30px'}),

            dbc.Card([
                dbc.CardBody([
                    html.H4("Spotify API Credentials", className="card-title", style={'color': SPOTIFY_GREEN}),
                    html.P("Update your Spotify API Client ID and Client Secret.", className="card-text", style={'color': SPOTIFY_WHITE}),
                    
                    dbc.Input(
                        id="settings-client-id-input",
                        placeholder="Enter new Spotify Client ID",
                        type="text",
                        className="mb-3",
                        style={'backgroundColor': '#282828', 'color': SPOTIFY_WHITE, 'border': '1px solid #404040'}
                    ),
                    dbc.Input(
                        id="settings-client-secret-input",
                        placeholder="Enter new Spotify Client Secret",
                        type="password",
                        className="mb-3",
                        style={'backgroundColor': '#282828', 'color': SPOTIFY_WHITE, 'border': '1px solid #404040'}
                    ),
                    dbc.Button(
                        "Update Credentials",
                        id="update-credentials-button",
                        color="success",
                        className="me-2",
                        style={'backgroundColor': SPOTIFY_GREEN, 'borderColor': SPOTIFY_GREEN, 'color': SPOTIFY_BLACK}
                    ),
                    dbc.Button(
                        "Clear All Data & Logout",
                        id="clear-data-button",
                        color="danger",
                        className="me-2",
                        style={'backgroundColor': '#e74c3c', 'borderColor': '#e74c3c', 'color': SPOTIFY_WHITE}
                    ),
                    dbc.Button(
                        "🗑️ Clean Database (Admin)",
                        id="clean-database-button",
                        color="warning",
                        className="me-2",
                        style={'backgroundColor': '#f39c12', 'borderColor': '#f39c12', 'color': SPOTIFY_BLACK}
                    ),
                    dbc.Button(
                        "🧹 Clear Cache Files (Critical)",
                        id="clear-cache-button",
                        color="danger",
                        className="me-2",
                        style={'backgroundColor': '#e74c3c', 'borderColor': '#e74c3c', 'color': SPOTIFY_WHITE}
                    ),
                    html.Div(id='update-credentials-status', className='mt-3', style={'color': SPOTIFY_WHITE})
                ])
            ], style={'backgroundColor': '#181818', 'border': '1px solid #282828', 'marginBottom': '30px'}),

            dbc.Card([
                dbc.CardBody([
                    html.H4("Data Mode", className="card-title", style={'color': SPOTIFY_GREEN}),
                    html.P("Switch between using your live Spotify data or sample data.", className="card-text", style={'color': SPOTIFY_WHITE}),
                    dbc.RadioItems(
                        options=[
                            {"label": "Use My Spotify Data", "value": "live"},
                            {"label": "Use Sample Data", "value": "sample"}
                        ],
                        id="data-mode-radio",
                        inline=True,
                        className="mb-3",
                        style={'color': SPOTIFY_WHITE},
                        inputStyle={'marginRight': '5px'},
                        labelStyle={'marginRight': '20px'}
                    ),
                    html.Div(id='data-mode-status', className='mt-3', style={'color': SPOTIFY_WHITE})
                ])
            ], style={'backgroundColor': '#181818', 'border': '1px solid #282828'}),

            html.Div([
                dcc.Link(
                    "← Back to Dashboard",
                    href="/",
                    className="ai-insights-link",
                    style={'marginTop': '30px', 'display': 'block', 'textAlign': 'center'}
                )
            ])

        ], style={
            'maxWidth': '600px',
            'margin': '50px auto',
            'padding': '30px',
            'backgroundColor': '#000000',
            'borderRadius': '15px',
            'boxShadow': '0 0 50px rgba(29, 185, 84, 0.2)',
            'border': '1px solid rgba(29, 185, 84, 0.3)'
        })
    ], style={
        'backgroundColor': SPOTIFY_BLACK,
        'minHeight': '100vh',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center'
    })
