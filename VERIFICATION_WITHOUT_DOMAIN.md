# Google OAuth Verification Without a Domain

## 🎯 Overview

You can complete Google's OAuth verification process without owning a domain by using free hosting services. This guide shows you how to set up everything using GitHub Pages or similar free services.

## 🚀 Step 1: Choose Your Free Hosting Solution

### Option A: GitHub Pages (Recommended)
**Pros:**
- Completely free
- Reliable and trusted by Google
- Easy to set up
- Professional appearance

**Setup:**
1. Create a GitHub account
2. Create a new repository: `calendar-assistant-docs`
3. Upload your legal documents
4. Enable GitHub Pages
5. Your site: `https://yourusername.github.io/calendar-assistant-docs`

### Option B: Netlify
**Pros:**
- Free hosting
- Automatic HTTPS
- Custom subdomain
- Easy deployment

**Setup:**
1. Create Netlify account
2. Upload files or connect GitHub
3. Your site: `https://your-app-name.netlify.app`

### Option C: Vercel
**Pros:**
- Free hosting
- Great for web apps
- Automatic HTTPS
- Easy deployment

## 📋 Step 2: Host Your Legal Documents

### Create the Document Structure
```
calendar-assistant-docs/
├── index.html
├── privacy.html
├── terms.html
├── css/
│   └── style.css
└── README.md
```

### Sample index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calendar Assistant - Legal Documents</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>Calendar Assistant</h1>
        <p>Legal documents and information for our Google Calendar integration app.</p>
        
        <div class="links">
            <a href="privacy.html" class="btn">Privacy Policy</a>
            <a href="terms.html" class="btn">Terms of Service</a>
        </div>
        
        <div class="info">
            <h2>About Calendar Assistant</h2>
            <p>Calendar Assistant is a web-based productivity application that helps users create and manage Google Calendar events using natural language input.</p>
            
            <h3>Key Features:</h3>
            <ul>
                <li>Natural language event creation</li>
                <li>AI-powered date/time parsing</li>
                <li>Google Calendar integration</li>
                <li>Multi-user support</li>
            </ul>
        </div>
    </div>
</body>
</html>
```

## 🔧 Step 3: Update Your Legal Documents

### Update Privacy Policy URLs
Replace all instances of `[Your Contact Email]` and `[Your Support URL]` with your actual information:

```markdown
## Contact Information

If you have any questions about this Privacy Policy, please contact us:

- **Email**: your-email@gmail.com
- **Support**: https://yourusername.github.io/calendar-assistant-docs
```

### Update Terms of Service URLs
```markdown
## Contact Information

If you have questions about these terms, please contact us:

- **Email**: your-email@gmail.com
- **Support**: https://yourusername.github.io/calendar-assistant-docs
- **Address**: [Your Address or "Contact via email"]
```

## 🌐 Step 4: Deploy Your App

### Option A: Deploy to Heroku (Free)
1. **Create Heroku account**
2. **Install Heroku CLI**
3. **Deploy your Flask app**:
   ```bash
   # In your project directory
   heroku create your-calendar-assistant
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```
4. **Your app URL**: `https://your-calendar-assistant.herokuapp.com`

### Option B: Deploy to Railway
1. **Create Railway account**
2. **Connect your GitHub repository**
3. **Deploy automatically**
4. **Your app URL**: `https://your-app-name.railway.app`

### Option C: Deploy to Render
1. **Create Render account**
2. **Connect your GitHub repository**
3. **Configure as Python app**
4. **Your app URL**: `https://your-app-name.onrender.com`

## 📝 Step 5: Update Google Cloud Console

### OAuth Consent Screen
- **App name**: Calendar Assistant
- **User support email**: your-email@gmail.com
- **Developer contact information**: your-email@gmail.com
- **App description**: Use the detailed description from the template
- **App domain**: your-app-name.herokuapp.com (or your chosen platform)
- **Authorized domains**: Add your hosting domain
- **Privacy policy URL**: https://yourusername.github.io/calendar-assistant-docs/privacy.html
- **Terms of service URL**: https://yourusername.github.io/calendar-assistant-docs/terms.html

### OAuth 2.0 Credentials
- **Authorized redirect URIs**:
  - `https://your-app-name.herokuapp.com/oauth2callback`
  - `http://localhost:5000/oauth2callback` (for development)

## ✅ Step 6: Complete Verification Application

### Updated Application Information
```
App Name: Calendar Assistant
Developer Email: your-email@gmail.com
Support Email: your-email@gmail.com
App URL: https://your-app-name.herokuapp.com
Privacy Policy URL: https://yourusername.github.io/calendar-assistant-docs/privacy.html
Terms of Service URL: https://yourusername.github.io/calendar-assistant-docs/terms.html
```

### Testing Instructions for Google
1. **Visit the app URL**: https://your-app-name.herokuapp.com
2. **Click "Login with Google"** to authenticate
3. **Grant calendar permissions** when prompted
4. **Try creating events** using natural language
5. **View created events** in the events list

## 🔒 Step 7: Security Considerations

### For Free Hosting
- **HTTPS**: All free hosting services provide HTTPS
- **Domain Verification**: Use your hosting provider's domain
- **SSL Certificate**: Automatically provided by hosting service

### Environment Variables
Set these in your hosting platform:
```bash
OPENAI_API_KEY=your-openai-key
FLASK_SECRET_KEY=your-secret-key
```

## 📊 Step 8: Verification Checklist (Updated)

### ✅ Pre-Verification Requirements
- [ ] **Legal Documents**: Hosted on GitHub Pages/Netlify
- [ ] **App Deployed**: Running on Heroku/Railway/Render
- [ ] **OAuth Consent Screen**: Complete with all URLs
- [ ] **OAuth Credentials**: Configured with production URLs
- [ ] **HTTPS**: Enabled on both app and documentation

### ✅ Legal Documentation
- [ ] **Privacy Policy**: Hosted at your free hosting URL
- [ ] **Terms of Service**: Hosted at your free hosting URL
- [ ] **Contact Information**: Updated with real email addresses
- [ ] **App Description**: Clear and professional

### ✅ Technical Requirements
- [ ] **App Functionality**: Tested and working
- [ ] **OAuth Flow**: Complete and secure
- [ ] **Error Handling**: Proper error messages
- [ ] **User Experience**: Smooth and intuitive

## 🎯 Benefits of This Approach

1. **Cost Effective**: Completely free to set up
2. **Professional**: Looks legitimate to Google reviewers
3. **Scalable**: Can upgrade to paid hosting later
4. **Reliable**: Free hosting services are stable
5. **Secure**: HTTPS and security features included

## 🚀 Next Steps

1. **Choose your hosting solution** (GitHub Pages + Heroku recommended)
2. **Set up your documentation site**
3. **Deploy your Flask app**
4. **Update all URLs in your documents**
5. **Configure Google Cloud Console**
6. **Submit verification application**

## 💡 Pro Tips

- **Use a professional email** (Gmail is fine)
- **Keep your app running** during the verification process
- **Respond quickly** to any Google inquiries
- **Test everything thoroughly** before submitting
- **Have a backup plan** in case free hosting has issues

---

**Note**: This approach is completely valid for Google verification. Many successful apps start with free hosting and upgrade later as they grow. 