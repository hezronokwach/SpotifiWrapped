import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from modules.api import SpotifyAPI

def get_top_albums(spotify_api, limit=10):
    """
    Extract top albums from user's listening history.
    
    Args:
        spotify_api: SpotifyAPI instance
        limit: Number of top albums to return
        
    Returns:
        DataFrame with album data
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
                'album': track.get('album', ''),
                'artist': track.get('artist', ''),
                'count': 1,
                'source': 'recently_played',
                'image_url': track.get('image_url', '')
            })
    
    if saved_tracks:
        for track in saved_tracks:
            all_tracks.append({
                'album': track.get('album', ''),
                'artist': track.get('artist', ''),
                'count': 2,  # Give saved tracks higher weight
                'source': 'saved_tracks',
                'image_url': track.get('image_url', '')
            })
    
    if top_tracks:
        for track in top_tracks:
            all_tracks.append({
                'album': track.get('album', ''),
                'artist': track.get('artist', ''),
                'count': 3,  # Give top tracks highest weight
                'source': 'top_tracks',
                'image_url': track.get('image_url', '')
            })
    
    # Create DataFrame
    df = pd.DataFrame(all_tracks)
    
    # Group by album and sum the counts
    album_counts = df.groupby(['album', 'artist', 'image_url']).agg(
        total_count=('count', 'sum'),
        sources=('source', lambda x: ', '.join(set(x)))
    ).reset_index()
    
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
            'listening_style': 'Unknown'
        }
    
    # Convert to DataFrame
    df = pd.DataFrame(recently_played)
    
    # Add datetime column
    df['played_at_dt'] = pd.to_datetime(df['played_at'])
    
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