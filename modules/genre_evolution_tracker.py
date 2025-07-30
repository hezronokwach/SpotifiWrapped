"""Genre evolution tracking and visualization for AI insights."""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List

class GenreEvolutionTracker:
    """Track and visualize genre preference evolution over time."""
    
    def __init__(self, db_path: str = 'data/spotify_data.db'):
        """Initialize the tracker with database path."""
        self.db_path = db_path
    
    def get_genre_evolution_data(self, user_id: str, months_back: int = 12) -> Dict:
        """Get genre evolution data over time."""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get genre listening data by month (with unknown genre filtering)
            query = '''
                SELECT
                    strftime('%Y-%m', h.played_at) as month,
                    g.genre_name,
                    COUNT(*) as play_count
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                JOIN genres g ON t.artist = g.artist_name
                WHERE h.user_id = ?
                AND h.played_at >= date('now', '-{} months')
                AND g.genre_name IS NOT NULL
                AND g.genre_name != ''
                AND g.genre_name != 'unknown'
                GROUP BY month, g.genre_name
                ORDER BY month, play_count DESC
            '''.format(months_back)

            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if df.empty:
                return {'timeline_data': [], 'insights': []}
            
            # Process data for visualization
            timeline_data = self._process_timeline_data(df)
            insights = self._generate_evolution_insights(df)
            
            return {
                'timeline_data': timeline_data,
                'insights': insights,
                'current_top_genres': self._get_current_top_genres(df),
                'biggest_changes': self._detect_biggest_changes(df)
            }
            
        except Exception as e:
            print(f"Error getting genre evolution data: {e}")
            return {'timeline_data': [], 'insights': []}
        finally:
            conn.close()
    
    def _process_timeline_data(self, df: pd.DataFrame) -> List[Dict]:
        """Process data for timeline visualization."""
        # Get top 5 genres overall
        top_genres = df.groupby('genre_name')['play_count'].sum().nlargest(5).index.tolist()
        
        # Create timeline data
        timeline_data = []
        for month in sorted(df['month'].unique()):
            month_data = df[df['month'] == month]
            month_genres = {}
            
            for genre in top_genres:
                genre_data = month_data[month_data['genre_name'] == genre]
                month_genres[genre] = genre_data['play_count'].sum() if not genre_data.empty else 0
            
            timeline_data.append({
                'month': month,
                'genres': month_genres,
                'total_plays': month_data['play_count'].sum()
            })
        
        return timeline_data
    
    def _generate_evolution_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate insights about genre evolution."""
        insights = []
        
        try:
            # Get monthly genre data
            monthly_data = df.groupby(['month', 'genre_name'])['play_count'].sum().reset_index()
            
            if len(monthly_data) < 2:
                return ["Not enough data to analyze genre evolution."]
            
            # Find trending genres (increasing over time)
            genre_trends = {}
            for genre in df['genre_name'].unique():
                genre_data = monthly_data[monthly_data['genre_name'] == genre].sort_values('month')
                if len(genre_data) >= 2:
                    first_half = genre_data.head(len(genre_data)//2)['play_count'].mean()
                    second_half = genre_data.tail(len(genre_data)//2)['play_count'].mean()
                    if first_half > 0:
                        trend = (second_half - first_half) / first_half
                        genre_trends[genre] = trend
            
            # Find top trending genre
            if genre_trends:
                top_trending = max(genre_trends.items(), key=lambda x: x[1])
                if top_trending[1] > 0.2:  # 20% increase
                    insights.append(f"📈 You're increasingly drawn to {top_trending[0]} - up {top_trending[1]:.0%} recently!")
            
            # Find most consistent genre
            genre_consistency = {}
            for genre in df['genre_name'].unique():
                genre_monthly = monthly_data[monthly_data['genre_name'] == genre]['play_count']
                if len(genre_monthly) >= 3:
                    consistency = 1 - (genre_monthly.std() / genre_monthly.mean()) if genre_monthly.mean() > 0 else 0
                    genre_consistency[genre] = consistency
            
            if genre_consistency:
                most_consistent = max(genre_consistency.items(), key=lambda x: x[1])
                insights.append(f"🎯 {most_consistent[0]} has been your most consistent genre companion")
            
            # Seasonal patterns
            df['month_num'] = pd.to_datetime(df['month']).dt.month
            seasonal_genres = df.groupby(['month_num', 'genre_name'])['play_count'].sum().reset_index()
            
            # Check for winter/summer preferences
            winter_months = [12, 1, 2]
            summer_months = [6, 7, 8]
            
            winter_data = seasonal_genres[seasonal_genres['month_num'].isin(winter_months)]
            summer_data = seasonal_genres[seasonal_genres['month_num'].isin(summer_months)]
            
            if not winter_data.empty and not summer_data.empty:
                winter_top = winter_data.groupby('genre_name')['play_count'].sum().idxmax()
                summer_top = summer_data.groupby('genre_name')['play_count'].sum().idxmax()
                
                if winter_top != summer_top:
                    insights.append(f"🌟 Your taste shifts seasonally: {winter_top} in winter, {summer_top} in summer")
            
        except Exception as e:
            print(f"Error generating evolution insights: {e}")
            insights.append("Unable to analyze genre evolution patterns.")
        
        return insights[:3]  # Limit to 3 insights
    
    def _get_current_top_genres(self, df: pd.DataFrame) -> List[Dict]:
        """Get current top genres with play counts."""
        # Get most recent month's data
        latest_month = df['month'].max()
        current_data = df[df['month'] == latest_month]
        
        top_genres = current_data.groupby('genre_name')['play_count'].sum().nlargest(5)
        
        return [{'genre': genre, 'plays': plays} for genre, plays in top_genres.items()]
    
    def _detect_biggest_changes(self, df: pd.DataFrame) -> List[Dict]:
        """Detect the biggest changes in genre preferences."""
        changes = []
        
        try:
            # Compare first and last month
            months = sorted(df['month'].unique())
            if len(months) < 2:
                return changes
            
            first_month = months[0]
            last_month = months[-1]
            
            first_data = df[df['month'] == first_month].groupby('genre_name')['play_count'].sum()
            last_data = df[df['month'] == last_month].groupby('genre_name')['play_count'].sum()
            
            # Find genres with biggest increases
            for genre in first_data.index.intersection(last_data.index):
                change = last_data[genre] - first_data[genre]
                if abs(change) >= 3:  # Significant change threshold
                    changes.append({
                        'genre': genre,
                        'change': change,
                        'direction': 'increased' if change > 0 else 'decreased'
                    })
            
            # Sort by absolute change
            changes.sort(key=lambda x: abs(x['change']), reverse=True)
            
        except Exception as e:
            print(f"Error detecting genre changes: {e}")
        
        return changes[:3]  # Top 3 changes
    
    def create_evolution_visualization(self, evolution_data: Dict) -> go.Figure:
        """Create genre evolution timeline visualization."""
        timeline_data = evolution_data['timeline_data']
        
        if not timeline_data:
            fig = go.Figure()
            fig.add_annotation(
                text="Not enough data for genre evolution",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="rgba(255, 255, 255, 0.7)")
            )
            fig.update_layout(
                plot_bgcolor='rgba(26, 26, 26, 0.8)',
                paper_bgcolor='rgba(26, 26, 26, 0.95)',
                height=400
            )
            return fig
        
        fig = go.Figure()
        
        # Get all genres
        all_genres = set()
        for month_data in timeline_data:
            all_genres.update(month_data['genres'].keys())
        
        # Color palette for genres
        colors = ['#1DB954', '#00D4FF', '#8B5CF6', '#F472B6', '#FBBF24', '#EF4444', '#10B981']
        
        # Add traces for each genre
        for i, genre in enumerate(all_genres):
            months = [data['month'] for data in timeline_data]
            values = [data['genres'].get(genre, 0) for data in timeline_data]
            
            fig.add_trace(go.Scatter(
                x=months,
                y=values,
                mode='lines+markers',
                name=genre,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8),
                hovertemplate=f'<b>{genre}</b><br>Month: %{{x}}<br>Plays: %{{y}}<extra></extra>'
            ))
        
        # Update layout with futuristic styling
        fig.update_layout(
            title=dict(
                text="Your Genre Evolution Journey",
                font=dict(family="Orbitron, monospace", size=18, color="#1DB954"),
                x=0.5
            ),
            xaxis=dict(
                title="Month",
                gridcolor="rgba(29, 185, 84, 0.2)",
                tickfont=dict(family="Orbitron, monospace", color="rgba(255, 255, 255, 0.8)")
            ),
            yaxis=dict(
                title="Play Count",
                gridcolor="rgba(29, 185, 84, 0.2)",
                tickfont=dict(family="Orbitron, monospace", color="rgba(255, 255, 255, 0.8)")
            ),
            plot_bgcolor='rgba(26, 26, 26, 0.8)',
            paper_bgcolor='rgba(26, 26, 26, 0.95)',
            font=dict(family="Orbitron, monospace", color="white"),
            legend=dict(
                bgcolor="rgba(26, 26, 26, 0.8)",
                bordercolor="rgba(29, 185, 84, 0.3)",
                borderwidth=1
            ),
            height=400
        )
        
        return fig
