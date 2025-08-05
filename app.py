from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from quickstart import parse_prompt, create_event, get_calendar_service, list_upcoming_events
from googleapiclient.discovery import build
import json
from datetime import datetime
import os
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Deployment configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# User sessions storage (in production, use a proper database)
user_sessions = {}

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
    from quickstart import get_google_auth_flow
    
    try:
        # Check if credentials.json exists
        if not os.path.exists('credentials.json'):
            flash('Google OAuth credentials not found. Please follow the setup guide in GOOGLE_OAUTH_SETUP.md', 'error')
            return redirect(url_for('login'))
        
        # Clear any existing OAuth session data to prevent conflicts
        session.pop('oauth_state', None)
        session.pop('oauth_redirect_uri', None)
        
        # Generate OAuth state for security
        oauth_state = secrets.token_urlsafe(32)
        session['oauth_state'] = oauth_state
        
        # Set redirect URI for OAuth callback
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
    from quickstart import get_credentials_from_auth_code, get_calendar_service
    
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
    """Handle adding events via AJAX."""
    try:
        user_id = session['user_id']
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'})
        
        # Parse the prompt
        title, start_time, duration = parse_prompt(prompt)
        
        if not start_time:
            return jsonify({'success': False, 'error': 'Could not parse date/time from prompt'})
        
        # Get calendar service for the current user
        service = get_calendar_service(user_id)
        
        if not service:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # Create the event
        created_event = create_event(service, title, start_time, duration)
        
        if created_event:
            return jsonify({
                'success': True,
                'message': f"Event '{title}' created successfully!",
                'link': created_event.get('htmlLink', ''),
                'title': title,
                'start_time': start_time.strftime('%B %d, %Y at %I:%M %p'),
                'duration': duration if duration else 'User specified'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create event'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@app.route('/list_events')
@login_required
def list_events():
    """List upcoming events."""
    try:
        user_id = session['user_id']
        service = get_calendar_service(user_id)
        
        if not service:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        events = list_upcoming_events(service, max_results=10)
        return jsonify({'success': True, 'events': events})
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 