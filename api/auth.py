"""
Authentication endpoints for Spotify OAuth and JWT token management
"""

from flask import Blueprint, request, jsonify, redirect, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os
import requests
import base64
from modules.api import SpotifyAPI

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Initiate Spotify OAuth flow with user credentials"""
    try:
        print("🔍 DEBUG: Login endpoint called")

        data = request.get_json()
        print(f"🔍 DEBUG: Request data: {data}")

        client_id = data.get('client_id') if data else None
        client_secret = data.get('client_secret') if data else None

        print(f"🔍 DEBUG: client_id: {client_id[:8] if client_id else 'None'}...")
        print(f"🔍 DEBUG: client_secret: {'***' if client_secret else 'None'}")

        if not client_id or not client_secret:
            print("❌ DEBUG: Missing client credentials")
            return jsonify({'error': 'Missing client credentials'}), 400

        # Generate secure session ID for this login attempt
        import secrets
        session_id = secrets.token_urlsafe(32)
        
        # Store credentials with session isolation
        session['login_session_id'] = session_id
        session[f'spotify_client_id_{session_id}'] = client_id
        session[f'spotify_client_secret_{session_id}'] = client_secret
        print(f"✅ DEBUG: User credentials stored with session ID: {session_id[:8]}...")

        # Get redirect URI dynamically based on request origin
        origin = request.headers.get('Origin', 'http://localhost:3000')
        if 'vercel.app' in origin:
            redirect_uri = f"{origin}/auth/callback"
        else:
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:3000/auth/callback')
        print(f"🔍 DEBUG: origin: {origin}")
        print(f"🔍 DEBUG: redirect_uri: {redirect_uri}")

        # Create SpotifyAPI instance with user credentials
        print("🔍 DEBUG: Creating SpotifyAPI instance...")
        spotify_api = SpotifyAPI(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )
        print("✅ DEBUG: SpotifyAPI instance created")

        print("🔍 DEBUG: Getting auth URL...")
        
        # Generate auth URL manually to ensure consistency
        import urllib.parse
        scope = 'user-top-read user-library-read playlist-read-private user-read-currently-playing user-read-recently-played user-follow-read'
        state = secrets.token_urlsafe(16)
        
        auth_params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scope,
            'show_dialog': 'true',
            'state': state
        }
        
        auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(auth_params)
        print(f"🔍 DEBUG: Manual auth_url: {auth_url}")
        
        # Store state for validation
        session[f'oauth_state_{client_id[:8]}'] = state
        print(f"🔍 DEBUG: Stored OAuth state: {state}")

        if not auth_url:
            print("❌ DEBUG: Failed to generate authorization URL")
            return jsonify({'error': 'Failed to generate authorization URL'}), 500

        print("✅ DEBUG: Login successful, returning auth URL")
        response = jsonify({'auth_url': auth_url})
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    except Exception as e:
        print(f"❌ DEBUG: Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/callback', methods=['POST'])
def callback():
    """Handle Spotify OAuth callback and create JWT token"""
    try:
        print("🔍 DEBUG: Callback endpoint called")

        data = request.get_json()
        print(f"🔍 DEBUG: Callback request data: {data}")
        print(f"🔍 DEBUG: Callback timestamp: {__import__('time').time()}")

        code = data.get('code')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        state = data.get('state')  # Get state parameter

        print(f"🔍 DEBUG: code: {code[:20] if code else 'None'}...")
        print(f"🔍 DEBUG: code length: {len(code) if code else 0}")
        print(f"🔍 DEBUG: client_id: {client_id[:8] if client_id else 'None'}...")
        print(f"🔍 DEBUG: client_secret: {'***' if client_secret else 'None'}")

        if not code:
            print("❌ DEBUG: No authorization code received")
            return jsonify({'error': 'No authorization code received'}), 400

        if not client_id or not client_secret:
            print("❌ DEBUG: Missing client credentials")
            return jsonify({'error': 'Missing client credentials'}), 400

        # Get redirect URI dynamically based on request origin
        origin = request.headers.get('Origin', 'http://localhost:3000')
        if 'vercel.app' in origin:
            redirect_uri = f"{origin}/auth/callback"
        else:
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:3000/auth/callback')
        print(f"🔍 DEBUG: origin: {origin}")
        print(f"🔍 DEBUG: redirect_uri: {redirect_uri}")
        print(f"🔍 DEBUG: redirect_uri matches origin: {redirect_uri == f'{origin}/auth/callback'}")
        

        # Validate state parameter if present
        if state:
            stored_state = session.get(f'oauth_state_{client_id[:8]}')
            print(f"🔍 DEBUG: Received state: {state}")
            print(f"🔍 DEBUG: Stored state: {stored_state}")
            if state != stored_state:
                print("❌ DEBUG: OAuth state mismatch")
                return jsonify({
                    'error': 'OAuth state mismatch. Please try logging in again.',
                    'code': 'STATE_MISMATCH'
                }), 400
            # Clean up state
            session.pop(f'oauth_state_{client_id[:8]}', None)
        
        # Validate code format
        import urllib.parse
        decoded_code = urllib.parse.unquote(code)
        print(f"🔍 DEBUG: Original code: {code[:20]}...")
        print(f"🔍 DEBUG: Decoded code: {decoded_code[:20]}...")
        print(f"🔍 DEBUG: Code needs decoding: {code != decoded_code}")
        print(f"🔍 DEBUG: Code timestamp check: {__import__('time').time()}")

        # Create SpotifyAPI instance with user credentials
        print("🔍 DEBUG: Creating SpotifyAPI instance for callback...")
        spotify_api = SpotifyAPI(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )
        print("✅ DEBUG: SpotifyAPI instance created")

        # Exchange code for tokens using direct method (more reliable)
        print("🔍 DEBUG: Exchanging code for access token...")
        print(f"🔍 DEBUG: Using redirect_uri for token exchange: {redirect_uri}")
        
        # Use direct token exchange with Spotify API (primary method)
        print("🔍 DEBUG: Using direct token exchange...")
        try:
            import requests
            import base64
            
            # Prepare token exchange request
            auth_string = f"{client_id}:{client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            token_data = {
                'grant_type': 'authorization_code',
                'code': decoded_code,
                'redirect_uri': redirect_uri
            }
            
            print(f"🔍 DEBUG: Direct token exchange with redirect_uri: {redirect_uri}")
            response = requests.post(
                'https://accounts.spotify.com/api/token',
                headers=headers,
                data=token_data,
                timeout=10
            )
            
            print(f"🔍 DEBUG: Token exchange response status: {response.status_code}")
            
            if response.status_code == 200:
                token_info = response.json()
                print(f"✅ DEBUG: Direct token exchange successful")
                print(f"🔍 DEBUG: Token info keys: {list(token_info.keys())}")
            else:
                print(f"❌ DEBUG: Direct token exchange failed: {response.status_code}")
                print(f"🔍 DEBUG: Error response: {response.text}")
                return jsonify({
                    'error': 'Authorization code expired or already used. Please try logging in again.',
                    'code': 'INVALID_GRANT',
                    'details': f'Status: {response.status_code}, Response: {response.text[:200]}'
                }), 400
                
        except Exception as direct_error:
            print(f"❌ DEBUG: Direct token exchange failed: {direct_error}")
            return jsonify({
                'error': 'Token exchange failed. Please try logging in again.',
                'code': 'TOKEN_EXCHANGE_ERROR',
                'details': str(direct_error)
            }), 400

        if not token_info:
            print("❌ DEBUG: Failed to get access token")
            return jsonify({
                'error': 'Failed to get access token. Please try logging in again.',
                'code': 'NO_TOKEN'
            }), 400

        # Get user profile to create JWT
        print("🔍 DEBUG: Getting user profile...")
        user_profile = spotify_api.get_user_profile()
        print(f"🔍 DEBUG: User profile received: {user_profile is not None}")
        if not user_profile:
            print("❌ DEBUG: Failed to get user profile")
            return jsonify({'error': 'Failed to get user profile'}), 400

        # Create secure JWT token with user isolation
        user_id = user_profile['id']
        
        # Generate unique session token for this user
        import secrets
        user_session_token = secrets.token_urlsafe(16)
        
        access_token = create_access_token(
            identity=user_id,
            additional_claims={
                'spotify_access_token': token_info['access_token'],
                'spotify_refresh_token': token_info.get('refresh_token'),
                'display_name': user_profile.get('display_name'),
                'email': user_profile.get('email'),
                'client_id': client_id,
                'client_secret': client_secret,
                'user_session_token': user_session_token,
                'spotify_user_id': user_id  # Explicit user ID for validation
            }
        )
        
        # Clear session credentials after JWT creation
        session.pop('login_session_id', None)
        for key in list(session.keys()):
            if key.startswith('spotify_client_'):
                session.pop(key, None)
        
        # Collect essential data immediately for new users
        try:
            from modules.database import SpotifyDatabase
            from datetime import datetime
            
            user_id = user_profile['id']
            db_path = f'data/user_{user_id}_spotify_data.db'
            user_db = SpotifyDatabase(db_path)
            
            # Save user profile
            user_db.save_user(user_profile)
            
            # Check if user already has data
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM tracks')
            track_count = cursor.fetchone()[0]
            conn.close()
            
            # Only collect data if database is empty
            if track_count == 0:
                print(f'🔍 DEBUG: Collecting essential data for new user {user_id}')
                
                # 1. Get recently played tracks (immediate)
                recently_played = spotify_api.get_recently_played(limit=50)
                if recently_played:
                    print(f'🎧 Saving {len(recently_played)} recently played tracks')
                    for track in recently_played:
                        user_db.save_track(track)
                        user_db.save_listening_history(
                            user_id=user_id,
                            track_id=track['id'],
                            played_at=track.get('played_at', datetime.now().isoformat()),
                            source='recently_played'
                        )
                
                # 2. Get saved tracks (immediate)
                saved_tracks = spotify_api.get_saved_tracks(limit=50)
                if saved_tracks:
                    print(f'💚 Saving {len(saved_tracks)} saved tracks')
                    for track in saved_tracks:
                        user_db.save_track(track)
                        user_db.save_listening_history(
                            user_id=user_id,
                            track_id=track['id'],
                            played_at=track.get('added_at', datetime.now().isoformat()),
                            source='saved'
                        )
                
                # 3. Extract genres for collected artists
                try:
                    print('🎭 Starting genre extraction...')
                    from modules.genre_extractor import GenreExtractor
                    genre_extractor = GenreExtractor(spotify_api, user_db)
                    
                    # Extract genres from recently played tracks (limit to avoid long delays)
                    genres_extracted = genre_extractor.extract_genres_from_recent_tracks(max_artists=30)
                    print(f'✅ Extracted {genres_extracted} genres from recent tracks')
                    
                except Exception as genre_error:
                    print(f'⚠️ Genre extraction failed: {genre_error}')
                    # Continue anyway - genre extraction is not critical
                
                print(f'✅ DEBUG: Essential data collection completed for {user_id}')
            else:
                print(f'🔍 DEBUG: User {user_id} already has {track_count} tracks, skipping data collection')
                
        except Exception as e:
            print(f'⚠️ DEBUG: Data collection failed during auth: {e}')
            # Don't fail the authentication if data collection fails

        
        return jsonify({
            'access_token': access_token,
            'refresh_token': token_info.get('refresh_token'),
            'expires_in': 3600,  # 1 hour
            'user': {
                'id': user_profile['id'],
                'display_name': user_profile.get('display_name'),
                'email': user_profile.get('email'),
                'images': user_profile.get('images', [])
            }
        })

    except Exception as e:
        print(f"❌ DEBUG: Callback error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    """Refresh JWT access token"""
    try:
        current_user = get_jwt_identity()
        
        # Create new access token with extended expiry
        new_access_token = create_access_token(
            identity=current_user,
            expires_delta=timedelta(hours=1)
        )

        return jsonify({
            'access_token': new_access_token,
            'expires_in': 3600
        })

    except Exception as e:
        return jsonify({'error': 'Failed to refresh token'}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/status')
@jwt_required()
def auth_status():
    """Check authentication status"""
    try:
        current_user = get_jwt_identity()
        return jsonify({
            'authenticated': True,
            'user_id': current_user
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/validate-credentials', methods=['POST'])
def validate_credentials():
    """Validate Spotify app credentials"""
    try:
        data = request.get_json()
        client_id = data.get('clientId')
        client_secret = data.get('clientSecret')

        if not client_id or not client_secret:
            return jsonify({'valid': False, 'error': 'Missing credentials'}), 400

        # Test credentials by requesting a client credentials token
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {'grant_type': 'client_credentials'}

        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers=headers,
            data=data,
            timeout=10
        )

        if response.status_code == 200:
            return jsonify({'valid': True})
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            error_message = error_data.get('error_description', 'Invalid credentials')
            return jsonify({'valid': False, 'error': error_message}), 400

    except requests.RequestException as e:
        return jsonify({'valid': False, 'error': 'Network error validating credentials'}), 500
    except Exception as e:
        return jsonify({'valid': False, 'error': 'Failed to validate credentials'}), 500
