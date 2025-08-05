#!/usr/bin/env python3
"""
Deployment helper script for Calendar Assistant
This script helps prepare your app for deployment
"""

import os
import json
import shutil
from pathlib import Path

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/index.html',
        'templates/login.html',
        'templates/profile.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def check_credentials():
    """Check if credentials.json exists"""
    if not os.path.exists('credentials.json'):
        print("⚠️  Warning: credentials.json not found")
        print("   You'll need to:")
        print("   1. Go to Google Cloud Console")
        print("   2. Create OAuth 2.0 credentials")
        print("   3. Download as credentials.json")
        print("   4. Place in project root")
        return False
    
    print("✅ credentials.json found")
    return True

def create_env_template():
    """Create a template .env file"""
    env_template = """# Environment Variables for Calendar Assistant
# Copy this file to .env and fill in your values

# Google OAuth (required)
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here

# Flask secret key (optional - will be auto-generated if not set)
SECRET_KEY=your_secret_key_here

# Database URL (optional - for future use)
DATABASE_URL=sqlite:///calendar_assistant.db
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env.template")

def show_deployment_options():
    """Show deployment options"""
    print("\n🚀 Deployment Options:")
    print("\n1. Railway (Recommended - Easiest)")
    print("   - Go to https://railway.app")
    print("   - Sign up with GitHub")
    print("   - Deploy from repository")
    print("   - Free tier available")
    
    print("\n2. Render")
    print("   - Go to https://render.com")
    print("   - Sign up with GitHub")
    print("   - Create new Web Service")
    print("   - Free tier available")
    
    print("\n3. PythonAnywhere")
    print("   - Go to https://pythonanywhere.com")
    print("   - Sign up for free account")
    print("   - Upload files manually")
    print("   - Free tier available")

def show_next_steps():
    """Show next steps after deployment"""
    print("\n📋 Next Steps After Deployment:")
    print("\n1. Get your deployment URL")
    print("2. Update Google Cloud Console:")
    print("   - Add your URL to authorized redirect URIs")
    print("   - Example: https://your-app.railway.app/oauth2callback")
    print("3. Test the OAuth flow")
    print("4. Share your app with users!")

def main():
    """Main deployment helper function"""
    print("🎯 Calendar Assistant Deployment Helper")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please fix missing files before deploying")
        return
    
    # Check credentials
    check_credentials()
    
    # Create environment template
    create_env_template()
    
    # Show deployment options
    show_deployment_options()
    
    # Show next steps
    show_next_steps()
    
    print("\n📚 For detailed instructions, see DEPLOYMENT_GUIDE.md")
    print("🔧 For legal document hosting, run: python setup_free_hosting.py")

if __name__ == "__main__":
    main() 