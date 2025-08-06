from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from calendar_api import get_google_auth_flow, get_credentials_from_auth_code, get_calendar_service
from googleapiclient.discovery import build
from mcp_client import MCPClient
import threading
import time
import json
from datetime import datetime
import os
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# User sessions storage (in production, use a proper database)
user_sessions = {}

# Global MCP client that stays alive
mcp_client = None
mcp_client_lock = threading.Lock()

def get_mcp_client():
    """Get or create the global MCP client."""
    global mcp_client
    with mcp_client_lock:
        if mcp_client is None:
            print("[FLASK] Creating new MCP client...")
            try:
                mcp_client = MCPClient()
                print("[FLASK] Starting MCP server...")
                
                # Try to start the server with retries
                max_retries = 3
                for attempt in range(max_retries):
                    if mcp_client.start_server():
                        print(f"[FLASK] MCP server started successfully on attempt {attempt + 1}")
                        break
                    else:
                        print(f"[FLASK] Failed to start MCP server on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(2)  # Wait before retry
                        else:
                            print("[FLASK] All attempts to start MCP server failed!")
                            return None
                            
            except Exception as e:
                print(f"[FLASK] Error creating MCP client: {e}")
                return None
                
        return mcp_client

def cleanup_mcp_client():
    """Clean up the global MCP client."""
    global mcp_client
    with mcp_client_lock:
        if mcp_client:
            print("[FLASK] Stopping MCP server...")
            mcp_client.stop_server()
            print("[FLASK] Cleaning up MCP client...")
            mcp_client = None
            print("[FLASK] MCP client cleaned up")

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    """Main page with calendar assistant interface."""
    user_id = session['user_id']
    user_info = user_sessions.get(user_id, {})
    return render_template('index.html', user_info=user_info)

@app.route('/login')
def login():
    """Login page."""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/auth/google')
def google_auth():
    """Initiate Google OAuth flow."""
    
    try:
        # Check if credentials are available (either from file or environment variables)
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not os.path.exists('credentials.json') and (not client_id or not client_secret):
            flash('Google OAuth credentials not found. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.', 'error')
            return redirect(url_for('login'))
        
        # Clear any existing OAuth session data to prevent conflicts
        session.pop('oauth_state', None)
        session.pop('oauth_redirect_uri', None)
        
        # Generate OAuth state for security
        oauth_state = secrets.token_urlsafe(32)
        session['oauth_state'] = oauth_state
        
        # Set redirect URI for OAuth callback (use HTTPS only in production)
        if os.getenv('FLASK_ENV') == 'production' or os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RENDER'):
            # Use HTTPS in production
            oauth_redirect_uri = url_for('oauth2callback', _external=True, _scheme='https')
        else:
            # Use HTTP for local development
            oauth_redirect_uri = url_for('oauth2callback', _external=True)
        session['oauth_redirect_uri'] = oauth_redirect_uri
        
        # Create OAuth flow
        flow = get_google_auth_flow(oauth_redirect_uri)
        
        # Generate authorization URL with additional parameters for better compatibility
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',  # Force consent screen to appear
            state=oauth_state
        )
        
        return redirect(auth_url)
        
    except Exception as e:
        flash(f'Failed to initiate authentication: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth callback from Google."""
    
    try:
        # Check for OAuth errors first
        error = request.args.get('error')
        if error:
            if error == 'access_denied':
                flash('Access denied. Please make sure you are added as a test user in the OAuth consent screen.', 'error')
            else:
                flash(f'OAuth error: {error}', 'error')
            return redirect(url_for('login'))
        
        # Verify state parameter with better error handling
        expected_state = session.get('oauth_state')
        received_state = request.args.get('state')
        
        if not expected_state:
            flash('OAuth session expired. Please try logging in again.', 'error')
            return redirect(url_for('login'))
        
        if not received_state:
            flash('No OAuth state received from Google. Please try again.', 'error')
            return redirect(url_for('login'))
        
        if expected_state != received_state:
            # Log the mismatch for debugging
            print(f"OAuth state mismatch - Expected: {expected_state[:10]}..., Received: {received_state[:10]}...")
            flash('OAuth state validation failed. This might happen if you are already logged in elsewhere. Please try again.', 'error')
            # Clear the session and redirect to login
            session.clear()
            return redirect(url_for('login'))
        
        # Get authorization code
        auth_code = request.args.get('code')
        if not auth_code:
            flash('No authorization code received', 'error')
            return redirect(url_for('login'))
        
        # Exchange code for credentials
        redirect_uri = session.get('oauth_redirect_uri')
        creds = get_credentials_from_auth_code(auth_code, redirect_uri)
        
        # Save credentials to user-specific file
        user_email = None
        try:
            # Use the calendar service to get user info
            temp_service = build("calendar", "v3", credentials=creds)
            # Try to get user info by making a simple API call
            calendar_list = temp_service.calendarList().list().execute()
            # The primary calendar usually contains user info
            primary_calendar = None
            for calendar in calendar_list.get('items', []):
                if calendar.get('primary'):
                    primary_calendar = calendar
                    break
            
            if primary_calendar:
                user_email = primary_calendar.get('id')
            else:
                # Fallback: use a default email or extract from credentials
                user_email = "user@example.com"  # This will be updated when we get real user info
            
            # Check if user is already logged in
            if user_email in user_sessions:
                flash(f'User {user_email} is already logged in. Please logout first if you want to switch accounts.', 'warning')
                return redirect(url_for('index'))
            
            # Save credentials to user-specific file
            token_file = f"token_{user_email.replace('@', '_at_').replace('.', '_')}.json"
            with open(token_file, "w") as token:
                token.write(creds.to_json())
            
            # Create user session
            user_id = user_email
            user_sessions[user_id] = {
                'email': user_email,
                'name': user_email.split('@')[0] if '@' in user_email else user_email,
                'picture': ''
            }
            
            # Store user info in session
            session['user_id'] = user_id
            
            # Clean up OAuth session data
            session.pop('oauth_state', None)
            session.pop('oauth_redirect_uri', None)
            
            flash(f'Welcome, {user_sessions[user_id]["name"]}!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Failed to get user info: {str(e)}', 'error')
            return redirect(url_for('login'))
        
    except Exception as e:
        error_msg = str(e)
        if 'Scope has changed' in error_msg:
            flash('OAuth scope mismatch detected. Please try logging in again. If the issue persists, clear your browser cookies and try again.', 'error')
            # Clear any existing tokens to force re-authentication
            import glob
            for token_file in glob.glob('token*.json'):
                try:
                    os.remove(token_file)
                except:
                    pass
        else:
            flash(f'OAuth callback failed: {error_msg}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout user."""
    if 'user_id' in session:
        user_id = session['user_id']
        if user_id in user_sessions:
            del user_sessions[user_id]
        session.pop('user_id', None)
        session.pop('_fresh', None)
    
    # Clear all session data including OAuth state
    session.clear()
    
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/reauth')
def reauth():
    """Force re-authentication by clearing session and redirecting to Google OAuth."""
    # Clear all session data
    session.clear()
    flash('Please authenticate again with Google.', 'info')
    return redirect(url_for('google_auth'))

@app.route('/add_event', methods=['POST'])
@login_required
def add_event():
    """Handle adding events via AJAX using MCP server with follow-up support."""
    try:
        user_id = session['user_id']
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        chat_context = data.get('chat_context', [])
        followup_response = data.get('followup_response', '')
        original_parsed_data = data.get('original_parsed_data', {})
        
        if not prompt and not followup_response:
            return jsonify({'success': False, 'error': 'No prompt or follow-up response provided'})
        
        print(f"[FLASK] Adding event - Prompt: '{prompt}', Followup: '{followup_response}', User: {user_id}")
        
        # Use persistent MCP client
        try:
            mcp_client = get_mcp_client()
            if mcp_client is None:
                result = {'success': False, 'error': 'Failed to start MCP server'}
            else:
                # Handle follow-up response
                if followup_response and original_parsed_data:
                    result = mcp_client.handle_followup_response(prompt, followup_response, user_id, original_parsed_data)
                else:
                    # Check if duration_minutes is provided directly
                    duration_minutes = data.get('duration_minutes')
                    if duration_minutes:
                        # Create event with specific duration
                        result = mcp_client.add_calendar_event_with_duration(prompt, user_id, duration_minutes, chat_context)
                    else:
                        # Use MCP client to create the event
                        result = mcp_client.add_calendar_event(prompt, user_id, chat_context)
        except Exception as e:
            print(f"[FLASK] MCP client error: {str(e)}")
            result = {'success': False, 'error': f'MCP client error: {str(e)}'}
        
        print(f"[FLASK] MCP result: {result}")
        
        if result.get('needs_followup', False):
            return jsonify({
                'success': False,
                'needs_followup': True,
                'followup_questions': result.get('followup_questions', []),
                'parsed_data': result.get('parsed_data', {}),
                'message': result.get('message', 'Please provide additional details.')
            })
        elif result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'title': result.get('title', 'Event created via MCP'),
                'start_time': result.get('start_time', 'Event details in message'),
                'duration': result.get('duration', 'Event details in message'),
                'location': result.get('location', 'Not specified'),
                'description': result.get('description', ''),
                'link': result.get('link', 'https://calendar.google.com')
            })
        else:
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        print(f"[FLASK] Error in add_event: {str(e)}")
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@app.route('/list_events')
@login_required
def list_events():
    """List upcoming events using MCP server."""
    try:
        user_id = session['user_id']
        
        # Use persistent MCP client to list events
        try:
            mcp_client = get_mcp_client()
            if mcp_client is None:
                result = {'success': False, 'error': 'Failed to start MCP server'}
            else:
                result = mcp_client.list_upcoming_events(user_id, max_results=10)
        except Exception as e:
            print(f"[FLASK] MCP client error: {str(e)}")
            result = {'success': False, 'error': f'MCP client error: {str(e)}'}
        
        if result['success']:
            return jsonify({'success': True, 'events': result['events']})
        else:
            return jsonify({'success': False, 'error': result['error']})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@app.route('/get_duration', methods=['POST'])
@login_required
def get_duration():
    """Handle duration input via AJAX."""
    try:
        data = request.get_json()
        duration_input = data.get('duration', '').strip()
        
        # Parse duration input
        if duration_input.lower() in ['1 hour', '1h']:
            duration_minutes = 60
        elif duration_input.lower() in ['1.5 hours', '1.5h']:
            duration_minutes = 90
        else:
            try:
                duration_minutes = int(duration_input)
            except ValueError:
                return jsonify({'success': False, 'error': 'Please enter a valid number of minutes'})
        
        return jsonify({'success': True, 'duration_minutes': duration_minutes})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@app.route('/profile')
@login_required
def profile():
    """User profile page."""
    user_id = session['user_id']
    user_info = user_sessions.get(user_id, {})
    return render_template('profile.html', user_info=user_info)

# Deployment configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    finally:
        cleanup_mcp_client() 