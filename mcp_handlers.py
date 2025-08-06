#!/usr/bin/env python3
"""
MCP Handlers Module
MCP-style tools and AI parsing for Google Calendar operations with enhanced features.
"""

import os
import json
from datetime import datetime
import dateparser
import openai
from dotenv import load_dotenv
import logging
import re

# Import calendar API functions
from calendar_api import get_calendar_service, create_event, list_upcoming_events

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

# MCP Tool Definitions
MCP_TOOLS = [
    {
        "name": "add_calendar_event",
        "description": "Add an event to Google Calendar from a natural language prompt with location and description support",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Natural language description of the event"
                },
                "user_id": {
                    "type": "string",
                    "description": "User identifier for authentication"
                },
                "chat_context": {
                    "type": "array",
                    "description": "Previous conversation context for follow-up questions",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["prompt", "user_id"]
        }
    },
    {
        "name": "list_upcoming_events",
        "description": "List upcoming events from Google Calendar",
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of events to return"
                },
                "user_id": {
                    "type": "string",
                    "description": "User identifier for authentication"
                }
            },
            "required": ["user_id"]
        }
    }
]

def get_openai_client():
    """Get OpenAI client with API key."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return openai.OpenAI(api_key=api_key)

def get_mcp_tools():
    """Get available MCP tools."""
    return MCP_TOOLS

def parse_prompt_with_ai(text, chat_context=None):
    """Parse natural language prompt using AI to extract event details including location."""
    logger.info(f"[AI] Attempting AI parsing...")
    logger.info(f"[AI] Starting AI parsing for prompt: '{text}'")
    
    try:
        client = get_openai_client()
        current_time = datetime.now()
        
        logger.info(f"[CONTEXT] Current context - Date: {current_time.strftime('%Y-%m-%d')}, Time: {current_time.strftime('%H:%M')}")
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": """You are a calendar assistant that extracts event details from natural language. 
                Return a JSON object with these fields:
                - title: The event title/description
                - date_time: The date and time in ISO format (YYYY-MM-DDTHH:MM:SS)
                - duration_minutes: Duration in minutes (only if explicitly mentioned)
                - location: Location/venue of the event (only if explicitly mentioned)
                - description: A brief description of the event (generate if not provided)
                - needs_followup: Boolean indicating if follow-up questions are needed
                - followup_questions: Array of questions to ask the user (e.g., duration, location details, etc.)
                
                IMPORTANT: 
                - Use 2025 as the current year. Today is 2025-08-06.
                - Current time is """ + current_time.strftime('%H:%M') + """
                - For relative times like "in 2 hours", calculate from current time
                - Set needs_followup to TRUE if duration_minutes is null/not provided
                - Set needs_followup to TRUE if location is not explicitly mentioned
                - Do NOT provide default values for missing information
                - Only set location if it's explicitly mentioned in the prompt
                - Only set duration_minutes if it's explicitly mentioned in the prompt
                - Generate meaningful descriptions based on the event type
                
                Examples:
                "team meeting tomorrow at 4pm" → {"title": "team meeting", "date_time": "2025-08-07T16:00:00", "needs_followup": true, "followup_questions": ["What's the duration?", "Where is the meeting?"]}
                "doctor appointment on Friday 2pm for 30 minutes at City Medical Center" → {"title": "doctor appointment", "date_time": "2025-08-09T14:00:00", "duration_minutes": 30, "location": "City Medical Center", "description": "Medical appointment"}
                "call with John in 2 hours" → {"title": "call with John", "date_time": "2025-08-06T13:10:00", "needs_followup": true, "followup_questions": ["What's the duration?", "Is this a video call?"]}
                
                Use 2025 as the current year. Return only valid JSON."""
            }
        ]
        
        # Add chat context if available
        if chat_context:
            messages.extend(chat_context)
        
        # Add current prompt
        messages.append({
            "role": "user",
            "content": f"Parse this calendar prompt: '{text}'"
        })
        
        logger.info(f"[API] Sending request to OpenAI API...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1
        )
        
        logger.info(f"[SUCCESS] Received response from OpenAI API")
        
        # Extract and parse the response
        content = response.choices[0].message.content.strip()
        logger.info(f"[RESPONSE] Raw AI response: {content}")
        
        # Try to extract JSON from the response
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                parsed_data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] Failed to parse JSON: {e}")
            # Fallback to basic parsing
            return parse_prompt(text)
        
        # Extract fields
        title = parsed_data.get('title', 'Untitled Event')
        date_time_str = parsed_data.get('date_time')
        duration_minutes = parsed_data.get('duration_minutes')
        location = parsed_data.get('location')
        description = parsed_data.get('description', '')
        needs_followup = parsed_data.get('needs_followup', False)
        followup_questions = parsed_data.get('followup_questions', [])
        
        logger.info(f"[DATA] Parsed data - Title: '{title}', Date/Time: '{date_time_str}', Duration: {duration_minutes}, Location: '{location}', Needs Followup: {needs_followup}")
        
        # Parse datetime
        if date_time_str:
            try:
                parsed_datetime = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
                logger.info(f"[SUCCESS] Successfully parsed datetime: {parsed_datetime}")
            except ValueError as e:
                logger.error(f"[ERROR] Failed to parse datetime: {e}")
                return parse_prompt(text)
        else:
            logger.error(f"[ERROR] No date_time in response")
            return parse_prompt(text)
        
        logger.info(f"[SUCCESS] AI parsing successful - Title: '{title}', Time: {parsed_datetime}, Duration: {duration_minutes}, Location: '{location}'")
        
        return {
            'success': True,
            'title': title,
            'date_time': parsed_datetime,
            'duration_minutes': duration_minutes,
            'location': location,
            'description': description,
            'needs_followup': needs_followup,
            'followup_questions': followup_questions
        }
        
    except Exception as e:
        logger.error(f"[ERROR] AI parsing failed: {e}")
        return parse_prompt(text)

def parse_prompt(text):
    """Fallback parsing using dateparser."""
    logger.info(f"[PARSE] Using fallback parsing for: '{text}'")
    
    try:
        # Basic parsing with dateparser
        parsed_datetime = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
        
        if not parsed_datetime:
            return {'success': False, 'error': 'Could not parse date/time from prompt'}
        
        # Extract title (remove time-related words)
        title = text
        time_words = ['today', 'tomorrow', 'next', 'at', 'on', 'in', 'for', 'minutes', 'hours', 'am', 'pm']
        for word in time_words:
            title = re.sub(rf'\b{word}\b', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+', ' ', title).strip()
        
        if not title:
            title = 'Untitled Event'
        
        return {
            'success': True,
            'title': title,
            'date_time': parsed_datetime,
            'duration_minutes': None,
            'location': None,
            'description': '',
            'needs_followup': True,
            'followup_questions': ['What\'s the duration?', 'Where is this event?']
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Fallback parsing failed: {e}")
        return {'success': False, 'error': f'Failed to parse prompt: {str(e)}'}

def add_calendar_event_mcp(prompt, user_id, chat_context=None):
    """Add calendar event using MCP-style interface with enhanced features."""
    logger.info(f"[MCP] Adding calendar event - Prompt: '{prompt}', User: {user_id}")
    
    try:
        # Get calendar service
        logger.info(f"[AUTH] MCP: Getting calendar service for user: {user_id}")
        service = get_calendar_service(user_id)
        
        if not service:
            logger.error(f"[ERROR] MCP: No calendar service available - authentication required")
            return {
                'success': False,
                'error': 'Authentication required. Please login first.',
                'needs_auth': True
            }
        
        # Parse the prompt
        logger.info(f"[PARSE] MCP: Parsing prompt with AI...")
        parsed_data = parse_prompt_with_ai(prompt, chat_context)
        
        if not parsed_data['success']:
            logger.error(f"[ERROR] MCP: Failed to parse prompt: {parsed_data.get('error')}")
            return {
                'success': False,
                'error': parsed_data.get('error', 'Failed to parse event details')
            }
        
        # Check if follow-up questions are needed
        if parsed_data.get('needs_followup', False):
            logger.info(f"[FOLLOWUP] MCP: Follow-up questions needed")
            return {
                'success': False,
                'needs_followup': True,
                'followup_questions': parsed_data.get('followup_questions', []),
                'parsed_data': parsed_data,
                'message': 'Please provide additional details to complete the event creation.'
            }
        
        # Create the event
        logger.info(f"[CREATE] MCP: Creating event - Title: '{parsed_data['title']}', Time: {parsed_data['date_time']}, Duration: {parsed_data.get('duration_minutes')}, Location: '{parsed_data.get('location')}'")
        
        result = create_event(
            service=service,
            title=parsed_data['title'],
            start_time=parsed_data['date_time'],
            duration_minutes=parsed_data.get('duration_minutes'),
            location=parsed_data.get('location'),
            description=parsed_data.get('description', '')
        )
        
        if result['success']:
            logger.info(f"[SUCCESS] MCP: Event created successfully - Link: {result.get('link', 'N/A')}")
            return {
                'success': True,
                'message': f"[SUCCESS] Event created successfully!\n\n**Event:** {parsed_data['title']}\n**Date/Time:** {parsed_data['date_time'].strftime('%B %d, %Y at %I:%M %p')}\n**Duration:** {parsed_data.get('duration_minutes', 'Default (1 hour)')} minutes\n**Location:** {parsed_data.get('location', 'Not specified')}\n**Link:** {result.get('link', 'https://calendar.google.com')}",
                'title': parsed_data['title'],
                'start_time': parsed_data['date_time'].strftime('%B %d, %Y at %I:%M %p'),
                'duration': parsed_data.get('duration_minutes', 'Default (1 hour)'),
                'location': parsed_data.get('location', 'Not specified'),
                'description': parsed_data.get('description', ''),
                'link': result.get('link', 'https://calendar.google.com')
            }
        else:
            logger.error(f"[ERROR] MCP: Failed to create event: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error', 'Failed to create event')
            }
            
    except Exception as e:
        logger.error(f"[ERROR] MCP: Exception in add_calendar_event_mcp: {e}")
        return {
            'success': False,
            'error': f'Error creating event: {str(e)}'
        }

def handle_followup_response(original_prompt, followup_response, user_id, original_parsed_data):
    """Handle follow-up responses and create the final event."""
    logger.info(f"[FOLLOWUP] Handling follow-up response: '{followup_response}'")
    
    try:
        # Get calendar service
        service = get_calendar_service(user_id)
        
        if not service:
            return {
                'success': False,
                'error': 'Authentication required. Please login first.',
                'needs_auth': True
            }
        
        # Simple parsing of follow-up response
        followup_data = {}
        
        # Check for duration
        duration_match = re.search(r'(\d+)\s*(?:minutes?|mins?|hours?|hrs?)', followup_response.lower())
        if duration_match:
            duration = int(duration_match.group(1))
            if 'hour' in followup_response.lower() or 'hr' in followup_response.lower():
                duration *= 60  # Convert hours to minutes
            followup_data['duration_minutes'] = duration
            logger.info(f"[FOLLOWUP] Extracted duration: {duration} minutes")
        
        # Check for location (look for "at" or location keywords)
        location_keywords = ['at', 'in', 'location', 'venue', 'place']
        for keyword in location_keywords:
            if keyword in followup_response.lower():
                # Extract text after the keyword
                parts = followup_response.lower().split(keyword)
                if len(parts) > 1:
                    location = parts[1].strip()
                    if location and len(location) > 2:  # Avoid very short locations
                        followup_data['location'] = location
                        logger.info(f"[FOLLOWUP] Extracted location: {location}")
                        break
        
        # If no specific location found, check if the whole response might be a location
        if 'location' not in followup_data and len(followup_response.strip()) > 3:
            # Check if it doesn't look like a duration
            if not re.search(r'\d+', followup_response):
                followup_data['location'] = followup_response.strip()
                logger.info(f"[FOLLOWUP] Using response as location: {followup_response.strip()}")
        
        # Merge original data with follow-up data
        final_data = original_parsed_data.copy()
        final_data.update(followup_data)
        
        logger.info(f"[FOLLOWUP] Final data: {final_data}")
        
        # Create the event
        result = create_event(
            service=service,
            title=final_data['title'],
            start_time=final_data['date_time'],
            duration_minutes=final_data.get('duration_minutes'),
            location=final_data.get('location'),
            description=final_data.get('description', '')
        )
        
        if result['success']:
            return {
                'success': True,
                'message': f"Event created successfully!",
                'title': final_data['title'],
                'start_time': final_data['date_time'].strftime('%B %d, %Y at %I:%M %p'),
                'duration': f"{final_data.get('duration_minutes', 60)} minutes",
                'location': final_data.get('location', 'Not specified'),
                'description': final_data.get('description', ''),
                'link': result.get('link', 'https://calendar.google.com')
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Failed to create event')
            }
            
    except Exception as e:
        logger.error(f"[ERROR] Exception in handle_followup_response: {e}")
        return {
            'success': False,
            'error': f'Error handling follow-up: {str(e)}'
        }

def list_upcoming_events_mcp(max_results=10, user_id=None):
    """List upcoming events using MCP-style interface."""
    logger.info(f"[MCP] Listing upcoming events - Max: {max_results}, User: {user_id}")
    
    try:
        # Get calendar service
        service = get_calendar_service(user_id)
        
        if not service:
            logger.error(f"[ERROR] MCP: No calendar service available - authentication required")
            return {
                'success': False,
                'error': 'Authentication required. Please login first.',
                'needs_auth': True
            }
        
        # List events
        events = list_upcoming_events(service, max_results)
        
        logger.info(f"[SUCCESS] MCP: Successfully listed {len(events)} events")
        return {
            'success': True,
            'events': events
        }
        
    except Exception as e:
        logger.error(f"[ERROR] MCP: Exception in list_upcoming_events_mcp: {e}")
        return {
            'success': False,
            'error': f'Error listing events: {str(e)}'
        }

def main():
    """Main function for testing."""
    print("MCP Handlers Module")
    print("Available tools:")
    for tool in MCP_TOOLS:
        print(f"  - {tool['name']}: {tool['description']}")

if __name__ == "__main__":
    main() 