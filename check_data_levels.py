#!/usr/bin/env python3
"""
Quick script to check your current data levels for AI analysis
"""
import sqlite3
import os
import glob

def check_user_data_levels():
    """Check data levels for all users"""
    
    # Find all user databases
    user_dbs = glob.glob('/tmp/user_*_spotify_data.db')
    
    if not user_dbs:
        print("❌ No user databases found!")
        print("   Make sure you've connected your Spotify account and collected some data.")
        return
    
    print("🔍 Checking data levels for AI analysis...\n")
    
    for db_path in user_dbs:
        # Extract user ID from filename
        filename = os.path.basename(db_path)
        user_id = filename.replace('user_', '').replace('_spotify_data.db', '')
        
        print(f"📊 User: {user_id}")
        print(f"   Database: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check listening history
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_plays,
                    COUNT(DISTINCT h.track_id) as unique_tracks,
                    COUNT(DISTINCT h.track_id) as tracks_with_features
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.user_id = ?
                AND t.energy IS NOT NULL
            ''', (user_id,))
            
            stats = cursor.fetchone()
            total_plays = stats[0] if stats else 0
            unique_tracks = stats[1] if stats else 0
            tracks_with_features = stats[2] if stats else 0
            
            # Calculate confidence level
            if total_plays >= 100 and unique_tracks >= 50:
                confidence = "🟢 EXCELLENT (0.9)"
                ai_status = "✅ Full AI analysis available"
            elif total_plays >= 50 and unique_tracks >= 25:
                confidence = "🟡 GOOD (0.75)"
                ai_status = "✅ Good AI analysis available"
            elif total_plays >= 20 and unique_tracks >= 10:
                confidence = "🟠 MODERATE (0.6)"
                ai_status = "⚠️  Basic AI analysis available"
            elif total_plays >= 10 and unique_tracks >= 5:
                confidence = "🔴 LOW (0.4)"
                ai_status = "⚠️  Limited AI analysis"
            else:
                confidence = "❌ INSUFFICIENT (0.2)"
                ai_status = "❌ Insufficient data - will show sample data"
            
            print(f"   📈 Total plays: {total_plays}")
            print(f"   🎵 Unique tracks: {unique_tracks}")
            print(f"   🎛️  Tracks with audio features: {tracks_with_features}")
            print(f"   🎯 Confidence level: {confidence}")
            print(f"   🤖 AI Status: {ai_status}")
            
            # Check recent activity
            cursor.execute('''
                SELECT MAX(played_at) as latest_play
                FROM listening_history
                WHERE user_id = ?
            ''', (user_id,))
            
            latest = cursor.fetchone()
            if latest and latest[0]:
                print(f"   ⏰ Latest activity: {latest[0]}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error checking database: {e}")
        
        print()
    
    print("💡 To improve your AI analysis:")
    print("   1. Listen to more music on Spotify")
    print("   2. Save/like more tracks")
    print("   3. Create and listen to playlists")
    print("   4. Wait for the app to collect more data")
    print("   5. Make sure you're not in demo mode")

if __name__ == "__main__":
    check_user_data_levels()
