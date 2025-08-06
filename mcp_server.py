#!/usr/bin/env python3
"""
True MCP Server for Google Calendar Operations
Implements the Model Context Protocol specification.
"""

import json
import sys
import logging
from datetime import datetime
import dateparser
import openai
import re
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
        logging.FileHandler('mcp_server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server implementing the Model Context Protocol."""
    
    def __init__(self):
        self.tools = [
            {
                "name": "add_calendar_event",
                "description": "Add an event to Google Calendar from a natural language prompt",
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
                            "description": "Previous conversation context",
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
            },
            {
                "name": "add_calendar_event_with_duration",
                "description": "Add an event to Google Calendar with specific duration",
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
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Duration of the event in minutes"
                        },
                        "chat_context": {
                            "type": "array",
                            "description": "Previous conversation context",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["prompt", "user_id", "duration_minutes"]
                }
            },
            {
                "name": "handle_followup_response",
                "description": "Handle follow-up response for incomplete event details",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "original_prompt": {
                            "type": "string",
                            "description": "Original event prompt"
                        },
                        "followup_response": {
                            "type": "string",
                            "description": "User's response to follow-up questions"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for authentication"
                        },
                        "original_parsed_data": {
                            "type": "object",
                            "description": "Originally parsed event data"
                        }
                    },
                    "required": ["original_prompt", "followup_response", "user_id", "original_parsed_data"]
                }
            }
        ]
    
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
                    - description: A brief description of the event (generate if not provided)
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
            
            # Add better error handling and timeout for Windows compatibility
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.1,
                    timeout=30  # 30 second timeout for OpenAI API
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
                
            except Exception as api_error:
                logger.error(f"[ERROR] OpenAI API call failed: {api_error}")
                return {'success': False, 'error': f'OpenAI API error: {str(api_error)}'}
            
        except Exception as e:
            logger.error(f"[ERROR] AI parsing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_add_calendar_event(self, params):
        """Handle add_calendar_event tool call."""
        logger.info(f"[MCP] add_calendar_event called with params: {params}")
        
        try:
            prompt = params.get('prompt', '')
            user_id = params.get('user_id', '')
            chat_context = params.get('chat_context', [])
            
            if not prompt or not user_id:
                return {
                    'success': False,
                    'error': 'Missing required parameters: prompt and user_id'
                }
            
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
    
    def handle_list_upcoming_events(self, params):
        """Handle list_upcoming_events tool call."""
        logger.info(f"[MCP] list_upcoming_events called with params: {params}")
        
        try:
            max_results = params.get('max_results', 10)
            user_id = params.get('user_id', '')
            
            if not user_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: user_id'
                }
            
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
    
    def handle_add_calendar_event_with_duration(self, params):
        """Handle add_calendar_event_with_duration tool call."""
        logger.info(f"[MCP] add_calendar_event_with_duration called with params: {params}")
        
        try:
            prompt = params.get('prompt', '')
            user_id = params.get('user_id', '')
            duration_minutes = params.get('duration_minutes', 60)
            chat_context = params.get('chat_context', [])
            
            if not prompt or not user_id:
                return {
                    'success': False,
                    'error': 'Missing required parameters: prompt and user_id'
                }
            
            # Get calendar service
            service = get_calendar_service(user_id)
            if not service:
                return {
                    'success': False,
                    'error': 'Authentication required. Please login first.',
                    'needs_auth': True
                }
            
            # Parse the prompt with AI
            parsed_data = self.parse_prompt_with_ai(prompt, chat_context)
            
            if not parsed_data or not parsed_data.get('success'):
                return {
                    'success': False,
                    'error': parsed_data.get('error', 'Failed to parse event details') if parsed_data else 'Failed to parse event details'
                }
            
            # Override duration with provided value
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
    
    def handle_followup_response(self, params):
        """Handle handle_followup_response tool call."""
        logger.info(f"[MCP] handle_followup_response called with params: {params}")
        
        try:
            original_prompt = params.get('original_prompt', '')
            followup_response = params.get('followup_response', '')
            user_id = params.get('user_id', '')
            original_parsed_data = params.get('original_parsed_data', {})
            
            if not original_prompt or not followup_response or not user_id:
                return {
                    'success': False,
                    'error': 'Missing required parameters: original_prompt, followup_response, and user_id'
                }
            
            # Get calendar service
            service = get_calendar_service(user_id)
            if not service:
                return {
                    'success': False,
                    'error': 'Authentication required. Please login first.',
                    'needs_auth': True
                }
            
            # Import the followup handler from mcp_handlers
            from mcp_handlers import handle_followup_response as mcp_handle_followup
            
            # Call the followup handler
            result = mcp_handle_followup(original_prompt, followup_response, user_id, original_parsed_data)
            
            return result
                
        except Exception as e:
            logger.error(f"[ERROR] Exception in handle_followup_response: {e}")
            return {
                'success': False,
                'error': f'Error handling followup response: {str(e)}'
            }
    
    def handle_tool_call(self, tool_name, params):
        """Route tool calls to appropriate handlers."""
        if tool_name == "add_calendar_event":
            return self.handle_add_calendar_event(params)
        elif tool_name == "list_upcoming_events":
            return self.handle_list_upcoming_events(params)
        elif tool_name == "add_calendar_event_with_duration":
            return self.handle_add_calendar_event_with_duration(params)
        elif tool_name == "handle_followup_response":
            return self.handle_followup_response(params)
        else:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }
    
    def process_request(self, request):
        """Process JSON-RPC request."""
        try:
            # Parse JSON-RPC request
            if isinstance(request, str):
                request = json.loads(request)
            
            method = request.get('method')
            params = request.get('params', {})
            request_id = request.get('id')
            
            logger.info(f"[MCP] Processing request - Method: {method}, ID: {request_id}")
            
            if method == "tools/list":
                # Return available tools
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            elif method == "tools/call":
                # Handle tool call
                tool_name = params.get('name')
                tool_params = params.get('arguments', {})
                
                result = self.handle_tool_call(tool_name, tool_params)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            else:
                # Unknown method
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return response
            
        except Exception as e:
            logger.error(f"[ERROR] Exception processing request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get('id') if isinstance(request, dict) else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self):
        """Run the MCP server, reading from stdin and writing to stdout."""
        logger.info("[MCP] Server starting...")
        print("MCP Server started", file=sys.stderr)  # Debug output
        
        try:
            while True:
                try:
                    # Read request from stdin with timeout protection
                    line = sys.stdin.readline()
                    if not line:
                        logger.info("[MCP] No more input, shutting down")
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    logger.info(f"[MCP] Received request: {line}")
                    
                    # Process request
                    response = self.process_request(line)
                    
                    # Send response to stdout
                    response_json = json.dumps(response)
                    logger.info(f"[MCP] Sending response: {response_json}")
                    print(response_json, flush=True)
                    
                except Exception as e:
                    logger.error(f"[ERROR] Error processing request: {e}")
                    # Send error response
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                
        except KeyboardInterrupt:
            logger.info("[MCP] Server stopped by user")
        except Exception as e:
            logger.error(f"[ERROR] Server error: {e}")
            print(f"Fatal server error: {e}", file=sys.stderr)

if __name__ == "__main__":
    import os
    import sys
    
    # Add current directory to Python path to ensure imports work
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        server = MCPServer()
        server.run()
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
        sys.exit(1) 