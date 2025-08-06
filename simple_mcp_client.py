#!/usr/bin/env python3
"""
Simplified MCP Client for Google Calendar Operations
Uses direct function calls but maintains MCP interface structure.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import dateparser
import openai
import re
import os
from dotenv import load_dotenv

# Import calendar API functions
from calendar_api import get_calendar_service, create_event, list_upcoming_events

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simple_mcp_client.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class SimpleMCPClient:
    """Simplified MCP Client that uses direct function calls."""
    
    def __init__(self):
        """Initialize the simplified MCP client."""
        self.request_id = 1
        
    def get_openai_client(self):
        """Get OpenAI client with API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return openai.OpenAI(api_key=api_key)
    
    def parse_prompt_with_ai(self, text, chat_context=None):
        """Parse natural language prompt using AI."""
        logger.info(f"[AI] Parsing prompt: '{text}'")
        
        try:
            client = self.get_openai_client()
            current_time = datetime.now()
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a calendar assistant that extracts event details from natural language. 
                    Return a JSON object with these fields:
                    - title: The event title/description
                    - date_time: The date and time in ISO format (YYYY-MM-DDTHH:MM:SS)
                    - duration_minutes: Duration in minutes (only if explicitly mentioned)
                    - location: Location/venue of the event (only if explicitly mentioned)
                    - description: A brief description of the event
                    - needs_followup: Boolean indicating if follow-up questions are needed
                    - followup_questions: Array of questions to ask the user
                    
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
                    "team meeting tomorrow at 3pm" → needs_followup: true, followup_questions: ["What's the duration?", "Where is the meeting?"]
                    "doctor appointment on Friday 2pm for 30 minutes at City Medical Center" → needs_followup: false
                    
                    Return only valid JSON."""
                }
            ]
            
            if chat_context:
                messages.extend(chat_context)
            
            messages.append({
                "role": "user",
                "content": f"Parse this calendar prompt: '{text}'"
            })
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"[AI] Response: {content}")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                parsed_data = json.loads(content)
            
            # Parse datetime
            date_time_str = parsed_data.get('date_time')
            if date_time_str:
                parsed_datetime = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
            else:
                raise ValueError("No date_time in response")
            
            return {
                'success': True,
                'title': parsed_data.get('title', 'Untitled Event'),
                'date_time': parsed_datetime,
                'duration_minutes': parsed_data.get('duration_minutes'),
                'location': parsed_data.get('location'),
                'description': parsed_data.get('description', ''),
                'needs_followup': parsed_data.get('needs_followup', False),
                'followup_questions': parsed_data.get('followup_questions', [])
            }
            
        except Exception as e:
            logger.error(f"[ERROR] AI parsing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_calendar_event(self, prompt: str, user_id: str, chat_context: Optional[list] = None) -> Dict[str, Any]:
        """Add calendar event using direct function calls."""
        logger.info(f"[MCP] Adding calendar event - Prompt: '{prompt}', User: {user_id}")
        
        try:
            # Get calendar service
            service = get_calendar_service(user_id)
            if not service:
                return {
                    'success': False,
                    'error': 'Authentication required. Please login first.',
                    'needs_auth': True
                }
            
            # Parse the prompt
            parsed_data = self.parse_prompt_with_ai(prompt, chat_context)
            
            if not parsed_data['success']:
                return {
                    'success': False,
                    'error': parsed_data.get('error', 'Failed to parse event details')
                }
            
            # Check if follow-up questions are needed
            if parsed_data.get('needs_followup', False):
                return {
                    'success': False,
                    'needs_followup': True,
                    'followup_questions': parsed_data.get('followup_questions', []),
                    'parsed_data': parsed_data,
                    'message': 'Please provide additional details to complete the event creation.'
                }
            
            # Create the event
            result = create_event(
                service=service,
                title=parsed_data['title'],
                start_time=parsed_data['date_time'],
                duration_minutes=parsed_data.get('duration_minutes'),
                location=parsed_data.get('location'),
                description=parsed_data.get('description', '')
            )
            
            if result['success']:
                return {
                    'success': True,
                    'message': 'Event created successfully!',
                    'title': parsed_data['title'],
                    'start_time': parsed_data['date_time'].strftime('%B %d, %Y at %I:%M %p'),
                    'duration': f"{parsed_data.get('duration_minutes', 60)} minutes",
                    'location': parsed_data.get('location', 'Not specified'),
                    'description': parsed_data.get('description', ''),
                    'link': result.get('link', 'https://calendar.google.com')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to create event')
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Exception in add_calendar_event: {e}")
            return {
                'success': False,
                'error': f'Error creating event: {str(e)}'
            }

    def add_calendar_event_with_duration(self, prompt: str, user_id: str, duration_minutes: int, chat_context: Optional[list] = None) -> Dict[str, Any]:
        """Add calendar event with specific duration."""
        logger.info(f"[MCP] Adding calendar event with duration - Prompt: '{prompt}', Duration: {duration_minutes}, User: {user_id}")
        
        try:
            # Get calendar service
            service = get_calendar_service(user_id)
            if not service:
                return {
                    'success': False,
                    'error': 'Authentication required. Please login first.',
                    'needs_auth': True
                }
            
            # Parse the prompt
            parsed_data = self.parse_prompt_with_ai(prompt, chat_context)
            
            if not parsed_data['success']:
                return {
                    'success': False,
                    'error': parsed_data.get('error', 'Failed to parse event details')
                }
            
            # Override duration with the provided value
            parsed_data['duration_minutes'] = duration_minutes
            
            # Create the event
            result = create_event(
                service=service,
                title=parsed_data['title'],
                start_time=parsed_data['date_time'],
                duration_minutes=duration_minutes,
                location=parsed_data.get('location'),
                description=parsed_data.get('description', '')
            )
            
            if result['success']:
                return {
                    'success': True,
                    'message': 'Event created successfully!',
                    'title': parsed_data['title'],
                    'start_time': parsed_data['date_time'].strftime('%B %d, %Y at %I:%M %p'),
                    'duration': f"{duration_minutes} minutes",
                    'location': parsed_data.get('location', 'Not specified'),
                    'description': parsed_data.get('description', ''),
                    'link': result.get('link', 'https://calendar.google.com')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to create event')
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Exception in add_calendar_event_with_duration: {e}")
            return {
                'success': False,
                'error': f'Error creating event: {str(e)}'
            }
    
    def list_upcoming_events(self, user_id: str, max_results: int = 10) -> Dict[str, Any]:
        """List upcoming events using direct function calls."""
        logger.info(f"[MCP] Listing upcoming events - User: {user_id}, Max: {max_results}")
        
        try:
            # Get calendar service
            service = get_calendar_service(user_id)
            if not service:
                return {
                    'success': False,
                    'error': 'Authentication required. Please login first.',
                    'needs_auth': True
                }
            
            # List events
            events = list_upcoming_events(service, max_results)
            
            return {
                'success': True,
                'events': events
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Exception in list_upcoming_events: {e}")
            return {
                'success': False,
                'error': f'Error listing events: {str(e)}'
            }
    
    def handle_followup_response(self, original_prompt, followup_response, user_id, original_parsed_data):
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
                    'message': 'Event created successfully!',
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

# Convenience functions for easy use
def create_simple_mcp_client() -> SimpleMCPClient:
    """Create and return a simple MCP client instance."""
    return SimpleMCPClient()

if __name__ == "__main__":
    # Test the simple MCP client
    client = create_simple_mcp_client()
    
    # Test listing events (without auth)
    result = client.list_upcoming_events("test@example.com", max_results=5)
    print(f"Test result: {result}")
    
    if result.get('needs_auth'):
        print("✅ Simple MCP client test passed!")
    else:
        print("❌ Simple MCP client test failed!") 