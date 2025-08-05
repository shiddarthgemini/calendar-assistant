# 🚀 Free Deployment Guide for Calendar Assistant

This guide will help you deploy your Calendar Assistant app for free on various platforms.

## 📋 Prerequisites

1. **GitHub Account** - For hosting your code
2. **Google Cloud Console** - For OAuth credentials
3. **Git** - For version control

## 🎯 Recommended: Railway (Easiest)

### Step 1: Prepare Your Code
```bash
# Make sure all files are committed to Git
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect it's a Python app
6. Wait for deployment (usually 2-3 minutes)

### Step 3: Configure Environment Variables
In Railway dashboard:
1. Go to your project → Variables tab
2. Add these environment variables:
   ```
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```

### Step 4: Update Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Add your Railway URL to authorized redirect URIs:
   ```
   https://your-app-name.railway.app/oauth2callback
   ```

## 🌐 Alternative: Render

### Step 1: Deploy to Render
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: calendar-assistant
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
6. Click "Create Web Service"

### Step 2: Configure Environment Variables
In Render dashboard:
1. Go to your service → Environment
2. Add the same environment variables as Railway

## 🐍 Alternative: PythonAnywhere

### Step 1: Create Account
1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account

### Step 2: Upload Your Code
1. Go to "Files" tab
2. Upload your project files or clone from GitHub
3. Install requirements:
   ```bash
   pip install --user -r requirements.txt
   ```

### Step 3: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Flask" and Python 3.11
4. Set source code to your app directory
5. Set WSGI file to point to your app.py

## 🔧 Environment Variables Setup

For all platforms, you'll need these environment variables:

```bash
# Google OAuth (required)
GOOGLE_CLIENT_ID=your_client_id_from_google_cloud_console
GOOGLE_CLIENT_SECRET=your_client_secret_from_google_cloud_console

# Optional: Custom secret key
SECRET_KEY=your_custom_secret_key
```

## 📁 File Structure for Deployment

Your project should have these files:
```
Calender_Assistant/
├── app.py                 # Main Flask app
├── requirements.txt       # Python dependencies
├── Procfile              # For Heroku/Railway
├── runtime.txt           # Python version
├── railway.json          # Railway config
├── render.yaml           # Render config
├── credentials.json      # Google OAuth credentials
├── templates/            # HTML templates
│   ├── index.html
│   ├── login.html
│   └── profile.html
└── DEPLOYMENT_GUIDE.md   # This file
```

## 🔐 Google Cloud Console Setup

### Step 1: Create OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Choose "Web application"
6. Add authorized redirect URIs:
   ```
   https://your-app-name.railway.app/oauth2callback
   https://your-app-name.onrender.com/oauth2callback
   http://localhost:5000/oauth2callback  # For local testing
   ```

### Step 2: Download Credentials
1. Download the JSON file
2. Rename it to `credentials.json`
3. Place it in your project root

## 🚨 Important Security Notes

1. **Never commit credentials.json to Git**
2. **Use environment variables for secrets**
3. **Enable HTTPS on your domain**
4. **Set up proper CORS if needed**

## 🔍 Troubleshooting

### Common Issues:

1. **Port Issues**: Make sure your app uses `os.environ.get('PORT', 5000)`
2. **Missing Dependencies**: Check `requirements.txt` is complete
3. **OAuth Errors**: Verify redirect URIs in Google Cloud Console
4. **Import Errors**: Make sure all files are in the correct location

### Debug Commands:
```bash
# Check if app runs locally
python app.py

# Test requirements installation
pip install -r requirements.txt

# Check Python version
python --version
```

## 📞 Support

If you encounter issues:
1. Check the platform's logs
2. Verify all environment variables are set
3. Ensure Google Cloud Console is configured correctly
4. Test locally first

## 🎉 Success!

Once deployed, your app will be available at:
- **Railway**: `https://your-app-name.railway.app`
- **Render**: `https://your-app-name.onrender.com`
- **PythonAnywhere**: `https://yourusername.pythonanywhere.com`

Remember to update your Google Cloud Console with the new URLs! 