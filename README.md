# Google Calendar Assistant with MCP Integration

This project provides a Google Calendar assistant that can parse natural language prompts and create calendar events. It also includes MCP (Model Context Protocol) integration for easy integration with AI assistants and other tools.

## Features

- **Natural Language Parsing**: Parse event descriptions like "Dentist appointment on August 15th at 3:30pm"
- **Google Calendar Integration**: Automatically create events in your Google Calendar
- **MCP Server**: Expose calendar functionality through MCP protocol
- **Smart Date/Time Parsing**: Uses multiple strategies to extract dates and times from text

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Calendar API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials and save as `credentials.json` in the project directory

### 3. First Run Authentication

Run the basic script first to authenticate:

```bash
python quickstart.py
```

This will open a browser window for OAuth authentication. After authentication, a `token.json` file will be created.

## Usage

### Basic Usage (Direct Script)

```bash
python quickstart.py
```

Edit the `prompt` variable in `quickstart.py` to change the event description.

### MCP Server Usage

The MCP server provides two main tools:

1. **add_calendar_event**: Add events from natural language prompts
2. **list_upcoming_events**: List upcoming calendar events

#### Running the MCP Server

```bash
python calendar_mcp_server.py
```

#### Testing the MCP Server

```bash
python test_mcp_client.py
```

#### MCP Configuration

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "calendar-assistant": {
      "command": "python",
      "args": ["calendar_mcp_server.py"],
      "env": {}
    }
  }
}
```

## Example Prompts

The system can handle various natural language formats:

- "Dentist appointment on August 15th at 3:30pm"
- "Team meeting tomorrow at 2:00pm"
- "Doctor visit on March 20th at 10:00am"
- "Lunch with John on Friday at 12:30pm"
- "Conference call on 12/15 at 3:00pm"

## MCP Tools

### add_calendar_event

Adds an event to Google Calendar from a natural language prompt.

**Parameters:**
- `prompt` (string, required): Natural language description of the event

**Example:**
```json
{
  "name": "add_calendar_event",
  "arguments": {
    "prompt": "Team meeting tomorrow at 2:00pm"
  }
}
```

### list_upcoming_events

Lists upcoming events from Google Calendar.

**Parameters:**
- `max_results` (integer, optional): Maximum number of events to return (default: 10)

**Example:**
```json
{
  "name": "list_upcoming_events",
  "arguments": {
    "max_results": 5
  }
}
```

## File Structure

```
Calender_Assistant/
├── quickstart.py              # Main calendar assistant script
├── calendar_mcp_server.py     # MCP server implementation
├── test_mcp_client.py         # Test client for MCP server
├── calendar-mcp.json          # MCP configuration
├── requirements.txt           # Python dependencies
├── credentials.json           # Google API credentials (you need to add this)
├── token.json                 # OAuth tokens (created after first run)
└── README.md                  # This file
```

## Troubleshooting

### OAuth Configuration Checker

Before running the application, you can check your OAuth setup:

```bash
python check_oauth_config.py
```

This will verify your credentials, dependencies, and provide setup guidance.

### Common Issues

1. **ModuleNotFoundError**: Make sure all dependencies are installed with `pip install -r requirements.txt`

2. **Authentication Issues**: Delete `token.json` and run `quickstart.py` again to re-authenticate

3. **Invalid OAuth State Parameter**: This error occurs when:
   - You're already logged in elsewhere
   - The OAuth session has expired
   - There's a conflict with test user configuration
   
   **Solutions:**
   - Use the "Force re-authentication" link on the login page
   - Clear your browser cookies and try again
   - Make sure you're added as a test user in Google Cloud Console

4. **Date Parsing Issues**: The system uses multiple parsing strategies. If one format doesn't work, try a different one (e.g., "tomorrow at 2pm" instead of "August 15th at 3:30pm")

5. **MCP Connection Issues**: Ensure the MCP server is running and the configuration is correct

6. **Test User Issues**: If you're getting "access_denied" errors:
   - Make sure your email is added as a test user in the OAuth consent screen
   - The app must be in "Testing" mode (not published)
   - Wait a few minutes after adding test users before trying to authenticate

### Web Application

For the web interface (`app.py`):

- **Session Issues**: If you encounter login problems, visit `/reauth` to force re-authentication
- **Multiple Users**: Each user gets their own token file and session
- **Token Files**: User tokens are stored as `token_{email}.json` files

### Timezone

The system automatically detects your local timezone. To change this, modify the timezone settings in the `parse_prompt` function and the `create_event` function.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 