#!/usr/bin/env python3
"""
Setup script for free hosting deployment
Creates the necessary files for hosting legal documents on GitHub Pages
"""

import os
import shutil

def create_directory_structure():
    """Create the directory structure for hosting"""
    directories = [
        'calendar-assistant-docs',
        'calendar-assistant-docs/css',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_index_html():
    """Create the main index.html file"""
    content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calendar Assistant - Legal Documents</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📅 Calendar Assistant</h1>
            <p>Legal documents and information for our Google Calendar integration app.</p>
        </header>
        
        <main>
            <div class="links">
                <a href="privacy.html" class="btn">🔒 Privacy Policy</a>
                <a href="terms.html" class="btn">📋 Terms of Service</a>
            </div>
            
            <div class="info">
                <h2>About Calendar Assistant</h2>
                <p>Calendar Assistant is a web-based productivity application that helps users create and manage Google Calendar events using natural language input.</p>
                
                <h3>Key Features:</h3>
                <ul>
                    <li>🎯 Natural language event creation</li>
                    <li>🤖 AI-powered date/time parsing</li>
                    <li>📅 Google Calendar integration</li>
                    <li>👥 Multi-user support</li>
                    <li>🔐 Secure OAuth 2.0 authentication</li>
                </ul>
                
                <h3>How It Works:</h3>
                <ol>
                    <li>Users log in with their Google account</li>
                    <li>They enter natural language descriptions like "team meeting tomorrow at 3pm"</li>
                    <li>Our AI parses the input and creates calendar events</li>
                    <li>Events appear in the user's Google Calendar</li>
                </ol>
            </div>
        </main>
        
        <footer>
            <p>For support or questions, please contact us via email.</p>
        </footer>
    </div>
</body>
</html>'''
    
    with open('calendar-assistant-docs/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Created index.html")

def create_css():
    """Create the CSS file for styling"""
    content = '''/* Calendar Assistant Documentation Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.95);
    min-height: 100vh;
    backdrop-filter: blur(10px);
}

header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px;
    margin: -2rem -2rem 3rem -2rem;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.links {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 3rem;
    flex-wrap: wrap;
}

.btn {
    display: inline-block;
    padding: 1rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    border-radius: 10px;
    font-weight: 600;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.info {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
}

.info h2 {
    color: #667eea;
    margin-bottom: 1rem;
    font-size: 1.8rem;
}

.info h3 {
    color: #764ba2;
    margin: 1.5rem 0 1rem 0;
    font-size: 1.3rem;
}

.info p {
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

.info ul, .info ol {
    margin-left: 2rem;
    margin-bottom: 1rem;
}

.info li {
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}

footer {
    text-align: center;
    padding: 2rem;
    color: #666;
    border-top: 1px solid #eee;
    margin-top: 2rem;
}

@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    header {
        margin: -1rem -1rem 2rem -1rem;
        padding: 1.5rem;
    }
    
    header h1 {
        font-size: 2rem;
    }
    
    .links {
        flex-direction: column;
        align-items: center;
    }
    
    .btn {
        width: 100%;
        max-width: 300px;
        text-align: center;
    }
}'''
    
    with open('calendar-assistant-docs/css/style.css', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Created style.css")

def create_readme():
    """Create a README file for the repository"""
    content = '''# Calendar Assistant - Legal Documents

This repository contains the legal documents for the Calendar Assistant application, hosted on GitHub Pages for Google OAuth verification.

## Files

- `index.html` - Main landing page with app information
- `privacy.html` - Privacy Policy
- `terms.html` - Terms of Service
- `css/style.css` - Styling for the pages

## Setup Instructions

1. **Enable GitHub Pages**:
   - Go to Settings > Pages
   - Select "Deploy from a branch"
   - Choose "main" branch
   - Save

2. **Your site will be available at**:
   `https://yourusername.github.io/calendar-assistant-docs`

3. **Update URLs in your legal documents**:
   - Replace `[Your Contact Email]` with your actual email
   - Replace `[Your Support URL]` with this GitHub Pages URL

## For Google OAuth Verification

Use these URLs in your Google Cloud Console:

- **Privacy Policy URL**: `https://yourusername.github.io/calendar-assistant-docs/privacy.html`
- **Terms of Service URL**: `https://yourusername.github.io/calendar-assistant-docs/terms.html`

## Contact

For questions about this documentation, please contact the developer via email.
'''
    
    with open('calendar-assistant-docs/README.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Created README.md")

def copy_legal_documents():
    """Copy the legal documents to the hosting directory"""
    # Copy privacy policy
    if os.path.exists('privacy_policy.md'):
        with open('privacy_policy.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML (basic conversion)
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - Calendar Assistant</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🔒 Privacy Policy</h1>
            <p>Calendar Assistant Privacy Policy</p>
        </header>
        
        <main>
            <div class="info">
                {content.replace('**', '<strong>').replace('##', '<h2>').replace('###', '<h3>').replace('- ', '<li>').replace('---', '<hr>')}
            </div>
        </main>
        
        <footer>
            <a href="index.html" class="btn">← Back to Home</a>
        </footer>
    </div>
</body>
</html>'''
        
        with open('calendar-assistant-docs/privacy.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ Created privacy.html")
    
    # Copy terms of service
    if os.path.exists('terms_of_service.md'):
        with open('terms_of_service.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML (basic conversion)
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - Calendar Assistant</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 Terms of Service</h1>
            <p>Calendar Assistant Terms of Service</p>
        </header>
        
        <main>
            <div class="info">
                {content.replace('**', '<strong>').replace('##', '<h2>').replace('###', '<h3>').replace('- ', '<li>').replace('---', '<hr>')}
            </div>
        </main>
        
        <footer>
            <a href="index.html" class="btn">← Back to Home</a>
        </footer>
    </div>
</body>
</html>'''
        
        with open('calendar-assistant-docs/terms.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ Created terms.html")

def main():
    """Main setup function"""
    print("🚀 Setting up Calendar Assistant documentation for free hosting...")
    print()
    
    create_directory_structure()
    create_index_html()
    create_css()
    create_readme()
    copy_legal_documents()
    
    print()
    print("✅ Setup complete!")
    print()
    print("📋 Next steps:")
    print("1. Create a GitHub repository named 'calendar-assistant-docs'")
    print("2. Upload the contents of the 'calendar-assistant-docs' folder")
    print("3. Enable GitHub Pages in the repository settings")
    print("4. Your site will be available at: https://yourusername.github.io/calendar-assistant-docs")
    print()
    print("🔧 Don't forget to:")
    print("- Update contact information in the legal documents")
    print("- Deploy your Flask app to Heroku/Railway/Render")
    print("- Configure Google Cloud Console with the new URLs")
    print()
    print("📚 See VERIFICATION_WITHOUT_DOMAIN.md for detailed instructions")

if __name__ == "__main__":
    main() 