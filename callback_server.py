#!/usr/bin/env python3
"""
Simple callback server to handle Spotify OAuth on port 8080
and communicate with the main Dash app on port 8000.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import tempfile
import os
import threading
import time

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to the callback endpoint."""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/callback':
            # Parse query parameters
            query_params = parse_qs(parsed_url.query)
            
            # Get authorization code or error
            code = query_params.get('code', [None])[0]
            error = query_params.get('error', [None])[0]
            
            if error:
                print(f"❌ OAuth Error: {error}")
                self.send_error_response(f"Authorization failed: {error}")
                return
            
            if code:
                print(f"✅ OAuth Success: Received authorization code: {code[:20]}...")
                
                # Store the code temporarily
                temp_dir = tempfile.gettempdir()
                code_file = os.path.join(temp_dir, 'spotify_auth_code.txt')
                with open(code_file, 'w') as f:
                    f.write(code)
                print(f"📝 Stored auth code in: {code_file}")
                
                # Send success response
                self.send_success_response()
                return
            
            self.send_error_response("No authorization code received")
        else:
            self.send_error_response("Invalid endpoint")
    
    def send_success_response(self):
        """Send a success response with auto-redirect."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_response = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spotify Authorization Successful</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: #191414; 
                    color: #1DB954; 
                    text-align: center; 
                    padding: 50px; 
                }
                .success { 
                    background: #1DB954; 
                    color: #000; 
                    padding: 20px; 
                    border-radius: 10px; 
                    display: inline-block; 
                    margin: 20px;
                }
            </style>
            <script>
                setTimeout(function() {
                    window.close();
                    // Try to redirect parent window
                    if (window.opener) {
                        window.opener.location.href = 'http://127.0.0.1:8000/';
                    }
                }, 3000);
            </script>
        </head>
        <body>
            <div class="success">
                <h2>🎵 Authorization Successful!</h2>
                <p>You can now close this window.</p>
                <p>Redirecting back to the app...</p>
                <p><a href="http://127.0.0.1:8000/" style="color: #000;">Click here if not redirected automatically</a></p>
            </div>
        </body>
        </html>
        '''
        self.wfile.write(html_response.encode())
    
    def send_error_response(self, error_message):
        """Send an error response."""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_response = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spotify Authorization Error</title>
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
                <h2>❌ Authorization Error</h2>
                <p>{error_message}</p>
                <p><a href="http://127.0.0.1:8000/" style="color: #000;">Return to app</a></p>
            </div>
        </body>
        </html>
        '''
        self.wfile.write(html_response.encode())
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        print(f"🔗 Callback: {format % args}")

def start_callback_server():
    """Start the callback server on port 8080."""
    server = HTTPServer(('127.0.0.1', 8080), CallbackHandler)
    print("🚀 Callback server starting on http://127.0.0.1:8080/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Callback server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_callback_server()
