import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
import pandas as pd
import time
import json
from datetime import datetime, timedelta

# Import custom modules
import sqlite3
from modules.api import SpotifyAPI
from modules.data_processing import DataProcessor, normalize_timestamp, calculate_duration_minutes
from modules.layout import DashboardLayout, create_onboarding_page
from modules.visualizations import (
    SpotifyVisualizations, SpotifyAnimations,
    SPOTIFY_GREEN, SPOTIFY_BLACK, SPOTIFY_WHITE, SPOTIFY_GRAY,
    create_album_card, create_personality_card, create_spotify_card
)

# Import data storage modules
from modules.database import SpotifyDatabase
from modules.data_collector import SpotifyDataCollector

# Import new modules
from modules.top_albums import get_top_albums, get_album_listening_patterns
from modules.analyzer import ListeningPersonalityAnalyzer
from modules.recent_tracks_collector import RecentTracksCollector
from modules.genre_extractor import GenreExtractor

# Import AI modules
from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
from modules.genre_evolution_tracker import GenreEvolutionTracker
from modules.wellness_analyzer import WellnessAnalyzer
from modules.enhanced_stress_detector import EnhancedStressDetector
from modules.stress_visualizations import create_enhanced_stress_analysis_card

# Load environment variables
load_dotenv()

# Initialize components
spotify_api = SpotifyAPI()
data_processor = DataProcessor()
dashboard_layout = DashboardLayout()
visualizations = SpotifyVisualizations()
animations = SpotifyAnimations()

# Initialize database and data collector
db = SpotifyDatabase()  # This will create tables if they don't exist
data_collector = SpotifyDataCollector(spotify_api, db)

# Initialize personality analyzer
personality_analyzer = ListeningPersonalityAnalyzer(spotify_api)

# Initialize recent tracks collector and genre extractor
recent_tracks_collector = RecentTracksCollector(spotify_api, db)
genre_extractor = GenreExtractor(spotify_api, db)

# Initialize AI modules
enhanced_personality_analyzer = EnhancedPersonalityAnalyzer()
genre_evolution_tracker = GenreEvolutionTracker()
wellness_analyzer = WellnessAnalyzer()
enhanced_stress_detector = EnhancedStressDetector()

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css',
        'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap'
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
    suppress_callback_exceptions=True  # Allow callbacks to components not in initial layout
)

app.title = "Spotify Wrapped Remix"

# Add callback route for Spotify OAuth
@app.server.route('/callback')
def spotify_callback():
    """Handle Spotify OAuth callback with comprehensive debugging."""
    from flask import request
    import traceback
    
    print("=" * 80)
    print("🔄 OAUTH CALLBACK TRIGGERED")
    print("=" * 80)
    
    # Log all request details
    print(f"📍 Request URL: {request.url}")
    print(f"📍 Request args: {dict(request.args)}")
    print(f"📍 Request method: {request.method}")
    print(f"📍 Request headers: {dict(request.headers)}")
    
    # Get the authorization code from the callback
    code = request.args.get('code')
    error = request.args.get('error')
    state = request.args.get('state')
    
    print(f"🔍 Authorization code: {code[:10] + '...' if code else 'None'}")
    print(f"🔍 Error: {error}")
    print(f"🔍 State: {state}")

    if error:
        print(f"❌ OAuth Error: {error}")
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spotify Authorization Failed</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #191414;
                    color: #FF5555;
                    text-align: center;
                    padding: 50px;
                }}
                .error {{
                    background: #FF5555;
                    color: #000;
                    padding: 20px;
                    border-radius: 10px;
                    display: inline-block;
                    margin: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>❌ Authorization Failed</h2>
                <p>Error: {error}</p>
                <p>Please try again.</p>
            </div>
        </body>
        </html>
        '''

    if code:
        print(f"✅ OAuth Success: Received authorization code: {code[:10]}...")
        
        # Check current Spotify API state
        print(f"🔍 Current spotify_api.sp: {spotify_api.sp is not None}")
        print(f"🔍 Current spotify_api.client_id: {spotify_api.client_id[:8] if spotify_api.client_id else 'None'}...")
        print(f"🔍 Current spotify_api.client_secret: {'***' if spotify_api.client_secret else 'None'}")
        print(f"🔍 Current spotify_api.redirect_uri: {spotify_api.redirect_uri}")

        # Try to exchange the code for a token immediately
        try:
            if spotify_api.sp and hasattr(spotify_api.sp, 'auth_manager'):
                print("🔄 Exchanging authorization code for access token...")
                token_info = spotify_api.sp.auth_manager.get_access_token(code, as_dict=True)
                if token_info:
                    print("✅ Token exchange successful!")
                    print(f"🔍 Token info keys: {list(token_info.keys()) if token_info else 'None'}")
                    
                    # Test the connection
                    user = spotify_api.sp.current_user()
                    if user:
                        print(f"✅ Successfully authenticated as {user.get('display_name', 'Unknown')}")
                        print(f"🔍 User ID: {user.get('id', 'Unknown')}")
                        
                        # Save authentication state to a temporary file for debugging
                        import json
                        debug_data = {
                            'timestamp': datetime.now().isoformat(),
                            'user_id': user.get('id'),
                            'display_name': user.get('display_name'),
                            'token_exchange': 'successful',
                            'client_id': spotify_api.client_id[:8] if spotify_api.client_id else 'None'
                        }
                        try:
                            with open('debug_oauth_success.json', 'w') as f:
                                json.dump(debug_data, f, indent=2)
                            print("💾 Debug data saved to debug_oauth_success.json")
                        except Exception as e:
                            print(f"⚠️ Could not save debug data: {e}")
                    else:
                        print("❌ Token exchange successful but user fetch failed")
                else:
                    print("❌ Token exchange failed - no token info returned")
            else:
                print("❌ No Spotify API object or auth manager available")
                print(f"🔍 spotify_api.sp: {spotify_api.sp}")
                if spotify_api.sp:
                    print(f"🔍 auth_manager: {hasattr(spotify_api.sp, 'auth_manager')}")
        except Exception as e:
            print(f"❌ Error during token exchange: {e}")
            print(f"🔍 Exception type: {type(e).__name__}")
            print(f"🔍 Exception traceback:")
            traceback.print_exc()

        # Return a success page with enhanced debugging
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spotify Authorization Successful</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #191414;
                    color: #1DB954;
                    text-align: center;
                    padding: 50px;
                }}
                .success {{
                    background: #1DB954;
                    color: #000;
                    padding: 20px;
                    border-radius: 10px;
                    display: inline-block;
                    margin: 20px;
                }}
                .debug {{
                    background: #333;
                    color: #fff;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px;
                    font-family: monospace;
                    font-size: 12px;
                    text-align: left;
                }}
            </style>
            <script>
                console.log('🔄 OAuth callback page loaded');
                console.log('🔍 window.opener:', window.opener);
                console.log('🔍 Current URL:', window.location.href);
                
                setTimeout(function() {{
                    console.log('🔄 Starting redirect process...');
                    // Try to refresh the parent window and close this popup
                    if (window.opener) {{
                        console.log('✅ Found window.opener, refreshing parent and closing popup');
                        // Refresh the parent window to trigger auth check
                        window.opener.location.reload();
                        window.close();
                    }} else {{
                        console.log('⚠️ No window.opener, redirecting current window to dashboard');
                        // If no opener, redirect this window to dashboard
                        window.location.href = '/dashboard';
                    }}
                }}, 2000);
            </script>
        </head>
        <body>
            <div class="success">
                <h2>🎵 Authorization Successful!</h2<p>Authorization completed successfully!</p>
                <p><strong><a href="/dashboard" style="color: #000; text-decoration: underline; font-size: 18px;">🏠 Click here to go to your Dashboard</a></strong></p>
                <p style="font-size: 14px; margin-top: 20px;">You can close this tab after clicking the dashboard link.</p>
            </div>
            <div class="debug">        
        </body>
        </html>
        '''

    print("❌ No authorization code received in callback")
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spotify Authorization Error</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #191414;
                color: #FF5555;
                text-align: center;
                padding: 50px;
            }
        </style>
    </head>
    <body>
        <h2>❌ No authorization code received</h2>
        <p>Please try the authorization process again.</p>
    </body>
    </html>
    '''

# Multi-page layout with navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Global store components (available on all pages)
    dcc.Store(id='user-data-store'),
    dcc.Store(id='current-track-store'),
    dcc.Store(id='wrapped-summary-store', data={}),  # Initialize with empty dict to trigger callback
    dcc.Store(id='personality-data-store'),
    dcc.Store(id='client-id-store', storage_type='session'),
    dcc.Store(id='client-secret-store', storage_type='session'),
    dcc.Store(id='use-sample-data-store', storage_type='session', data={'use_sample': False}),
    dcc.Store(id='auth-status-store', storage_type='session', data={'authenticated': False}),

    # Auto-refresh component (global)
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # in milliseconds (30 seconds)
        n_intervals=0
    ),

    # Hidden global refresh button (for callbacks) - always available
    html.Button(id='refresh-button', style={'display': 'none'}, n_clicks=0),

    html.Div([
        # Header with navigation
        html.Div([
            html.H1("Spotify Wrapped Remix", style={
                'color': '#1DB954',
                'fontFamily': 'Orbitron, monospace',
                'fontWeight': '700',
                'margin': '0'
            }),
            html.Div([
                dcc.Link("🚀 Get Started", href="/onboarding", className="nav-link onboarding-nav-link"),
                dcc.Link("🏠 Dashboard", href="/dashboard", className="nav-link"),
                dcc.Link("🤖 AI Insights", href="/ai-insights", className="nav-link ai-nav-link"),
                dcc.Link("⚙️ Settings", href="/settings", className="nav-link settings-nav-link")
            ], className="nav-links")
        ], className="header-with-nav"),

        html.Div(id='page-content'),
    ])
])

# --- Onboarding Callbacks ---

@app.callback(
    Output('custom-redirect-collapse', 'is_open'),
    Input('toggle-advanced-button', 'n_clicks'),
    State('custom-redirect-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_advanced_options(n_clicks, is_open):
    """Toggle the advanced options collapse."""
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
    [Output('auth-status-store', 'data'),
     Output('client-id-store', 'data'),
     Output('client-secret-store', 'data'),
     Output('use-sample-data-store', 'data')],
    [Input('connect-button', 'n_clicks')],
    [State('client-id-input', 'value'),
     State('client-secret-input', 'value')],
    prevent_initial_call=True
)
def handle_onboarding(connect_clicks, client_id, client_secret):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'connect-button':
        if not client_id or not client_secret:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        print(f"🔐 DEBUG: Attempting to connect with Client ID: {client_id[:8]}...")
        print(f"🔐 DEBUG: Client Secret provided: {len(client_secret)} characters")
        print(f"🔐 DEBUG: Redirect URI: {os.getenv('REDIRECT_URI')}")

        # Clear all cached data first
        print("🧹 DEBUG: Clearing all cached data for new credentials...")
        spotify_api.clear_all_cached_data()

        # Set new credentials
        print("🔗 DEBUG: Setting new credentials...")
        spotify_api.set_credentials(client_id, client_secret, os.getenv('REDIRECT_URI'))

        print(f"🔍 DEBUG: Spotify API object created: {spotify_api.sp is not None}")
        print(f"🔍 DEBUG: Use sample data flag: {spotify_api.use_sample_data}")

        if spotify_api.sp:
            # Check if we need authorization using our safe method
            auth_result = spotify_api.is_authenticated()
            print(f"🔍 DEBUG: Authentication check result: {auth_result}")

            if auth_result:
                print("✅ DEBUG: Connection successful!")
                return {'authenticated': True}, client_id, client_secret, {'use_sample': False}
            else:
                print("⚠️ DEBUG: Need authorization")
                # Get auth URL using our safe method
                auth_url = spotify_api.get_auth_url()
                if auth_url:
                    # Store credentials in session even when authorization is needed
                    return dash.no_update, client_id, client_secret, dash.no_update
                else:
                    print(f"❌ DEBUG: Could not get auth URL")
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            print("❌ DEBUG: Connection failed - no Spotify API object created")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    return dash.no_update

# Auto-check for completed authentication
@app.callback(
    [Output('auth-status-store', 'data', allow_duplicate=True),
     Output('client-id-store', 'data', allow_duplicate=True),
     Output('client-secret-store', 'data', allow_duplicate=True),
     Output('use-sample-data-store', 'data', allow_duplicate=True)],
    [Input('interval-component', 'n_intervals')],
    [State('auth-status-store', 'data'),
     State('client-id-store', 'data'),
     State('client-secret-store', 'data'),
     State('url', 'pathname')],
    prevent_initial_call=True
)
def check_auth_status(n_intervals, current_auth_status, stored_client_id, stored_client_secret, pathname):
    """Periodically check if authentication has been completed with enhanced debugging."""
    # Reduce frequency - only check every 5th interval (every 2.5 minutes instead of 30 seconds)
    if n_intervals % 5 != 0:
        return dash.no_update
        
    print("=" * 60)
    print(f"🔄 AUTH CHECK CALLBACK TRIGGERED (interval #{n_intervals})")
    print("=" * 60)
    
    print(f"🔍 Stored client_id: {stored_client_id[:8] if stored_client_id else 'None'}...")
    print(f"🔍 Stored client_secret: {'***' if stored_client_secret else 'None'}")
    print(f"🔍 Current auth status: {current_auth_status}")
    print(f"🔍 Current spotify_api.client_id: {spotify_api.client_id[:8] if spotify_api.client_id else 'None'}...")
    print(f"🔍 Current spotify_api.sp: {spotify_api.sp is not None}")
    
    # Check if we have a debug file from OAuth success
    try:
        import os
        if os.path.exists('debug_oauth_success.json'):
            print("🔍 Found debug_oauth_success.json file!")
            with open('debug_oauth_success.json', 'r') as f:
                debug_data = json.load(f)
            print(f"🔍 Debug file contents: {debug_data}")
            # Remove the file after reading
            os.remove('debug_oauth_success.json')
            print("🗑️ Removed debug file")
            
            # If we found the debug file, that means OAuth was successful
            # Use stored credentials or keep existing ones
            client_id_to_use = stored_client_id or spotify_api.client_id
            client_secret_to_use = stored_client_secret or spotify_api.client_secret
            
            if client_id_to_use and client_secret_to_use:
                print("✅ DEBUG: OAuth success detected via debug file!")
                return {'authenticated': True}, client_id_to_use, client_secret_to_use, {'use_sample': False}
        else:
            print("🔍 No debug_oauth_success.json file found")
    except Exception as e:
        print(f"⚠️ Error checking debug file: {e}")
    
    # Only check if we have stored credentials but aren't authenticated yet
    if stored_client_id and stored_client_secret and (not current_auth_status or not current_auth_status.get('authenticated')):
        print("🔄 Conditions met for auth check - proceeding...")
        
        # Set credentials if not already set
        if spotify_api.client_id != stored_client_id or spotify_api.client_secret != stored_client_secret:
            print("🔄 Setting credentials in spotify_api...")
            spotify_api.set_credentials(stored_client_id, stored_client_secret, os.getenv('REDIRECT_URI'))
            print(f"✅ Credentials set - spotify_api.sp: {spotify_api.sp is not None}")

        # Check authentication status
        print("🔄 Checking authentication status...")
        auth_result = spotify_api.is_authenticated()
        print(f"🔍 Authentication result: {auth_result}")
        
        if spotify_api.sp and auth_result:
            print("✅ DEBUG: Auto-detected successful authentication!")
            
            # Try to get user info to confirm
            try:
                user = spotify_api.sp.current_user()
                print(f"✅ User info retrieved: {user.get('display_name', 'Unknown') if user else 'None'}")
            except Exception as e:
                print(f"⚠️ Could not get user info: {e}")
            
            return {'authenticated': True}, stored_client_id, stored_client_secret, {'use_sample': False}
        else:
            print("❌ Authentication check failed")
            print(f"🔍 spotify_api.sp: {spotify_api.sp is not None}")
            print(f"🔍 auth_result: {auth_result}")
    else:
        print("⏭️ Skipping auth check - conditions not met")
        if not stored_client_id:
            print("   - No stored client_id")
        if not stored_client_secret:
            print("   - No stored client_secret")
        if current_auth_status and current_auth_status.get('authenticated'):
            print("   - Already authenticated")

    print("=" * 60)
    return dash.no_update

# Separate callback for connect-status component (only on onboarding page)
@app.callback(
    Output('connect-status', 'children'),
    [Input('auth-status-store', 'data'),
     Input('connect-button', 'n_clicks'),
     Input('url', 'pathname')],
    [State('client-id-input', 'value'),
     State('client-secret-input', 'value')],
    prevent_initial_call=True
)
def update_connect_status(auth_data, connect_clicks, pathname, client_id, client_secret):
    """Update connect status only when on onboarding page."""
    if pathname != '/onboarding':
        return dash.no_update

    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div()

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle connect button click
    if trigger_id == 'connect-button' and connect_clicks:
        if not client_id or not client_secret:
            return html.Div([
                html.P("❌ Please provide both Client ID and Client Secret.", style={'color': '#FF5555', 'marginBottom': '10px'}),
            ])

        # Check if we need authorization
        if spotify_api.sp:
            auth_result = spotify_api.is_authenticated()
            if not auth_result:
                # Get auth URL
                auth_url = spotify_api.get_auth_url()
                if auth_url:
                    return html.Div([
                        html.H5("🔐 Authorization Required", style={'color': '#1DB954', 'marginBottom': '15px'}),
                        html.P("Click the button below to authorize this app to access your Spotify data:", style={'color': '#FFFFFF', 'marginBottom': '15px'}),
                        html.A(
                            "🎵 Authorize Spotify Access",
                            href=auth_url,
                            target="_blank",
                            style={
                                'display': 'inline-block',
                                'padding': '12px 24px',
                                'backgroundColor': '#1DB954',
                                'color': '#000000',
                                'textDecoration': 'none',
                                'borderRadius': '25px',
                                'fontWeight': 'bold',
                                'fontSize': '16px',
                                'transition': 'all 0.3s ease',
                                'boxShadow': '0 4px 15px rgba(29, 185, 84, 0.3)'
                            },
                            className="spotify-auth-button"
                        ),
                        html.P("After authorizing, you'll be redirected back to the app automatically.", style={'color': '#B3B3B3', 'marginTop': '15px', 'fontSize': '14px'})
                    ], style={
                        'padding': '20px',
                        'backgroundColor': 'rgba(29, 185, 84, 0.1)',
                        'border': '1px solid rgba(29, 185, 84, 0.3)',
                        'borderRadius': '10px',
                        'textAlign': 'center'
                    })
                else:
                    return html.Div([
                        html.P("❌ Could not generate authorization URL. Please check your credentials and redirect URI.", style={'color': '#FF5555'})
                    ])

        return html.Div([
            html.P("❌ Connection failed. Please check your credentials and redirect URI.", style={'color': '#FF5555'})
        ])

    # Handle auth status updates
    if auth_data and auth_data.get('authenticated'):
        return html.Div([
            html.P("✅ Authentication successful!", style={'color': '#1DB954', 'marginBottom': '10px'}),
            html.P("Redirecting to dashboard...", style={'color': '#FFFFFF'})
        ])

    return html.Div()

# --- Settings Page Callbacks ---

@app.callback(
    [Output('auth-status-store', 'data', allow_duplicate=True),
     Output('client-id-store', 'data', allow_duplicate=True),
     Output('client-secret-store', 'data', allow_duplicate=True),
     Output('update-credentials-status', 'children')],
    [Input('update-credentials-button', 'n_clicks'),
     Input('clear-data-button', 'n_clicks')],
    [State('settings-client-id-input', 'value'),
     State('settings-client-secret-input', 'value')],
    prevent_initial_call=True
)
def handle_settings_actions(update_clicks, clear_clicks, client_id, client_secret):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'update-credentials-button':
        if not client_id or not client_secret:
            return dash.no_update, dash.no_update, dash.no_update, "Please provide both Client ID and Client Secret."

        # Clear all cached data first
        print("Clearing all cached data for new credentials...")
        spotify_api.clear_all_cached_data()

        # Set new credentials
        spotify_api.set_credentials(client_id, client_secret, os.getenv('REDIRECT_URI'))
        if spotify_api.sp:
            return {'authenticated': True}, client_id, client_secret, "✅ Credentials updated successfully! Please refresh the page."
        else:
            return dash.no_update, dash.no_update, dash.no_update, "❌ Connection failed. Please check your credentials."

    elif button_id == 'clear-data-button':
        # Clear all data and logout
        print("Clearing all data and logging out...")
        spotify_api.clear_all_cached_data()
        return {'authenticated': False}, None, None, "✅ All data cleared. You have been logged out."

    return dash.no_update

# --- Page Display ---

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('auth-status-store', 'data')],
    [State('client-id-store', 'data'),
     State('client-secret-store', 'data'),
     State('use-sample-data-store', 'data')]
)
def display_page(pathname, auth_data, client_id_data, client_secret_data, use_sample_data_flag):
    """Display the appropriate page based on the URL pathname and authentication status."""
    print(f"🔍 DISPLAY_PAGE DEBUG: pathname={pathname}, auth_data={auth_data}")
    print(f"🔍 DISPLAY_PAGE DEBUG: client_id_data={client_id_data[:8] if client_id_data else 'None'}...")
    print(f"🔍 DISPLAY_PAGE DEBUG: client_secret_data={'***' if client_secret_data else 'None'}")
    print(f"🔍 DISPLAY_PAGE DEBUG: spotify_api.client_id={spotify_api.client_id[:8] if spotify_api.client_id else 'None'}...")
    print(f"🔍 DISPLAY_PAGE DEBUG: spotify_api.sp={spotify_api.sp is not None}")

    # Route-based page display
    if pathname == '/onboarding':
        return create_onboarding_page()
    elif pathname == '/ai-insights':
        return create_ai_insights_page()
    elif pathname == '/settings':
        from modules.layout import create_settings_page
        return create_settings_page()
    elif pathname == '/dashboard':
        # Dashboard route - check if we have working spotify_api even if session storage is broken
        print(f"🔍 DEBUG: Dashboard access check - auth_data: {auth_data}")
        
        # Check if spotify_api is working (user is actually authenticated)
        if spotify_api.sp and spotify_api.is_authenticated():
            print("✅ DEBUG: Spotify API is working, allowing dashboard access")
            return dashboard_layout.create_layout()
        
        # Fallback to session storage check
        is_authenticated = bool(auth_data and auth_data.get('authenticated'))
        
        if not is_authenticated:
            print("❌ DEBUG: Not authenticated, redirecting to onboarding")
            return dcc.Location(pathname='/onboarding', id='redirect-to-onboarding')
        
        # Re-initialize API with stored credentials if needed for dashboard functionality
        if client_id_data and client_secret_data:
            if spotify_api.client_id != client_id_data or spotify_api.client_secret != client_secret_data:
                print("🔄 DEBUG: Re-initializing API with stored credentials for dashboard access")
                spotify_api.set_credentials(client_id_data, client_secret_data, os.getenv('REDIRECT_URI'))
        
        print("✅ DEBUG: Authentication verified, showing dashboard")
        return dashboard_layout.create_layout()
    else:
        # Default root path - redirect based on authentication
        # Check if spotify_api is working first
        if spotify_api.sp and spotify_api.is_authenticated():
            print("✅ DEBUG: Spotify API is working, redirecting to dashboard")
            return dcc.Location(pathname='/dashboard', id='redirect-to-dashboard')
        
        # Fallback to session storage check
        is_authenticated = bool(auth_data and auth_data.get('authenticated'))
        
        if is_authenticated:
            return dcc.Location(pathname='/dashboard', id='redirect-to-dashboard')
        else:
            return dcc.Location(pathname='/onboarding', id='redirect-to-onboarding')

# --- Data Callbacks ---

# Update user data
@app.callback(
    Output('user-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks'),
    State('client-id-store', 'data'),
    State('client-secret-store', 'data'),
    State('use-sample-data-store', 'data')
)
def update_user_data(n_intervals, n_clicks, client_id_data, client_secret_data, use_sample_data_flag):
    """Fetch and store user profile data, or use sample data."""
    print("👤 DEBUG: Fetching user profile data...")
    print(f"👤 DEBUG: client_id_data: {client_id_data[:8] if client_id_data else 'None'}...")
    print(f"👤 DEBUG: client_secret_data: {'***' if client_secret_data else 'None'}")
    print(f"👤 DEBUG: use_sample_data_flag: {use_sample_data_flag}")
    print(f"👤 DEBUG: spotify_api.sp: {spotify_api.sp is not None}")
    print(f"👤 DEBUG: spotify_api.use_sample_data: {spotify_api.use_sample_data}")
    print(f"👤 DEBUG: spotify_api.client_id: {spotify_api.client_id[:8] if spotify_api.client_id else 'None'}...")
    print(f"👤 DEBUG: spotify_api.client_secret: {'***' if spotify_api.client_secret else 'None'}")

    use_sample = use_sample_data_flag and use_sample_data_flag.get('use_sample', False)
    print(f"👤 DEBUG: Final use_sample decision: {use_sample}")

    if use_sample:
        print("📊 DEBUG: Using sample data for user profile.")
        return {
            'display_name': 'Sample User',
            'id': 'sample-user-id',
            'followers': 123,
            'following': 45,
            'image_url': '',
            'product': 'premium'
        }

    if not spotify_api.sp:
        if client_id_data and client_secret_data:
            print("🔄 DEBUG: Re-initializing Spotify API with stored credentials...")
            spotify_api.set_credentials(client_id_data, client_secret_data, os.getenv('REDIRECT_URI'))
        else:
            print("❌ DEBUG: Spotify API not initialized. Cannot fetch user data.")
            return {}

    try:
        # Always try to fetch from API first when we have a connection
        print("🌐 DEBUG: Attempting to fetch user data from Spotify API...")
        user_data = spotify_api.get_user_profile()
        if user_data:
            print(f"✅ DEBUG: Got user data from API: {user_data}")
            # Save user data to database only
            db.save_user(user_data)

            # Start comprehensive data collection for new users
            print("🔄 Starting comprehensive data collection...")
            try:
                # 1. Collect recently played tracks (last 50)
                recently_played = spotify_api.get_recently_played(limit=50)
                if recently_played:
                    print(f"📀 Collecting {len(recently_played)} recently played tracks...")
                    for track in recently_played:
                        db.save_track(track)
                        played_at = track.get('played_at', datetime.now().isoformat())
                        db.save_listening_history(
                            user_id=user_data['id'],
                            track_id=track['id'],
                            played_at=played_at,
                            source='recently_played'
                        )

                # 2. Collect top tracks for different time ranges
                for time_range in ['short_term', 'medium_term', 'long_term']:
                    top_tracks = spotify_api.get_top_tracks(limit=20, time_range=time_range)
                    if top_tracks:
                        print(f"🎵 Collecting {len(top_tracks)} top tracks ({time_range})...")
                        for track in top_tracks:
                            db.save_track(track)
                            db.save_listening_history(
                                user_id=user_data['id'],
                                track_id=track['id'],
                                played_at=datetime.now().isoformat(),
                                source=f'top_{time_range}'
                            )

                # 3. Collect saved tracks (liked songs)
                saved_tracks = spotify_api.get_saved_tracks(limit=50)
                if saved_tracks:
                    print(f"💚 Collecting {len(saved_tracks)} saved tracks...")
                    for track in saved_tracks:
                        db.save_track(track)
                        added_at = track.get('added_at', datetime.now().isoformat())
                        db.save_listening_history(
                            user_id=user_data['id'],
                            track_id=track['id'],
                            played_at=added_at,
                            source='saved'
                        )

                # 4. Start historical data collection for the past two weeks
                data_collector.collect_historical_data(user_data['id'])

                print("✅ Data collection completed successfully!")

            except Exception as e:
                print(f"⚠️ Error during data collection: {e}")
                # Continue anyway - user can still use the app

            return user_data

        # Try to get user data from database if API fails
        print("⚠️ DEBUG: API failed, trying to load from database...")
        try:
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, display_name, followers FROM users ORDER BY last_updated DESC LIMIT 1')
            row = cursor.fetchone()
            conn.close()

            if row:
                user_data = {
                    'id': row[0],
                    'display_name': row[1],
                    'followers': row[2],
                    'following': 0,
                    'image_url': '',
                    'product': 'Unknown'
                }
                print(f"📁 DEBUG: Loaded user data from database: {user_data}")
                return user_data
        except Exception as e:
            print(f"❌ DEBUG: Error loading user data from database: {e}")

        print("❌ DEBUG: No user data available from any source.")
        return {}
    except Exception as e:
        print(f"Error in update_user_data callback: {e}")
        return {}

# Update header with user data
@app.callback(
    Output('header-container', 'children'),
    Input('user-data-store', 'data')
)
def update_header(user_data):
    """Update the header with user profile data."""
    print(f"Updating header with user data: {user_data}")  # Debug log
    header = dashboard_layout.create_header(user_data)
    print(f"Created header: {header}")  # Debug log
    return header

# Update current track
@app.callback(
    Output('current-track-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('use-sample-data-store', 'data')
)
def update_current_track(n_intervals, use_sample_data_flag):
    """Fetch and store currently playing track, or return sample data."""
    use_sample = use_sample_data_flag and use_sample_data_flag.get('use_sample', False)

    print(f"🎵 DEBUG: Current track update - use_sample: {use_sample}, spotify_api.sp: {spotify_api.sp is not None}")

    # Never use sample data - always try to get real data
    if use_sample:
        print("🚫 DEBUG: Sample data requested but disabled - fetching real data instead")
        use_sample = False

    try:
        current_track = spotify_api.get_currently_playing()
        if current_track and 'track' in current_track:
            # Get user profile to get user_id
            user_data = spotify_api.get_user_profile()
            if user_data:
                current_track['user_id'] = user_data['id']

            # Save to CSV for backward compatibility
            data_processor.save_data([current_track], 'current_track.csv')

            # Save to database if we have user_id
            if 'user_id' in current_track:
                # Make sure we have all required fields
                if 'id' not in current_track:
                    current_track['id'] = f"current-{datetime.now().timestamp()}"

                # Ensure track has all required fields
                track_data = {
                    'id': current_track['id'],
                    'name': current_track.get('track', 'Unknown Track'),
                    'artist': current_track.get('artist', 'Unknown Artist'),
                    'album': current_track.get('album', 'Unknown Album'),
                    'duration_ms': current_track.get('duration_ms', 0),
                    'popularity': current_track.get('popularity', 0),
                    'preview_url': current_track.get('preview_url', ''),
                    'image_url': current_track.get('image_url', ''),
                    'added_at': datetime.now().replace(microsecond=0).isoformat()
                }

                db.save_track(track_data)
                db.save_listening_history(
                    user_id=current_track['user_id'],
                    track_id=track_data['id'],
                    played_at=datetime.now().replace(microsecond=0).isoformat(),
                    source='current'
                )

            return current_track

        # If no current track, try to get the most recent one from the database
        user_data = spotify_api.get_user_profile()
        if user_data and user_data.get('id') != 'sample-user-id': # Don't query DB if using sample user
            conn = sqlite3.connect(db.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get the most recent track
            cursor.execute('''
                SELECT
                    t.track_id as id,
                    t.name as track,
                    t.artist,
                    t.album,
                    t.duration_ms,
                    t.image_url,
                    h.played_at
                FROM tracks t
                JOIN listening_history h ON t.track_id = h.track_id
                WHERE h.user_id = ?
                ORDER BY h.played_at DESC
                LIMIT 1
            ''', (user_data['id'],))

            row = cursor.fetchone()
            conn.close()

            if row:
                # Create a "not currently playing" track object
                track_data = dict(row)
                track_data['is_playing'] = False
                track_data['progress_ms'] = 0
                return track_data

        return {}
    except Exception as e:
        print(f"Error updating current track: {e}")
        return {}

# Update current track display
@app.callback(
    Output('current-track-container', 'children'),
    Input('current-track-store', 'data')
)
def update_current_track_display(current_track):
    """Update the currently playing track display."""
    # Check if current_track is None or empty or if is_playing is False
    if not current_track or current_track.get('is_playing') is False:
        return html.Div([
            html.H3("Not Currently Playing", style={'color': SPOTIFY_WHITE, 'textAlign': 'center'}),
            html.P("Play something on Spotify to see it here", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
        ], style={
            'padding': '20px',
            'borderRadius': '10px',
            'backgroundColor': '#121212',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
            'margin': '20px 0',
            'textAlign': 'center'
        })

    # Check if we have the required fields
    if 'track' not in current_track:
        if 'name' in current_track:
            # Use name field instead
            current_track['track'] = current_track['name']
        else:
            return html.Div([
                html.H3("Track Information Unavailable", style={'color': SPOTIFY_WHITE, 'textAlign': 'center'}),
                html.P("Unable to retrieve track details", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
            ], style={
                'padding': '20px',
                'borderRadius': '10px',
                'backgroundColor': '#121212',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
                'margin': '20px 0',
                'textAlign': 'center'
            })

    # Set default values for missing fields
    if 'progress_ms' not in current_track:
        current_track['progress_ms'] = 0

    if 'duration_ms' not in current_track:
        current_track['duration_ms'] = 0

    # Calculate progress percentage - handle None values
    if current_track.get('duration_ms') is None:
        current_track['duration_ms'] = 0
    if current_track.get('progress_ms') is None:
        current_track['progress_ms'] = 0

    progress_percent = (current_track['progress_ms'] / current_track['duration_ms'] * 100) if current_track['duration_ms'] > 0 else 0

    # Format duration
    duration_sec = current_track['duration_ms'] / 1000
    progress_sec = current_track['progress_ms'] / 1000
    duration_str = f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}"
    progress_str = f"{int(progress_sec // 60)}:{int(progress_sec % 60):02d}"

    return html.Div([
        html.H3("Currently Playing", style={'color': SPOTIFY_GREEN, 'textAlign': 'center', 'marginBottom': '20px'}),

        # Track info with album art
        html.Div([
            # Album art
            html.Div([
                html.Img(
                    src=current_track.get('image_url', ''),
                    style={'width': '100%', 'borderRadius': '8px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}
                ) if current_track.get('image_url') else html.Div(
                    style={'width': '100%', 'paddingBottom': '100%', 'backgroundColor': SPOTIFY_GRAY, 'borderRadius': '8px'}
                )
            ], style={'width': '150px', 'display': 'inline-block', 'verticalAlign': 'top'}),

            # Track details
            html.Div([
                html.H4(current_track['track'], style={'color': SPOTIFY_WHITE, 'marginBottom': '5px'}),
                html.P(f"by {current_track['artist']}", style={'color': SPOTIFY_GRAY, 'marginBottom': '5px'}),
                html.P(f"from {current_track['album']}", style={'color': SPOTIFY_GRAY, 'marginBottom': '15px'}),

                # Progress bar
                html.Div([
                    html.Div(style={
                        'width': f'{progress_percent}%',
                        'backgroundColor': SPOTIFY_GREEN,
                        'height': '4px',
                        'borderRadius': '2px'
                    })
                ], style={
                    'width': '100%',
                    'backgroundColor': '#333333',
                    'height': '4px',
                    'borderRadius': '2px',
                    'marginBottom': '5px'
                }),

                # Time indicators
                html.Div([
                    html.Span(progress_str, style={'color': SPOTIFY_GRAY, 'fontSize': '0.8em'}),
                    html.Span(duration_str, style={'color': SPOTIFY_GRAY, 'fontSize': '0.8em', 'float': 'right'})
                ])
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '20px', 'width': 'calc(100% - 180px)'})
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
    ], style={
        'padding': '20px',
        'borderRadius': '10px',
        'backgroundColor': '#121212',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
        'margin': '20px 0'
    })

# Update top tracks chart
@app.callback(
    Output('top-tracks-chart', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_tracks_chart(n_intervals, n_clicks):
    """Update the top tracks chart using Spotify's official top tracks."""
    # Use Spotify's official top tracks directly - this is the correct approach!
    try:
        # Get top tracks from Spotify's algorithm (short_term = last 4 weeks)
        top_tracks_data = spotify_api.get_top_tracks(limit=10, time_range='short_term')

        if not top_tracks_data:
            # Try medium_term if short_term has no data
            top_tracks_data = spotify_api.get_top_tracks(limit=10, time_range='medium_term')

        if not top_tracks_data:
            # Try long_term if medium_term has no data
            top_tracks_data = spotify_api.get_top_tracks(limit=10, time_range='long_term')

        if not top_tracks_data:
            return html.Div("No top tracks data available. Listen to more music on Spotify to see your top tracks!",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        # Convert to DataFrame for visualization
        tracks_df = pd.DataFrame(top_tracks_data)

        # Save tracks to database for other analysis (but don't use for ranking)
        user_data = spotify_api.get_user_profile()
        if user_data and n_clicks is not None and n_clicks > 0:
            for track in top_tracks_data:
                db.save_track(track)

    except Exception as e:
        print(f"Error getting top tracks: {e}")
        return html.Div("Error loading top tracks",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Enhanced top tracks ranking with duration weighting and improved scoring
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            t.popularity,
            t.image_url,
            t.duration_ms,
            COUNT(DISTINCT h.history_id) as play_count,
            SUM(CASE
                WHEN t.duration_ms > 0 THEN t.duration_ms
                ELSE 180000
            END) as total_listening_time_ms,
            AVG(CASE
                WHEN t.duration_ms > 0 THEN t.duration_ms
                ELSE 180000
            END) as avg_duration_ms,
            -- Enhanced weighted score: play frequency (50%) + listening time (30%) + popularity (20%)
            (
                (COUNT(DISTINCT h.history_id) * 0.5) +
                (SUM(CASE WHEN t.duration_ms > 0 THEN t.duration_ms ELSE 180000 END) / 1000000.0 * 0.3) +
                (t.popularity / 100.0 * 0.2)
            ) as weighted_score
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
        AND h.source IN ('played', 'recently_played', 'current')  -- Only actual listening events
        AND t.name IS NOT NULL AND t.name != ''
        GROUP BY t.track_id, t.name, t.artist, t.album, t.popularity, t.image_url, t.duration_ms
        HAVING play_count >= 2  -- Minimum 2 plays to be considered
        ORDER BY weighted_score DESC
        LIMIT 10
    ''', (current_date,))

    top_tracks_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Convert to DataFrame
    if top_tracks_data:
        top_tracks_df = pd.DataFrame(top_tracks_data)
        # Add rank column
        top_tracks_df['rank'] = range(1, len(top_tracks_df) + 1)
    else:
        # Create empty DataFrame with the right columns
        top_tracks_df = pd.DataFrame(columns=['track', 'artist', 'album', 'popularity', 'rank'])

    # Create visualization
    return visualizations.create_top_tracks_soundwave(top_tracks_df)

# Update saved tracks list
@app.callback(
    Output('saved-tracks-chart', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_saved_tracks_chart(n_intervals, n_clicks):
    """Update the saved tracks chart."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        user_data = spotify_api.get_user_profile()
        if user_data:
            # Fetch saved tracks and save to database
            saved_tracks_data = spotify_api.get_saved_tracks(limit=10)
            if saved_tracks_data:
                # Save to database
                for track in saved_tracks_data:
                    db.save_track(track)
                    # Use the improved timestamp normalization
                    timestamp = track.get('added_at')
                    played_at = normalize_timestamp(timestamp)
                    if not played_at:
                        # If normalization fails, use current time
                        played_at = datetime.now().replace(microsecond=0).isoformat()

                    db.save_listening_history(
                        user_id=user_data['id'],
                        track_id=track['id'],
                        played_at=played_at,
                        source='saved'
                    )

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for saved tracks with duration information - prevent duplicates
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            t.image_url,
            t.duration_ms,
            t.popularity,
            MAX(h.played_at) as added_at
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE h.source = 'saved'
        AND t.name IS NOT NULL
        AND t.artist IS NOT NULL
        GROUP BY t.track_id, t.name, t.artist, t.album, t.image_url, t.duration_ms, t.popularity
        ORDER BY added_at DESC
        LIMIT 20
    ''')

    saved_tracks_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Convert to DataFrame and process
    if saved_tracks_data:
        saved_tracks_df = pd.DataFrame(saved_tracks_data)

        # Calculate duration in minutes
        if 'duration_ms' in saved_tracks_df.columns:
            saved_tracks_df['duration_minutes'] = saved_tracks_df['duration_ms'].apply(calculate_duration_minutes)

        # Ensure added_at is properly formatted
        if 'added_at' in saved_tracks_df.columns:
            saved_tracks_df['added_at'] = saved_tracks_df['added_at'].apply(normalize_timestamp)
            saved_tracks_df['added_at'] = pd.to_datetime(saved_tracks_df['added_at'], errors='coerce')
            # Remove rows with invalid timestamps
            saved_tracks_df = saved_tracks_df.dropna(subset=['added_at'])

        print(f"Processed {len(saved_tracks_df)} saved tracks for visualization")
    else:
        # Create empty DataFrame with the right columns
        saved_tracks_df = pd.DataFrame(columns=['track', 'artist', 'album', 'added_at', 'duration_minutes'])

    # Create list visualization
    return visualizations.create_saved_tracks_list(saved_tracks_df)

# Update playlists list
@app.callback(
    Output('playlists-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_playlists_list(n_intervals, n_clicks):
    """Update the playlists fancy list."""
    # Get playlists data directly from API (playlists don't need database storage for this view)
    try:
        playlists_data = spotify_api.get_playlists(limit=10)
        playlists_df = pd.DataFrame(playlists_data) if playlists_data else pd.DataFrame()
    except Exception as e:
        print(f"Error getting playlists: {e}")
        playlists_df = pd.DataFrame()

    # Create visualization - import the standalone function
    from modules.visualizations import create_playlists_fancy_list
    return create_playlists_fancy_list(playlists_df)

# Update audio features chart
@app.callback(
    Output('audio-features-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_audio_features_chart(n_intervals, n_clicks):
    """Update the audio features chart."""
    # Fetch new data if refresh button clicked
    if n_clicks is not None and n_clicks > 0:
        user_data = spotify_api.get_user_profile()
        if user_data:
            # Get audio features for top tracks
            audio_features_data = spotify_api.get_audio_features_for_top_tracks(limit=5)
            if audio_features_data:
                # Save to database
                for track in audio_features_data:
                    # Save track with audio features
                    db.save_track({
                        'id': track['id'],
                        'name': track['track'],
                        'artist': track['artist'],
                        'duration_ms': track.get('duration_ms', 0),
                        'popularity': 0,  # Not available in this context
                        'preview_url': '',  # Not available in this context
                        'image_url': '',  # Not available in this context
                        'added_at': datetime.now().replace(microsecond=0).isoformat(),
                        # Audio features
                        'danceability': track.get('danceability', 0),
                        'energy': track.get('energy', 0),
                        'key': track.get('key', 0),
                        'loudness': track.get('loudness', 0),
                        'mode': track.get('mode', 0),
                        'speechiness': track.get('speechiness', 0),
                        'acousticness': track.get('acousticness', 0),
                        'instrumentalness': track.get('instrumentalness', 0),
                        'liveness': track.get('liveness', 0),
                        'valence': track.get('valence', 0),
                        'tempo': track.get('tempo', 0)
                    })

                    # Save listening history entry with consistent datetime format
                    db.save_listening_history(
                        user_id=user_data['id'],
                        track_id=track['id'],
                        played_at=datetime.now().replace(microsecond=0).isoformat(),
                        source='audio_features'
                    )

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for top tracks using enhanced ranking system (consistent with main top tracks)
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT
            t.track_id as id,
            t.name as track,
            t.artist,
            t.album,
            COUNT(DISTINCT h.history_id) as play_count,
            SUM(CASE
                WHEN t.duration_ms > 0 THEN t.duration_ms
                ELSE 180000
            END) as total_listening_time_ms,
            -- Enhanced weighted score: play frequency (50%) + listening time (30%) + popularity (20%)
            (
                (COUNT(DISTINCT h.history_id) * 0.5) +
                (SUM(CASE WHEN t.duration_ms > 0 THEN t.duration_ms ELSE 180000 END) / 1000000.0 * 0.3) +
                (t.popularity / 100.0 * 0.2)
            ) as weighted_score
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
        AND date(h.played_at) <= ?
        AND h.source IN ('played', 'recently_played', 'current')  -- Only actual listening events
        AND t.name IS NOT NULL AND t.name != ''
        GROUP BY t.track_id, t.name, t.artist, t.album, t.popularity, t.duration_ms
        HAVING play_count >= 2  -- Minimum 2 plays to be considered
        ORDER BY weighted_score DESC
        LIMIT 5
    ''', (current_date,))

    tracks_data = [dict(row) for row in cursor.fetchall()]

    # Get audio features for these tracks
    audio_features_data = []
    for track in tracks_data:
        # Get audio features from API
        features = spotify_api.get_audio_features_safely(track['id'])

        # Combine track info with audio features
        audio_features_data.append({
            'track': track['track'],
            'artist': track['artist'],
            'id': track['id'],
            'danceability': features.get('danceability', 0),
            'energy': features.get('energy', 0),
            'key': features.get('key', 0),
            'loudness': features.get('loudness', 0),
            'mode': features.get('mode', 0),
            'speechiness': features.get('speechiness', 0),
            'acousticness': features.get('acousticness', 0),
            'instrumentalness': features.get('instrumentalness', 0),
            'liveness': features.get('liveness', 0),
            'valence': features.get('valence', 0),
            'tempo': features.get('tempo', 0)
        })

    conn.close()

    # Convert to DataFrame
    if audio_features_data:
        audio_features_df = pd.DataFrame(audio_features_data)
    else:
        # Create empty DataFrame with the right columns
        audio_features_df = pd.DataFrame(columns=[
            'track', 'artist', 'id', 'danceability', 'energy', 'key', 'loudness',
            'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
            'valence', 'tempo'
        ])

    # Create visualization
    return visualizations.create_audio_features_radar(audio_features_df)

# Update top artists chart
@app.callback(
    Output('top-artists-chart', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_artists_chart(n_intervals, n_clicks):
    """Update the top artists chart using Spotify's official top artists."""
    print(f"=== TOP ARTISTS CALLBACK TRIGGERED: intervals={n_intervals}, clicks={n_clicks} ===")

    # Use Spotify's official top artists directly - this is the correct approach!
    try:
        # Get top artists from Spotify's algorithm (short_term = last 4 weeks)
        top_artists_data = spotify_api.get_top_artists(limit=10, time_range='short_term')

        if not top_artists_data:
            # Try medium_term if short_term has no data
            top_artists_data = spotify_api.get_top_artists(limit=10, time_range='medium_term')

        if not top_artists_data:
            # Try long_term if medium_term has no data
            top_artists_data = spotify_api.get_top_artists(limit=10, time_range='long_term')

        if not top_artists_data:
            return html.Div("No top artists data available. Listen to more music on Spotify to see your top artists!",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        # Convert to DataFrame for visualization
        artists_df = pd.DataFrame(top_artists_data)

        print(f"✅ Got {len(top_artists_data)} top artists from Spotify API")
        for i, artist in enumerate(top_artists_data[:3]):
            print(f"  {i+1}. {artist['artist']} (popularity: {artist['popularity']})")

    except Exception as e:
        print(f"Error getting top artists: {e}")
        return html.Div("Error loading top artists",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

    # Create visualization using the Spotify API data
    visualizations = SpotifyVisualizations()
    return visualizations.create_top_artists_soundwave(artists_df)

# Update top track highlight
@app.callback(
    Output('top-track-highlight-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_track_highlight(n_intervals, n_clicks):
    """Update the top track highlight card."""
    try:
        # Get top track from database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Play count calculation: COUNT(DISTINCT h.history_id) counts unique listening events
        # This uses all historical data while preventing duplicate counting from same timestamp/source
        # Database UNIQUE constraint on (user_id, track_id, played_at) prevents exact duplicates
        cursor.execute('''
            SELECT t.name as track_name, t.artist as artist_name, t.album as album_name,
                   t.popularity, t.image_url,
                   COUNT(DISTINCT h.history_id) as play_count,
                   COUNT(h.history_id) as total_entries
            FROM tracks t
            JOIN listening_history h ON t.track_id = h.track_id
            WHERE t.name IS NOT NULL AND t.name != ''
            AND t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
            AND h.source IN ('played', 'recently_played', 'current')  -- Only actual listening events
            GROUP BY t.track_id, t.name, t.artist, t.album, t.popularity, t.image_url
            ORDER BY play_count DESC, t.popularity DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        conn.close()

        if result:
            track_data = {
                'track': result[0],      # track_name
                'artist': result[1],     # artist_name
                'album': result[2] or 'Unknown Album',  # album_name
                'popularity': result[3] or 0,           # popularity
                'image_url': result[4] or '',           # image_url
                'play_count': result[5]                 # play_count
            }
            return visualizations.create_top_track_highlight_component(track_data)
        else:
            return html.Div([
                html.H3("Your #1 Track", style={'color': SPOTIFY_GREEN, 'textAlign': 'center'}),
                html.P("Start listening to discover your top track!", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
            ], style={'padding': '20px'})

    except Exception as e:
        print(f"Error updating top track highlight: {e}")
        return html.Div("Error loading top track", style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

# Update top artist highlight
@app.callback(
    Output('top-artist-highlight-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_artist_highlight(n_intervals, n_clicks):
    """Update the top artist highlight card."""
    try:
        # Get top artist from database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Play count calculation for artists: COUNT(DISTINCT h.history_id) counts unique listening events
        # This uses all historical data while preventing duplicate counting from same timestamp/source
        cursor.execute('''
            SELECT t.artist as artist_name,
                   COUNT(DISTINCT h.history_id) as play_count,
                   AVG(t.popularity) as avg_popularity,
                   MAX(t.image_url) as image_url,
                   COUNT(h.history_id) as total_entries
            FROM tracks t
            JOIN listening_history h ON t.track_id = h.track_id
            WHERE t.artist IS NOT NULL AND t.artist != ''
            AND t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
            AND h.source IN ('played', 'recently_played', 'current')  -- Only actual listening events
            GROUP BY t.artist
            ORDER BY play_count DESC, avg_popularity DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        conn.close()

        if result:
            artist_data = {
                'artist': result[0],
                'play_count': result[1],
                'popularity': int(result[2]) if result[2] else 0,
                'image_url': result[3] or ''
            }
            return visualizations.create_top_artist_highlight_component(artist_data)
        else:
            return html.Div([
                html.H3("Your Top Artist", style={'color': SPOTIFY_GREEN, 'textAlign': 'center'}),
                html.P("Start listening to discover your top artist!", style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
            ], style={'padding': '20px'})

    except Exception as e:
        print(f"Error updating top artist highlight: {e}")
        return html.Div("Error loading top artist", style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

# Update genre chart
@app.callback(
    Output('genre-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_genre_chart(n_intervals, n_clicks):
    """Update the genre chart."""
    try:
        print("=== Genre Chart Update Started ===")

        # Fetch new data if refresh button clicked
        if n_clicks is not None and n_clicks > 0:
            print("Fetching genre data from recently played tracks...")
            user_data = spotify_api.get_user_profile()
            if user_data:
                print(f"User ID: {user_data['id']}")

                # IMPORTANT: Save user to database first to ensure user exists
                try:
                    print(f"Saving user {user_data['display_name']} to database")
                    db.save_user(user_data)
                    print(f"User saved successfully")
                except Exception as e:
                    print(f"ERROR saving user to database: {e}")
                    import traceback
                    traceback.print_exc()

                # Verify user exists in database
                conn = sqlite3.connect(db.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_data['id'],))
                user_exists = cursor.fetchone() is not None
                conn.close()

                if not user_exists:
                    print(f"WARNING: User {user_data['id']} not found in database after save attempt")
                    print("Creating user record again")
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO users (user_id, display_name, followers, last_updated)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (user_data['id'], user_data.get('display_name', 'Unknown'), user_data.get('followers', 0)))
                    conn.commit()
                    conn.close()
                    print(f"User {user_data['id']} created manually")

                # Fetch up to 200 recently played tracks using pagination
                print("Fetching up to 200 recently played tracks...")
                all_tracks = []
                before_timestamp = None

                # Spotify API has a limit of 50 tracks per call, so we need to paginate
                # We'll make up to 4 calls to get up to 200 tracks with better error handling
                max_batches = 4
                successful_batches = 0

                for i in range(max_batches):
                    try:
                        print(f"Fetching batch {i+1}/{max_batches}...")

                        # Get recently played tracks with retry logic
                        tracks = spotify_api.get_recently_played(limit=50, before=before_timestamp)

                        if not tracks or len(tracks) == 0:
                            print("No more tracks available")
                            break

                        print(f"Retrieved {len(tracks)} tracks in batch {i+1}")
                        all_tracks.extend(tracks)
                        successful_batches += 1

                        # Save tracks to database
                        for track in tracks:
                            db.save_track(track)

                            # Normalize the timestamp
                            played_at = normalize_timestamp(track.get('played_at'))
                            if not played_at:
                                # If normalization fails, use current time
                                played_at = datetime.now().replace(microsecond=0).isoformat()

                            # Save listening history
                            db.save_listening_history(
                                user_id=user_data['id'],
                                track_id=track['id'],
                                played_at=played_at,
                                source='played'
                            )

                        # Update the timestamp for the next request
                        # We use the played_at time of the last track as the 'before' parameter
                        last_track = tracks[-1]
                        played_at = last_track.get('played_at')

                        if played_at:
                            try:
                                # Use normalize_timestamp to parse consistently
                                normalized_timestamp = normalize_timestamp(played_at)
                                if normalized_timestamp:
                                    dt = datetime.fromisoformat(normalized_timestamp)
                                    # Convert to timestamp for the next request
                                    # Subtract 1 millisecond to avoid getting the same track again
                                    before_timestamp = int(dt.timestamp() * 1000) - 1
                                    print(f"Next request will fetch tracks before {dt}")
                                else:
                                    print(f"Failed to normalize timestamp: {played_at}")
                                    break
                            except ValueError as e:
                                print(f"Error parsing timestamp: {e}")
                                break
                        else:
                            print("Last track has no played_at timestamp")
                            break

                        # Progressive delay to avoid rate limiting
                        if i == 0:
                            time.sleep(1)  # Short delay after first batch
                        elif i == 1:
                            time.sleep(2)  # Longer delay after second batch
                        else:
                            time.sleep(3)  # Even longer delay for subsequent batches

                    except Exception as e:
                        print(f"Error fetching recently played tracks in batch {i+1}: {e}")

                        # Check if it's a rate limit error
                        if "429" in str(e) or "rate limit" in str(e).lower():
                            print("Rate limit detected, waiting longer before retry...")
                            time.sleep(10)  # Wait 10 seconds for rate limit

                            # Try one more time for this batch
                            try:
                                tracks = spotify_api.get_recently_played(limit=50, before=before_timestamp)
                                if tracks:
                                    print(f"Retry successful for batch {i+1}, retrieved {len(tracks)} tracks")
                                    all_tracks.extend(tracks)
                                    successful_batches += 1

                                    # Process tracks as before...
                                    for track in tracks:
                                        db.save_track(track)
                                        played_at = normalize_timestamp(track.get('played_at'))
                                        if not played_at:
                                            played_at = datetime.now().replace(microsecond=0).isoformat()
                                        db.save_listening_history(
                                            user_id=user_data['id'],
                                            track_id=track['id'],
                                            played_at=played_at,
                                            source='played'
                                        )

                                    # Update timestamp for next request
                                    last_track = tracks[-1]
                                    played_at = last_track.get('played_at')
                                    if played_at:
                                        normalized_timestamp = normalize_timestamp(played_at)
                                        if normalized_timestamp:
                                            dt = datetime.fromisoformat(normalized_timestamp)
                                            before_timestamp = int(dt.timestamp() * 1000) - 1
                                else:
                                    print(f"Retry failed for batch {i+1}")
                                    break
                            except Exception as retry_e:
                                print(f"Retry also failed for batch {i+1}: {retry_e}")
                                break
                        else:
                            import traceback
                            traceback.print_exc()
                            break

                print(f"Total tracks fetched: {len(all_tracks)} from {successful_batches}/{max_batches} successful batches")

                # Extract unique artists from the tracks
                artists = set()
                for track in all_tracks:
                    artist_name = track.get('artist')
                    if artist_name:
                        artists.add(artist_name)

                print(f"Found {len(artists)} unique artists in recently played tracks")

                # Process each artist to get their genres with improved rate limiting
                processed_count = 0
                for artist_name in artists:
                    print(f"Processing genres for artist: {artist_name} ({processed_count + 1}/{len(artists)})")

                    # Check if we already have genres for this artist
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM genres WHERE artist_name = ?", (artist_name,))
                    existing_genres = cursor.fetchone()[0]
                    conn.close()

                    if existing_genres > 0:
                        print(f"Already have {existing_genres} genres for artist: {artist_name}")
                        continue

                    # Use our new function to get genres
                    genres = spotify_api.get_artist_genres(artist_name)

                    if genres:
                        print(f"Found {len(genres)} genres for artist {artist_name}: {genres}")

                        # Save each genre to the database
                        for genre in genres:
                            if genre and genre.strip():  # Skip empty or whitespace-only genres
                                success = db.save_genre(genre.strip(), artist_name)
                                if success:
                                    print(f"Successfully saved genre '{genre}' for artist '{artist_name}'")
                                else:
                                    print(f"Failed to save genre '{genre}' to database")
                    else:
                        print(f"No genres found for artist {artist_name}")
                        # Save a placeholder to avoid repeated lookups
                        db.save_genre("unknown", artist_name)

                    processed_count += 1

                    # Improved rate limiting
                    if processed_count % 5 == 0:
                        print(f"Taking a longer break after processing {processed_count} artists...")
                        time.sleep(3)  # Longer break every 5 artists
                    else:
                        time.sleep(1)  # Standard delay

        # Process all artists in the database to ensure we have genres for all of them
        print("Processing genres for all artists in the database...")

        # Get all artists from the database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT artist FROM tracks")
        all_artists = [row[0] for row in cursor.fetchall()]
        conn.close()

        print(f"Found {len(all_artists)} unique artists in the database")

        # Process each artist to get their genres with better batching
        processed_artists = 0
        max_artists_per_session = 50  # Limit processing to avoid long delays

        for artist_name in all_artists[:max_artists_per_session]:  # Limit to first 50 artists
            # Check if we already have genres for this artist
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM genres WHERE artist_name = ?", (artist_name,))
            genre_count = cursor.fetchone()[0]
            conn.close()

            # If we don't have genres for this artist, get them
            if genre_count == 0:
                print(f"Getting genres for artist: {artist_name} ({processed_artists + 1}/{min(len(all_artists), max_artists_per_session)})")

                # Get genres for this artist
                genres = spotify_api.get_artist_genres(artist_name)

                # Save each genre to the database
                if genres:
                    for genre in genres:
                        if genre and genre.strip():  # Skip empty or whitespace-only genres
                            success = db.save_genre(genre.strip(), artist_name)
                            if success:
                                print(f"Successfully saved genre '{genre}' for artist '{artist_name}'")
                else:
                    # If no genres found, save a placeholder to avoid repeated lookups
                    print(f"No genres found for artist {artist_name}, saving placeholder")
                    db.save_genre("unknown", artist_name)

                processed_artists += 1

                # Improved rate limiting
                if processed_artists % 10 == 0:
                    print(f"Taking an extended break after processing {processed_artists} artists...")
                    time.sleep(5)  # Extended break every 10 artists
                elif processed_artists % 5 == 0:
                    print(f"Taking a longer break after processing {processed_artists} artists...")
                    time.sleep(2)  # Longer break every 5 artists
                else:
                    time.sleep(1)  # Standard delay
            else:
                print(f"Already have {genre_count} genres for artist: {artist_name}")

        if len(all_artists) > max_artists_per_session:
            print(f"Processed {max_artists_per_session} artists this session. {len(all_artists) - max_artists_per_session} remaining for next refresh.")

        # Get user data if not already available
        if 'user_data' not in locals() or user_data is None:
            user_data = spotify_api.get_user_profile()

        # Get user data to determine user_id
        user_data = spotify_api.get_user_profile()
        if not user_data:
            print("No user data available for genre chart")
            genre_data = []
        else:
            user_id = user_data['id']
            current_date = datetime.now().strftime('%Y-%m-%d')

            # Use standardized genre query function
            genre_data = db.get_user_top_genres(
                user_id=user_id,
                limit=10,
                exclude_unknown=True,
                include_sources=['played', 'recently_played', 'current'],
                date_filter=current_date
            )

        # Convert to DataFrame
        if genre_data:
            genre_df = pd.DataFrame(genre_data)
            print(f"Genre data loaded from listening history: {len(genre_df)} genres")
            print(f"Top genres: {genre_df['genre'].tolist()}")
        else:
            print("No genre data in listening history")
            # Create an empty DataFrame
            genre_df = pd.DataFrame(columns=['genre', 'count'])

        # Create visualization
        print("Creating genre pie chart...")
        fig = visualizations.create_genre_pie_chart(genre_df)
        print("Genre pie chart created")

        print("=== Genre Chart Update Completed ===")
        return fig
    except Exception as e:
        print(f"Error updating genre chart: {e}")
        import traceback
        traceback.print_exc()

        # Return empty figure with error message
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text="Error loading genre data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=SPOTIFY_GRAY, size=16)
        )
        fig.update_layout(
            paper_bgcolor='#121212',
            plot_bgcolor='#121212',
            margin=dict(t=0, b=0, l=0, r=0)
        )
        return fig

def cleanup_historical_data():
    """Clean up historical listening data to fix unrealistic minute calculations."""
    user_data = spotify_api.get_user_profile()
    if not user_data:
        print("No user data available for cleanup")
        return

    print("Starting historical data cleanup...")
    cleanup_stats = db.cleanup_listening_history(user_data['id'])

    if 'error' in cleanup_stats:
        print(f"Cleanup failed: {cleanup_stats['error']}")
    else:
        print(f"Cleanup completed successfully:")
        print(f"  - Initial entries: {cleanup_stats['initial_count']}")
        print(f"  - Final entries: {cleanup_stats['final_count']}")
        print(f"  - Total removed: {cleanup_stats['total_removed']}")
        print(f"  - Exact duplicates removed: {cleanup_stats['duplicates_removed']}")
        print(f"  - Future entries removed: {cleanup_stats['future_entries_removed']}")
        print(f"  - Hourly duplicates removed: {cleanup_stats['hourly_duplicates_removed']}")

# Update listening patterns chart
@app.callback(
    Output('listening-patterns-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_listening_patterns_chart(n_intervals):
    """Update the listening patterns chart."""
    user_data = spotify_api.get_user_profile()
    if not user_data:
        return visualizations.create_empty_chart("Log in to see your listening patterns")

    # First, clean up any problematic data in the database
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        # 1. Update any future timestamps to current time
        cursor.execute('''
            UPDATE listening_history
            SET played_at = datetime('now')
            WHERE date(played_at) > ?
        ''', (current_date,))

        if cursor.rowcount > 0:
            print(f"Fixed {cursor.rowcount} future timestamps in the database")

        # 2. Remove duplicate entries with the same timestamp and track_id
        # First identify duplicates
        cursor.execute('''
            WITH duplicates AS (
                SELECT history_id, user_id, track_id, played_at, source,
                       ROW_NUMBER() OVER (PARTITION BY user_id, track_id, played_at ORDER BY history_id) as row_num
                FROM listening_history
                WHERE user_id = ?
            )
            DELETE FROM listening_history
            WHERE history_id IN (
                SELECT history_id FROM duplicates WHERE row_num > 1
            )
        ''', (user_data['id'],))

        if cursor.rowcount > 0:
            print(f"Removed {cursor.rowcount} duplicate entries from the database")

        conn.commit()
    except Exception as e:
        print(f"Error cleaning up database: {e}")
    finally:
        conn.close()

    # Get data from database
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for listening patterns with proper filtering
    # Only include actual listening events (not top tracks) and ensure dates are valid
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Use localtime for user-friendly display
    # SQLite datetime() function with 'localtime' modifier automatically adjusts to local timezone
    print(f"TIMEZONE DEBUG: Current local time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"TIMEZONE DEBUG: Current UTC time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

    # Query listening patterns by day and hour (using play counts instead of minutes)

    cursor.execute('''
        SELECT
            strftime('%w', datetime(played_at, 'localtime')) as day_of_week,
            strftime('%H', datetime(played_at, 'localtime')) as hour_of_day,
            COUNT(*) as play_count
        FROM listening_history h
        JOIN tracks t ON h.track_id = t.track_id
        WHERE h.user_id = ?
        AND h.played_at IS NOT NULL
        AND h.source IN ('played', 'recently_played', 'current')  -- Only include actual listening events
        AND datetime(h.played_at) <= datetime('now')  -- Ensure dates are not in the future
        AND datetime(h.played_at) >= datetime('now', '-7 days')  -- Only last 7 days
        GROUP BY day_of_week, hour_of_day
        ORDER BY day_of_week, hour_of_day
    ''', (user_data['id'],))

    patterns_data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if patterns_data:
        # Convert numeric day of week to name
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        patterns_df = pd.DataFrame(patterns_data)
        patterns_df['day_name'] = patterns_df['day_of_week'].astype(int).map(lambda x: day_names[x])

        print(f"Listening patterns data: {len(patterns_df)} time slots with total {patterns_df['play_count'].sum()} tracks played")
        return visualizations.create_listening_patterns_heatmap(patterns_df, date_range_days=7)

    # If no data in database, try to fetch recent data from API and save to database
    recently_played = spotify_api.get_recently_played(limit=50)
    if recently_played and user_data:
        # Save to database
        for track in recently_played:
            db.save_track(track)
            # Normalize the timestamp using our utility function
            played_at = normalize_timestamp(track.get('played_at'))
            if not played_at:
                # If normalization fails, use current time
                played_at = datetime.now().replace(microsecond=0).isoformat()

            db.save_listening_history(
                user_id=user_data['id'],
                track_id=track['id'],
                played_at=played_at,
                source='recently_played'
            )

        # Try database query again
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print(f"TIMEZONE DEBUG (retry): Current local time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"TIMEZONE DEBUG (retry): Current UTC time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

        # Query listening patterns by day and hour (retry attempt)

        cursor.execute('''
            SELECT
                strftime('%w', datetime(played_at, 'localtime')) as day_of_week,
                strftime('%H', datetime(played_at, 'localtime')) as hour_of_day,
                COUNT(*) as play_count
            FROM listening_history h
            JOIN tracks t ON h.track_id = t.track_id
            WHERE h.user_id = ?
            AND h.played_at IS NOT NULL
            AND h.source IN ('played', 'recently_played', 'current')  -- Only include actual listening events
            AND datetime(h.played_at) <= datetime('now')  -- Ensure dates are not in the future
            AND datetime(h.played_at) >= datetime('now', '-7 days')  -- Only last 7 days
            GROUP BY day_of_week, hour_of_day
            ORDER BY day_of_week, hour_of_day
        ''', (user_data['id'],))

        patterns_data = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if patterns_data:
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            patterns_df = pd.DataFrame(patterns_data)
            patterns_df['day_name'] = patterns_df['day_of_week'].astype(int).map(lambda x: day_names[x])

            print(f"Listening patterns data (retry): {len(patterns_df)} time slots with total {patterns_df['play_count'].sum()} tracks played")
            return visualizations.create_listening_patterns_heatmap(patterns_df, date_range_days=7)

    # Create empty DataFrame with the right columns
    patterns_df = pd.DataFrame(columns=['day_of_week', 'hour_of_day', 'play_count', 'day_name'])
    return visualizations.create_listening_patterns_heatmap(patterns_df, date_range_days=7)

# New callback for top albums section
@app.callback(
    Output('top-albums-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_top_albums(n_intervals, n_clicks):
    """Update the top albums section."""
    try:
        # Get user data first to ensure we have a valid user
        user_data = spotify_api.get_user_profile()
        if not user_data:
            return html.Div("Log in to see your top albums",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        # Get top albums directly from database
        try:
            top_albums_data = get_top_albums(spotify_api, limit=10)
            if top_albums_data.empty:
                return html.Div("No album data available. Please refresh your data to see your top albums.",
                               style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})
            top_albums_df = top_albums_data
        except Exception as e:
            print(f"Error getting top albums: {e}")
            return html.Div("Error loading album data",
                           style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

        # Create album cards
        album_cards = []
        for i, (_, album) in enumerate(top_albums_df.iterrows()):
            album_card = create_album_card(
                album_name=album.get('album', 'Unknown Album'),
                artist_name=album.get('artist', 'Unknown Artist'),
                rank=i+1,
                image_url=album.get('image_url', ''),
                score=album.get('total_count', 0)
            )
            album_cards.append(album_card)

        return html.Div(
            album_cards,
            style={
                'display': 'flex',
                'flexDirection': 'row',
                'overflowX': 'auto',
                'overflowY': 'hidden',
                'gap': '20px',
                'padding': '20px',
                'scrollBehavior': 'smooth',
                'WebkitOverflowScrolling': 'touch',
                'minHeight': '320px'
            }
        )
    except Exception as e:
        print(f"Error updating top albums: {e}")
        return html.Div("Error loading album data",
                       style={'color': SPOTIFY_GRAY, 'textAlign': 'center', 'padding': '20px'})

# Album listening patterns are now part of the DNA section in wrapped summary

def get_listening_style(completion_rate, sequential_score):
    """Determine listening style based on metrics."""
    album_focused = sequential_score > 40 or completion_rate > 30

    if album_focused:
        if sequential_score > 70:
            return "Album Purist"
        return "Album Explorer"

    if sequential_score < 20:
        return "Track Hopper"
    return "Mood Curator"

# DJ mode stats are now part of the DNA section in wrapped summary

# Update wrapped summary
@app.callback(
    Output('wrapped-summary-store', 'data'),
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals'),
     Input('url', 'pathname')],  # Trigger when page loads
    prevent_initial_call=False  # Allow initial call to load data immediately
)
def update_wrapped_summary(n_clicks, n_intervals, pathname):
    """Generate and store Spotify Wrapped style summary using only database data."""
    try:
        print(f"Updating wrapped summary - clicks: {n_clicks}, intervals: {n_intervals}, pathname: {pathname}")

        # Always generate fresh data for Music DNA card
        # Clear cache if refresh button was clicked
        if n_clicks is not None and n_clicks > 0:
            print("Clearing cache due to refresh button click")
            try:
                import os
                cache_file = os.path.join(data_processor.data_dir, 'wrapped_summary.json')
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                    print("Cleared cached summary file")
            except Exception as e:
                print(f"Error clearing cache: {e}")

        # Generate summary from database (always fresh)
        summary = generate_wrapped_summary_from_db()
        print(f"Generated summary with total_minutes: {summary.get('total_minutes', 'NOT_FOUND')}")
        return summary
    except Exception as e:
        print(f"Error updating wrapped summary: {e}")
        return {}



# Update wrapped summary display
@app.callback(
    Output('wrapped-summary-container', 'children'),
    Input('wrapped-summary-store', 'data')
)
def update_wrapped_summary_display(summary):
    """Update the Wrapped summary display."""
    # Handle the case when summary is None or empty - generate data immediately
    if summary is None or not summary:
        print("Summary is empty, generating fresh data...")
        try:
            # Generate fresh summary data immediately
            summary = generate_wrapped_summary_from_db()
            if not summary:
                # If still no data, show a friendly message
                return html.Div([
                    html.H3("🎵 Your Musical Journey Awaits", style={'color': SPOTIFY_GREEN, 'textAlign': 'center'}),
                    html.P("Start listening to music to see your personalized insights!",
                          style={'color': SPOTIFY_GRAY, 'textAlign': 'center'})
                ], style={
                    'padding': '30px',
                    'borderRadius': '10px',
                    'backgroundColor': '#121212',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.5)',
                    'margin': '20px 0',
                    'textAlign': 'center'
                })
        except Exception as e:
            print(f"Error generating summary in display callback: {e}")
            summary = {}

    # Initialize default values for all required fields to prevent NoneType errors
    if 'top_track' not in summary or summary['top_track'] is None:
        summary['top_track'] = {'name': 'Start listening to discover your top track', 'artist': 'Unknown'}

    if 'top_artist' not in summary or summary['top_artist'] is None:
        summary['top_artist'] = {'name': 'Start listening to discover your top artist', 'genres': 'Exploring genres'}

    if 'music_mood' not in summary or summary['music_mood'] is None:
        summary['music_mood'] = {'mood': 'Discovering Your Sound', 'valence': 0.5, 'energy': 0.5}

    if 'genre_highlight' not in summary or summary['genre_highlight'] is None:
        summary['genre_highlight'] = {'name': 'Exploring New Genres', 'count': 0}

    # Create visualizations instance to use the new components
    vis = visualizations

    # Create the enhanced wrapped summary component
    wrapped_summary = vis.create_wrapped_summary_component(summary)

    # Return only the wrapped summary component
    return wrapped_summary

# Update stat cards
@app.callback(
    [
        Output('total-minutes-stat', 'children'),
        Output('unique-artists-stat', 'children'),
        Output('listening-sessions-stat', 'children'),
        Output('playlist-count-stat', 'children')
    ],
    Input('interval-component', 'n_intervals')
)
def update_stat_cards(n_intervals):
    """Update the stat cards with user statistics."""
    user_data = spotify_api.get_user_profile()
    if not user_data:
        return create_empty_stats()

    # Get stats from database first
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    # Calculate total minutes and music variety from database - FIXED to avoid duplication
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Debug: Check what's in the database
    cursor.execute('''
        SELECT source, COUNT(*) as count
        FROM listening_history h
        WHERE date(h.played_at) <= ?
        GROUP BY source
        ORDER BY count DESC
    ''', (current_date,))
    source_counts = cursor.fetchall()
    print(f"DEBUG: Listening history sources: {dict(source_counts)}")

    # FIXED: Count unique listening events, not total track durations
    # This prevents counting the same track multiple times from different sources
    cursor.execute('''
        SELECT
            COUNT(DISTINCT h.history_id) as unique_listening_events,
            COUNT(DISTINCT t.artist) as unique_artists,
            COUNT(DISTINCT h.track_id) as unique_tracks,
            COUNT(DISTINCT t.album) as unique_albums,
            AVG(t.duration_ms) as avg_track_duration_ms
        FROM listening_history h
        JOIN tracks t ON h.track_id = t.track_id
        WHERE h.source IN ('played', 'recently_played', 'current')  -- Only actual listening events
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
        AND t.duration_ms IS NOT NULL
        AND t.duration_ms > 0
    ''', (current_date,))

    db_stats = cursor.fetchone()
    conn.close()

    # Calculate estimated listening time based on unique events and average track duration
    if db_stats and db_stats[0]:
        unique_listening_events = db_stats[0] or 0
        avg_track_duration_ms = db_stats[4] or 210000  # Default to 3.5 minutes if no data

        # Estimate total listening time: events * average track duration
        # This is more accurate than summing all track durations
        estimated_total_ms = unique_listening_events * avg_track_duration_ms
        total_minutes = int(estimated_total_ms / 60000)

        unique_artists = db_stats[1] or 0
        unique_tracks = db_stats[2] or 0
        unique_albums = db_stats[3] or 0

        print(f"FIXED CALCULATION: {unique_listening_events} events × {avg_track_duration_ms/60000:.1f}min = {total_minutes} total minutes")
    else:
        total_minutes = 0
        unique_artists = 0
        unique_tracks = 0
        unique_albums = 0

    # Calculate Total Listening Sessions (more meaningful than variety score)
    # Count unique listening sessions based on distinct dates
    cursor = sqlite3.connect(db.db_path).cursor()
    cursor.execute('''
        SELECT COUNT(DISTINCT DATE(played_at)) as session_count
        FROM listening_history
        WHERE source IN ('played', 'recently_played', 'current')
    ''')
    session_result = cursor.fetchone()
    listening_sessions = session_result[0] if session_result and session_result[0] else 0
    cursor.close()

    if total_minutes == 0:
        # Fallback to CSV data
        recently_played_df = data_processor.load_data('recently_played.csv')
        if not recently_played_df.empty and 'duration_ms' in recently_played_df.columns:
            total_minutes = int(recently_played_df['duration_ms'].sum() / 60000)

    # Get playlist count from Spotify API directly
    playlists_data = spotify_api.get_playlists()
    playlist_count = len(playlists_data) if playlists_data else 0

    # Create stat cards
    from modules.visualizations import create_stat_card

    total_minutes_card = create_stat_card(
        "Minutes Listened",
        f"{total_minutes:,}",
        icon="fa-clock",
        color=SPOTIFY_GREEN
    )

    unique_artists_card = create_stat_card(
        "Unique Artists",
        str(unique_artists),
        icon="fa-user",
        color="#1ED760"
    )

    listening_sessions_card = create_stat_card(
        "Listening Sessions",
        str(listening_sessions),
        icon="fa-calendar-day",
        color="#8b5cf6"
    )

    playlist_count_card = create_stat_card(
        "Your Playlists",
        str(playlist_count),
        icon="fa-list",
        color="#F037A5"
    )

    return total_minutes_card, unique_artists_card, listening_sessions_card, playlist_count_card

def create_empty_stats():
    """Create empty stat cards when no user data is available."""
    from modules.visualizations import create_stat_card
    return [
        create_stat_card("Minutes Listened", "0", icon="fa-clock", color=SPOTIFY_GREEN),
        create_stat_card("Unique Artists", "0", icon="fa-user", color="#1ED760"),
        create_stat_card("Music Variety", "0%", icon="fa-palette", color="#8b5cf6"),
        create_stat_card("Your Playlists", "0", icon="fa-list", color="#F037A5")
    ]

def generate_wrapped_summary_from_db():
    """Generate a Spotify Wrapped style summary using database data."""
    print("Starting wrapped summary generation...")

    # Try to load from cached file first (only if very recent - 1 minute)
    try:
        import os
        import time
        cache_file = os.path.join(data_processor.data_dir, 'wrapped_summary.json')
        if os.path.exists(cache_file):
            # Check if cache is very recent (less than 1 minute old)
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < 60:  # 1 minute only
                with open(cache_file, 'r') as f:
                    import json
                    cached_summary = json.load(f)
                    print(f"Using very recent cached summary (age: {cache_age:.1f}s)")
                    if cached_summary and 'total_minutes' in cached_summary:  # Ensure it has the data we need
                        return cached_summary
            else:
                print(f"Cache is too old ({cache_age:.1f}s), regenerating")
    except Exception as e:
        print(f"Error loading cached summary: {e}")

    user_data = spotify_api.get_user_profile()
    if not user_data:
        print("No user data available")
        return {}

    summary = {
        'timestamp': datetime.now().isoformat(),
        'top_track': None,
        'top_artist': None,
        'total_minutes': 0,
        'music_mood': None,
        'genre_highlight': None
    }

    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if we have any data in the database
    cursor.execute('SELECT COUNT(*) as count FROM listening_history')
    history_count = cursor.fetchone()['count']
    print(f"Database has {history_count} listening history entries")

    # Get top track from Spotify's official API - this is the correct approach!
    try:
        # Get top tracks from Spotify's algorithm (short_term = last 4 weeks)
        top_tracks_data = spotify_api.get_top_tracks(limit=1, time_range='short_term')

        if not top_tracks_data:
            # Try medium_term if short_term has no data
            top_tracks_data = spotify_api.get_top_tracks(limit=1, time_range='medium_term')

        if not top_tracks_data:
            # Try long_term if medium_term has no data
            top_tracks_data = spotify_api.get_top_tracks(limit=1, time_range='long_term')

        if top_tracks_data:
            top_track = top_tracks_data[0]
            summary['top_track'] = {
                'name': top_track['name'],
                'artist': top_track['artist']
            }
            print(f"✅ Got top track from Spotify API: {top_track['name']} by {top_track['artist']}")
        else:
            # Fallback to database if Spotify API fails
            current_date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT
                    t.track_id as id,
                    t.name as track,
                    t.artist,
                    COUNT(h.history_id) as play_count
                FROM tracks t
                JOIN listening_history h ON t.track_id = h.track_id
                WHERE t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
                AND h.source NOT LIKE 'top_%'  -- Exclude top tracks data
                AND date(h.played_at) <= ?     -- Ensure dates are not in the future
                GROUP BY t.track_id
                ORDER BY play_count DESC
                LIMIT 1
            ''', (current_date,))

            top_track_row = cursor.fetchone()
            if top_track_row:
                top_track = dict(top_track_row)
                summary['top_track'] = {
                    'name': top_track['track'],
                    'artist': top_track['artist']
                }
                print(f"📁 Using database fallback for top track: {top_track['track']} by {top_track['artist']}")
            else:
                # Default top track if none found
                summary['top_track'] = {
                    'name': 'Start listening to discover your top track',
                    'artist': 'Unknown'
                }
                print("❌ No top track data available")
    except Exception as e:
        print(f"Error getting top track: {e}")
        summary['top_track'] = {
            'name': 'Error loading top track',
            'artist': 'Unknown'
        }

    # Get top artist from Spotify's official API
    try:
        # Get top artists from Spotify's algorithm (short_term = last 4 weeks)
        top_artists_data = spotify_api.get_top_artists(limit=1, time_range='short_term')

        if not top_artists_data:
            # Try medium_term if short_term has no data
            top_artists_data = spotify_api.get_top_artists(limit=1, time_range='medium_term')

        if not top_artists_data:
            # Try long_term if medium_term has no data
            top_artists_data = spotify_api.get_top_artists(limit=1, time_range='long_term')

        if top_artists_data:
            top_artist_name = top_artists_data[0]['artist']
            print(f"✅ Got top artist from Spotify API: {top_artist_name}")
        else:
            # Fallback to database if Spotify API fails
            current_date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT
                    t.artist as artist,
                    COUNT(h.history_id) as play_count
                FROM tracks t
                JOIN listening_history h ON t.track_id = h.track_id
                WHERE t.artist IS NOT NULL AND t.artist != ''
                AND h.source NOT LIKE 'top_%'  -- Exclude top tracks data
                AND date(h.played_at) <= ?     -- Ensure dates are not in the future
                GROUP BY t.artist
                ORDER BY play_count DESC
                LIMIT 1
            ''', (current_date,))

            top_artist_row = cursor.fetchone()
            if top_artist_row:
                top_artist = dict(top_artist_row)
                top_artist_name = top_artist['artist']
                print(f"📁 Using database fallback for top artist: {top_artist_name}")
            else:
                top_artist_name = None
                print("❌ No top artist data available")
    except Exception as e:
        print(f"Error getting top artist: {e}")
        top_artist_name = None

    if top_artist_name:

        # Get genres for this artist from the dedicated genres table
        cursor.execute('''
            SELECT
                genre_name as genre
            FROM genres
            WHERE artist_name = ?
            GROUP BY genre_name
            ORDER BY count DESC
            LIMIT 5
        ''', (top_artist_name,))

        genres = [dict(row)['genre'] for row in cursor.fetchall()]

        summary['top_artist'] = {
            'name': top_artist_name,
            'genres': ', '.join(genres) if genres else 'Exploring genres'
        }
    else:
        # Default top artist if none found
        summary['top_artist'] = {
            'name': 'Start listening to discover your top artist',
            'genres': 'Exploring genres'
        }

    # Get audio features for mood - handle case with limited data
    cursor.execute('''
        SELECT
            AVG(CASE WHEN t.danceability IS NULL THEN 0.5 ELSE t.danceability END) as avg_danceability,
            AVG(CASE WHEN t.energy IS NULL THEN 0.5 ELSE t.energy END) as avg_energy,
            AVG(CASE WHEN t.valence IS NULL THEN 0.5 ELSE t.valence END) as avg_valence,
            AVG(CASE WHEN t.tempo IS NULL THEN 120 ELSE t.tempo END) as avg_tempo,
            COUNT(*) as track_count
        FROM tracks t
        JOIN listening_history h ON t.track_id = h.track_id
        WHERE h.source NOT LIKE 'top_%'  -- Exclude top tracks data
        AND date(h.played_at) <= ?     -- Ensure dates are not in the future
    ''', (current_date,))

    audio_features_row = cursor.fetchone()
    if audio_features_row and audio_features_row['track_count'] > 0:
        features = dict(audio_features_row)
        avg_valence = features.get('avg_valence', 0.5) or 0.5
        avg_energy = features.get('avg_energy', 0.5) or 0.5
        avg_tempo = features.get('avg_tempo', 120) or 120

        # Determine mood quadrant
        if avg_valence > 0.5 and avg_energy > 0.5:
            mood = "Happy & Energetic"
        elif avg_valence > 0.5 and avg_energy <= 0.5:
            mood = "Peaceful & Positive"
        elif avg_valence <= 0.5 and avg_energy > 0.5:
            mood = "Angry & Intense"
        else:
            mood = "Sad & Chill"

        summary['music_mood'] = {
            'mood': mood,
            'valence': avg_valence,
            'energy': avg_energy
        }

        # Add tempo to the summary
        summary['tempo'] = avg_tempo
    else:
        # Default mood if no audio features found
        summary['music_mood'] = {
            'mood': "Discovering Your Sound",
            'valence': 0.5,
            'energy': 0.5
        }

    # Get top genre using standardized function (consistent with genre chart)
    user_id = user_data['id']
    top_genres = db.get_user_top_genres(
        user_id=user_id,
        limit=1,
        exclude_unknown=True,
        include_sources=['played', 'recently_played', 'current'],
        date_filter=current_date
    )

    if top_genres:
        top_genre = top_genres[0]
        summary['genre_highlight'] = {
            'name': top_genre['genre'],
            'count': top_genre['count']
        }
    else:
        # Default genre highlight if none found
        summary['genre_highlight'] = {
            'name': 'Exploring New Genres',
            'count': 0
        }

    # Calculate total listening minutes (FIXED to match stats card calculation)
    cursor.execute('''
        SELECT
            COUNT(DISTINCT h.history_id) as unique_listening_events,
            AVG(t.duration_ms) as avg_track_duration_ms
        FROM listening_history h
        JOIN tracks t ON h.track_id = t.track_id
        WHERE h.source IN ('played', 'recently_played', 'current')
        AND date(h.played_at) <= ?
        AND t.duration_ms IS NOT NULL
        AND t.duration_ms > 0
    ''', (current_date,))

    minutes_row = cursor.fetchone()
    if minutes_row and minutes_row[0]:  # Check first column (unique_listening_events)
        unique_listening_events = minutes_row[0] or 0
        avg_track_duration_ms = minutes_row[1] or 210000  # Default to 3.5 minutes

        # Calculate estimated total listening time
        estimated_total_ms = unique_listening_events * avg_track_duration_ms
        total_minutes = round(estimated_total_ms / 60000)

        summary['total_minutes'] = total_minutes
        summary['total_hours'] = round(total_minutes / 60, 1)
        print(f"Calculated total minutes: {summary['total_minutes']} (from {unique_listening_events} events)")
        print(f"Calculated total hours: {summary['total_hours']}")
    else:
        summary['total_minutes'] = 0
        summary['total_hours'] = 0
        print("No listening time data found")

    conn.close()

    # Add DJ stats and album patterns data
    try:
        # Get DJ stats (AI DJ usage)
        is_premium = user_data.get('product', 'free') == 'premium'
        if is_premium:
            # Estimate AI DJ usage for premium users
            estimated_minutes = max(1, int(summary.get('total_minutes', 0) * 0.15))  # 15% of listening
            percentage_of_listening = min(100, max(5, int((estimated_minutes / max(1, summary.get('total_minutes', 1))) * 100)))
            dj_mode_user = True
        else:
            estimated_minutes = 0
            percentage_of_listening = 0
            dj_mode_user = False

        summary['dj_stats'] = {
            'estimated_minutes': estimated_minutes,
            'percentage_of_listening': percentage_of_listening,
            'dj_mode_user': dj_mode_user,
            'is_premium': is_premium
        }

        # Get album patterns (sequential listening)
        from modules.top_albums import get_album_listening_patterns
        album_patterns = get_album_listening_patterns(spotify_api)
        summary['album_patterns'] = album_patterns

        print(f"Added DJ stats: {summary['dj_stats']}")
        print(f"Added album patterns: {summary['album_patterns']}")

    except Exception as e:
        print(f"Error adding DJ stats and album patterns: {e}")
        # Set defaults if error
        summary['dj_stats'] = {
            'estimated_minutes': 0,
            'percentage_of_listening': 0,
            'dj_mode_user': False,
            'is_premium': False
        }
        summary['album_patterns'] = {
            'sequential_listening_score': 0,
            'album_completion_rate': 0,
            'listening_style': 'Unknown'
        }

    # Save summary to cache
    try:
        import os
        import json
        cache_file = os.path.join(data_processor.data_dir, 'wrapped_summary.json')
        with open(cache_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Saved summary to cache: {cache_file}")
    except Exception as e:
        print(f"Error saving summary to cache: {e}")

    # Add personality type using AI enhancer
    try:
        user_data = spotify_api.get_user_profile()
        if user_data and user_data.get('id'):
            from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
            ai_analyzer = EnhancedPersonalityAnalyzer()
            ai_personality = ai_analyzer.generate_enhanced_personality(user_data['id'])

            if ai_personality and ai_personality.get('personality_type'):
                summary['personality_type'] = ai_personality.get('personality_type', 'Music Explorer')
                print(f"✅ Added personality type: {summary['personality_type']}")
            else:
                summary['personality_type'] = 'Music Explorer'
                print("📁 Using default personality type: Music Explorer")
        else:
            summary['personality_type'] = 'Music Explorer'
            print("❌ No user data for personality type")
    except Exception as e:
        print(f"Error generating personality type: {e}")
        summary['personality_type'] = 'Music Explorer'

    print(f"Final summary: {summary}")
    return summary

# Error handling callback
@app.callback(
    Output('error-message', 'children'),
    Output('error-message', 'style'),
    Input('interval-component', 'n_intervals')
)
def update_error_message(n_intervals):
    """Update error message if API connection fails."""
    if spotify_api.sp is None:
        error_style = {
            'color': '#FF5555',
            'textAlign': 'center',
            'margin': '10px',
            'padding': '10px',
            'backgroundColor': '#2A0A0A',
            'borderRadius': '5px',
            'display': 'block'
        }
        return [
            "Error connecting to Spotify API. Please check your credentials and internet connection.",
            html.Br(),
            "The dashboard will display limited data until connection is restored."
        ], error_style

    # No error, hide the message
    error_style = {
        'display': 'none'
    }
    return "", error_style

# Collection status callback removed - no longer showing collection status message

# AI Insights Page Callbacks
@app.callback(
    Output('ai-personality-card', 'children'),
    Input('url', 'pathname')
)
def update_ai_personality_card(pathname):
    """Update AI personality card with enhanced descriptions."""
    if pathname != '/ai-insights':
        return html.Div()

    try:
        user_data = spotify_api.get_user_profile()
        if not user_data:
            return html.Div("Please authenticate with Spotify first.", className="alert alert-warning")

        user_id = user_data['id']

        # Get AI-enhanced personality analysis
        ai_personality = enhanced_personality_analyzer.generate_enhanced_personality(user_id)

        return create_spotify_card(
            title="🧠 AI-Enhanced Personality",
            content=html.Div([
                html.Div([
                    html.H4(ai_personality.get('personality_type', 'Music Explorer'),
                           style={'color': '#1DB954', 'fontFamily': 'Orbitron, monospace'}),
                    html.Div(f"Confidence: {ai_personality.get('confidence_score', 0.5):.0%}",
                           className="confidence-badge")
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '15px'}),

                html.Div(ai_personality.get('ai_description', 'No description available'),
                        className="ai-description"),

                html.Hr(style={'margin': '20px 0', 'border': '1px solid rgba(29, 185, 84, 0.3)'}),

                html.H5("🎵 AI Recommendations", style={'color': '#1DB954', 'fontFamily': 'Orbitron, monospace'}),
                html.Div([
                    html.Div([
                        html.Strong(f"{rec['name']} by {rec['artist']}"),
                        html.Br(),
                        html.Small(rec['reason'], style={'color': '#00D4FF', 'fontSize': '0.9rem'})
                    ], style={'marginBottom': '10px'}) for rec in ai_personality.get('recommendations', [])[:3]
                ])
            ]),
            icon="fa-brain",
            card_type="glass"
        )

    except Exception as e:
        print(f"Error updating AI personality card: {e}")
        return html.Div(f"Error loading AI personality: {str(e)}", className="alert alert-danger")

@app.callback(
    Output('genre-evolution-chart', 'figure'),
    Input('url', 'pathname')
)
def update_genre_evolution_chart(pathname):
    """Update genre evolution chart."""
    if pathname != '/ai-insights':
        return {}

    try:
        user_data = spotify_api.get_user_profile()
        if not user_data:
            return {}

        user_id = user_data['id']

        # Get genre evolution data
        evolution_data = genre_evolution_tracker.get_genre_evolution_data(user_id)

        # Create visualization
        return genre_evolution_tracker.create_evolution_visualization(evolution_data)

    except Exception as e:
        print(f"Error updating genre evolution chart: {e}")
        return {}

@app.callback(
    Output('wellness-analysis-card', 'children'),
    Input('url', 'pathname')
)
def update_wellness_analysis_card(pathname):
    """Update wellness analysis card with enhanced stress detection."""
    if pathname != '/ai-insights':
        return html.Div()

    try:
        user_data = spotify_api.get_user_profile()
        if not user_data:
            return html.Div("Please authenticate with Spotify first.", className="alert alert-warning")

        user_id = user_data['id']

        # Try enhanced stress analysis first, fallback to basic if needed
        try:
            print(f"DEBUG: Attempting enhanced stress analysis for user {user_id}")
            stress_data = enhanced_stress_detector.analyze_stress_patterns(user_id)
            print(f"DEBUG: Enhanced stress analysis successful, stress_score: {stress_data.get('stress_score', 'NOT_FOUND')}")
            # Use the enhanced visualization
            return create_enhanced_stress_analysis_card(stress_data)
        except Exception as enhanced_error:
            print(f"Enhanced stress detector failed: {enhanced_error}")
            import traceback
            traceback.print_exc()
            # Fallback to basic wellness analysis
            print(f"DEBUG: Falling back to wellness analyzer")
            wellness_data = wellness_analyzer.analyze_wellness_patterns(user_id)
            print(f"DEBUG: Wellness analysis result: wellness_score={wellness_data.get('wellness_score', 'NOT_FOUND')}")
            
            # Convert wellness data to stress data format for compatibility
            if 'wellness_score' in wellness_data:
                # Convert wellness score (higher = better) to stress score (higher = worse)
                stress_score = max(0, 100 - wellness_data['wellness_score'])
                wellness_data['stress_score'] = stress_score
                print(f"DEBUG: Converted wellness_score {wellness_data['wellness_score']} to stress_score {stress_score}")
            # Create basic wellness card with enhanced styling
            return create_spotify_card(
                title="🏥 Wellness Analysis",
                content=html.Div([
                    html.Div([
                        html.H2(f"{wellness_data['wellness_score']}", className="wellness-score"),
                        html.P("Wellness Score", style={'textAlign': 'center', 'color': 'rgba(255,255,255,0.7)'})
                    ]),
                    html.Hr(style={'margin': '20px 0', 'border': '1px solid rgba(29, 185, 84, 0.3)'}),
                    html.H5("🎵 Therapeutic Suggestions", style={'color': '#1DB954', 'fontFamily': 'Orbitron, monospace'}),
                    html.Div([
                        html.Div([
                            html.H6(suggestion['title'], className="therapeutic-suggestion"),
                            html.P(suggestion['description'], style={'fontSize': '0.9rem', 'color': 'rgba(255,255,255,0.8)'})
                        ], style={'marginBottom': '15px'}) for suggestion in wellness_data.get('therapeutic_suggestions', [])[:3]
                    ])
                ]),
                icon="fa-heart",
                card_type="glass"
            )

    except Exception as e:
        print(f"Error updating wellness analysis card: {e}")
        # Fallback to basic wellness analysis
        try:
            wellness_data = wellness_analyzer.analyze_wellness_patterns(user_id)
            return create_spotify_card(
                title="🏥 Wellness Analysis",
                content=html.Div([
                    html.Div([
                        html.H2(f"{wellness_data['wellness_score']}", className="wellness-score"),
                        html.P("Wellness Score", style={'textAlign': 'center', 'color': 'rgba(255,255,255,0.7)'})
                    ]),
                    html.Hr(style={'margin': '20px 0', 'border': '1px solid rgba(29, 185, 84, 0.3)'}),
                    html.H5("🎵 Therapeutic Suggestions", style={'color': '#1DB954', 'fontFamily': 'Orbitron, monospace'}),
                    html.Div([
                        html.Div([
                            html.H6(suggestion['title'], className="therapeutic-suggestion"),
                            html.P(suggestion['description'], style={'fontSize': '0.9rem', 'color': 'rgba(255,255,255,0.8)'})
                        ], style={'marginBottom': '15px'}) for suggestion in wellness_data.get('therapeutic_suggestions', [])[:3]
                    ])
                ]),
                icon="fa-heart",
                card_type="glass"
            )
        except Exception as fallback_error:
            print(f"Fallback wellness analysis also failed: {fallback_error}")
            return html.Div(f"Error loading stress analysis: {str(e)}", className="alert alert-danger")

@app.callback(
    Output('advanced-recommendations-card', 'children'),
    Input('url', 'pathname')
)
def update_advanced_recommendations_card(pathname):
    """Update advanced recommendations card."""
    if pathname != '/ai-insights':
        return html.Div()

    try:
        user_data = spotify_api.get_user_profile()
        if not user_data:
            return html.Div("Please authenticate with Spotify first.", className="alert alert-warning")

        user_id = user_data['id']

        # Get content-based recommendations
        recommendations = enhanced_personality_analyzer._get_content_based_recommendations(user_id, limit=8)
        print(f"DEBUG: Got {len(recommendations)} recommendations for user {user_id}")

        # Create content based on whether we have recommendations
        if recommendations:
            content = html.Div([
                html.P("Based on your music DNA and listening patterns",
                      style={'color': 'rgba(255,255,255,0.7)', 'marginBottom': '20px'}),

                html.Div([
                    html.Div([
                        html.Div([
                            html.Img(src=rec.get('image_url', ''),
                                   style={'width': '40px', 'height': '40px', 'borderRadius': '4px', 'marginRight': '10px'}),
                            html.Div([
                                html.Strong(rec['name']),
                                html.Br(),
                                html.Small(rec['artist'], style={'color': 'rgba(255,255,255,0.7)'}),
                                html.Br(),
                                html.Small(rec['reason'], style={'color': '#1DB954', 'fontSize': '0.8rem'})
                            ])
                        ], style={'display': 'flex', 'alignItems': 'center', 'padding': '10px',
                                'backgroundColor': 'rgba(255,255,255,0.05)', 'borderRadius': '8px', 'marginBottom': '8px'})
                    ]) for rec in recommendations
                ])
            ])
        else:
            # Get user's music DNA for display
            try:
                user_data = enhanced_personality_analyzer._get_user_listening_data(user_id)
                content = html.Div([
                    html.H4("🧬 Your Music DNA Profile", style={'color': '#1DB954', 'textAlign': 'center', 'marginBottom': '20px'}),

                    # Show user's preferences
                    html.Div([
                        html.Div([
                            html.Strong("🕺 Danceability: "),
                            html.Span(f"{user_data.get('avg_danceability', 0.5):.1%}", style={'color': '#00D4FF'})
                        ], style={'marginBottom': '8px'}),
                        html.Div([
                            html.Strong("⚡ Energy: "),
                            html.Span(f"{user_data.get('avg_energy', 0.5):.1%}", style={'color': '#00D4FF'})
                        ], style={'marginBottom': '8px'}),
                        html.Div([
                            html.Strong("😊 Mood: "),
                            html.Span(f"{user_data.get('avg_valence', 0.5):.1%}", style={'color': '#00D4FF'})
                        ], style={'marginBottom': '8px'}),
                        html.Div([
                            html.Strong("🎭 Top Genre: "),
                            html.Span(user_data.get('top_genre', 'Mixed'), style={'color': '#1DB954'})
                        ], style={'marginBottom': '15px'})
                    ], style={'backgroundColor': 'rgba(29, 185, 84, 0.1)', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'}),

                    html.P("🎵 Your music DNA is ready, but we need more diverse tracks in our database to find perfect matches!",
                          style={'color': 'rgba(255,255,255,0.8)', 'textAlign': 'center', 'marginBottom': '10px'}),
                    html.P("The algorithm is looking for tracks that match your preferences but you haven't heard yet.",
                          style={'color': 'rgba(255,255,255,0.6)', 'fontSize': '0.9rem', 'textAlign': 'center', 'fontStyle': 'italic'})
                ])
            except:
                content = html.Div([
                    html.P("🎵 Building your music DNA...",
                          style={'color': 'rgba(255,255,255,0.7)', 'marginBottom': '15px', 'textAlign': 'center'}),
                    html.P("We need more listening data to generate personalized recommendations. Keep listening to music and check back soon!",
                          style={'color': 'rgba(255,255,255,0.6)', 'fontSize': '0.9rem', 'textAlign': 'center', 'fontStyle': 'italic'}),
                    html.Div([
                        html.I(className="fas fa-dna", style={'fontSize': '3rem', 'color': '#1DB954', 'opacity': '0.3'})
                    ], style={'textAlign': 'center', 'margin': '20px 0'})
                ])

        return create_spotify_card(
            title="🎯 Advanced Recommendations",
            content=content,
            icon="fa-magic",
            card_type="glass"
        )

    except Exception as e:
        print(f"Error updating advanced recommendations card: {e}")
        return html.Div(f"Error loading recommendations: {str(e)}", className="alert alert-danger")



def create_ai_insights_page():
    """Create the dedicated AI insights page with balanced masonry grid."""
    return html.Div([
        # Hidden components needed for callbacks (but not displayed)
        html.Div([
            html.Div(id='header-container', style={'display': 'none'}),
            html.Div(id='collection-status', style={'display': 'none'}),
            html.Div(id='wrapped-summary-container', style={'display': 'none'}),
            html.Div(id='personality-container', style={'display': 'none'})
        ], style={'display': 'none'}),

        # Page header
        html.Div([
            html.H1("🤖 AI Music Insights", className="ai-page-title"),
            html.P("Discover how AI understands your music taste and get personalized insights",
                   className="ai-page-subtitle")
        ], className="ai-page-header"),

        # Balanced Masonry Grid Container
        html.Div([
            # Left Column - Balanced with multiple shorter cards
            html.Div([
                # AI Personality Enhancement Card (Short - ~400px)
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-brain", style={'marginRight': '12px'}),
                            html.H3("AI-Enhanced Personality", style={'margin': '0'})
                        ], className="ai-card-header"),
                        html.Div(id='ai-personality-card')
                    ])
                ], className="ai-insights-card ai-card-personality"),
                
                # Genre Evolution Card (Medium - ~500px)
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-line", style={'marginRight': '12px'}),
                            html.H3("Genre Evolution", style={'margin': '0'})
                        ], className="ai-card-header"),
                        html.Div([
                            dcc.Graph(id='genre-evolution-chart', style={'height': '400px'})
                        ])
                    ])
                ], className="ai-insights-card ai-card-genre-evolution"),
                
                # Advanced Recommendations Card (Medium - ~400px)
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-magic", style={'marginRight': '12px'}),
                            html.H3("Advanced Recommendations", style={'margin': '0'})
                        ], className="ai-card-header"),
                        html.Div(id='advanced-recommendations-card')
                    ])
                ], className="ai-insights-card ai-card-wellness")
            ], className="ai-insights-left-column"),
            
            # Right Column - Single long card
            html.Div([
                # Stress Analysis Card (Very Long - ~1000px)
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-brain", style={'marginRight': '12px'}),
                            html.H3("Enhanced Stress Analysis", style={'margin': '0'})
                        ], className="ai-card-header"),
                        html.Div(id='wellness-analysis-card')
                    ])
                ], className="ai-insights-card ai-card-stress")
            ], className="ai-insights-right-column")
        ], className="ai-insights-masonry-container")
    ], className="ai-insights-page")

# Main entry point
if __name__ == '__main__':
    # Initial data fetch is now handled by callbacks based on user input
    # The app will start and wait for user to provide credentials or choose sample data

    # Start background collector thread only if not in debug mode and not running cleanup
    import sys
    if not (len(sys.argv) > 1 and sys.argv[1] == '--cleanup'):
        def background_data_collector():
            """Background thread to periodically collect data."""
            while True:
                try:
                    # Get current user
                    user_data = spotify_api.get_user_profile()
                    if user_data:
                        # Update database with latest data
                        data_collector.collect_historical_data(
                            user_data['id'],
                            datetime.now() - timedelta(hours=24)  # Last 24 hours
                        )

                    # Wait for 30 minutes before next collection
                    time.sleep(1800)

                except Exception as e:
                    print(f"Error in background collector: {e}")
                    time.sleep(300)  # Wait 5 minutes on error

        import threading
        collector_thread = threading.Thread(target=background_data_collector, daemon=True)
        collector_thread.start()

    # Check if cleanup is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--cleanup':
        print("Running historical data cleanup...")
        cleanup_historical_data()
        print("Cleanup completed. You can now run the app normally.")
        sys.exit(0)

    # Run the app
    # For production deployment (Render, Railway, etc.)
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    app.run(host='0.0.0.0', port=port, debug=debug)
