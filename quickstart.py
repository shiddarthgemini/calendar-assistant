import datetime
import os.path
from datetime import timezone
import tzlocal  # NEW: for local timezone

# NEW: Get the local timezone string (e.g., 'Asia/Kolkata', 'America/New_York')
local_timezone = tzlocal.get_localzone_name()

# NEW: Import the dateparser library
import dateparser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import dateparser
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
import openai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.readonly']

def get_openai_client():
    """Get OpenAI client with API key from environment variable."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-api-key'")
        return None
    
    return openai.OpenAI(api_key=api_key)

def parse_prompt_with_ai(text):
    """Use OpenAI to parse natural language into structured event data."""
    client = get_openai_client()
    if not client:
        return None, None, None
    
    # Get current date and time for context
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day
    current_hour = current_date.hour
    current_minute = current_date.minute
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a calendar assistant that extracts event details from natural language. 
                    Return a JSON object with these fields:
                    - title: The event title/description
                    - date_time: The date and time in ISO format (YYYY-MM-DDTHH:MM:SS)
                    - duration_minutes: Duration in minutes (only include if explicitly mentioned in the prompt)
                    
                    IMPORTANT: 
                    - Use {current_year} as the current year. Today is {current_year}-{current_month:02d}-{current_day:02d}.
                    - Current time is {current_hour:02d}:{current_minute:02d}
                    - For relative times like "in 2 hours", calculate from current time
                    - Only include duration_minutes if the user explicitly specifies it
                    
                    Examples:
                    "team meeting tomorrow at 4pm" → {{"title": "team meeting", "date_time": "{current_year}-08-06T16:00:00"}}
                    "doctor appointment on Friday 2pm for 30 minutes" → {{"title": "doctor appointment", "date_time": "{current_year}-08-09T14:00:00", "duration_minutes": 30}}
                    "call with John in 2 hours" → {{"title": "call with John", "date_time": "{current_year}-08-05T{current_hour+2:02d}:{current_minute:02d}"}}
                    
                    Use {current_year} as the current year. Return only valid JSON."""
                },
                {
                    "role": "user", 
                    "content": f"Parse this calendar prompt: '{text}'"
                }
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        # Try to extract JSON from the response
        if content.startswith('```json'):
            content = content[7:-3]  # Remove ```json and ```
        elif content.startswith('```'):
            content = content[3:-3]  # Remove ``` and ```
        
        parsed_data = json.loads(content)
        
        # Convert ISO string to datetime object
        date_time_str = parsed_data.get('date_time')
        if date_time_str:
            # Add timezone info if not present
            if 'T' in date_time_str and '+' not in date_time_str and 'Z' not in date_time_str:
                local_tz = get_localzone()
                offset_hours = int(local_tz.utcoffset(datetime.now()).total_seconds() // 3600)
                offset_str = f"{offset_hours:+03d}:00"
                date_time_str += offset_str
            
            # Clean up the datetime string for parsing
            date_time_str = date_time_str.replace('Z', '+00:00')
            # Fix any malformed timezone offsets
            if '+-' in date_time_str:
                date_time_str = date_time_str.replace('+-', '-')
            
            start_time = datetime.fromisoformat(date_time_str)
            title = parsed_data.get('title', text)
            duration = parsed_data.get('duration_minutes')
            
            print(f"AI parsed: Title='{title}', Time={start_time}")
            if duration:
                print(f"Duration: {duration}min")
            else:
                print("Duration: Not specified")
            
            return title, start_time, duration
            
    except Exception as e:
        print(f"OpenAI parsing failed: {e}")
        return None, None, None
    
    return None, None, None

def parse_prompt(text):
    """Parse a natural language prompt to extract event details."""
    print(f"--- Parsing prompt: '{text}' ---")
    
    # First try AI parsing
    title, start_time, duration = parse_prompt_with_ai(text)
    if start_time:
        return title, start_time, duration
    
    # Fallback to regex parsing if AI fails
    print("AI parsing failed, using regex fallback...")
    
    # Get local timezone
    local_tz = get_localzone()
    
    # Configure dateparser settings
    settings = {
        'PREFER_DATES_FROM': 'future',
        'PREFER_DAY_OF_MONTH': 'first',
        'RETURN_AS_TIMEZONE_AWARE': True,
        'TIMEZONE': str(local_tz)
    }
    
    # Strategy 1: Try to parse the entire text first
    start_time = dateparser.parse(text, settings=settings)
    if start_time:
        print(f"Parsed entire text: {start_time}")
        return text, start_time, 60

    # Strategy 2: If that fails, try to extract date/time phrases
    if not start_time:
        import re
        date_time_patterns = [
            r'(\w+ \d+(?:st|nd|rd|th)? at \d+(?::\d+)?(?:am|pm)?)',
            r'(\d+(?:st|nd|rd|th)? \w+ at \d+(?::\d+)?(?:am|pm)?)',
            r'(\w+ \d+(?:st|nd|rd|th)? \d+(?::\d+)?(?:am|pm)?)',
            r'(\d+/\d+ at \d+(?::\d+)?(?:am|pm)?)',
            r'(\d+-\d+ at \d+(?::\d+)?(?:am|pm)?)',
            r'(at \d+(?::\d+)?(?:am|pm)?)',
            r'(\d+(?::\d+)?(?:am|pm))',  # matches '4pm', '4:00pm'
        ]
        for pattern in date_time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_time_str = match.group(1)
                print(f"Found date/time pattern: '{date_time_str}'")
                start_time = dateparser.parse(date_time_str, settings=settings)
                if start_time:
                    break
    
    # Strategy 3: If still no luck, try parsing just the date part
    if not start_time:
        date_patterns = [
            r'(\w+ \d+(?:st|nd|rd|th)?)',
            r'(\d+(?:st|nd|rd|th)? \w+)',
            r'(\d+/\d+)',
            r'(\d+-\d+)'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                print(f"Found date pattern: '{date_str}'")
                start_time = dateparser.parse(date_str, settings=settings)
                if start_time:
                    # Try to add time if we find it
                    time_match = re.search(r'(\d+(?::\d+)?(?:am|pm))', text, re.IGNORECASE)
                    if time_match:
                        time_str = time_match.group(1)
                        print(f"Found time pattern: '{time_str}'")
                        combined_str = f"{date_str} {time_str}"
                        start_time = dateparser.parse(combined_str, settings=settings)
                    break

    if not start_time:
        print("Could not parse date/time from prompt")
        return text, None, 60

    return text, start_time, 60


def get_google_auth_flow(redirect_uri=None):
    """Get Google OAuth flow for web application."""
    # Try to use environment variables first (for deployment)
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if client_id and client_secret:
        # Use environment variables
        client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    else:
        # Fallback to credentials.json file (for local development)
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    
    if redirect_uri:
        flow.redirect_uri = redirect_uri
    return flow

def get_credentials_from_auth_code(auth_code, redirect_uri=None):
    """Exchange authorization code for credentials."""
    flow = get_google_auth_flow(redirect_uri)
    flow.fetch_token(code=auth_code)
    return flow.credentials

def get_calendar_service(user_id=None):
    """Get authenticated Google Calendar service for existing users."""
    creds = None
    
    # Use user-specific token file if user_id is provided
    if user_id:
        token_file = f"token_{user_id.replace('@', '_at_').replace('.', '_')}.json"
    else:
        token_file = "token.json"
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(token_file, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                return None
        else:
            # No valid credentials found - return None for web OAuth flow
            return None

    return build("calendar", "v3", credentials=creds)

def create_event(service, title, start_time, duration_minutes=None):
    """Creates an event based on the parsed details."""
    print("--- Creating a new event from parsed details ---")

    # Check if a start time was actually found
    if not start_time:
        print("Could not create event: No start time was found in the prompt.")
        return None

    # Use default duration if not specified (for web interface compatibility)
    if duration_minutes is None:
        duration_minutes = 60  # Default to 1 hour
    
    # Calculate end time based on duration
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Get local timezone
    local_tz = get_localzone()

    event = {
        'summary': title,
        'description': f"Created from the prompt: '{title}'",
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': str(local_tz),
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': str(local_tz),
        },
    }

    # Try to create in the primary calendar first
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created in primary calendar")
    except Exception as e:
        print(f"Could not create in primary calendar: {e}")
        # Try to list available calendars
        try:
            calendar_list = service.calendarList().list().execute()
            print("Available calendars:")
            for calendar in calendar_list.get('items', []):
                print(f"  - {calendar['summary']} (ID: {calendar['id']})")
        except:
            pass
        raise e
    
    print(f"Event created successfully!")
    print(f"Link: {created_event.get('htmlLink')}")
    return created_event


def list_upcoming_events(service, max_results=10):
    """List upcoming events from the calendar."""
    try:
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + "Z"
        
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        formatted_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No title")
            link = event.get("htmlLink", "")
            
            # Format the start time
            try:
                if "T" in start:  # Has time
                    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    formatted_start = start_dt.strftime("%B %d, %Y at %I:%M %p")
                else:  # Date only
                    start_dt = datetime.fromisoformat(start)
                    formatted_start = start_dt.strftime("%B %d, %Y")
            except:
                formatted_start = start
                
            formatted_events.append({
                "summary": summary,
                "start_time": formatted_start,
                "link": link
            })
        
        return formatted_events
        
    except Exception as e:
        print(f"Error listing events: {e}")
        return []


def main():
    """Main function to authenticate and run the process."""
    
    # ===================================================================
    # <<<--- TRY CHANGING THIS PROMPT! --->>>
    prompt = "Dentist appointment on August 15th at 3:30pm"
    # ===================================================================

    try:
        service = get_calendar_service()

        # 1. Parse the user's prompt
        title, start_time, duration = parse_prompt(prompt)

        # 2. If parsing was successful, create the event
        if start_time:
            create_event(service, title, start_time, duration)
        else:
            print("Could not understand the prompt.")

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()