# Google OAuth Setup for Multi-User Calendar Assistant

## Prerequisites
1. A Google account
2. Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and press "Enable"

## Step 2: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace domain)
3. Fill in the required information:
   - App name: "Calendar Assistant"
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes:
   - Click "Add or Remove Scopes"
   - Find and select "Google Calendar API v3"
   - Add these scopes:
     - `https://www.googleapis.com/auth/calendar`
     - `https://www.googleapis.com/auth/calendar.readonly`
     - `https://www.googleapis.com/auth/calendar.events`
5. Add test users (your email address)
6. Save and continue

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Name: "Calendar Assistant Web Client"
5. Add authorized redirect URIs:
   - For local development: `http://localhost:5000/oauth2callback`
   - For production: `https://yourdomain.com/oauth2callback`
6. Click "Create"
7. Download the JSON file and rename it to `credentials.json`
8. Place `credentials.json` in the root directory of your project

## Step 4: Update Application Configuration

1. Make sure `credentials.json` is in the same directory as `app.py`
2. The file structure should look like:
   ```
   Calender_Assistant/
   ├── app.py
   ├── quickstart.py
   ├── credentials.json  ← This file
   ├── templates/
   └── ...
   ```

## Step 5: Test the Application

1. Run the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and go to `http://localhost:5000`
3. You should be redirected to the login page
4. Click "Login with Google"
5. Complete the OAuth flow
6. You should be redirected back to the calendar assistant

## Troubleshooting

### "credentials.json not found" error
- Make sure you downloaded the OAuth 2.0 client credentials JSON file
- Rename it to `credentials.json`
- Place it in the root directory of your project

### "redirect_uri_mismatch" error
- Check that the redirect URI in your OAuth credentials matches exactly
- For local development: `http://localhost:5000/oauth2callback`
- Make sure there are no extra spaces or characters

### "access_denied" error
- Make sure you added your email as a test user in the OAuth consent screen
- Check that the Google Calendar API is enabled
- Wait a few minutes after adding test users before trying to authenticate

### "invalid_client" error
- Verify that your `credentials.json` file is valid and not corrupted
- Make sure you're using the correct client ID for web applications

### "Scope has changed" error
This error occurs when the OAuth scopes in your Google Cloud Console don't match what the application is requesting. To fix this:

1. **Update OAuth Consent Screen Scopes:**
   - Go to Google Cloud Console > APIs & Services > OAuth consent screen
   - Click "Edit App"
   - Go to "Scopes" section
   - Add these scopes:
     - `https://www.googleapis.com/auth/calendar`
     - `https://www.googleapis.com/auth/calendar.readonly`
     - `https://www.googleapis.com/auth/calendar.events`
   - Save and publish changes

2. **Clear Existing Tokens:**
   - Delete any existing `token*.json` files
   - Clear browser cookies
   - Try logging in again

### "Invalid OAuth state parameter" error
This error occurs when there's a mismatch between the OAuth state generated at the start of authentication and the state returned by Google. Common causes:

1. **Session Expiration**: The OAuth session expired before completion
   - **Solution**: Try logging in again or use the "Force re-authentication" link

2. **Multiple Login Attempts**: You tried to authenticate multiple times simultaneously
   - **Solution**: Clear your browser cookies and try again

3. **Test User Configuration**: Issues with test user setup in Google Cloud Console
   - **Solution**: 
     - Make sure your email is properly added as a test user
     - Wait a few minutes after adding test users
     - Check that the app is in "Testing" mode (not published)

4. **Browser Cache Issues**: Stale OAuth state in browser cache
   - **Solution**: Clear browser cache and cookies, then try again

### OAuth Configuration Checker

Run the configuration checker to diagnose setup issues:

```bash
python check_oauth_config.py
```

This will verify your credentials, dependencies, and provide specific guidance for any issues found.

## Security Notes

- Never commit `credentials.json` to version control
- The file is already in `.gitignore` to prevent accidental commits
- For production, use environment variables or secure secret management
- Regularly rotate your OAuth client secrets

## Production Deployment

For production deployment:

1. Update the authorized redirect URIs in Google Cloud Console
2. Use HTTPS for all redirect URIs
3. Set up proper session management (database instead of in-memory)
4. Use environment variables for sensitive configuration
5. Set up proper logging and monitoring 