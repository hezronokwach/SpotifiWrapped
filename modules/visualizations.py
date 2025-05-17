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
import manim
from manim import *

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

class SpotifyVisualizations:
    def __init__(self):
        """Initialize visualizations with Spotify theme."""
        self.theme = {
            'background_color': SPOTIFY_BLACK,
            'text_color': SPOTIFY_WHITE,
            'accent_color': SPOTIFY_GREEN,
            'secondary_color': SPOTIFY_GRAY,
            'font_family': 'Gotham, Helvetica Neue, Helvetica, Arial, sans-serif'
        }
        
        # Default layout settings for all charts
        self.layout_defaults = {
            'plot_bgcolor': self.theme['background_color'],
            'paper_bgcolor': self.theme['background_color'],
            'font': {
                'color': self.theme['text_color'],
                'family': self.theme['font_family']
            },
            'title': {
                'font': {
                    'color': self.theme['accent_color'],
                    'family': self.theme['font_family'],
                    'size': 24
                }
            },
            'margin': {'t': 50, 'b': 50, 'l': 50, 'r': 50}
        }
    
    def _apply_theme(self, fig):
        """Apply Spotify theme to a plotly figure."""
        fig.update_layout(**self.layout_defaults)
        return fig
    
    def create_top_tracks_chart(self, df):
        """Create a bar chart of top tracks with popularity scores."""
        if df.empty or 'track' not in df.columns:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No top tracks data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
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
            color='artist',
            orientation='h',
            color_discrete_sequence=SPOTIFY_PALETTE,
            labels={
                'track': '',
                'popularity': 'Popularity Score',
                'artist': 'Artist'
            },
            title='Your Top Tracks'
        )
        
        # Add track rank if available
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
        if df.empty or 'added_at' not in df.columns or 'end_date' not in df.columns:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No saved tracks data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            return self._apply_theme(fig)
        
        # Ensure datetime format
        df['added_at'] = pd.to_datetime(df['added_at'])
        df['end_date'] = pd.to_datetime(df['end_date'])
        
        # Sort by added_at date
        df = df.sort_values('added_at', ascending=False)
        
        # Create timeline
        fig = px.timeline(
            df,
            x_start='added_at',
            x_end='end_date',
            y='track',
            color='artist',
            color_discrete_sequence=SPOTIFY_PALETTE,
            labels={
                'track': '',
                'artist': 'Artist',
                'added_at': 'Date Added'
            },
            title='Recently Saved Tracks'
        )
        
        # Update layout for better appearance
        fig.update_layout(
            height=600,
            xaxis_title="Date Added",
            yaxis_title="",
            legend_title_text="",
            yaxis={'categoryorder': 'array', 'categoryarray': df['track'].tolist()[::-1]}
        )
        
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
        
        return self._apply_theme(fig)
    
    def create_playlists_chart(self, df):
        """Create a bar chart of playlists by track count."""
        if df.empty or 'playlist' not in df.columns:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No playlists data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            return self._apply_theme(fig)
        
        # Sort by track count
        df = df.sort_values('total_tracks', ascending=False)
        
        # Create visibility column for color coding
        if 'public' in df.columns and 'collaborative' in df.columns:
            df['visibility'] = df.apply(
                lambda x: 'Collaborative' if x['collaborative'] else ('Public' if x['public'] else 'Private'), 
                axis=1
            )
        else:
            df['visibility'] = 'Unknown'
        
        # Create bar chart
        fig = px.bar(
            df,
            x='playlist',
            y='total_tracks',
            color='visibility',
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
            yaxis_title="Number of Tracks",
            legend_title_text="",
            xaxis={'tickangle': 45}
        )
        
        # Add hover template with more info
        hover_template = (
            "<b>%{x}</b><br>" +
            "Tracks: %{y}<br>" +
            "Type: %{marker.color}<br>"
        )
        
        if 'owner' in df.columns:
            hover_template += "Owner: %{customdata}<br>"
            custom_data = df[['owner']].values
            
            fig.update_traces(
                hovertemplate=hover_template,
                customdata=custom_data
            )
        
        return self._apply_theme(fig)
    
    def create_audio_features_radar(self, df):
        """Create a radar chart of audio features for top tracks."""
        if df.empty or not all(col in df.columns for col in ['track', 'feature', 'value']):
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No audio features data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            return self._apply_theme(fig)
        
        # Get unique tracks
        tracks = df['track'].unique()
        
        # Create radar chart
        fig = go.Figure()
        
        # Add a trace for each track
        for i, track in enumerate(tracks):
            track_data = df[df['track'] == track]
            
            # Sort features in a consistent order
            features = track_data['feature'].tolist()
            values = track_data['value'].tolist()
            
            # Add the first value at the end to close the polygon
            features.append(features[0])
            values.append(values[0])
            
            # Get color from palette
            color = SPOTIFY_PALETTE[i % len(SPOTIFY_PALETTE)]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=features,
                fill='toself',
                name=track,
                line_color=color,
                fillcolor=color + '50'  # Add transparency
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
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No genre data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            return self._apply_theme(fig)
        
        # Sort by count and take top 10
        df = df.sort_values('count', ascending=False).head(10)
        
        # Create pie chart
        fig = px.pie(
            df,
            values='count',
            names='genre',
            color_discrete_sequence=SPOTIFY_PALETTE,
            title='Your Top Genres'
        )
        
        # Update layout for better appearance
        fig.update_layout(
            height=500,
            legend_title_text=""
        )
        
        # Update traces for better hover info
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}'
        )
        
        return self._apply_theme(fig)
    
    def create_listening_patterns_heatmap(self, df):
        """Create a heatmap of listening patterns by day and hour."""
        if df.empty or 'day_of_week' not in df.columns or 'hour_of_day' not in df.columns:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No listening pattern data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            return self._apply_theme(fig)
        
        # Create pivot table for heatmap
        pivot_df = df.pivot_table(
            index='day_of_week', 
            columns='hour_of_day', 
            aggfunc='size', 
            fill_value=0
        )
        
        # Reorder days of week
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_df = pivot_df.reindex(days_order)
        
        # Create heatmap
        fig = px.imshow(
            pivot_df,
            labels=dict(x="Hour of Day", y="Day of Week", color="Play Count"),
            x=[str(hour) for hour in range(24)],
            y=days_order,
            color_continuous_scale=px.colors.sequential.Viridis,
            title='Your Listening Patterns'
        )
        
        # Update layout for better appearance
        fig.update_layout(
            height=500,
            coloraxis_colorbar=dict(
                title="Play Count",
                tickvals=[pivot_df.values.min(), pivot_df.values.max()],
                ticktext=["Low", "High"]
            )
        )
        
        return self._apply_theme(fig)
    
    def create_top_artists_chart(self, df):
        """Create a bar chart of top artists."""
        if df.empty or 'artist' not in df.columns:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No top artists data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(color=self.theme['text_color'], size=16)
            )
            return self._apply_theme(fig)
        
        # Sort by rank if available, otherwise by popularity
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
        
        # Add artist rank if available
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
        
        # Add artist images if image_url is available
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
            # Header
            html.H3("Now Playing", style={'color': self.theme['accent_color'], 'marginBottom': '20px'}),
            
            # Track info with image
            html.Div([
                # Album cover
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
                    
                    # Duration
                    html.Span(duration_str, style={
                        'color': self.theme['secondary_color'], 
                        'fontSize': '12px',
                        'float': 'right'
                    })
                ])
            ])
        ], style={
            'backgroundColor': '#121212',
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
            # Header
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
                    'backgroundColor': '#121212',
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
                    'backgroundColor': '#121212',
                    'padding': '30px',
                    'borderRadius': '10px',
                    'margin': '20px 0'
                })
            ]),
            
            # Music mood section
            html.Div([
                html.H3("Your Music Mood", style={'color': self.theme['text_color'], 'textAlign': 'center'}),
                html.Div([
                    html.H1(summary_data['music_mood']['mood'], style={
                        'color': self.theme['accent_color'],
                        'textAlign': 'center',
                        'fontSize': '48px',
                        'margin': '10px 0'
                    }),
                    html.Div([
                        html.Div([
                            html.Span("Valence", style={'color': self.theme['text_color']}),
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
                        ])
                    ])
                ], style={
                    'backgroundColor': '#121212',
                    'padding': '30px',
                    'borderRadius': '10px',
                    'margin': '20px 0'
                })
            ]),
            
            # Genre highlight section
            html.Div([
                html.H3("Your Top Genre", style={'color': self.theme['text_color'], 'textAlign': 'center'}),
                html.Div([
                    html.H1(summary_data['genre_highlight']['name'], style={
                        'color': self.theme['accent_color'],
                        'textAlign': 'center',
                        'fontSize': '48px',
                        'margin': '10px 0'
                    })
                ], style={
                    'backgroundColor': '#121212',
                    'padding': '30px',
                    'borderRadius': '10px',
                    'margin': '20px 0'
                })
            ])
        ], style={
            'backgroundColor': '#191414',
            'padding': '30px',
            'borderRadius': '15px',
            'boxShadow': '0 8px 16px rgba(0,0,0,0.5)',
            'margin': '20px 0'
        })

# Manim animations for Spotify Wrapped
class SpotifyAnimations:
    """Class for creating Manim animations for Spotify Wrapped."""
    
    @staticmethod
    def create_top_track_animation(track_name, artist_name, output_file="top_track_animation.mp4"):
        """Create an animation revealing the top track."""
        class TopTrackScene(Scene):
            def construct(self):
                # Set background color to Spotify black
                self.camera.background_color = "#191414"
                
                # Create text objects
                header = Text("Your Top Track of 2023", font="Arial", color="#1DB954")
                track = Text(track_name, font="Arial", color="#FFFFFF")
                artist = Text(f"by {artist_name}", font="Arial", color="#AAAAAA")
                
                # Position text
                header.to_edge(UP, buff=1)
                track.scale(1.5)
                artist.next_to(track, DOWN, buff=0.5)
                
                # Create animation sequence
                self.play(Write(header), run_time=1)
                self.wait(0.5)
                
                # Reveal track name with typewriter effect
                self.play(AddTextLetterByLetter(track), run_time=2)
                self.wait(0.5)
                
                # Fade in artist name
                self.play(FadeIn(artist), run_time=1)
                self.wait(2)
                
                # Final flourish - pulse effect
                self.play(
                    track.animate.scale(1.1),
                    rate_func=there_and_back,
                    run_time=1
                )
                self.wait(1)
        
        # Render the animation
        scene = TopTrackScene()
        scene.render()
        
        return output_file
    
    @staticmethod
    def create_genre_animation(genres, output_file="genre_animation.mp4"):
        """Create an animation showing top genres."""
        class GenreScene(Scene):
            def construct(self):
                # Set background color to Spotify black
                self.camera.background_color = "#191414"
                
                # Create header
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
                    rate_func=wiggle,
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
                    ChangeDecimalToValue(counter, minutes_listened),
                    run_time=3,
                    rate_func=smooth
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
                self.play(AddTextLetterByLetter(mood_text), run_time=1.5)
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
                    rate_func=smooth
                )
                
                self.wait(1)
                
                # Final flourish - pulse the mood circle
                self.play(
                    mood_circle.animate.scale(1.2),
                    rate_func=there_and_back,
                    run_time=1
                )
                self.wait(1)
        
        # Render the animation
        scene = MoodScene()
        scene.render()
        
        return output_file

# Helper functions for creating interactive components
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

def create_stat_card(title, value, icon=None, color=SPOTIFY_GREEN):
    """Create a simple stat card."""
    return html.Div([
        html.Div([
            html.I(className=f"fas {icon}", style={'fontSize': '24px'}) if icon else None,
        ], style={'marginBottom': '10px', 'color': color}),
        html.Div(title, style={'color': SPOTIFY_GRAY, 'fontSize': '0.9em', 'marginBottom': '5px'}),
        html.Div(value, style={'color': SPOTIFY_WHITE, 'fontSize': '1.8em', 'fontWeight': 'bold'})
    ], style={
        'backgroundColor': '#121212',
        'padding': '20px',
        'borderRadius': '10px',
        'textAlign': 'center',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
        'height': '100%'
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

# Export the main visualization class
__all__ = ['SpotifyVisualizations', 'SpotifyAnimations', 'create_spotify_card', 
           'create_track_list_item', 'create_artist_list_item', 'create_stat_card',
           'create_progress_bar', 'create_spotify_button']
                
                