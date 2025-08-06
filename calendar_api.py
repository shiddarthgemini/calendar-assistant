#!/usr/bin/env python3
"""
Google Calendar API Module
Core functions for Google Calendar operations.
"""

import datetime
import os.path
from datetime import timezone
import tzlocal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pickle
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging with more detailed output (Windows compatible)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('calendar_debug.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.readonly']

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
    """Get credentials from authorization code."""
    flow = get_google_auth_flow(redirect_uri)
    flow.fetch_token(code=auth_code)
    return flow.credentials

def get_calendar_service(user_id=None):
    """Get Google Calendar service for a specific user."""
    creds = None
    
    if user_id:
        # Load user-specific token file
        token_file = f"token_{user_id.replace('@', '_at_').replace('.', '_')}.json"
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If no user-specific credentials, try default token
    if not creds and os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If credentials don't exist or are invalid, return None
    if not creds or not creds.valid:
        return None
    
    # If credentials are expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            logger.error(f"Error refreshing credentials: {e}")
            return None
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Error building calendar service: {e}")
        return None

def create_event(service, title, start_time, duration_minutes=None, location=None, description=None):
    """Create a calendar event with location and description."""
    logger.info(f"[CREATE] Creating event - Title: '{title}', Start: {start_time}, Duration: {duration_minutes}, Location: '{location}', Description: '{description}'")
    
    if not service:
        logger.error("[ERROR] No calendar service available")
        return {'success': False, 'error': 'No calendar service available'}
    
    # Convert to local timezone
    local_tz = get_localzone()
    start_time = start_time.replace(tzinfo=local_tz)
    logger.info(f"[TIMEZONE] Timezone adjusted - Start: {start_time}, Timezone: {local_tz}")
    
    # Calculate end time
    if duration_minutes:
        end_time = start_time + timedelta(minutes=duration_minutes)
        logger.info(f"[DURATION] Duration specified: {duration_minutes} minutes")
    else:
        end_time = start_time + timedelta(hours=1)  # Default 1 hour
        logger.info(f"[DURATION] Using default duration: 1 hour")
    
    logger.info(f"[ENDTIME] Calculated end time: {end_time}")
    
    event = {
        'summary': title,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': str(local_tz),
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': str(local_tz),
        },
    }
    
    # Add location if provided
    if location:
        event['location'] = location
        logger.info(f"[LOCATION] Added location: {location}")
    
    # Add description if provided
    if description:
        event['description'] = description
        logger.info(f"[DESCRIPTION] Added description: {description}")

    try:
        logger.info(f"[API] Sending event to Google Calendar API...")
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        logger.info(f"[SUCCESS] Event created successfully: {title}")
        return {
            'success': True,
            'event': created_event,
            'link': created_event.get('htmlLink', 'https://calendar.google.com')
        }
    except Exception as e:
        logger.error(f"[ERROR] Error creating event: {e}")
        return {'success': False, 'error': str(e)}

def list_upcoming_events(service, max_results=10):
    """List upcoming events from the calendar."""
    if not service:
        logger.error("No calendar service available")
        return []
    
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
        logger.error(f"Error listing events: {e}")
        return [] 