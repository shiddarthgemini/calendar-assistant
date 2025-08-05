#!/usr/bin/env python3
"""
Command Line Interface for Google Calendar Assistant
Usage: python calendar_cli.py
"""

import sys
import argparse
from quickstart import parse_prompt, create_event, get_calendar_service

def add_event(prompt):
    """Add an event from a natural language prompt."""
    print(f"📅 Adding event: '{prompt}'")
    
    # Parse the prompt
    title, start_time, duration = parse_prompt(prompt)
    
    if not start_time:
        print("❌ Could not parse the event details. Please provide a clearer description with date and time.")
        return False
    
    try:
        # Get calendar service
        service = get_calendar_service()
        
        # Create the event
        created_event = create_event(service, title, start_time, duration)
        
        if created_event:
            print("✅ Event created successfully!")
            print(f"📎 Link: {created_event.get('htmlLink')}")
            return True
        else:
            print("❌ Failed to create event")
            return False
        
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return False

def list_events(max_results=10):
    """List upcoming events."""
    print(f"📋 Listing next {max_results} upcoming events...")
    
    try:
        # Get calendar service
        service = get_calendar_service()
        
        # Call the Calendar API
        import datetime
        now = datetime.datetime.utcnow().isoformat() + "Z"
        
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
            print("📭 No upcoming events found.")
            return
        
        print("\n📅 Upcoming Events:")
        print("-" * 50)
        
        for i, event in enumerate(events, 1):
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No title")
            
            # Format the start time
            try:
                if "T" in start:  # Has time
                    start_dt = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
                    formatted_start = start_dt.strftime("%B %d, %Y at %I:%M %p")
                else:  # Date only
                    start_dt = datetime.datetime.fromisoformat(start)
                    formatted_start = start_dt.strftime("%B %d, %Y")
            except:
                formatted_start = start
                
            print(f"{i}. {summary}")
            print(f"   📅 {formatted_start}")
            print()
        
    except Exception as e:
        print(f"❌ Error listing events: {e}")

def interactive_mode():
    """Run in interactive mode."""
    print("🗓️  Calendar Assistant - Interactive Mode")
    print("=" * 50)
    print("Commands:")
    print("  add <description>  - Add an event (e.g., 'add team meeting tomorrow at 2pm')")
    print("  list [number]      - List upcoming events (default: 10)")
    print("  help               - Show this help")
    print("  quit               - Exit")
    print()
    
    while True:
        try:
            command = input("📝 calendar> ").strip()
            
            if not command:
                continue
                
            if command.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            elif command.lower() == 'help':
                print("Commands:")
                print("  add <description>  - Add an event (e.g., 'add team meeting tomorrow at 2pm')")
                print("  list [number]      - List upcoming events (default: 10)")
                print("  help               - Show this help")
                print("  quit               - Exit")
                
            elif command.lower().startswith('add '):
                prompt = command[4:].strip()
                if prompt:
                    add_event(prompt)
                else:
                    print("❌ Please provide an event description after 'add'")
                    
            elif command.lower().startswith('list'):
                parts = command.split()
                max_results = 10
                if len(parts) > 1:
                    try:
                        max_results = int(parts[1])
                    except ValueError:
                        print("❌ Please provide a valid number for list command")
                        continue
                list_events(max_results)
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

def main():
    parser = argparse.ArgumentParser(description="Google Calendar Assistant CLI")
    parser.add_argument("command", nargs="?", choices=["add", "list", "interactive"], 
                       help="Command to run")
    parser.add_argument("--prompt", "-p", help="Event description for 'add' command")
    parser.add_argument("--max", "-m", type=int, default=10, 
                       help="Maximum number of events to list (default: 10)")
    parser.add_argument("prompt_text", nargs="*", help="Event description (for add command)")
    
    args = parser.parse_args()
    
    if args.command == "add":
        # Combine prompt_text into a single string
        if args.prompt:
            add_event(args.prompt)
        elif args.prompt_text:
            prompt = " ".join(args.prompt_text)
            add_event(prompt)
        else:
            print("❌ Please provide an event description")
            print("Example: python calendar_cli.py add 'team meeting tomorrow at 2pm'")
            print("Example: python calendar_cli.py add --prompt 'team meeting tomorrow at 2pm'")
            
    elif args.command == "list":
        list_events(args.max)
        
    elif args.command == "interactive":
        interactive_mode()
        
    else:
        # No command provided, run interactive mode
        interactive_mode()

if __name__ == "__main__":
    main() 