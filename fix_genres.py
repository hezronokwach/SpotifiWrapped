#!/usr/bin/env python3
"""
Script to fix genre misclassifications in the database.
This will correct artists like Bien, Bensoul, Okello Max who are misclassified as gengetone.
"""

import sqlite3
import os
from modules.database import SpotifyDatabase

def fix_genre_misclassifications():
    """Fix genre misclassifications in the database."""
    
    # Define artist corrections
    corrections = {
        # Kenyan R&B/Soul artists misclassified as gengetone
        'Bien': {'from': 'gengetone', 'to': 'afro r&b'},
        'Bensoul': {'from': 'gengetone', 'to': 'afro r&b'},
        'Okello Max': {'from': 'gengetone', 'to': 'afro r&b'},
        'Njerae': {'from': 'gengetone', 'to': 'afro r&b'},
        'Sauti Sol': {'from': 'gengetone', 'to': 'afro r&b'},
        'Crystal Asige': {'from': 'gengetone', 'to': 'afro r&b'},
        'Fena Gitu': {'from': 'gengetone', 'to': 'afro r&b'},
        'Nikita Kering': {'from': 'gengetone', 'to': 'afro r&b'},
        'Karun': {'from': 'gengetone', 'to': 'afro r&b'},
        
        # Kenyan Hip Hop artists misclassified as gengetone
        'Nyashinski': {'from': 'gengetone', 'to': 'kenyan hip hop'},
        'Khaligraph Jones': {'from': 'gengetone', 'to': 'kenyan hip hop'},
        'Octopizzo': {'from': 'gengetone', 'to': 'kenyan hip hop'},
        'King Kaka': {'from': 'gengetone', 'to': 'kenyan hip hop'},
        'Collo': {'from': 'gengetone', 'to': 'kenyan hip hop'},
    }
    
    db_path = 'data/spotify_data.db'
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== FIXING GENRE MISCLASSIFICATIONS ===\n")
    
    total_corrections = 0
    
    try:
        for artist_name, correction in corrections.items():
            from_genre = correction['from']
            to_genre = correction['to']
            
            # Check if this artist has the incorrect genre
            cursor.execute('''
                SELECT genre_id, count FROM genres 
                WHERE artist_name = ? AND genre_name = ?
            ''', (artist_name, from_genre))
            
            result = cursor.fetchone()
            if result:
                genre_id, count = result
                
                # Check if the correct genre already exists for this artist
                cursor.execute('''
                    SELECT genre_id, count FROM genres 
                    WHERE artist_name = ? AND genre_name = ?
                ''', (artist_name, to_genre))
                
                existing_correct = cursor.fetchone()
                
                if existing_correct:
                    # Merge the counts
                    existing_id, existing_count = existing_correct
                    new_count = count + existing_count
                    
                    # Update the correct genre with combined count
                    cursor.execute('''
                        UPDATE genres SET count = ? WHERE genre_id = ?
                    ''', (new_count, existing_id))
                    
                    # Delete the incorrect genre
                    cursor.execute('DELETE FROM genres WHERE genre_id = ?', (genre_id,))
                    
                    print(f"✅ {artist_name}: Merged {from_genre} ({count}) with existing {to_genre} ({existing_count}) = {new_count}")
                else:
                    # Simply update the genre name
                    cursor.execute('''
                        UPDATE genres SET genre_name = ? WHERE genre_id = ?
                    ''', (to_genre, genre_id))
                    
                    print(f"✅ {artist_name}: Changed {from_genre} → {to_genre} ({count} plays)")
                
                total_corrections += 1
            else:
                print(f"ℹ️  {artist_name}: No {from_genre} genre found (already correct or not in database)")
        
        conn.commit()
        print(f"\n🎉 Successfully applied {total_corrections} genre corrections!")
        
        # Show updated genre distribution
        print("\n=== UPDATED GENRE DISTRIBUTION ===")
        cursor.execute('''
            SELECT genre_name, SUM(count) as total_count 
            FROM genres 
            GROUP BY genre_name 
            ORDER BY total_count DESC 
            LIMIT 15
        ''')
        
        for genre, count in cursor.fetchall():
            print(f"{genre}: {count}")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_genre_misclassifications()
