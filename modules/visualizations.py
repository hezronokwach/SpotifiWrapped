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
    """Create a stat card for displaying metrics."""
    return html.Div([
        html.Div([
            html.I(className=f"fas {icon}", style={
                'fontSize': '24px',
                'color': color
            })
        ], style={
            'textAlign': 'center',
            'marginBottom': '10px'
        }),
        html.H4(value, style={
            'textAlign': 'center',
            'color': SPOTIFY_WHITE,
            'fontSize': '28px',
            'fontWeight': 'bold',
            'marginBottom': '5px'
        }),
        html.P(title, style={
            'textAlign': 'center',
            'color': SPOTIFY_GRAY,
            'fontSize': '14px'
        })
    ], style={
        'backgroundColor': '#181818',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
        'height': '100%'
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
        style={"max-width": "200px", "margin": "10px"}
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

        # Create timeline
        fig = px.timeline(
            df,
            x_start='added_at',
            x_end='end_date' if 'end_date' in df.columns else 'added_at',
            y='track',
            color='artist',
            color_discrete_sequence=SPOTIFY_PALETTE,
            labels={
                'added_at': 'Date Added',
                'track': '',
                'artist': 'Artist'
            },
            title='Recently Saved Tracks'
        )

        # Reverse y-axis to show most recent at the top
        fig.update_yaxes(autorange="reversed")

        # Add hover template with more info
        hover_template = (
            "<b>%{y}</b><br>" +
            "Artist: %{customdata[0]}<br>" +
            "Added: %{x}<br>"
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

        # Update layout for better appearance
        fig.update_layout(
            height=500,
            xaxis_title="",
            yaxis_title=""
        )

        return self._apply_theme(fig)

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
            height=600,
            showlegend=True
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
            height=500,
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

    def create_listening_patterns_heatmap(self, df):
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

            # Create pivot table for heatmap
            pivot_df = df.pivot_table(
                index='day_of_week',
                columns='hour_of_day',
                values='play_count' if 'play_count' in df.columns else None,
                aggfunc='sum' if 'play_count' in df.columns else 'size',
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
                hovertemplate='Day: %{y}<br>Hour: %{x}<br>Play Count: %{z}<extra></extra>'
            ))

            # Update layout for better appearance
            fig.update_layout(
                title='Your Listening Patterns',
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
        """Create a Spotify Wrapped style summary component."""
        if not summary_data:
            return html.Div([
                html.H3("Wrapped Summary Not Available", style={'color': self.theme['text_color']}),
                html.P("We need more listening data to generate your Wrapped summary.", style={'color': self.theme['secondary_color']})
            ], style={'textAlign': 'center', 'padding': '20px'})

        # Create component
        return html.Div([
            # Title
            html.H2("Your 2023 Wrapped", style={
                'color': self.theme['accent_color'],
                'textAlign': 'center',
                'fontSize': '32px',
                'marginBottom': '30px'
            }),

            # Top track section
            html.Div([
                html.H3("Your Top Track", style={'color': self.theme['text_color'], 'textAlign': 'center'}),
                html.Div([
                    html.H1(summary_data['top_track']['name'], style={
                        'color': self.theme['accent_color'],
                        'textAlign': 'center',
                        'fontSize': '48px',
                        'margin': '10px 0'
                    }),
                    html.H3(f"by {summary_data['top_track']['artist']}", style={
                        'color': self.theme['secondary_color'],
                        'textAlign': 'center',
                        'fontWeight': 'normal'
                    })
                ], style={
                    'backgroundColor': '#181818',
                    'padding': '30px',
                    'borderRadius': '10px',
                    'margin': '20px 0'
                })
            ]),

            # Top artist section
            html.Div([
                html.H3("Your Top Artist", style={'color': self.theme['text_color'], 'textAlign': 'center'}),
                html.Div([
                    html.H1(summary_data['top_artist']['name'], style={
                        'color': self.theme['accent_color'],
                        'textAlign': 'center',
                        'fontSize': '48px',
                        'margin': '10px 0'
                    }),
                    html.H3(f"Genres: {summary_data['top_artist']['genres']}", style={
                        'color': self.theme['secondary_color'],
                        'textAlign': 'center',
                        'fontWeight': 'normal'
                    })
                ], style={
                    'backgroundColor': '#181818',
                    'padding': '30px',
                    'borderRadius': '10px',
                    'margin': '20px 0'
                })
            ]),
        ], style={
            'backgroundColor': '#121212',
            'padding': '30px',
            'borderRadius': '15px',
            'boxShadow': '0 8px 16px rgba(0,0,0,0.5)'
        })

    def create_sound_story_component(self, summary_data, spotify_api=None):
        """Create a combined Sound Story and Music Mood component with Top Genre integration."""
        if not summary_data:
            return html.Div([
                html.H3("Sound Story Not Available", style={'color': self.theme['text_color']}),
                html.P("We need more listening data to generate your Sound Story.", style={'color': self.theme['secondary_color']})
            ], style={'textAlign': 'center', 'padding': '20px'})

        # Create component
        return html.Div([
            # Main title and subtitle
            html.H2("Your Sound Story",
                style={
                    'color': self.theme['accent_color'],
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
                    'color': self.theme['text_color'],
                    'textAlign': 'center',
                    'fontSize': '1.2rem',
                    'marginBottom': '40px',
                    'opacity': '0.9'
                }
            ),

            # Main content grid - 4 columns
            html.Div([
                # Column 1: Music Mood
                html.Div([
                    html.I(className="fas fa-smile", style={
                        'fontSize': '2rem',
                        'color': self.theme['accent_color'],
                        'marginBottom': '15px'
                    }),
                    html.H3("Your Music Mood", style={'color': self.theme['text_color'], 'marginBottom': '10px'}),
                    html.H4(summary_data['music_mood']['mood'],
                        style={'color': self.theme['accent_color'], 'fontSize': '2rem', 'marginBottom': '15px'}),

                    # Mood visualization - Valence
                    html.Div([
                        html.Span("Positivity", style={'color': self.theme['text_color']}),
                        html.Div([
                            html.Div(style={
                                'width': f"{summary_data['music_mood']['valence'] * 100}%",
                                'backgroundColor': self.theme['accent_color'],
                                'height': '8px',
                                'borderRadius': '4px'
                            })
                        ], style={
                            'width': '100%',
                            'backgroundColor': self.theme['secondary_color'],
                            'height': '8px',
                            'borderRadius': '4px',
                            'margin': '5px 0 15px 0'
                        })
                    ]),

                    # Mood visualization - Energy
                    html.Div([
                        html.Span("Energy", style={'color': self.theme['text_color']}),
                        html.Div([
                            html.Div(style={
                                'width': f"{summary_data['music_mood']['energy'] * 100}%",
                                'backgroundColor': self.theme['accent_color'],
                                'height': '8px',
                                'borderRadius': '4px'
                            })
                        ], style={
                            'width': '100%',
                            'backgroundColor': self.theme['secondary_color'],
                            'height': '8px',
                            'borderRadius': '4px',
                            'margin': '5px 0'
                        })
                    ]),

                    # Mood description
                    html.P(self._get_mood_description(summary_data['music_mood']['mood']),
                        style={'color': self.theme['secondary_color'], 'fontSize': '0.9rem', 'marginTop': '15px'})
                ], style={
                    'textAlign': 'center',
                    'padding': '25px',
                    'backgroundColor': '#181818',
                    'borderRadius': '15px',
                    'height': '100%'
                }, className='col-md-3'),

                # Column 2: Top Genre
                html.Div([
                    html.I(className="fas fa-tag", style={
                        'fontSize': '2rem',
                        'color': self.theme['accent_color'],
                        'marginBottom': '15px'
                    }),
                    html.H3("Your Top Genre", style={'color': self.theme['text_color'], 'marginBottom': '10px'}),
                    html.H4(summary_data['genre_highlight']['name'],
                        style={'color': self.theme['accent_color'], 'fontSize': '2rem', 'marginBottom': '15px'}),

                    # Genre artist image (if available) or icon
                    self._get_genre_artist_image(summary_data['genre_highlight']['name'], spotify_api),

                    # Genre description
                    html.P(self._get_genre_description(summary_data['genre_highlight']['name']),
                        style={'color': self.theme['secondary_color'], 'fontSize': '0.9rem', 'marginTop': '15px'})
                ], style={
                    'textAlign': 'center',
                    'padding': '25px',
                    'backgroundColor': '#181818',
                    'borderRadius': '15px',
                    'height': '100%'
                }, className='col-md-3'),

                # Column 3: Listening Style
                html.Div([
                    html.I(className="fas fa-headphones", style={
                        'fontSize': '2rem',
                        'color': self.theme['accent_color'],
                        'marginBottom': '15px'
                    }),
                    html.H3("Your Listening Style", style={'color': self.theme['text_color'], 'marginBottom': '10px'}),

                    # Get listening style from metrics if available
                    html.H4(summary_data.get('metrics', {}).get('listening_style', 'Eclectic Explorer'),
                        style={'color': self.theme['accent_color'], 'fontSize': '2rem', 'marginBottom': '15px'}),

                    # Listening style visualization
                    html.Div([
                        html.Div([
                            html.Span("Variety", style={'color': self.theme['text_color']}),
                            html.Div([
                                html.Div(style={
                                    'width': f"{summary_data.get('metrics', {}).get('variety_score', 50)}%",
                                    'backgroundColor': self.theme['accent_color'],
                                    'height': '8px',
                                    'borderRadius': '4px'
                                })
                            ], style={
                                'width': '100%',
                                'backgroundColor': self.theme['secondary_color'],
                                'height': '8px',
                                'borderRadius': '4px',
                                'margin': '5px 0 15px 0'
                            })
                        ]),

                        html.Div([
                            html.Span("Discovery", style={'color': self.theme['text_color']}),
                            html.Div([
                                html.Div(style={
                                    'width': f"{summary_data.get('metrics', {}).get('discovery_score', 50)}%",
                                    'backgroundColor': self.theme['accent_color'],
                                    'height': '8px',
                                    'borderRadius': '4px'
                                })
                            ], style={
                                'width': '100%',
                                'backgroundColor': self.theme['secondary_color'],
                                'height': '8px',
                                'borderRadius': '4px',
                                'margin': '5px 0'
                            })
                        ])
                    ]),

                    # Listening style description
                    html.P(self._get_listening_style_description(summary_data.get('metrics', {}).get('listening_style', 'Eclectic Explorer')),
                        style={'color': self.theme['secondary_color'], 'fontSize': '0.9rem', 'marginTop': '15px'})
                ], style={
                    'textAlign': 'center',
                    'padding': '25px',
                    'backgroundColor': '#181818',
                    'borderRadius': '15px',
                    'height': '100%'
                }, className='col-md-3'),

                # Column 4: Tempo (New)
                html.Div([
                    html.I(className="fas fa-running", style={
                        'fontSize': '2rem',
                        'color': self.theme['accent_color'],
                        'marginBottom': '15px'
                    }),
                    html.H3("Your Music Tempo", style={'color': self.theme['text_color'], 'marginBottom': '10px'}),

                    # Get tempo from summary data or use default
                    html.H4(f"{int(summary_data.get('tempo', 120))} BPM",
                        style={'color': self.theme['accent_color'], 'fontSize': '2rem', 'marginBottom': '15px'}),

                    # Tempo visualization - use a gauge-like display
                    html.Div([
                        html.Div(style={
                            'display': 'flex',
                            'justifyContent': 'space-between',
                            'marginBottom': '5px'
                        }, children=[
                            html.Span("Slow", style={'color': self.theme['text_color']}),
                            html.Span("Fast", style={'color': self.theme['text_color']})
                        ]),
                        html.Div([
                            html.Div(style={
                                'width': f"{min(100, max(0, (int(summary_data.get('tempo', 120)) - 60) / 1.8))}%",
                                'backgroundColor': self.theme['accent_color'],
                                'height': '8px',
                                'borderRadius': '4px'
                            })
                        ], style={
                            'width': '100%',
                            'backgroundColor': self.theme['secondary_color'],
                            'height': '8px',
                            'borderRadius': '4px',
                            'margin': '5px 0 15px 0'
                        })
                    ]),

                    # Tempo description
                    html.P(
                        self._get_tempo_description(int(summary_data.get('tempo', 120))),
                        style={'color': self.theme['secondary_color'], 'fontSize': '0.9rem', 'marginTop': '15px'}
                    )
                ], style={
                    'textAlign': 'center',
                    'padding': '25px',
                    'backgroundColor': '#181818',
                    'borderRadius': '15px',
                    'height': '100%'
                }, className='col-md-3')
            ], className='row')
        ], style={
            'backgroundColor': '#121212',
            'padding': '30px',
            'borderRadius': '15px',
            'boxShadow': '0 8px 16px rgba(0,0,0,0.5)',
            'margin': '20px 0'
        })

    def _get_mood_description(self, mood):
        """Get a description for a given mood."""
        descriptions = {
            "Happy & Energetic": "You gravitate toward upbeat, positive music that keeps your energy high. Your playlist is the life of the party!",
            "Peaceful & Positive": "You enjoy uplifting music with a calmer vibe. Your playlist is perfect for relaxing while staying positive.",
            "Angry & Intense": "You connect with passionate, intense music that expresses stronger emotions. Your playlist has depth and power.",
            "Sad & Chill": "You appreciate reflective, emotional music with a laid-back feel. Your playlist tells deep stories and creates atmosphere."
        }
        return descriptions.get(mood, "Your musical taste creates a unique emotional landscape that reflects your personality.")

    def _get_genre_artist_image(self, genre_name, spotify_api):
        """Get a random artist image for a genre."""
        import random

        if not spotify_api or genre_name == 'unknown' or genre_name == 'Exploring New Genres':
            # Return a generic icon if no API or unknown genre
            return html.Div([
                html.I(className=self._get_genre_icon(genre_name), style={
                    'fontSize': '4rem',
                    'color': self.theme['accent_color'],
                    'opacity': '0.8',
                    'marginBottom': '20px'
                })
            ])

        try:
            # Get artists for this genre
            artists = spotify_api.get_artists_by_genre(genre_name, limit=10)

            if not artists:
                # Fall back to icon if no artists found
                return html.Div([
                    html.I(className=self._get_genre_icon(genre_name), style={
                        'fontSize': '4rem',
                        'color': self.theme['accent_color'],
                        'opacity': '0.8',
                        'marginBottom': '20px'
                    })
                ])

            # Filter artists with images
            artists_with_images = [artist for artist in artists if artist.get('image_url')]

            if not artists_with_images:
                # Fall back to icon if no artists have images
                return html.Div([
                    html.I(className=self._get_genre_icon(genre_name), style={
                        'fontSize': '4rem',
                        'color': self.theme['accent_color'],
                        'opacity': '0.8',
                        'marginBottom': '20px'
                    })
                ])

            # Pick a random artist
            random_artist = random.choice(artists_with_images)

            # Return the artist image with name
            return html.Div([
                html.Img(
                    src=random_artist['image_url'],
                    style={
                        'width': '120px',
                        'height': '120px',
                        'borderRadius': '50%',
                        'objectFit': 'cover',
                        'border': f'3px solid {self.theme["accent_color"]}',
                        'marginBottom': '10px'
                    }
                ),
                html.P(
                    f"Artist in this genre: {random_artist['name']}",
                    style={
                        'color': self.theme['secondary_color'],
                        'fontSize': '0.9rem',
                        'marginBottom': '15px'
                    }
                )
            ])

        except Exception as e:
            print(f"Error getting artist image for genre {genre_name}: {e}")
            # Fall back to icon on error
            return html.Div([
                html.I(className=self._get_genre_icon(genre_name), style={
                    'fontSize': '4rem',
                    'color': self.theme['accent_color'],
                    'opacity': '0.8',
                    'marginBottom': '20px'
                })
            ])

    def _get_genre_icon(self, genre):
        """Get an appropriate icon for a genre."""
        genre = genre.lower()
        if any(word in genre for word in ['rock', 'metal', 'punk', 'grunge']):
            return "fa-guitar"
        elif any(word in genre for word in ['pop', 'dance', 'disco']):
            return "fa-music"
        elif any(word in genre for word in ['rap', 'hip hop', 'hip-hop']):
            return "fa-microphone"
        elif any(word in genre for word in ['electronic', 'techno', 'house', 'edm']):
            return "fa-laptop"
        elif any(word in genre for word in ['jazz', 'blues', 'soul']):
            return "fa-saxophone"
        elif any(word in genre for word in ['classical', 'orchestra']):
            return "fa-violin"
        elif any(word in genre for word in ['country', 'folk']):
            return "fa-hat-cowboy"
        else:
            return "fa-compact-disc"

    def _get_genre_description(self, genre):
        """Get a description for a genre."""
        genre = genre.lower()
        if any(word in genre for word in ['rock', 'metal', 'punk', 'grunge']):
            return "You're drawn to the raw energy and authentic expression of rock music. The electric guitar speaks to your soul."
        elif any(word in genre for word in ['pop']):
            return "You appreciate catchy melodies and polished production. Pop music's universal appeal resonates with your taste."
        elif any(word in genre for word in ['rap', 'hip hop', 'hip-hop']):
            return "You connect with the lyrical prowess and cultural significance of hip-hop. The rhythm and poetry of rap speaks to you."
        elif any(word in genre for word in ['electronic', 'techno', 'house', 'edm']):
            return "You're attracted to innovative sounds and futuristic production. Electronic music's endless possibilities match your forward-thinking nature."
        elif any(word in genre for word in ['jazz', 'blues', 'soul']):
            return "You value musical sophistication and emotional depth. The improvisational nature of jazz reflects your appreciation for spontaneity."
        elif any(word in genre for word in ['classical', 'orchestra']):
            return "You have a taste for timeless composition and musical complexity. Classical music's rich history and depth resonate with you."
        elif any(word in genre for word in ['country', 'folk']):
            return "You connect with authentic storytelling and traditional musical roots. The sincerity of country and folk music speaks to your values."
        else:
            return f"Your preference for {genre} shows your unique musical personality and specific taste that sets you apart."

    def _get_listening_style_description(self, style):
        """Get a description for a listening style."""
        descriptions = {
            "Album Purist": "You appreciate albums as complete works of art, listening to them from start to finish as the artist intended.",
            "Album Explorer": "You enjoy exploring albums but don't always listen to them in sequence or completion.",
            "Track Hopper": "You prefer individual tracks over full albums, creating your own unique listening journey.",
            "Mood Curator": "You select music based on mood and atmosphere, regardless of album structure.",
            "Eclectic Explorer": "You have diverse musical interests and enjoy discovering new sounds across different genres.",
            "Loyal Listener": "You have strong favorites and return to them regularly, building deep connections with your preferred artists.",
            "Trend Follower": "You stay current with the latest music and enjoy being part of cultural conversations.",
            "Nostalgic Soul": "You have a special connection to music from specific eras that hold personal significance."
        }
        return descriptions.get(style, "Your listening habits create a unique musical fingerprint that reflects your personality.")

    def _get_tempo_description(self, tempo):
        """Get a description for a given tempo value in BPM."""
        if tempo < 70:
            return "You gravitate toward slower, more relaxed music. These tempos are common in ballads, ambient music, and some jazz and blues."
        elif tempo < 90:
            return "Your music tends to have a moderate, relaxed pace. This tempo range is common in R&B, slow rock, and some hip-hop tracks."
        elif tempo < 110:
            return "Your preferred music has a moderate tempo, similar to a walking pace. This range is common in pop, rock, and reggae."
        elif tempo < 130:
            return "You enjoy music with an energetic tempo. This range is common in dance music, upbeat pop, and many rock songs."
        elif tempo < 150:
            return "Your music tends to be fast-paced and energetic. This tempo range is common in dance, techno, and some rock genres."
        else:
            return "You're drawn to very fast-paced, high-energy music. These tempos are common in EDM, drum and bass, metal, and some hip-hop."



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

def create_spotify_card(title, content, icon=None):
    """Create a styled card component for the dashboard."""
    header = html.Div([
        html.I(className=f"fas {icon}", style={'marginRight': '10px'}) if icon else None,
        html.H3(title, style={'margin': '0', 'display': 'inline'})
    ], style={
        'borderBottom': f'1px solid {SPOTIFY_GRAY}',
        'paddingBottom': '10px',
        'marginBottom': '15px',
        'color': SPOTIFY_GREEN
    })

    return html.Div([
        header,
        html.Div(content)
    ], style={
        'backgroundColor': '#121212',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
        'margin': '15px 0'
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
                subtext = Text("of music in 2023", font="Arial", color="#AAAAAA")

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


