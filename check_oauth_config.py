#!/usr/bin/env python3
"""
OAuth Configuration Checker for Calendar Assistant
This script helps diagnose OAuth setup issues.
"""

import os
import json
from urllib.parse import urlparse

def check_credentials_file():
    """Check if credentials.json exists and is valid."""
    print("🔍 Checking credentials.json...")
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("   Please download your OAuth 2.0 client credentials from Google Cloud Console")
        print("   and save them as 'credentials.json' in this directory.")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        # Check required fields
        if 'installed' not in creds:
            print("❌ Missing required field: installed")
            return False
        
        installed = creds['installed']
        required_fields = ['client_id', 'client_secret', 'redirect_uris']
        for field in required_fields:
            if field not in installed:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check redirect URIs
        redirect_uris = creds['installed']['redirect_uris']
        local_uri = 'http://localhost:5000/oauth2callback'
        
        if local_uri not in redirect_uris:
            print(f"❌ Missing redirect URI: {local_uri}")
            print("   Please add this URI to your OAuth 2.0 client in Google Cloud Console")
            return False
        
        print("✅ credentials.json is valid")
        print(f"   Client ID: {creds['installed']['client_id'][:20]}...")
        print(f"   Redirect URIs: {redirect_uris}")
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def check_environment():
    """Check if required environment variables are set."""
    print("\n🔍 Checking environment variables...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not set (optional for basic functionality)")

def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = [
        'flask',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-api-python-client',
        'dateparser',
        'pytz',
        'tzlocal'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'google-auth':
                __import__('google.auth')
            elif package == 'google-api-python-client':
                __import__('googleapiclient.discovery')
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_google_cloud_setup():
    """Provide guidance on Google Cloud Console setup."""
    print("\n🔍 Google Cloud Console Setup Checklist:")
    print("   ✅ Create a Google Cloud Project")
    print("   ✅ Enable Google Calendar API")
    print("   ✅ Configure OAuth consent screen")
    print("   ✅ Add test users (your email address)")
    print("   ✅ Create OAuth 2.0 client credentials")
    print("   ✅ Download credentials.json")
    print("   ✅ Add redirect URI: http://localhost:5000/oauth2callback")

def main():
    """Main function to run all checks."""
    print("=" * 60)
    print("Calendar Assistant - OAuth Configuration Checker")
    print("=" * 60)
    
    all_good = True
    
    # Run checks
    if not check_credentials_file():
        all_good = False
    
    check_environment()
    
    if not check_dependencies():
        all_good = False
    
    check_google_cloud_setup()
    
    print("\n" + "=" * 60)
    if all_good:
        print("✅ All checks passed! Your OAuth configuration looks good.")
        print("   You can now run: python app.py")
    else:
        print("❌ Some issues were found. Please fix them before running the app.")
        print("\n📖 For detailed setup instructions, see GOOGLE_OAUTH_SETUP.md")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 