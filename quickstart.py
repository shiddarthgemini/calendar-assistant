#!/usr/bin/env python3
"""
Quickstart Module - Compatibility Layer
This module provides backward compatibility by importing functions from the new modular structure.
"""

# Import all functions from the new modules
from calendar_api import (
    get_google_auth_flow,
    get_credentials_from_auth_code,
    get_calendar_service,
    create_event,
    list_upcoming_events,
    SCOPES
)

from mcp_handlers import (
    add_calendar_event_mcp,
    list_upcoming_events_mcp,
    parse_prompt,
    parse_prompt_with_ai,
    get_openai_client,
    get_mcp_tools,
    MCP_TOOLS
)

# Configure logging for backward compatibility
import logging
from dotenv import load_dotenv

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

def main():
    """Main function for testing."""
    print("Google Calendar MCP Module (Compatibility Layer)")
    print("Available tools:")
    for tool in MCP_TOOLS:
        print(f"  - {tool['name']}: {tool['description']}")

if __name__ == "__main__":
    main()