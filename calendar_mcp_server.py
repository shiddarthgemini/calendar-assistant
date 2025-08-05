#!/usr/bin/env python3
"""
MCP Server for Google Calendar Assistant
This server allows adding calendar events through MCP protocol.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

# Import your existing calendar functions
from quickstart import parse_prompt, create_event, get_calendar_service

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("calendar-assistant")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="add_calendar_event",
                description="Add an event to Google Calendar from a natural language prompt",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Natural language description of the event (e.g., 'Dentist appointment on August 15th at 3:30pm')"
                        }
                    },
                    "required": ["prompt"]
                }
            ),
            Tool(
                name="list_upcoming_events",
                description="List upcoming events from Google Calendar",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of events to return (default: 10)",
                            "default": 10
                        }
                    }
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    
    if name == "add_calendar_event":
        return await handle_add_calendar_event(arguments)
    elif name == "list_upcoming_events":
        return await handle_list_upcoming_events(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def handle_add_calendar_event(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle adding a calendar event."""
    prompt = arguments.get("prompt", "")
    
    if not prompt:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Error: No prompt provided. Please provide a description of the event."
                )
            ]
        )
    
    try:
        # Get calendar service
        service = get_calendar_service()
        
        # Parse the prompt
        event_details = parse_prompt(prompt)
        
        if not event_details:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Could not parse the event details from: '{prompt}'. Please provide a clearer description with date and time."
                    )
                ]
            )
        
        # Create the event
        create_event(service, event_details)
        
        start_time = event_details["start_time"]
        summary = event_details["summary"]
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"✅ Event created successfully!\n\n"
                         f"**Event:** {summary}\n"
                         f"**Date/Time:** {start_time.strftime('%B %d, %Y at %I:%M %p')}\n"
                         f"**Timezone:** America/Chicago"
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error creating calendar event: {str(e)}"
                )
            ]
        )

async def handle_list_upcoming_events(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle listing upcoming events."""
    max_results = arguments.get("max_results", 10)
    
    try:
        # Get calendar service
        service = get_calendar_service()
        
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        
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

        if not events:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="No upcoming events found."
                    )
                ]
            )

        # Format the events
        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No title")
            
            # Parse the start time for better formatting
            try:
                if "T" in start:  # Has time
                    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    formatted_start = start_dt.strftime("%B %d, %Y at %I:%M %p")
                else:  # Date only
                    start_dt = datetime.fromisoformat(start)
                    formatted_start = start_dt.strftime("%B %d, %Y")
            except:
                formatted_start = start
                
            event_list.append(f"• **{summary}** - {formatted_start}")

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"📅 **Upcoming Events:**\n\n" + "\n".join(event_list)
                )
            ]
        )
        
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error listing events: {str(e)}"
                )
            ]
        )

async def main():
    """Run the MCP server."""
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            initialization_options={
                "server_name": "calendar-assistant",
                "server_version": "1.0.0",
            }
        )

if __name__ == "__main__":
    asyncio.run(main()) 