#!/usr/bin/env python3
"""
Test client for the Calendar MCP Server
This demonstrates how to use the MCP server to add calendar events.
"""

import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

async def test_calendar_mcp():
    """Test the calendar MCP server."""
    
    # Connect to the MCP server
    async with stdio_client(command="python", args=["calendar_mcp_server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # Test adding a calendar event
            print("Testing calendar event creation...")
            result = await session.call_tool(
                "add_calendar_event",
                {"prompt": "Team meeting tomorrow at 2:00pm"}
            )
            
            print("Result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)
                else:
                    print(content)
            print()
            
            # Test listing upcoming events
            print("Testing event listing...")
            result = await session.call_tool(
                "list_upcoming_events",
                {"max_results": 5}
            )
            
            print("Result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)
                else:
                    print(content)

if __name__ == "__main__":
    asyncio.run(test_calendar_mcp()) 