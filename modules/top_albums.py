import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from modules.api import SpotifyAPI

def get_top_albums(spotify_api, limit=10, user_db=None):
    """
    Get top albums based on comprehensive listening metrics from database.

    Args:
        spotify_api: SpotifyAPI instance
        limit: Number of albums to return
        user_db: User-specific database instance

    Returns:
        DataFrame with enhanced album data including completion rates and listening time
    """
    from modules.database import SpotifyDatabase
    import sqlite3
    from datetime import datetime

    try:
        # Use provided user database or get current user's database
        if user_db is None:
            # This function should be called with a user_db parameter
            print("❌ ERROR: get_top_albums called without user_db parameter")
            return pd.DataFrame()

        conn = sqlite3.connect(user_db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        current_date = datetime.now().strftime('%Y-%m-%d')

        # Get user_id from the database
        cursor.execute("SELECT user_id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        if not user_result:
            print("❌ ERROR: No user found in database")
            return pd.DataFrame()
        user_id = user_result[0]

        # Enhanced album ranking query with completion rate and listening time
        cursor.execute('''
            WITH album_stats AS (
                SELECT
                    t.album,
                    t.artist,
                    MAX(t.image_url) as image_url,
                    COUNT(DISTINCT h.history_id) as total_plays,
                    COUNT(DISTINCT t.track_id) as unique_tracks_played,
                    SUM(CASE
                        WHEN t.duration_ms > 0 THEN t.duration_ms
                        ELSE 180000
                    END) as total_listening_time_ms,
                    AVG(CASE
                        WHEN t.duration_ms > 0 THEN t.duration_ms
                        ELSE 180000
                    END) as avg_track_duration_ms,
                    MAX(t.popularity) as max_popularity,
                    AVG(t.popularity) as avg_popularity
                FROM tracks t
                JOIN listening_history h ON t.track_id = h.track_id
                WHERE h.user_id = ?
                AND t.album IS NOT NULL
                AND t.album != ''
                AND t.track_id NOT LIKE 'artist-%'
                AND t.track_id NOT LIKE 'genre-%'
                AND date(h.played_at) <= ?
                AND h.source IN ('played', 'recently_played', 'current', 'saved')
                GROUP BY t.album, t.artist
                HAVING total_plays >= 2  -- Minimum 2 plays per album
            ),
            album_completion AS (
                SELECT
                    album,
                    artist,
                    -- Estimate album completion rate based on unique tracks vs typical album size
                    CASE
                        WHEN unique_tracks_played >= 10 THEN 1.0  -- Full album listening
                        WHEN unique_tracks_played >= 5 THEN 0.8   -- Most of album
                        WHEN unique_tracks_played >= 3 THEN 0.6   -- Half album
                        WHEN unique_tracks_played >= 2 THEN 0.4   -- Few tracks
                        ELSE 0.2  -- Single track
                    END as completion_rate,
                    -- Calculate listening intensity (plays per unique track)
                    CAST(total_plays AS FLOAT) / unique_tracks_played as listening_intensity,
                    -- Calculate total listening time in minutes
                    total_listening_time_ms / 60000.0 as total_listening_minutes,
                    -- Enhanced weighted score:
                    -- Listening time (40%) + Play frequency (30%) + Completion rate (20%) + Popularity (10%)
                    (
                        (total_listening_time_ms / 1000000.0 * 0.4) +
                        (total_plays * 0.3) +
                        (CASE
                            WHEN unique_tracks_played >= 10 THEN 1.0
                            WHEN unique_tracks_played >= 5 THEN 0.8
                            WHEN unique_tracks_played >= 3 THEN 0.6
                            WHEN unique_tracks_played >= 2 THEN 0.4
                            ELSE 0.2
                        END * 0.2) +
                        (avg_popularity / 100.0 * 0.1)
                    ) as weighted_score,
                    *
                FROM album_stats
            )
            SELECT
                album,
                artist,
                image_url,
                total_plays,
                unique_tracks_played,
                completion_rate,
                listening_intensity,
                total_listening_minutes,
                weighted_score,
                ROUND(weighted_score * 100 / (SELECT MAX(weighted_score) FROM album_completion)) as normalized_score
            FROM album_completion
            ORDER BY weighted_score DESC
            LIMIT ?
        ''', (user_id, current_date, limit))

        albums_data = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Convert to DataFrame and add rank
        if albums_data:
            albums_df = pd.DataFrame(albums_data)
            albums_df['rank'] = range(1, len(albums_df) + 1)

            # Rename normalized_score to total_count for compatibility
            albums_df['total_count'] = albums_df['normalized_score']

            print(f"Enhanced album ranking returned {len(albums_df)} albums")
            if len(albums_df) > 0:
                for i, album in albums_df.head(5).iterrows():
                    print(f"  {album['rank']}. {album['album']} by {album['artist']}")
                    print(f"     Plays: {album['total_plays']}, Tracks: {album['unique_tracks_played']}, "
                          f"Completion: {album['completion_rate']:.1%}, Time: {album['total_listening_minutes']:.1f}min")

            return albums_df
        else:
            print("No albums found in database, falling back to legacy method")
            return get_top_albums_legacy(spotify_api, limit)

    except Exception as e:
        print(f"Error in enhanced album ranking: {e}")
        print("Falling back to legacy method")
        return get_top_albums_legacy(spotify_api, limit)

def get_top_albums_legacy(spotify_api, limit=10):
    """
    Legacy API-based top albums function (kept for fallback).
    """
    # Get recently played tracks to analyze album frequency
    recently_played = spotify_api.get_recently_played(limit=50)

    # Get saved tracks as they indicate user preference
    saved_tracks = spotify_api.get_saved_tracks(limit=50)

    # Get top tracks to extract their albums
    top_tracks = spotify_api.get_top_tracks(limit=50)

    # Combine all data sources
    all_tracks = []

    if recently_played:
        for track in recently_played:
            all_tracks.append({
                'album': track.get('album_name', track.get('album', '')),
                'artist': track.get('album_artist', track.get('artist', '')),
                'count': 1,
                'source': 'recently_played',
                'image_url': track.get('album_image_url', track.get('image_url', ''))
            })

    if saved_tracks:
        for track in saved_tracks:
            all_tracks.append({
                'album': track.get('album_name', track.get('album', '')),
                'artist': track.get('album_artist', track.get('artist', '')),
                'count': 2,  # Give saved tracks higher weight
                'source': 'saved_tracks',
                'image_url': track.get('album_image_url', track.get('image_url', ''))
            })

    if top_tracks:
        for track in top_tracks:
            all_tracks.append({
                'album': track.get('album_name', track.get('album', '')),
                'artist': track.get('album_artist', track.get('artist', '')),
                'count': 3,  # Give top tracks highest weight
                'source': 'top_tracks',
                'image_url': track.get('album_image_url', track.get('image_url', ''))
            })

    # Create DataFrame
    df = pd.DataFrame(all_tracks)

    if df.empty:
        return pd.DataFrame(columns=['album', 'artist', 'image_url', 'total_count', 'rank'])

    # Group by album and sum the counts
    album_counts = df.groupby(['album', 'artist', 'image_url']).agg(
        total_count=('count', 'sum'),
        sources=('source', lambda x: ', '.join(set(x)))
    ).reset_index()

    # Normalize listening scores to be between 0-100
    if not album_counts.empty:
        max_count = album_counts['total_count'].max()
        album_counts['total_count'] = (album_counts['total_count'] / max_count * 100).round()

    # Sort by count in descending order
    album_counts = album_counts.sort_values('total_count', ascending=False)

    # Get top albums
    top_albums = album_counts.head(limit)

    # Add rank
    top_albums['rank'] = range(1, len(top_albums) + 1)

    return top_albums

def visualize_top_albums(spotify_api, limit=10, save_path=None):
    """
    Create a visualization of user's top albums.
    
    Args:
        spotify_api: SpotifyAPI instance
        limit: Number of top albums to display
        save_path: Path to save the visualization image
        
    Returns:
        Matplotlib figure
    """
    top_albums = get_top_albums(spotify_api, limit)
    
    if top_albums.empty:
        print("No album data available")
        return None
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create bar chart
    sns.set_style("darkgrid")
    ax = sns.barplot(x='total_count', y='album', data=top_albums, 
                    palette='viridis', hue='artist', dodge=False)
    
    # Add labels
    plt.title('Your Top Albums', fontsize=18)
    plt.xlabel('Listening Score', fontsize=14)
    plt.ylabel('Album', fontsize=14)
    
    # Add artist names to the labels
    labels = [f"{row['album']} - {row['artist']}" for _, row in top_albums.iterrows()]
    ax.set_yticklabels(labels)
    
    # Add rank numbers
    for i, (_, row) in enumerate(top_albums.iterrows()):
        plt.text(0.5, i, f"#{row['rank']}", fontweight='bold', 
                va='center', ha='center', color='white')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return plt.gcf()

def get_album_listening_patterns(spotify_api):
    """
    Analyze if user tends to listen to full albums or individual tracks.
    
    Args:
        spotify_api: SpotifyAPI instance
        
    Returns:
        Dictionary with album listening pattern metrics
    """
    # Get recently played tracks
    recently_played = spotify_api.get_recently_played(limit=50)
    
    if not recently_played:
        return {
            'album_completion_rate': 0,
            'sequential_listening_score': 0,
            'album_focused': False,
            'listening_style': 'Music Explorer'
        }
    
    # Convert to DataFrame
    df = pd.DataFrame(recently_played)
    
    # Add datetime column - use ISO8601 format
    df['played_at_dt'] = pd.to_datetime(df['played_at'], format='ISO8601')
    
    # Sort by played_at
    df = df.sort_values('played_at_dt')
    
    # Group by album
    album_groups = df.groupby('album')
    
    # Calculate metrics
    total_albums = len(album_groups)
    albums_with_multiple_tracks = sum(1 for _, group in album_groups if len(group) > 1)
    
    # Calculate sequential listening (tracks from same album played consecutively)
    sequential_count = 0
    for i in range(1, len(df)):
        if df.iloc[i]['album'] == df.iloc[i-1]['album']:
            sequential_count += 1
    
    # Calculate metrics
    if total_albums > 0:
        album_completion_rate = albums_with_multiple_tracks / total_albums
    else:
        album_completion_rate = 0
        
    if len(df) > 1:
        sequential_listening_score = sequential_count / (len(df) - 1)
    else:
        sequential_listening_score = 0
    
    # Determine listening style
    album_focused = sequential_listening_score > 0.4 or album_completion_rate > 0.3
    
    if album_focused:
        if sequential_listening_score > 0.7:
            listening_style = "Album Purist"
        else:
            listening_style = "Album Explorer"
    else:
        if sequential_listening_score < 0.2:
            listening_style = "Track Hopper"
        else:
            listening_style = "Mood Curator"
    
    return {
        'album_completion_rate': round(album_completion_rate * 100, 2),
        'sequential_listening_score': round(sequential_listening_score * 100, 2),
        'album_focused': album_focused,
        'listening_style': listening_style
    }