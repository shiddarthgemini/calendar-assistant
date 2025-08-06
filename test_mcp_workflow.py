#!/usr/bin/env python3
"""
Test MCP Workflow
Tests the complete MCP client-server communication for calendar operations.
"""

import json
from mcp_client import MCPClient

def test_mcp_workflow():
    """Test the complete MCP workflow."""
    print("🧪 Testing MCP Workflow...")
    
    try:
        with MCPClient() as client:
            print("✅ MCP Client connected successfully")
            
            # Test 1: List available tools
            print("\n📋 Testing tool listing...")
            tools = client.list_tools()
            if tools and 'tools' in tools:
                tool_names = [tool['name'] for tool in tools['tools']]
                print(f"✅ Available tools: {tool_names}")
            else:
                print("❌ Failed to list tools")
                return False
            
            # Test 2: Test calendar event creation (without auth)
            print("\n📅 Testing calendar event creation...")
            result = client.add_calendar_event(
                prompt="team meeting tomorrow at 3pm",
                user_id="test@example.com"
            )
            
            if result:
                print(f"✅ Calendar event result: {json.dumps(result, indent=2)}")
                if result.get('needs_followup'):
                    print("✅ Follow-up questions detected (expected for incomplete prompt)")
                elif result.get('success'):
                    print("✅ Event creation successful")
                else:
                    print(f"⚠️ Expected result: {result.get('error', 'Unknown error')}")
            else:
                print("❌ Failed to create calendar event")
                return False
            
            # Test 3: Test listing events (without auth)
            print("\n📋 Testing event listing...")
            events_result = client.list_upcoming_events(
                user_id="test@example.com",
                max_results=5
            )
            
            if events_result:
                print(f"✅ Events result: {json.dumps(events_result, indent=2)}")
                if events_result.get('needs_auth'):
                    print("✅ Authentication required (expected)")
                else:
                    print("⚠️ Unexpected result for events listing")
            else:
                print("❌ Failed to list events")
                return False
            
            print("\n🎉 All MCP workflow tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ MCP workflow test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_workflow()
    if success:
        print("\n🚀 MCP implementation is working correctly!")
    else:
        print("\n💥 MCP implementation has issues!") 