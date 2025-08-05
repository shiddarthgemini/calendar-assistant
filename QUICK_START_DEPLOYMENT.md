# ⚡ Quick Start: Deploy Your Calendar Assistant in 5 Minutes

## 🎯 Fastest Way: Railway

### Step 1: Push to GitHub
```bash
# If you haven't already, create a GitHub repository
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/calendar-assistant.git
git push -u origin main
```

### Step 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Wait 2-3 minutes for deployment

### Step 3: Configure Environment Variables
In Railway dashboard:
1. Go to your project → Variables
2. Add these variables:
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

## 🎉 Done!

Your app will be live at: `https://your-app-name.railway.app`

## 🔧 Legal Documents (For Google OAuth)

1. Create a new GitHub repository: `calendar-assistant-docs`
2. Upload the contents of the `calendar-assistant-docs` folder
3. Enable GitHub Pages in repository settings
4. Your legal docs will be at: `https://yourusername.github.io/calendar-assistant-docs`

## 📞 Need Help?

- Check `DEPLOYMENT_GUIDE.md` for detailed instructions
- Run `python deploy.py` to check your setup
- See `VERIFICATION_WITHOUT_DOMAIN.md` for Google OAuth setup 