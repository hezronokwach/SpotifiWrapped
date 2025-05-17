def process_top_artists(self, artists_data):
    """
    Process top artists data and extract genre information.
    
    Args:
        artists_data: List of artist objects from Spotify API
    """
    try:
        print("=== Processing Top Artists Data ===")
        
        if not artists_data:
            print("No artists data provided")
            return
            
        print(f"Processing {len(artists_data)} artists")
        
        # Extract artist information
        artists_list = []
        for i, artist in enumerate(artists_data):
            artist_info = {
                'name': artist.get('name', 'Unknown'),
                'popularity': artist.get('popularity', 0),
                'followers': artist.get('followers', {}).get('total', 0) if artist.get('followers') else 0,
                'genres': ', '.join(artist.get('genres', [])),
                'image_url': artist.get('images', [{}])[0].get('url', '') if artist.get('images') else ''
            }
            artists_list.append(artist_info)
            
            if i < 3:  # Debug first 3 artists
                print(f"Processed artist: {artist_info['name']}")
                print(f"  Genres: {artist_info['genres']}")
        
        # Save artists data
        self.save_data(artists_list, 'top_artists.csv')
        print(f"Saved {len(artists_list)} artists to top_artists.csv")
        
        # Extract and count genres
        all_genres = []
        for artist in artists_data:
            genres = artist.get('genres', [])
            for genre in genres:
                all_genres.append(genre)
        
        from collections import Counter
        genre_counts = Counter(all_genres)
        
        # Create genre analysis data
        genre_list = []
        for genre, count in genre_counts.items():
            genre_list.append({
                'genre': genre,
                'count': count
            })
        
        # Sort by count (descending)
        genre_list = sorted(genre_list, key=lambda x: x['count'], reverse=True)
        
        print(f"Extracted {len(genre_list)} unique genres")
        if genre_list:
            print("Top 5 genres:")
            for i, genre_item in enumerate(genre_list[:5]):
                print(f"  {i+1}. {genre_item['genre']}: {genre_item['count']} occurrences")
        
        # Save genre data
        self.save_data(genre_list, 'genre_analysis.csv')
        print(f"Saved {len(genre_list)} genres to genre_analysis.csv")
        
        print("=== Top Artists Processing Completed ===")
        
    except Exception as e:
        print(f"Error processing top artists: {e}")
        import traceback
        traceback.print_exc()