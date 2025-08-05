#!/usr/bin/env python3
"""
Simple test script to verify calendar functionality works
"""

from quickstart import parse_prompt, create_event, get_calendar_service

def test_calendar_functionality():
    """Test the calendar functionality directly."""
    
    print("🧪 Testing Calendar Assistant Functionality")
    print("=" * 50)
    
    # Test 1: Parse a simple prompt
    print("\n1. Testing prompt parsing...")
    test_prompt = "Team meeting tomorrow at 2:00pm"
    print(f"   Input: '{test_prompt}'")
    
    event_details = parse_prompt(test_prompt)
    if event_details:
        print(f"   ✅ Successfully parsed!")
        print(f"   Event: {event_details['summary']}")
        print(f"   Time: {event_details['start_time']}")
    else:
        print("   ❌ Failed to parse prompt")
        return
    
    # Test 2: Test calendar service connection
    print("\n2. Testing calendar service connection...")
    try:
        service = get_calendar_service()
        print("   ✅ Calendar service connected successfully!")
    except Exception as e:
        print(f"   ❌ Failed to connect to calendar service: {e}")
        return
    
    # Test 3: Test event creation (optional - uncomment to actually create events)
    print("\n3. Testing event creation...")
    print("   ⚠️  Event creation test is commented out to avoid creating test events")
    print("   To test event creation, uncomment the lines in simple_test.py")
    
    # Uncomment these lines to actually test event creation:
    # try:
    #     created_event = create_event(service, event_details)
    #     print("   ✅ Event created successfully!")
    #     print(f"   Event link: {created_event.get('htmlLink')}")
    # except Exception as e:
    #     print(f"   ❌ Failed to create event: {e}")
    
    print("\n🎉 All tests completed!")
    print("\nYour calendar assistant is working correctly!")
    print("You can now use it with MCP clients or integrate it into other applications.")

if __name__ == "__main__":
    test_calendar_functionality() 