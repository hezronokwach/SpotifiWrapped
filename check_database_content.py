#!/usr/bin/env python3
"""
Check what's actually in your database
"""
import sqlite3
import os

def check_database_content():
    """Check what data exists in the database"""
    
    db_path = 'data/user_31l7kphabrzch4qviylsa6t7x5km_spotify_data.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"🔍 Checking database: {db_path}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tracks table
        cursor.execute("SELECT COUNT(*) FROM tracks")
        total_tracks = cursor.fetchone()[0]
        print(f"📀 Total tracks in database: {total_tracks}")
        
        # Check tracks with audio features
        cursor.execute("SELECT COUNT(*) FROM tracks WHERE energy IS NOT NULL")
        tracks_with_features = cursor.fetchone()[0]
        print(f"🎛️  Tracks with audio features: {tracks_with_features}")
        
        # Check listening history
        cursor.execute("SELECT COUNT(*) FROM listening_history")
        total_history = cursor.fetchone()[0]
        print(f"📈 Total listening history entries: {total_history}")
        
        # Check listening history for this user
        cursor.execute("SELECT COUNT(*) FROM listening_history WHERE user_id = ?", ('31l7kphabrzch4qviylsa6t7x5km',))
        user_history = cursor.fetchone()[0]
        print(f"👤 User listening history entries: {user_history}")
        
        # Check recent tracks
        cursor.execute("SELECT name, artist, energy, valence FROM tracks WHERE energy IS NOT NULL LIMIT 5")
        sample_tracks = cursor.fetchall()
        
        if sample_tracks:
            print(f"\n🎵 Sample tracks with audio features:")
            for track in sample_tracks:
                print(f"   • {track[1]} - {track[0]} (energy: {track[2]:.2f}, valence: {track[3]:.2f})")
        else:
            print(f"\n❌ No tracks with audio features found")
            
        # Check what sources we have
        cursor.execute("SELECT DISTINCT source, COUNT(*) FROM listening_history GROUP BY source")
        sources = cursor.fetchall()
        
        if sources:
            print(f"\n📊 Data sources:")
            for source, count in sources:
                print(f"   • {source}: {count} entries")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database_content()