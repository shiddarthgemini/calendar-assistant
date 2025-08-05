#!/usr/bin/env python3
"""
Check available Google Calendars
"""

from quickstart import get_calendar_service

def check_calendars():
    """List all available calendars."""
    print("📋 Checking available Google Calendars...")
    print("=" * 50)
    
    try:
        service = get_calendar_service()
        
        # Get calendar list
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        if not calendars:
            print("❌ No calendars found!")
            return
        
        print(f"Found {len(calendars)} calendar(s):")
        print()
        
        for i, calendar in enumerate(calendars, 1):
            calendar_id = calendar['id']
            summary = calendar.get('summary', 'No name')
            primary = calendar.get('primary', False)
            access_role = calendar.get('accessRole', 'unknown')
            
            print(f"{i}. {summary}")
            print(f"   ID: {calendar_id}")
            print(f"   Primary: {'Yes' if primary else 'No'}")
            print(f"   Access: {access_role}")
            print()
        
        # Check which calendar is primary
        primary_calendar = None
        for calendar in calendars:
            if calendar.get('primary', False):
                primary_calendar = calendar
                break
        
        if primary_calendar:
            print(f"🎯 Primary calendar: {primary_calendar['summary']}")
            print(f"   ID: {primary_calendar['id']}")
        else:
            print("⚠️  No primary calendar found")
            
    except Exception as e:
        print(f"❌ Error checking calendars: {e}")

if __name__ == "__main__":
    check_calendars() 