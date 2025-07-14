import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.io as pio
import colorsys
import random
from manim import Scene, Text, UP, DOWN, LEFT, RIGHT, ORIGIN, Write, FadeIn, Circle, Rectangle, VGroup


# Set Spotify-themed colors
SPOTIFY_GREEN = '#1DB954'
SPOTIFY_BLACK = '#191414'
SPOTIFY_WHITE = '#FFFFFF'
SPOTIFY_GRAY = '#535353'

# Custom color palette for consistent branding
SPOTIFY_PALETTE = [
    '#1DB954',  # Spotify green
    '#1ED760',  # Lighter green
    '#2D46B9',  # Blue
    '#F037A5',  # Pink
    '#FFFF00',  # Yellow
    '#FF5500',  # Orange
    '#509BF5',  # Light blue
    '#AF2896'   # Purple
]

# Set default template for all plotly figures
pio.templates.default = "plotly_dark"

class SpotifyAnimations:
    """Class for creating Spotify Wrapped style animations."""
    def __init__(self):
        pass

    # Animation methods will be implemented here

def create_stat_card(title, value, icon="fa-music", color=SPOTIFY_GREEN):
    """Create a futuristic stat card for displaying metrics with enhanced animations."""

    # Generate unique ID for this card
    import uuid
    card_id = f"stat-card-{uuid.uuid4().hex[:8]}"

    return html.Div([
        # Animated background effect
        html.Div(className="data-flow", style={
            'position': 'absolute',
            'top': '0',
            'left': '0',
            'right': '0',
            'bottom': '0',
            'background': f'linear-gradient(45deg, transparent, {color}20, transparent)',
            'opacity': '0.3'
        }),

        # Icon with glow effect
        html.Div([
            html.I(className=f"fas {icon}", style={
                'fontSize': '32px',
                'color': color,
                'filter': f'drop-shadow(0 0 10px {color}50)',
                'transition': 'all 0.3s ease'
            })
        ], style={
            'textAlign': 'center',
            'marginBottom': '15px',
            'position': 'relative',
            'zIndex': '2'
        }),

        # Value with counter animation effect
        html.H4(value, id=f"{card_id}-value", style={
            'textAlign': 'center',
            'color': SPOTIFY_WHITE,
            'fontSize': '32px',
            'fontWeight': '700',
            'marginBottom': '8px',
            'fontFamily': 'Orbitron, monospace',
            'textShadow': f'0 0 20px {color}30',
            'position': 'relative',
            'zIndex': '2'
        }),

        # Title with subtle glow
        html.P(title, style={
            'textAlign': 'center',
            'color': SPOTIFY_GRAY,
            'fontSize': '13px',
            'fontWeight': '500',
            'textTransform': 'uppercase',
            'letterSpacing': '1px',
            'position': 'relative',
            'zIndex': '2'
        }),

        # Futuristic border accent
        html.Div(style={
            'position': 'absolute',
            'bottom': '0',
            'left': '20%',
            'right': '20%',
            'height': '2px',
            'background': f'linear-gradient(90deg, transparent, {color}, transparent)',
            'borderRadius': '1px',
            'boxShadow': f'0 0 10px {color}50'
        })
    ],
    id=card_id,
    className='spotify-card card-glass pulse',
    style={
        'padding': '24px',
        'borderRadius': '16px',
        'height': '160px',
        'position': 'relative',
        'overflow': 'hidden',
        'border': f'1px solid {color}30',
        'background': f'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
        'backdropFilter': 'blur(20px)',
        'transition': 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        'cursor': 'pointer'
    })
def create_album_card(album_name, artist_name, rank, image_url="", score=0):
    """
    Create a card for displaying album information.

    Args:
        album_name: Name of the album
        artist_name: Name of the artist
        rank: Rank of the album in the top albums list
        image_url: URL to the album cover image
        score: Listening score for the album

    Returns:
        A dbc.Card component
    """
    # Use a default image if none provided
    if not image_url:
        image_url = "https://via.placeholder.com/300?text=No+Image"

    return dbc.Card(
        [
            dbc.CardImg(src=image_url, top=True, className="album-img"),
            dbc.CardBody(
                [
                    html.Div(
                        f"#{rank}",
                        className="album-rank",
                        style={
                            "position": "absolute",
                            "top": "10px",
                            "left": "10px",
                            "background-color": SPOTIFY_BLACK,
                            "color": SPOTIFY_WHITE,
                            "padding": "5px 10px",
                            "border-radius": "15px",
                            "font-weight": "bold"
                        }
                    ),
                    html.H5(album_name, className="card-title text-truncate"),
                    html.P(artist_name, className="card-text text-muted text-truncate"),
                    html.Div(
                        [
                            html.Span("Listening Score: "),
                            html.Span(
                                f"{score}",
                                style={"color": SPOTIFY_GREEN, "font-weight": "bold"}
                            )
                        ],
                        className="mt-2"
                    )
                ]
            )
        ],
        className="album-card h-100 shadow-sm",
        style={"maxWidth": "200px", "margin": "10px"}
    )

def create_personality_card(primary_type, secondary_type, description, recommendations, metrics):
    """
    Create a card for displaying personality analysis.

    Args:
        primary_type: Primary personality type
        secondary_type: Secondary personality type
        description: Description of the primary personality type
        recommendations: List of recommendations
        metrics: Dictionary of metrics

    Returns:
        A dbc.Card component
    """
    # Create radar chart for metrics
    radar_metrics = {
        'Variety': metrics.get('variety_score', 0),
        'Discovery': metrics.get('discovery_score', 0),
        'Consistency': metrics.get('consistency_score', 0),
        'Mood': metrics.get('mood_score', 0),
        'Time Pattern': metrics.get('time_pattern_score', 0)
    }

    # Create radar chart
    categories = list(radar_metrics.keys())
    values = list(radar_metrics.values())

    # Add the first value at the end to close the polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor=f'rgba(29, 185, 84, 0.3)',  # Spotify green with transparency
        line=dict(color=SPOTIFY_GREEN, width=2),
        name='Your Metrics'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        margin=dict(l=70, r=70, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Create recommendations list
    recommendations_list = [
        html.Li(rec, className="mb-2") for rec in recommendations
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                html.H4("Your Music Personality", className="text-center"),
                style={"background-color": SPOTIFY_BLACK, "color": SPOTIFY_WHITE}
            ),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        primary_type,
                                        className="mb-1",
                                        style={"color": SPOTIFY_GREEN, "font-weight": "bold"}
                                    ),
                                    html.P(
                                        f"with a touch of {secondary_type}",
                                        className="text-muted"
                                    ),
                                    html.P(description, className="mt-3"),
                                ],
                                className="col-md-7"
                            ),
                            html.Div(
                                dcc.Graph(
                                    figure=fig,
                                    config={'displayModeBar': False},
                                    style={"height": "300px"}
                                ),
                                className="col-md-5"
                            )
                        ],
                        className="row mb-4"
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.H5("Recommendations for You", className="mb-3"),
                            html.Ul(recommendations_list, className="recommendations-list")
                        ]
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("Album Listening Style"),
                                    html.P(
                                        metrics.get('listening_style', 'Unknown'),
                                        style={"color": SPOTIFY_GREEN, "font-weight": "bold", "font-size": "1.2rem"}
                                    ),
                                    html.P(
                                        f"Album Completion: {metrics.get('album_completion_rate', 0)}%",
                                        className="mb-0 small"
                                    )
                                ],
                                className="col-md-6"
                            ),
                            html.Div(
                                [
                                    html.H6("DJ Mode Usage"),
                                    html.P(
                                        f"{metrics.get('percentage_of_listening', 0)}% of your listening",
                                        style={"color": SPOTIFY_GREEN, "font-weight": "bold", "font-size": "1.2rem"}
                                    ),
                                    html.P(
                                        f"Estimated minutes: {metrics.get('estimated_minutes', 0)}",
                                        className="mb-0 small"
                                    )
                                ],
                                className="col-md-6"
                            )
                        ],
                        className="row mt-3"
                    )
                ]
            )
        ],
        className="mb-4 shadow"
    )

def create_dj_mode_card(dj_stats):
    """
    Create a card for displaying DJ mode statistics.

    Args:
        dj_stats: Dictionary with DJ mode statistics

    Returns:
        A dbc.Card component
    """
    # Calculate percentage for progress bar
    percentage = min(100, dj_stats.get('percentage_of_listening', 0))

    # Check if user is premium (this should be provided by the app)
    is_premium = dj_stats.get('is_premium', False)

    if not is_premium:
        # Show a message for non-premium users
        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H4("Spotify DJ (Premium Feature)", className="text-center"),
                    style={"background-color": SPOTIFY_BLACK, "color": SPOTIFY_WHITE}
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.I(className="fas fa-crown", style={
                                    "fontSize": "32px",
                                    "color": SPOTIFY_GREEN,
                                    "marginBottom": "15px",
                                    "display": "block",
                                    "textAlign": "center"
                                }),
                                html.P(
                                    "Spotify DJ is a premium-only feature that uses AI to curate a personalized soundtrack.",
                                    className="text-center"
                                ),
                                html.P(
                                    "Upgrade to Spotify Premium to access this feature.",
                                    className="text-center text-muted"
                                )
                            ]
                        )
                    ]
                )
            ],
            className="mb-4 shadow"
        )

    # For premium users or if we want to show the stats anyway
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H4("Spotify DJ Usage", className="text-center"),
                style={"background-color": SPOTIFY_BLACK, "color": SPOTIFY_WHITE}
            ),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.H2(
                                f"{dj_stats.get('estimated_minutes', 0)} minutes",
                                className="text-center mb-3",
                                style={"color": SPOTIFY_GREEN}
                            ),
                            html.P(
                                "Estimated time spent using Spotify DJ",
                                className="text-center text-muted"
                            ),
                            html.Div(
                                [
                                    html.Span("Usage Level: "),
                                    html.Span(
                                        "Active User" if dj_stats.get('dj_mode_user', False) else "Occasional User",
                                        style={"font-weight": "bold"}
                                    )
                                ],
                                className="text-center mb-3"
                            ),
                            html.P(
                                f"Percentage of your listening time: {percentage}%",
                                className="mb-2"
                            ),
                            dbc.Progress(
                                value=percentage,
                                color="success",
                                className="mb-3",
                                style={"height": "10px"}
                            ),
                            html.P(
                                "Spotify DJ uses AI to curate a personalized soundtrack just for you, "
                                "with commentary about the music and artists you're listening to.",
                                className="text-muted small"
                            )
                        ]
                    )
                ]
            )
        ],
        className="mb-4 shadow"
    )

def create_album_listening_style_card(patterns):
    """
    Create a card for displaying album listening style.

    Args:
        patterns: Dictionary with album listening patterns

    Returns:
        A dbc.Card component
    """
    # Determine style description based on listening style
    style_descriptions = {
        "Album Purist": "You appreciate albums as complete works of art, listening to them from start to finish as the artist intended.",
        "Album Explorer": "You enjoy exploring albums but don't always listen to them in sequence or completion.",
        "Track Hopper": "You prefer individual tracks over full albums, creating your own unique listening journey.",
        "Mood Curator": "You select music based on mood and atmosphere, regardless of album structure."
    }

    style_description = style_descriptions.get(
        patterns.get('listening_style', ''),
        "Your album listening style is unique and personalized."
    )

    # Create progress bars for metrics
    album_completion = patterns.get('album_completion_rate', 0)
    sequential_listening = patterns.get('sequential_listening_score', 0)

    return dbc.Card(
        [
            dbc.CardHeader(
                html.H4("Album Listening Style", className="text-center"),
                style={"background-color": SPOTIFY_BLACK, "color": SPOTIFY_WHITE}
            ),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.H2(
                                patterns.get('listening_style', 'Unknown'),
                                className="text-center mb-3",
                                style={"color": SPOTIFY_GREEN}
                            ),
                            html.P(
                                style_description,
                                className="text-center mb-4"
                            ),
                            html.Div(
                                [
                                    html.P("Album Completion Rate", className="mb-1"),
                                    dbc.Progress(
                                        value=album_completion,
                                        color="success",
                                        className="mb-3",
                                        style={"height": "10px"}
                                    ),
                                    html.P(
                                        f"{album_completion}% of albums you listen to multiple tracks from",
                                        className="text-muted small mb-3"
                                    ),

                                    html.P("Sequential Listening Score", className="mb-1"),
                                    dbc.Progress(
                                        value=sequential_listening,
                                        color="success",
                                        className="mb-3",
                                        style={"height": "10px"}
                                    ),
                                    html.P(
                                        f"{sequential_listening}% of the time you listen to tracks from the same album in sequence",
                                        className="text-muted small"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ],
        className="mb-4 shadow"
    )

class SpotifyVisualizations:
    """Class for creating Spotify data visualizations."""

    def __init__(self):
        """Initialize with Spotify-themed colors."""
        self.theme = {
            'background_color': SPOTIFY_BLACK,
            'paper_color': '#121212',
            'text_color': SPOTIFY_WHITE,
            'secondary_color': SPOTIFY_GRAY,
            'accent_color': SPOTIFY_GREEN
        }

    def _apply_theme(self, fig):
        """Apply Spotify theme to a plotly figure."""
        fig.update_layout(
            plot_bgcolor=self.theme['background_color'],
            paper_bgcolor=self.theme['paper_color'],
            font_color=self.theme['text_color'],
            title_font_color=self.theme['accent_color'],
            legend_title_font_color=self.theme['accent_color'],
            coloraxis_colorbar=dict(
                tickfont=dict(color=self.theme['text_color'])
            )
        )

        # Update axes
        fig.update_xaxes(
            gridcolor=self.theme['secondary_color'],
            zerolinecolor=self.theme['secondary_color']
        )
        fig.update_yaxes(
            gridcolor=self.theme['secondary_color'],
            zerolinecolor=self.theme['secondary_color']
        )

        return fig

    def create_empty_chart(self, message="No data available"):
        """Create an empty chart with a message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=self.theme['text_color'], size=16)
        )

        # Add a subtle Spotify logo-like circle
        fig.add_shape(
            type="circle",
            xref="paper", yref="paper",
            x0=0.4, y0=0.4, x1=0.6, y1=0.6,
            line=dict(color=self.theme['accent_color'], width=2),
            fillcolor="rgba(29, 185, 84, 0.1)"
        )

        # Add a helpful message about data collection
        fig.add_annotation(
            text="Data will appear as you listen to more music",
            xref="paper", yref="paper",
            x=0.5, y=0.4, showarrow=False,
            font=dict(color=self.theme['secondary_color'], size=14)
        )

        return self._apply_theme(fig)


    def create_top_tracks_chart(self, df):
        """Create a bar chart of top tracks."""
        if df.empty or 'track' not in df.columns:
            # Return empty figure with a more user-friendly message
            fig = go.Figure()
            fig.add_annotation(
                text="Your top tracks will appear here as you listen to more music",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            fig.add_annotation(
                text="This chart shows your most frequently played tracks",
                xref="paper", yref="paper",
                x=0.5, y=0.4, showarrow=False,
                font=dict(color=self.theme['secondary_color'], size=14)
            )

            # Add a simple placeholder visualization
            for i in range(3):
                fig.add_shape(
                    type="rect",
                    xref="paper", yref="paper",
                    x0=0.3, y0=0.2 + (i * 0.05), x1=0.5 + (i * 0.1), y1=0.25 + (i * 0.05),
                    line=dict(color=self.theme['accent_color'], width=2),
                    fillcolor=f"rgba({29 + (i * 20)}, {185 - (i * 20)}, 84, 0.1)"
                )

            return self._apply_theme(fig)

        # Sort by rank if available, otherwise by popularity
        if 'rank' in df.columns:
            df = df.sort_values('rank')
        elif 'popularity' in df.columns:
            df = df.sort_values('popularity', ascending=False)

        # Limit to top 10 tracks
        df = df.head(10)

        # Create horizontal bar chart
        fig = px.bar(
            df,
            y='track',
            x='popularity' if 'popularity' in df.columns else [1] * len(df),
            orientation='h',
            color='artist',
            color_discrete_sequence=SPOTIFY_PALETTE,
            labels={
                'track': '',
                'popularity': 'Popularity Score',
                'artist': 'Artist'
            },
            title='Your Top Tracks'
        )

        # Add rank numbers if available
        if 'rank' in df.columns:
            for i, row in df.iterrows():
                fig.add_annotation(
                    x=0,
                    y=row['track'],
                    text=f"#{row['rank']}",
                    showarrow=False,
                    xanchor='right',
                    xshift=-10,
                    font=dict(color=self.theme['accent_color'], size=14)
                )

        # Add album cover images if image_url is available
        if 'image_url' in df.columns:
            for i, row in df.iterrows():
                if pd.notna(row.get('image_url')):
                    fig.add_layout_image(
                        dict(
                            source=row['image_url'],
                            xref="paper", yref="y",
                            x=1.05, y=row['track'],
                            sizex=0.1, sizey=0.1,
                            xanchor="left", yanchor="middle"
                        )
                    )

        # Update layout for better appearance
        fig.update_layout(
            height=600,
            xaxis_title="",
            yaxis_title="",
            legend_title_text="",
            yaxis={'categoryorder': 'array', 'categoryarray': df['track'].tolist()[::-1]}
        )

        # Add hover template with more info
        hover_template = (
            "<b>%{y}</b><br>" +
            "Artist: %{customdata[0]}<br>" +
            "Popularity: %{x}<br>"
        )

        if 'album' in df.columns:
            hover_template += "Album: %{customdata[1]}<br>"
            custom_data = df[['artist', 'album']].values
        else:
            custom_data = df[['artist']].values

        fig.update_traces(
            hovertemplate=hover_template,
            customdata=custom_data
        )

        return self._apply_theme(fig)

    def create_saved_tracks_timeline(self, df):
        """Create a timeline of saved tracks."""
        if df.empty or 'added_at' not in df.columns:
            # Return empty figure with a more user-friendly message
            fig = go.Figure()
            fig.add_annotation(
                text="Your saved tracks will appear here as you save more music",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            fig.add_annotation(
                text="This timeline shows when you saved tracks to your library",
                xref="paper", yref="paper",
                x=0.5, y=0.4, showarrow=False,
                font=dict(color=self.theme['secondary_color'], size=14)
            )

            # Add a simple placeholder timeline
            from datetime import datetime, timedelta
            now = datetime.now()

            # Create placeholder data
            dates = [(now - timedelta(days=i*3)) for i in range(3)]

            for i, date in enumerate(dates):
                fig.add_shape(
                    type="line",
                    xref="paper", yref="paper",
                    x0=0.3, y0=0.2 + (i * 0.05),
                    x1=0.7 - (i * 0.1), y1=0.2 + (i * 0.05),
                    line=dict(color=SPOTIFY_PALETTE[i], width=3)
                )

                # Add a dot at the end of each line
                fig.add_shape(
                    type="circle",
                    xref="paper", yref="paper",
                    x0=0.7 - (i * 0.1) - 0.01, y0=0.2 + (i * 0.05) - 0.01,
                    x1=0.7 - (i * 0.1) + 0.01, y1=0.2 + (i * 0.05) + 0.01,
                    fillcolor=SPOTIFY_PALETTE[i],
                    line=dict(color=SPOTIFY_PALETTE[i])
                )

            return self._apply_theme(fig)

        # Convert added_at to datetime
        df['added_at'] = pd.to_datetime(df['added_at'], format='ISO8601')

        # Sort by added_at
        df = df.sort_values('added_at', ascending=False)

        # Limit to most recent 10 tracks
        df = df.head(10)

        # Create a scatter plot instead of timeline for better visualization
        fig = px.scatter(
            df,
            x='added_at',
            y='track',
            color='artist',
            size='duration_minutes' if 'duration_minutes' in df.columns else None,
            color_discrete_sequence=SPOTIFY_PALETTE,
            labels={
                'added_at': 'Date Added',
                'track': 'Track',
                'artist': 'Artist',
                'duration_minutes': 'Duration (min)'
            },
            title='Recently Saved Tracks Timeline'
        )

        # Reverse y-axis to show most recent at the top
        fig.update_yaxes(autorange="reversed")

        # Add hover template with more info
        hover_template = (
            "<b>%{y}</b><br>" +
            "Artist: %{customdata[0]}<br>" +
            "Added: %{x}<br>"
        )

        custom_data_cols = ['artist']
        if 'album' in df.columns:
            hover_template += "Album: %{customdata[1]}<br>"
            custom_data_cols.append('album')

        if 'duration_minutes' in df.columns:
            hover_template += "Duration: %{customdata[" + str(len(custom_data_cols)) + "]} min<br>"
            custom_data_cols.append('duration_minutes')

        custom_data = df[custom_data_cols].values

        fig.update_traces(
            hovertemplate=hover_template,
            customdata=custom_data
        )

        # Update layout for better appearance
        fig.update_layout(
            height=500,
            xaxis_title="",
            yaxis_title=""
        )

        return self._apply_theme(fig)

    def create_saved_tracks_list(self, df):
        """Create a list view of saved tracks instead of a timeline chart."""
        if df.empty:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-heart", style={
                        'fontSize': '48px',
                        'color': SPOTIFY_GREEN,
                        'marginBottom': '20px'
                    }),
                    html.H4("No Saved Tracks Yet", style={
                        'color': SPOTIFY_WHITE,
                        'marginBottom': '10px'
                    }),
                    html.P("Your saved tracks will appear here when you start saving music to your library", style={
                        'color': SPOTIFY_GRAY,
                        'fontSize': '14px'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '40px'
                })
            ])

        # Create list of tracks
        track_items = []
        for idx, row in df.head(10).iterrows():  # Show only top 10
            track_item = html.Div([
                # Track image
                html.Div([
                    html.Img(
                        src=row.get('image_url', ''),
                        style={
                            'width': '50px',
                            'height': '50px',
                            'borderRadius': '8px',
                            'objectFit': 'cover'
                        }
                    ) if row.get('image_url') else html.Div([
                        html.I(className="fas fa-music", style={
                            'fontSize': '20px',
                            'color': SPOTIFY_GRAY
                        })
                    ], style={
                        'width': '50px',
                        'height': '50px',
                        'borderRadius': '8px',
                        'backgroundColor': '#333',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center'
                    })
                ], style={'marginRight': '15px'}),

                # Track info
                html.Div([
                    html.Div([
                        html.Span(row.get('track', 'Unknown Track'), style={
                            'color': SPOTIFY_WHITE,
                            'fontWeight': '600',
                            'fontSize': '16px'
                        }),
                    ]),
                    html.Div([
                        html.Span(f"by {row.get('artist', 'Unknown Artist')}", style={
                            'color': SPOTIFY_GRAY,
                            'fontSize': '14px'
                        }),
                        html.Span(" • ", style={'color': SPOTIFY_GRAY, 'margin': '0 8px'}),
                        html.Span(row.get('album', 'Unknown Album'), style={
                            'color': SPOTIFY_GRAY,
                            'fontSize': '14px'
                        })
                    ])
                ], style={'flex': '1'}),

                # Added date
                html.Div([
                    html.Span(
                        row.get('added_at', '').strftime('%b %d') if pd.notna(row.get('added_at')) else 'Recently',
                        style={
                            'color': SPOTIFY_GRAY,
                            'fontSize': '12px'
                        }
                    )
                ], style={'textAlign': 'right'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'padding': '12px 0',
                'borderBottom': '1px solid #333',
                'transition': 'background-color 0.2s ease'
            }, className='track-item')

            track_items.append(track_item)

        return html.Div([
            html.Div([
                html.H5(f"Recently Saved ({len(df)} total)", style={
                    'color': SPOTIFY_WHITE,
                    'marginBottom': '20px',
                    'fontSize': '18px'
                })
            ]),
            html.Div(track_items, style={
                'maxHeight': '400px',
                'overflowY': 'auto'
            })
        ], style={'padding': '20px'})

    def create_playlists_chart(self, df):
        """Create a bar chart of playlists by track count."""
        if df.empty or 'playlist' not in df.columns:
            # Return empty figure with a more user-friendly message
            fig = go.Figure()
            fig.add_annotation(
                text="Your playlists will appear here when data is available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            fig.add_annotation(
                text="This chart shows your playlists and their track counts",
                xref="paper", yref="paper",
                x=0.5, y=0.4, showarrow=False,
                font=dict(color=self.theme['secondary_color'], size=14)
            )

            # Add a simple placeholder bar chart
            for i in range(3):
                fig.add_shape(
                    type="rect",
                    xref="paper", yref="paper",
                    x0=0.3 + (i * 0.1), y0=0.2,
                    x1=0.35 + (i * 0.1), y1=0.2 + (0.1 * (i+1)),
                    line=dict(color=SPOTIFY_PALETTE[i], width=2),
                    fillcolor=SPOTIFY_PALETTE[i]
                )

            return self._apply_theme(fig)

        # Sort by track count
        if 'total_tracks' in df.columns:
            df = df.sort_values('total_tracks', ascending=False)

        # Limit to top 10 playlists
        df = df.head(10)

        # Create color column based on playlist visibility
        if 'public' in df.columns:
            df['visibility'] = df.apply(
                lambda x: 'Collaborative' if x.get('collaborative', False) else ('Public' if x.get('public', False) else 'Private'),
                axis=1
            )

        # Create bar chart
        fig = px.bar(
            df,
            x='playlist',
            y='total_tracks',
            color='visibility' if 'visibility' in df.columns else None,
            color_discrete_sequence=SPOTIFY_PALETTE,
            labels={
                'playlist': 'Playlist',
                'total_tracks': 'Number of Tracks',
                'visibility': 'Visibility'
            },
            title='Your Playlists'
        )

        # Update layout for better appearance
        fig.update_layout(
            height=500,
            xaxis_title="",
            yaxis_title="Number of Tracks"
        )

        # Rotate x-axis labels for better readability
        fig.update_xaxes(tickangle=45)

        return self._apply_theme(fig)

    def create_audio_features_radar(self, df):
        """Create a radar chart of audio features."""
        if df.empty or not all(col in df.columns for col in ['track', 'danceability', 'energy', 'valence']):
            # Return empty figure with a more user-friendly message
            fig = go.Figure()
            fig.add_annotation(
                text="Audio features will appear here as you listen to more music",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            fig.add_annotation(
                text="This chart shows the musical characteristics of your tracks",
                xref="paper", yref="paper",
                x=0.5, y=0.4, showarrow=False,
                font=dict(color=self.theme['secondary_color'], size=14)
            )

            # Create a simple placeholder radar chart
            categories = ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Instrumentalness']
            # Add the first value at the end to close the polygon
            categories.append(categories[0])

            # Create placeholder values
            values = [0.5, 0.6, 0.4, 0.7, 0.3, 0.5]  # Last value repeats first to close the polygon

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                fillcolor=f'rgba(29, 185, 84, 0.2)',  # Spotify green with transparency
                line=dict(color=SPOTIFY_GREEN, width=1, dash='dot'),
                name='Sample Features'
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=False
            )

            return self._apply_theme(fig)

        # Select features for radar chart
        features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']

        # Create radar chart
        fig = go.Figure()

        # Add a trace for each track
        for i, row in df.iterrows():
            values = [row[feature] for feature in features]
            # Add the first value again to close the loop
            values.append(values[0])

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=features + [features[0]],  # Add the first feature again to close the loop
                fill='toself',
                name=row['track'],
                line=dict(color=SPOTIFY_PALETTE[i % len(SPOTIFY_PALETTE)])
            ))

        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title='Audio Features Comparison',
            height=420,
            showlegend=True,
            margin=dict(t=50, b=50, l=20, r=20)
        )

        return self._apply_theme(fig)

    def create_genre_pie_chart(self, df):
        """Create a pie chart of top genres."""
        if df.empty or 'genre' not in df.columns:
            # Return empty figure with a more user-friendly message
            fig = go.Figure()
            fig.add_annotation(
                text="Listening to music to gather genre data...",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            fig.add_annotation(
                text="Your genre preferences will appear here as you listen",
                xref="paper", yref="paper",
                x=0.5, y=0.4, showarrow=False,
                font=dict(color=self.theme['secondary_color'], size=14)
            )

            # Add a simple placeholder circle
            fig.add_shape(
                type="circle",
                xref="paper", yref="paper",
                x0=0.3, y0=0.3, x1=0.7, y1=0.7,
                line=dict(color=self.theme['accent_color'], width=2),
                fillcolor="rgba(29, 185, 84, 0.1)"
            )

            return self._apply_theme(fig)

        # Sort by count and take top 10
        if 'count' not in df.columns:
            # If count column doesn't exist, create it by counting occurrences
            genre_counts = df['genre'].value_counts().reset_index()
            genre_counts.columns = ['genre', 'count']
            df = genre_counts

        # Filter out "unknown" placeholder genres
        df = df[df['genre'] != 'unknown']

        # If we have no genres after filtering, show a message
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Still gathering genre data...",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            fig.add_annotation(
                text="This may take a moment as we analyze your music",
                xref="paper", yref="paper",
                x=0.5, y=0.4, showarrow=False,
                font=dict(color=self.theme['secondary_color'], size=14)
            )
            return self._apply_theme(fig)

        df = df.sort_values('count', ascending=False).head(10)

        # If we have very few genres, add some placeholder categories
        if len(df) == 1:
            # Add a "Other" category to make the pie chart more meaningful
            df = pd.concat([
                df,
                pd.DataFrame([{'genre': 'Exploring more genres...', 'count': df['count'].iloc[0] * 0.2}])
            ])
        elif len(df) == 2:
            # Add a third category for better visualization
            df = pd.concat([
                df,
                pd.DataFrame([{'genre': 'Discovering new genres...', 'count': df['count'].iloc[0] * 0.15}])
            ])

        # Create pie chart
        fig = px.pie(
            df,
            values='count',
            names='genre',
            color_discrete_sequence=SPOTIFY_PALETTE,
            title='Your Top Genres',
            hole=0.4,  # Create a donut chart for better appearance
            labels={'count': 'Number of Tracks', 'genre': 'Genre'}
        )

        # Update layout for better appearance
        fig.update_layout(
            height=420,
            legend_title_text="",
            margin=dict(t=50, b=50, l=20, r=20),
            title={
                'text': 'Your Top Genres',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 24, 'color': self.theme['accent_color']}
            }
        )

        # Update traces for better hover info
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hoverinfo='label+percent+value',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}',
            marker=dict(
                line=dict(color=self.theme['background_color'], width=2),
                colors=SPOTIFY_PALETTE
            ),
            pull=[0.05 if i == 0 else 0 for i in range(len(df))]  # Pull out the first slice
        )

        return self._apply_theme(fig)

    def create_listening_patterns_heatmap(self, df, date_range_days=7):
        """Create a heatmap of listening patterns by day and hour."""
        if df.empty or 'day_of_week' not in df.columns or 'hour_of_day' not in df.columns:
            # Return empty figure with a more user-friendly message
            fig = go.Figure()
            fig.add_annotation(
                text="Listening patterns will appear here as you listen to more music",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            fig.add_annotation(
                text="This visualization shows when you listen to music most frequently",
                xref="paper", yref="paper",
                x=0.5, y=0.4, showarrow=False,
                font=dict(color=self.theme['secondary_color'], size=14)
            )

            # Add a simple placeholder visualization
            fig.add_shape(
                type="rect",
                xref="paper", yref="paper",
                x0=0.3, y0=0.2, x1=0.7, y1=0.3,
                line=dict(color=self.theme['accent_color'], width=2),
                fillcolor="rgba(29, 185, 84, 0.1)"
            )

            return self._apply_theme(fig)

        try:
            # Ensure day_of_week is a string and hour_of_day is an integer
            if 'day_name' in df.columns:
                # If day_name exists, use it instead of day_of_week
                df['day_of_week'] = df['day_name']
            elif df['day_of_week'].dtype != 'object':
                # Convert numeric day_of_week to day names
                day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                df['day_of_week'] = df['day_of_week'].astype(int).map(lambda x: day_names[x])

            # Ensure hour_of_day is an integer
            if df['hour_of_day'].dtype == 'object':
                # Try to convert string hours to integers
                df['hour_of_day'] = pd.to_numeric(df['hour_of_day'], errors='coerce').fillna(0).astype(int)

            # Create pivot table for heatmap - prefer minutes_played if available
            if 'minutes_played' in df.columns:
                value_column = 'minutes_played'
                title_suffix = ' (Minutes Played)'
                hover_label = 'Minutes'
            elif 'play_count' in df.columns:
                value_column = 'play_count'
                title_suffix = ' (Play Count)'
                hover_label = 'Plays'
            else:
                value_column = None
                title_suffix = ''
                hover_label = 'Count'

            pivot_df = df.pivot_table(
                index='day_of_week',
                columns='hour_of_day',
                values=value_column,
                aggfunc='sum' if value_column else 'size',
                fill_value=0
            )

            # Reorder days of week
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            # Make sure all days are in the pivot table
            for day in days_order:
                if day not in pivot_df.index:
                    pivot_df.loc[day] = [0] * len(pivot_df.columns)

            pivot_df = pivot_df.reindex(days_order)

            # Make sure all hours are in the pivot table
            all_hours = list(range(24))
            for hour in all_hours:
                if hour not in pivot_df.columns:
                    pivot_df[hour] = 0

            # Sort columns (hours)
            pivot_df = pivot_df.reindex(columns=sorted(pivot_df.columns))

            # Create heatmap using go.Heatmap instead of px.imshow for more control
            fig = go.Figure(data=go.Heatmap(
                z=pivot_df.values,
                x=[str(hour) for hour in pivot_df.columns],
                y=pivot_df.index,
                colorscale='Viridis',
                hoverongaps=False,
                hovertemplate=f'Day: %{{y}}<br>Hour: %{{x}}<br>{hover_label}: %{{z}}<extra></extra>'
            ))

            # Create title with date range
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range_days)
            date_range_text = f" ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"

            # Update layout for better appearance
            fig.update_layout(
                title=f'Your Listening Patterns{title_suffix}{date_range_text}',
                xaxis_title='Hour of Day',
                yaxis_title='Day of Week',
                height=500,
                xaxis=dict(
                    tickmode='array',
                    tickvals=[str(hour) for hour in range(24)],
                    ticktext=[f"{hour}:00" for hour in range(24)]
                )
            )

            return self._apply_theme(fig)

        except Exception as e:
            # If pivot table creation fails, return empty figure with error message
            print(f"Error creating listening patterns heatmap: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating listening patterns visualization: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            return self._apply_theme(fig)

    def create_top_artists_chart(self, df):
        """Create a bar chart of top artists."""
        if df.empty or 'artist' not in df.columns:
            # Return empty figure with a more user-friendly message
            fig = go.Figure()
            fig.add_annotation(
                text="Your top artists will appear here as you listen to more music",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            fig.add_annotation(
                text="This chart shows the artists you listen to most frequently",
                xref="paper", yref="paper",
                x=0.5, y=0.4, showarrow=False,
                font=dict(color=self.theme['secondary_color'], size=14)
            )

            # Add a simple placeholder visualization
            for i in range(3):
                fig.add_shape(
                    type="circle",
                    xref="paper", yref="paper",
                    x0=0.4 - (i * 0.05), y0=0.2 + (i * 0.05),
                    x1=0.6 - (i * 0.05), y1=0.3 + (i * 0.05),
                    line=dict(color=SPOTIFY_PALETTE[i], width=2),
                    fillcolor=f"rgba({29 + (i * 20)}, {185 - (i * 20)}, 84, 0.1)"
                )

            return self._apply_theme(fig)

        # Sort by rank or popularity
        if 'rank' in df.columns:
            df = df.sort_values('rank')
        elif 'popularity' in df.columns:
            df = df.sort_values('popularity', ascending=False)

        # Limit to top 10 artists
        df = df.head(10)

        # Create horizontal bar chart
        fig = px.bar(
            df,
            y='artist',
            x='popularity' if 'popularity' in df.columns else [1] * len(df),
            orientation='h',
            color='artist',
            color_discrete_sequence=SPOTIFY_PALETTE,
            labels={
                'artist': '',
                'popularity': 'Popularity Score'
            },
            title='Your Top Artists'
        )

        # Add rank numbers if available
        if 'rank' in df.columns:
            for i, row in df.iterrows():
                fig.add_annotation(
                    x=0,
                    y=row['artist'],
                    text=f"#{row['rank']}",
                    showarrow=False,
                    xanchor='right',
                    xshift=-10,
                    font=dict(color=self.theme['accent_color'], size=14)
                )

        # Add artist images if available
        if 'image_url' in df.columns:
            for i, row in df.iterrows():
                if pd.notna(row.get('image_url')):
                    fig.add_layout_image(
                        dict(
                            source=row['image_url'],
                            xref="paper", yref="y",
                            x=1.05, y=row['artist'],
                            sizex=0.1, sizey=0.1,
                            xanchor="left", yanchor="middle"
                        )
                    )

        # Update layout for better appearance
        fig.update_layout(
            height=600,
            xaxis_title="",
            yaxis_title="",
            showlegend=False,
            yaxis={'categoryorder': 'array', 'categoryarray': df['artist'].tolist()[::-1]}
        )

        # Add hover template with more info
        hover_template = (
            "<b>%{y}</b><br>" +
            "Popularity: %{x}<br>"
        )

        if 'genres' in df.columns and 'followers' in df.columns:
            hover_template += "Genres: %{customdata[0]}<br>Followers: %{customdata[1]:,}<br>"
            custom_data = df[['genres', 'followers']].values

            fig.update_traces(
                hovertemplate=hover_template,
                customdata=custom_data
            )

        return self._apply_theme(fig)

    def create_current_track_component(self, track_data):
        """Create a component to display currently playing track."""
        if not track_data or track_data.get('track') == 'None':
            return html.Div([
                html.H3("Not currently playing", style={'color': self.theme['text_color']}),
                html.P("Play something on Spotify to see it here", style={'color': self.theme['secondary_color']})
            ], style={'textAlign': 'center', 'padding': '20px'})

        # Calculate progress percentage
        progress_percent = (track_data['progress_ms'] / track_data['duration_ms'] * 100) if track_data['duration_ms'] > 0 else 0

        # Format duration and progress
        duration_sec = track_data['duration_ms'] / 1000
        progress_sec = track_data['progress_ms'] / 1000
        duration_str = f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}"
        progress_str = f"{int(progress_sec // 60)}:{int(progress_sec % 60):02d}"

        # Create component
        return html.Div([
            # Title
            html.H3("Now Playing", style={'color': self.theme['accent_color'], 'marginBottom': '20px'}),

            # Track info
            html.Div([
                # Album art
                html.Div([
                    html.Img(
                        src=track_data.get('image_url', ''),
                        style={'width': '100%', 'height': 'auto', 'borderRadius': '8px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}
                    ) if track_data.get('image_url') else html.Div(
                        style={'width': '100%', 'paddingBottom': '100%', 'backgroundColor': self.theme['secondary_color'], 'borderRadius': '8px'}
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # Track details
                html.Div([
                    html.H4(track_data['track'], style={'color': self.theme['text_color'], 'marginTop': '0'}),
                    html.P(track_data['artist'], style={'color': self.theme['secondary_color']}),
                    html.P(track_data['album'], style={'color': self.theme['secondary_color'], 'fontStyle': 'italic'})
                ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '5%'})
            ], style={'marginBottom': '20px'}),

            # Progress bar
            html.Div([
                html.Div([
                    # Progress time
                    html.Span(progress_str, style={'color': self.theme['secondary_color'], 'fontSize': '12px'}),

                    # Progress bar
                    html.Div([
                        html.Div(style={
                            'width': f'{progress_percent}%',
                            'backgroundColor': self.theme['accent_color'],
                            'height': '4px',
                            'borderRadius': '2px'
                        })
                    ], style={
                        'width': '100%',
                        'backgroundColor': self.theme['secondary_color'],
                        'height': '4px',
                        'borderRadius': '2px',
                        'margin': '8px 0'
                    }),

                    # Duration time
                    html.Span(duration_str, style={
                        'color': self.theme['secondary_color'],
                        'fontSize': '12px',
                        'float': 'right'
                    })
                ])
            ])
        ], style={
            'backgroundColor': '#181818',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.5)'
        })

    def create_wrapped_summary_component(self, summary_data):
        """Create an enhanced Spotify Wrapped style summary component with comprehensive insights in a 2x3 grid."""
        if not summary_data:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-music", style={
                        'fontSize': '48px',
                        'color': '#1DB954',
                        'marginBottom': '20px'
                    }),
                    html.H3("Your Musical Journey Awaits", style={
                        'color': '#FFFFFF',
                        'marginBottom': '10px'
                    }),
                    html.P("Start listening to unlock your personalized Spotify Wrapped insights!", style={
                        'color': '#B3B3B3',
                        'fontSize': '16px'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '40px',
                    'background': 'linear-gradient(135deg, rgba(29,185,84,0.1), rgba(0,212,255,0.1))',
                    'borderRadius': '16px',
                    'border': '1px solid rgba(29,185,84,0.3)'
                })
            ])

        # Calculate unique insights
        total_minutes = summary_data.get('total_minutes', 0)
        hours = total_minutes // 60

        # Get metrics with defaults
        metrics = summary_data.get('metrics', {})
        listening_style = metrics.get('listening_style', 'Eclectic Explorer')
        discovery_score = metrics.get('discovery_score', 75)
        variety_score = metrics.get('variety_score', 80)

        # Create enhanced 2x3 grid layout
        return html.Div([
            # Header with animated gradient
            html.Div([
                html.H2("🎵 Your Music DNA", style={
                    'background': 'linear-gradient(45deg, #1DB954, #00D4FF, #8B5CF6)',
                    'backgroundClip': 'text',
                    'WebkitBackgroundClip': 'text',
                    'color': 'transparent',
                    'fontSize': '28px',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'marginBottom': '30px'
                })
            ]),

            # Enhanced 2x3 grid layout
            html.Div([
                # Row 1: Listening Time, Top Genre, Music Mood
                html.Div([
                    # Listening Time
                    html.Div([
                        html.I(className="fas fa-clock", style={'fontSize': '24px', 'color': '#FF6B6B'}),
                        html.H3(f"{hours:,} Hours", style={'color': '#FFFFFF', 'margin': '10px 0 5px 0'}),
                        html.P("of pure musical bliss", style={'color': '#B3B3B3', 'fontSize': '14px'})
                    ], style={
                        'textAlign': 'center',
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, rgba(255,107,107,0.2), rgba(255,107,107,0.05))',
                        'borderRadius': '12px',
                        'border': '1px solid rgba(255,107,107,0.3)',
                        'transition': 'transform 0.3s ease',
                        'cursor': 'pointer',
                        'height': '120px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center'
                    }, className='hover-lift'),

                    # Top Genre
                    html.Div([
                        html.I(className="fas fa-palette", style={'fontSize': '24px', 'color': '#4ECDC4'}),
                        html.H3(summary_data.get('genre_highlight', {}).get('name', 'Exploring'), style={
                            'color': '#FFFFFF',
                            'margin': '10px 0 5px 0',
                            'fontSize': '16px'
                        }),
                        html.P("is your vibe", style={'color': '#B3B3B3', 'fontSize': '14px'})
                    ], style={
                        'textAlign': 'center',
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, rgba(78,205,196,0.2), rgba(78,205,196,0.05))',
                        'borderRadius': '12px',
                        'border': '1px solid rgba(78,205,196,0.3)',
                        'transition': 'transform 0.3s ease',
                        'cursor': 'pointer',
                        'height': '120px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center'
                    }, className='hover-lift'),

                    # Music Mood
                    html.Div([
                        html.I(className="fas fa-heart", style={'fontSize': '24px', 'color': '#FFD93D'}),
                        html.H3(summary_data.get('music_mood', {}).get('mood', 'Discovering'), style={
                            'color': '#FFFFFF',
                            'margin': '10px 0 5px 0',
                            'fontSize': '16px'
                        }),
                        html.P("energy level", style={'color': '#B3B3B3', 'fontSize': '14px'})
                    ], style={
                        'textAlign': 'center',
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, rgba(255,217,61,0.2), rgba(255,217,61,0.05))',
                        'borderRadius': '12px',
                        'border': '1px solid rgba(255,217,61,0.3)',
                        'transition': 'transform 0.3s ease',
                        'cursor': 'pointer',
                        'height': '120px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center'
                    }, className='hover-lift')
                ], style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(3, 1fr)',
                    'gap': '20px',
                    'marginBottom': '20px'
                }),

                # Row 2: Listening Style, Discovery Score, Variety Score
                html.Div([
                    # Listening Style
                    html.Div([
                        html.I(className="fas fa-headphones", style={'fontSize': '24px', 'color': '#9B59B6'}),
                        html.H3(listening_style, style={
                            'color': '#FFFFFF',
                            'margin': '10px 0 5px 0',
                            'fontSize': '16px'
                        }),
                        html.P("listening style", style={'color': '#B3B3B3', 'fontSize': '14px'})
                    ], style={
                        'textAlign': 'center',
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, rgba(155,89,182,0.2), rgba(155,89,182,0.05))',
                        'borderRadius': '12px',
                        'border': '1px solid rgba(155,89,182,0.3)',
                        'transition': 'transform 0.3s ease',
                        'cursor': 'pointer',
                        'height': '120px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center'
                    }, className='hover-lift'),

                    # Discovery Score
                    html.Div([
                        html.I(className="fas fa-search", style={'fontSize': '24px', 'color': '#E67E22'}),
                        html.H3(f"{discovery_score}%", style={
                            'color': '#FFFFFF',
                            'margin': '10px 0 5px 0',
                            'fontSize': '18px'
                        }),
                        html.P("discovery score", style={'color': '#B3B3B3', 'fontSize': '14px'})
                    ], style={
                        'textAlign': 'center',
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, rgba(230,126,34,0.2), rgba(230,126,34,0.05))',
                        'borderRadius': '12px',
                        'border': '1px solid rgba(230,126,34,0.3)',
                        'transition': 'transform 0.3s ease',
                        'cursor': 'pointer',
                        'height': '120px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center'
                    }, className='hover-lift'),

                    # Variety Score
                    html.Div([
                        html.I(className="fas fa-rainbow", style={'fontSize': '24px', 'color': '#3498DB'}),
                        html.H3(f"{variety_score}%", style={
                            'color': '#FFFFFF',
                            'margin': '10px 0 5px 0',
                            'fontSize': '18px'
                        }),
                        html.P("variety score", style={'color': '#B3B3B3', 'fontSize': '14px'})
                    ], style={
                        'textAlign': 'center',
                        'padding': '20px',
                        'background': 'linear-gradient(135deg, rgba(52,152,219,0.2), rgba(52,152,219,0.05))',
                        'borderRadius': '12px',
                        'border': '1px solid rgba(52,152,219,0.3)',
                        'transition': 'transform 0.3s ease',
                        'cursor': 'pointer',
                        'height': '120px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center'
                    }, className='hover-lift')
                ], style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(3, 1fr)',
                    'gap': '20px',
                    'marginBottom': '30px'
                })
            ]),

            # Enhanced fun fact section
            html.Div([
                html.Div([
                    html.I(className="fas fa-lightbulb", style={
                        'fontSize': '20px',
                        'color': '#8B5CF6',
                        'marginRight': '10px'
                    }),
                    html.Span("Fun Fact: ", style={
                        'color': '#8B5CF6',
                        'fontWeight': 'bold'
                    }),
                    html.Span(self._generate_enhanced_fun_fact(summary_data), style={
                        'color': '#FFFFFF'
                    })
                ], style={
                    'padding': '20px',
                    'background': 'linear-gradient(135deg, rgba(139,92,246,0.1), rgba(139,92,246,0.05))',
                    'borderRadius': '12px',
                    'border': '1px solid rgba(139,92,246,0.3)',
                    'textAlign': 'center'
                })
            ])
        ], style={
            'padding': '0',
            'borderRadius': '16px'
        })

    def _generate_enhanced_fun_fact(self, summary_data):
        """Generate an enhanced fun fact based on user's listening data with more variety."""
        import random

        total_minutes = summary_data.get('total_minutes', 0)
        hours = total_minutes // 60
        metrics = summary_data.get('metrics', {})
        discovery_score = metrics.get('discovery_score', 75)
        variety_score = metrics.get('variety_score', 80)

        # Create a pool of fun facts based on different metrics
        facts = []

        # Time-based facts
        if hours > 100:
            facts.extend([
                f"You've listened to enough music to soundtrack {hours // 24} full days!",
                f"Your {hours:,} hours of music could power a small radio station!",
                f"You've spent more time with music than most people spend sleeping in a week!"
            ])
        elif hours > 50:
            facts.extend([
                f"Your {hours} hours of music could fill a weekend music festival!",
                f"You've discovered enough music to soundtrack {hours // 2} movies!",
                f"Your listening time equals a full work week of pure musical bliss!"
            ])
        elif hours > 20:
            facts.extend([
                f"You've discovered {hours} hours of musical magic!",
                f"Your music collection could soundtrack a full day of adventures!",
                f"You've explored enough music to fill a long road trip!"
            ])
        else:
            facts.extend([
                "Your musical journey is just beginning - keep exploring!",
                "Every great music lover started with their first song!",
                "You're building the soundtrack to your life, one track at a time!"
            ])

        # Discovery-based facts
        if discovery_score > 85:
            facts.extend([
                f"With a {discovery_score}% discovery score, you're a true musical explorer!",
                "You're always ahead of the curve when it comes to finding new music!",
                "Your friends probably come to you for music recommendations!"
            ])
        elif discovery_score > 70:
            facts.extend([
                f"Your {discovery_score}% discovery score shows you love finding hidden gems!",
                "You strike the perfect balance between new discoveries and old favorites!",
                "You're building a diverse musical palette with every listen!"
            ])

        # Variety-based facts
        if variety_score > 85:
            facts.extend([
                f"With {variety_score}% variety, your taste spans musical universes!",
                "You're proof that good music has no boundaries!",
                "Your playlist could satisfy any mood or moment!"
            ])
        elif variety_score > 70:
            facts.extend([
                f"Your {variety_score}% variety score shows you appreciate musical diversity!",
                "You're open-minded about music and it shows in your listening habits!",
                "Your eclectic taste makes every listening session an adventure!"
            ])

        # Genre-based facts
        top_genre = summary_data.get('genre_highlight', {}).get('name', '')
        if top_genre and top_genre != 'Exploring New Genres':
            facts.append(f"Your love for {top_genre} shows you have refined musical taste!")

        # Mood-based facts
        mood = summary_data.get('music_mood', {}).get('mood', '')
        if mood and mood != 'Discovering Your Sound':
            facts.append(f"Your {mood} music mood perfectly matches your vibe!")

        # Return a random fact from the pool
        return random.choice(facts) if facts else "Your unique musical journey is creating its own story!"

    def create_top_track_highlight_component(self, track_data):
        """Create a highlight component for the top track."""
        return html.Div([
            # Track image
            html.Div([
                html.Img(
                    src=track_data.get('image_url', ''),
                    style={
                        'width': '120px',
                        'height': '120px',
                        'borderRadius': '12px',
                        'objectFit': 'cover',
                        'border': f'3px solid {SPOTIFY_GREEN}',
                        'boxShadow': f'0 0 20px {SPOTIFY_GREEN}50'
                    }
                ) if track_data.get('image_url') else html.Div([
                    html.I(className="fas fa-music", style={
                        'fontSize': '48px',
                        'color': SPOTIFY_GREEN
                    })
                ], style={
                    'width': '120px',
                    'height': '120px',
                    'borderRadius': '12px',
                    'backgroundColor': SPOTIFY_GRAY,
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'border': f'3px solid {SPOTIFY_GREEN}'
                })
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            # Track info
            html.Div([
                html.H3(track_data['track'], style={
                    'color': SPOTIFY_WHITE,
                    'fontSize': '20px',
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'textAlign': 'center'
                }),
                html.P(f"by {track_data['artist']}", style={
                    'color': SPOTIFY_GRAY,
                    'fontSize': '16px',
                    'marginBottom': '8px',
                    'textAlign': 'center'
                }),
                html.P(f"Album: {track_data.get('album', 'Unknown')}", style={
                    'color': SPOTIFY_GRAY,
                    'fontSize': '14px',
                    'marginBottom': '12px',
                    'textAlign': 'center'
                }),
                html.Div([
                    html.Span("🎵 Your Most Played Track", style={
                        'color': SPOTIFY_GREEN,
                        'fontSize': '14px',
                        'fontWeight': 'bold'
                    })
                ], style={'textAlign': 'center'})
            ])
        ], style={
            'padding': '20px',
            'textAlign': 'center',
            'background': 'linear-gradient(135deg, rgba(29,185,84,0.1), rgba(29,185,84,0.05))',
            'borderRadius': '16px',
            'border': f'1px solid {SPOTIFY_GREEN}30'
        })

    def create_top_artist_highlight_component(self, artist_data):
        """Create a highlight component for the top artist."""
        return html.Div([
            # Artist image
            html.Div([
                html.Img(
                    src=artist_data.get('image_url', ''),
                    style={
                        'width': '120px',
                        'height': '120px',
                        'borderRadius': '50%',
                        'objectFit': 'cover',
                        'border': f'3px solid {SPOTIFY_GREEN}',
                        'boxShadow': f'0 0 20px {SPOTIFY_GREEN}50'
                    }
                ) if artist_data.get('image_url') else html.Div([
                    html.I(className="fas fa-microphone", style={
                        'fontSize': '48px',
                        'color': SPOTIFY_GREEN
                    })
                ], style={
                    'width': '120px',
                    'height': '120px',
                    'borderRadius': '50%',
                    'backgroundColor': SPOTIFY_GRAY,
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'border': f'3px solid {SPOTIFY_GREEN}'
                })
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),

            # Artist info
            html.Div([
                html.H3(artist_data['artist'], style={
                    'color': SPOTIFY_WHITE,
                    'fontSize': '20px',
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'textAlign': 'center'
                }),
                html.P(f"{artist_data.get('play_count', 0)} plays", style={
                    'color': SPOTIFY_GRAY,
                    'fontSize': '16px',
                    'marginBottom': '8px',
                    'textAlign': 'center'
                }),
                html.P(f"Popularity: {artist_data.get('popularity', 0)}/100", style={
                    'color': SPOTIFY_GRAY,
                    'fontSize': '14px',
                    'marginBottom': '12px',
                    'textAlign': 'center'
                }),
                html.Div([
                    html.Span("🎤 Your Top Artist", style={
                        'color': SPOTIFY_GREEN,
                        'fontSize': '14px',
                        'fontWeight': 'bold'
                    })
                ], style={'textAlign': 'center'})
            ])
        ], style={
            'padding': '20px',
            'textAlign': 'center',
            'background': 'linear-gradient(135deg, rgba(29,185,84,0.1), rgba(29,185,84,0.05))',
            'borderRadius': '16px',
            'border': f'1px solid {SPOTIFY_GREEN}30'
        })


def create_track_list_item(track_data):
    """Create a styled list item for a track."""
    return html.Div([
        # Album cover
        html.Div([
            html.Img(
                src=track_data.get('image_url', ''),
                style={'width': '100%', 'height': 'auto', 'borderRadius': '4px'}
            ) if track_data.get('image_url') else html.Div(
                style={'width': '100%', 'paddingBottom': '100%', 'backgroundColor': SPOTIFY_GRAY, 'borderRadius': '4px'}
            )
        ], style={'width': '50px', 'display': 'inline-block', 'verticalAlign': 'middle'}),

        # Track info
        html.Div([
            html.Div(track_data['track'], style={'color': SPOTIFY_WHITE, 'fontWeight': 'bold'}),
            html.Div(track_data['artist'], style={'color': SPOTIFY_GRAY, 'fontSize': '0.9em'})
        ], style={'display': 'inline-block', 'verticalAlign': 'middle', 'marginLeft': '15px'})
    ], style={
        'padding': '10px',
        'borderRadius': '5px',
        'transition': 'background-color 0.3s',
        'cursor': 'pointer',
        ':hover': {
            'backgroundColor': '#1A1A1A'
        }
    })

def create_artist_list_item(artist_data):
    """Create a styled list item for an artist."""
    return html.Div([
        # Artist image
        html.Div([
            html.Img(
                src=artist_data.get('image_url', ''),
                style={'width': '100%', 'height': 'auto', 'borderRadius': '50%'}
            ) if artist_data.get('image_url') else html.Div(
                style={'width': '100%', 'paddingBottom': '100%', 'backgroundColor': SPOTIFY_GRAY, 'borderRadius': '50%'}
            )
        ], style={'width': '50px', 'display': 'inline-block', 'verticalAlign': 'middle'}),

        # Artist info
        html.Div([
            html.Div(artist_data['artist'], style={'color': SPOTIFY_WHITE, 'fontWeight': 'bold'}),
            html.Div(f"Popularity: {artist_data.get('popularity', 'N/A')}", style={'color': SPOTIFY_GRAY, 'fontSize': '0.9em'})
        ], style={'display': 'inline-block', 'verticalAlign': 'middle', 'marginLeft': '15px'})
    ], style={
        'padding': '10px',
        'borderRadius': '5px',
        'transition': 'background-color 0.3s',
        'cursor': 'pointer',
        ':hover': {
            'backgroundColor': '#1A1A1A'
        }
    })

def create_playlists_fancy_list(df):
    """Create a fancy list display for playlists."""
    if df.empty or 'playlist' not in df.columns:
        return html.Div([
            html.Div([
                html.I(className="fas fa-music", style={
                    'fontSize': '48px',
                    'color': SPOTIFY_GREEN,
                    'marginBottom': '20px'
                }),
                html.H4("No Playlists Found", style={
                    'color': SPOTIFY_WHITE,
                    'marginBottom': '10px'
                }),
                html.P("Your playlists will appear here when available", style={
                    'color': SPOTIFY_GRAY,
                    'fontSize': '14px'
                })
            ], style={
                'textAlign': 'center',
                'padding': '40px 20px',
                'backgroundColor': 'rgba(255, 255, 255, 0.05)',
                'borderRadius': '12px',
                'border': '1px dashed rgba(29, 185, 84, 0.3)'
            })
        ])

    # Sort by track count and limit to top 10
    if 'total_tracks' in df.columns:
        df = df.sort_values('total_tracks', ascending=False)
    df = df.head(10)

    playlist_items = []
    for _, row in df.iterrows():
        playlist_item = html.Div([
            # Playlist icon/image
            html.Div([
                html.Img(
                    src=row.get('image_url', ''),
                    style={
                        'width': '50px',
                        'height': '50px',
                        'borderRadius': '8px',
                        'objectFit': 'cover'
                    }
                ) if row.get('image_url') else html.Div([
                    html.I(className="fas fa-list-music", style={
                        'fontSize': '24px',
                        'color': SPOTIFY_GREEN
                    })
                ], style={
                    'width': '50px',
                    'height': '50px',
                    'borderRadius': '8px',
                    'backgroundColor': 'rgba(29, 185, 84, 0.1)',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'border': '1px solid rgba(29, 185, 84, 0.3)'
                })
            ], style={'display': 'inline-block', 'verticalAlign': 'middle'}),

            # Playlist info
            html.Div([
                html.Div([
                    html.Span(row['playlist'], style={
                        'color': SPOTIFY_WHITE,
                        'fontWeight': '600',
                        'fontSize': '16px',
                        'display': 'block',
                        'marginBottom': '4px'
                    }),
                    html.Span(f"{row.get('total_tracks', 0)} tracks", style={
                        'color': SPOTIFY_GRAY,
                        'fontSize': '14px'
                    }),
                    html.Span(" • ", style={'color': SPOTIFY_GRAY, 'margin': '0 8px'}),
                    html.Span(
                        'Public' if row.get('public', False) else 'Private',
                        style={
                            'color': SPOTIFY_GREEN if row.get('public', False) else '#F037A5',
                            'fontSize': '12px',
                            'fontWeight': '500',
                            'textTransform': 'uppercase',
                            'letterSpacing': '0.5px'
                        }
                    )
                ])
            ], style={
                'display': 'inline-block',
                'verticalAlign': 'middle',
                'marginLeft': '16px',
                'flex': '1'
            })
        ], className='playlist-item', style={
            'display': 'flex',
            'alignItems': 'center',
            'padding': '16px',
            'marginBottom': '12px',
            'backgroundColor': 'rgba(255, 255, 255, 0.03)',
            'borderRadius': '12px',
            'border': '1px solid rgba(255, 255, 255, 0.1)',
            'transition': 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            'cursor': 'pointer',
            'position': 'relative',
            'overflow': 'hidden'
        })

        playlist_items.append(playlist_item)

    return html.Div(playlist_items, style={
        'maxHeight': '400px',
        'overflowY': 'auto',
        'padding': '8px'
    })

def create_spotify_card(title, content, icon=None, card_type="default", className=None):
    """Create a styled card component for the dashboard with futuristic design."""

    # Enhanced header with futuristic styling
    header = html.Div([
        html.Div([
            html.I(className=f"fas {icon}", style={
                'marginRight': '12px',
                'fontSize': '1.2rem',
                'background': 'linear-gradient(45deg, #1DB954, #1ED760)',
                'backgroundClip': 'text',
                'WebkitBackgroundClip': 'text',
                'WebkitTextFillColor': 'transparent',
                'filter': 'drop-shadow(0 0 8px rgba(29, 185, 84, 0.3))'
            }) if icon else None,
            html.H3(title, style={
                'margin': '0',
                'display': 'inline',
                'fontFamily': 'Orbitron, monospace',
                'fontWeight': '600',
                'fontSize': '1.3rem',
                'background': 'linear-gradient(45deg, #FFFFFF, #B3B3B3)',
                'backgroundClip': 'text',
                'WebkitBackgroundClip': 'text',
                'WebkitTextFillColor': 'transparent'
            })
        ], style={'display': 'flex', 'alignItems': 'center'})
    ], style={
        'marginBottom': '4px',
        'position': 'relative',
        'paddingBottom': '0'
    })

    # Card type specific styling
    card_styles = {
        'default': 'spotify-card',
        'holographic': 'spotify-card card-holographic',
        'neon': 'spotify-card card-neon',
        'glass': 'spotify-card card-glass',
        'matrix': 'spotify-card card-matrix'
    }

    # Combine card type class with additional className if provided
    final_className = card_styles.get(card_type, 'spotify-card')
    if className:
        final_className += f' {className}'

    return html.Div([
        header,
        html.Div(content, style={
            'position': 'relative',
            'zIndex': '1',
            'flex': '1',
            'display': 'flex',
            'flexDirection': 'column'
        })
    ], className=final_className, style={
        'padding': '16px',
        'borderRadius': '16px',
        'margin': '15px 0',
        'position': 'relative',
        'overflow': 'hidden',
        'display': 'flex',
        'flexDirection': 'column'
    })

def create_progress_bar(value, max_value=100, label=None, color=SPOTIFY_GREEN):
    """Create a styled progress bar."""
    percent = (value / max_value) * 100 if max_value > 0 else 0

    return html.Div([
        html.Div(label, style={'color': SPOTIFY_WHITE, 'marginBottom': '5px'}) if label else None,
        html.Div([
            html.Div(style={
                'width': f'{percent}%',
                'backgroundColor': color,
                'height': '8px',
                'borderRadius': '4px'
            })
        ], style={
            'width': '100%',
            'backgroundColor': SPOTIFY_GRAY,
            'height': '8px',
            'borderRadius': '4px'
        }),
        html.Div(f"{value} / {max_value}", style={'color': SPOTIFY_GRAY, 'fontSize': '0.8em', 'marginTop': '5px'})
    ])

def create_spotify_button(text, id=None, color=SPOTIFY_GREEN):
    """Create a Spotify-styled button."""
    return html.Button(text, id=id, style={
        'backgroundColor': color,
        'color': SPOTIFY_BLACK,
        'border': 'none',
        'borderRadius': '30px',
        'padding': '12px 30px',
        'fontSize': '14px',
        'fontWeight': 'bold',
        'cursor': 'pointer',
        'textTransform': 'uppercase',
        'letterSpacing': '1px',
        'transition': 'all 0.3s',
        ':hover': {
            'backgroundColor': '#1ED760',
            'transform': 'scale(1.05)'
        }
    })

class SpotifyAnimations:
    """Class for creating Spotify Wrapped style animations using Manim."""

    @staticmethod
    def create_top_tracks_animation(tracks, output_file="top_tracks_animation.mp4"):
        """Create an animation showing top tracks."""
        from manim import Scene, Text, UP, DOWN, LEFT, RIGHT, ORIGIN, Write, FadeIn, Create, VGroup

        class TopTracksScene(Scene):
            def construct(self):
                # Set background color to Spotify black
                self.camera.background_color = "#191414"

                # Create title
                title = Text("Your Top Tracks", font="Arial", color="#1DB954")
                title.to_edge(UP, buff=1)

                # Create track texts
                track_texts = []
                for i, track in enumerate(tracks[:5]):  # Show top 5 tracks
                    text = Text(f"{i+1}. {track['track']} - {track['artist']}",
                               font="Arial", color="#FFFFFF")
                    text.scale(0.8)
                    track_texts.append(text)

                # Position track texts in a vertical stack
                VGroup(*track_texts).arrange(DOWN, buff=0.5).center()

                # Create animation sequence
                self.play(Write(title), run_time=1)
                self.wait(0.5)

                # Reveal tracks one by one
                for text in track_texts:
                    self.play(FadeIn(text, shift=UP*0.5), run_time=0.7)

                self.wait(2)

        # Render the animation
        scene = TopTracksScene()
        scene.render()

        return output_file

    @staticmethod
    def create_top_artists_animation(artists, output_file="top_artists_animation.mp4"):
        """Create an animation showing top artists."""
        from manim import Scene, Text, UP, DOWN, LEFT, RIGHT, ORIGIN, Write, FadeIn, Create, VGroup

        class TopArtistsScene(Scene):
            def construct(self):
                # Set background color to Spotify black
                self.camera.background_color = "#191414"

                # Create title
                title = Text("Your Top Artists", font="Arial", color="#1DB954")
                title.to_edge(UP, buff=1)

                # Create artist texts
                artist_texts = []
                for i, artist in enumerate(artists[:5]):  # Show top 5 artists
                    text = Text(f"{i+1}. {artist['artist']}",
                               font="Arial", color="#FFFFFF")
                    text.scale(0.8)
                    artist_texts.append(text)

                # Position artist texts in a vertical stack
                VGroup(*artist_texts).arrange(DOWN, buff=0.5).center()

                # Create animation sequence
                self.play(Write(title), run_time=1)
                self.wait(0.5)

                # Reveal artists one by one
                for text in artist_texts:
                    self.play(FadeIn(text, shift=UP*0.5), run_time=0.7)

                self.wait(2)

        # Render the animation
        scene = TopArtistsScene()
        scene.render()

        return output_file

    @staticmethod
    def create_genre_animation(genres, output_file="genre_animation.mp4"):
        """Create an animation showing top genres."""
        from manim import Scene, Text, UP, DOWN, LEFT, RIGHT, ORIGIN, Write, FadeIn, VGroup

        class GenreScene(Scene):
            def construct(self):
                # Set background color to Spotify black
                self.camera.background_color = "#191414"

                # Create title
                header = Text("Your Top Genres", font="Arial", color="#1DB954")
                header.to_edge(UP, buff=1)

                # Create genre text objects
                genre_texts = []
                colors = ["#1DB954", "#1ED760", "#2D46B9", "#F037A5", "#FFFF00"]

                for i, genre in enumerate(genres[:5]):  # Show top 5 genres
                    color = colors[i % len(colors)]
                    text = Text(genre, font="Arial", color=color)
                    text.scale(1.5 - (i * 0.2))  # Decreasing size
                    genre_texts.append(text)

                # Position genre texts in a vertical stack
                VGroup(*genre_texts).arrange(DOWN, buff=0.4).center()

                # Create animation sequence
                self.play(Write(header), run_time=1)
                self.wait(0.5)

                # Reveal genres one by one
                for text in genre_texts:
                    self.play(FadeIn(text, shift=UP*0.5), run_time=0.7)

                self.wait(1)

                # Final flourish - shuffle effect
                self.play(
                    *[text.animate.shift(0.2 * UP * ((-1) ** i)) for i, text in enumerate(genre_texts)],
                    rate_func=lambda t: np.sin(t * np.pi * 2),
                    run_time=1.5
                )
                self.wait(1)

        # Render the animation
        scene = GenreScene()
        scene.render()

        return output_file

    @staticmethod
    def create_listening_stats_animation(minutes_listened, output_file="listening_stats_animation.mp4"):
        """Create an animation showing listening statistics."""
        from manim import Scene, Text, UP, DOWN, LEFT, RIGHT, ORIGIN, Write, FadeIn, FadeOut, Integer

        class ListeningStatsScene(Scene):
            def construct(self):
                # Set background color to Spotify black
                self.camera.background_color = "#191414"

                # Create text objects
                header = Text("Your Listening Time", font="Arial", color="#1DB954")

                # Format minutes into hours and minutes
                hours = minutes_listened // 60
                mins = minutes_listened % 60
                time_str = f"{hours:,} hours {mins} minutes"

                time_text = Text(time_str, font="Arial", color="#FFFFFF")
                subtext = Text("of music in 2024", font="Arial", color="#AAAAAA")

                # Position text
                header.to_edge(UP, buff=1)
                time_text.scale(1.5)
                subtext.next_to(time_text, DOWN, buff=0.5)

                # Create animation sequence
                self.play(Write(header), run_time=1)
                self.wait(0.5)

                # Counting animation for time
                counter = Integer(0)
                counter.scale(1.5)
                counter.set_color("#FFFFFF")

                self.play(FadeIn(counter))
                self.play(
                    counter.animate.set_value(minutes_listened),
                    run_time=3,
                    rate_func=lambda t: t
                )
                self.play(FadeOut(counter))

                # Show formatted time
                self.play(FadeIn(time_text), run_time=1)
                self.wait(0.5)

                # Show subtext
                self.play(Write(subtext), run_time=1)
                self.wait(1)

                # Final flourish
                self.play(
                    time_text.animate.set_color("#1DB954"),
                    run_time=1
                )
                self.wait(1)

        # Render the animation
        scene = ListeningStatsScene()
        scene.render()

        return output_file

    @staticmethod
    def create_mood_animation(mood, valence, energy, output_file="mood_animation.mp4"):
        """Create an animation showing the user's music mood."""

        class MoodScene(Scene):
            def construct(self):
                # Set background color to Spotify black
                self.camera.background_color = "#191414"

                # Create text objects
                header = Text("Your Music Mood", font="Arial", color="#1DB954")
                mood_text = Text(mood, font="Arial", color="#FFFFFF")

                # Create mood visualization
                mood_circle = Circle(radius=2, color="#1DB954", fill_opacity=0.5)

                # Position elements
                header.to_edge(UP, buff=1)
                mood_text.next_to(header, DOWN, buff=1)
                mood_text.scale(1.5)

                # Create animation sequence
                self.play(Write(header), run_time=1)
                self.wait(0.5)

                # Reveal mood text
                self.play(Write(mood_text), run_time=1.5)
                self.wait(0.5)

                # Show mood circle
                self.play(
                    FadeIn(mood_circle),
                    mood_text.animate.scale(0.8).to_edge(UP, buff=2),
                    run_time=1.5
                )

                # Create and animate valence and energy bars
                valence_label = Text("Valence", font="Arial", color="#AAAAAA").scale(0.7)
                energy_label = Text("Energy", font="Arial", color="#AAAAAA").scale(0.7)

                valence_bar = Rectangle(height=0.3, width=4, fill_opacity=1, color="#1DB954")
                energy_bar = Rectangle(height=0.3, width=4, fill_opacity=1, color="#1DB954")

                valence_bg = Rectangle(height=0.3, width=4, fill_opacity=0.3, color="#AAAAAA")
                energy_bg = Rectangle(height=0.3, width=4, fill_opacity=0.3, color="#AAAAAA")

                # Position bars
                valence_group = VGroup(valence_label, valence_bg)
                energy_group = VGroup(energy_label, energy_bg)

                valence_group.arrange(DOWN, buff=0.2)
                energy_group.arrange(DOWN, buff=0.2)

                VGroup(valence_group, energy_group).arrange(DOWN, buff=0.7).to_edge(DOWN, buff=1)

                # Align bars
                valence_bar.move_to(valence_bg)
                energy_bar.move_to(energy_bg)

                # Set initial width to 0
                valence_bar.stretch(0.01, 0)
                energy_bar.stretch(0.01, 0)

                # Align to left
                valence_bar.align_to(valence_bg, LEFT)
                energy_bar.align_to(energy_bg, LEFT)

                # Show labels and backgrounds
                self.play(
                    FadeIn(valence_group),
                    FadeIn(energy_group),
                    run_time=1
                )

                # Add bars and animate to correct width
                self.play(FadeIn(valence_bar), FadeIn(energy_bar))
                self.play(
                    valence_bar.animate.stretch(valence, 0),
                    energy_bar.animate.stretch(energy, 0),
                    run_time=2,
                    rate_func=lambda t: t
                )

                self.wait(1)

                # Final flourish - pulse the mood circle
                self.play(
                    mood_circle.animate.scale(1.2),
                    rate_func=lambda t: np.sin(t * np.pi),
                    run_time=1
                )
                self.wait(1)

        # Render the animation
        scene = MoodScene()
        scene.render()

        return output_file

# Export the main visualization classes and helper functions
__all__ = ['SpotifyVisualizations', 'SpotifyAnimations', 'create_spotify_card',
           'create_track_list_item', 'create_artist_list_item', 'create_stat_card',
           'create_progress_bar', 'create_spotify_button']


