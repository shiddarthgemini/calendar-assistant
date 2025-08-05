# 🌐 Multi-User Calendar Assistant

A beautiful web application that allows anyone to log in with their Google account and create calendar events using natural language with AI assistance.

## ✨ Features

- 🔐 **Google OAuth Authentication** - Secure login with Google accounts
- 🤖 **AI-Powered Parsing** - Uses OpenAI to understand natural language
- 📅 **Google Calendar Integration** - Creates events in user's own calendar
- 🎨 **Modern Web UI** - Beautiful, responsive interface
- 👥 **Multi-User Support** - Each user has their own calendar access
- ✅ **Confirmation Dialogs** - Review events before creating
- 📱 **Mobile Responsive** - Works on all devices

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- Google Cloud Project with Calendar API enabled
- OpenAI API key

### 2. Setup Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:5000/auth/google`
     - `http://127.0.0.1:5000/auth/google`
5. Download the credentials file and rename it to `credentials.json`
6. Place it in the project root directory

### 3. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 4. Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Application

```bash
python app.py
```

The app will be available at: `http://localhost:5000`

## 🔧 How It Works

### User Flow

1. **Login**: Users visit the app and click "Continue with Google"
2. **OAuth**: Google OAuth flow authenticates the user
3. **Session**: User session is created with their Google account info
4. **Calendar Access**: App gets access to user's Google Calendar
5. **Event Creation**: Users can create events using natural language
6. **Confirmation**: Review and confirm events before creation

### Multi-User Architecture

- **Session Management**: Flask sessions store user authentication
- **Per-User Tokens**: Each user gets their own Google OAuth token file
- **Isolated Calendars**: Users only see and modify their own calendars
- **Secure Storage**: Tokens are stored securely per user

### File Structure

```
├── app.py                 # Main Flask application
├── quickstart.py          # Calendar API functions
├── templates/
│   ├── login.html         # Login page
│   ├── index.html         # Main calendar interface
│   └── profile.html       # User profile page
├── credentials.json       # Google OAuth credentials
├── .env                   # Environment variables
├── token_*.json          # User-specific OAuth tokens
└── requirements.txt       # Python dependencies
```

## 🎯 Usage Examples

### Natural Language Commands

Users can type commands like:

- `"team meeting tomorrow at 3pm"`
- `"call with John in 2 hours"`
- `"doctor appointment on Friday 2pm for 30 minutes"`
- `"lunch meeting next Monday at noon"`
- `"project review meeting next week Tuesday 10am"`

### Features

- **Smart Parsing**: AI understands various date/time formats
- **Duration Handling**: Automatic or user-specified event duration
- **Confirmation**: Review parsed details before creating
- **Event List**: View upcoming events from your calendar
- **Profile Management**: View account information

## 🔒 Security Features

- **OAuth 2.0**: Secure Google authentication
- **Session Management**: Flask session security
- **Token Isolation**: Each user has separate OAuth tokens
- **HTTPS Ready**: Configure for production deployment
- **Input Validation**: Sanitized user inputs

## 🚀 Production Deployment

### For Production Use

1. **Set Secret Key**: Use a strong, persistent secret key
2. **Database**: Replace in-memory sessions with a database
3. **HTTPS**: Configure SSL/TLS certificates
4. **Environment**: Set `FLASK_ENV=production`
5. **WSGI Server**: Use Gunicorn or uWSGI
6. **Domain**: Update OAuth redirect URIs for your domain

### Example Production Setup

```bash
# Install production dependencies
pip install gunicorn

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=your_secure_secret_key

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🛠️ Customization

### Adding Features

- **Database Integration**: Add user management database
- **Event Templates**: Pre-defined event templates
- **Calendar Views**: Different calendar view options
- **Notifications**: Email/SMS reminders
- **Team Features**: Shared calendars and events

### Styling

The app uses Bootstrap 5 with custom CSS. Modify the styles in the template files to match your brand.

## 📝 API Endpoints

- `GET /` - Main calendar interface (requires login)
- `GET /login` - Login page
- `GET /auth/google` - Google OAuth flow
- `GET /logout` - Logout user
- `GET /profile` - User profile page
- `POST /add_event` - Create calendar event
- `GET /list_events` - List upcoming events
- `POST /get_duration` - Handle event duration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Google Calendar API documentation
3. Check OpenAI API documentation
4. Open an issue on GitHub

## 🔧 Troubleshooting

### Common Issues

1. **OAuth Errors**: Ensure redirect URIs are correct in Google Cloud Console
2. **Calendar Access**: Users must grant calendar permissions
3. **Token Issues**: Delete user token files to re-authenticate
4. **OpenAI Errors**: Check API key and billing status

### Debug Mode

Run with debug mode for detailed error messages:

```bash
export FLASK_DEBUG=1
python app.py
```

---

**Happy Calendar Management! 📅✨** 