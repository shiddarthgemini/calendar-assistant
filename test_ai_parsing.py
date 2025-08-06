#!/usr/bin/env python3
"""
Test script to check AI parsing for follow-up detection
"""

import os
import json
import openai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ai_parsing():
    """Test AI parsing for different prompts."""
    
    # Set up OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return
    
    client = openai.OpenAI(api_key=api_key)
    current_time = datetime.now()
    
    # AI system prompt
    system_prompt = """You are a calendar assistant that extracts event details from natural language. 
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
    
    # Test prompts
    test_prompts = [
        "doctor appointment on Friday 2pm for 30 minutes",
        "team meeting tomorrow at 3pm",
        "call with John in 2 hours",
        "lunch meeting today at noon for 1 hour at Cafe Central"
    ]
    
    print("🧪 Testing AI Parsing for Follow-up Detection")
    print("=" * 60)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📋 Test {i}: '{prompt}'")
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this calendar prompt: '{prompt}'"}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            print(f"AI Response: {content}")
            
            # Try to parse JSON
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                else:
                    parsed_data = json.loads(content)
                
                print(f"✅ Parsed successfully:")
                print(f"   Title: {parsed_data.get('title')}")
                print(f"   Date/Time: {parsed_data.get('date_time')}")
                print(f"   Duration: {parsed_data.get('duration_minutes')}")
                print(f"   Location: {parsed_data.get('location')}")
                print(f"   Needs Follow-up: {parsed_data.get('needs_followup')}")
                print(f"   Follow-up Questions: {parsed_data.get('followup_questions', [])}")
                
                # Check if follow-up detection is working
                if "team meeting tomorrow at 3pm" in prompt:
                    if parsed_data.get('needs_followup'):
                        print("   ✅ Correctly identified need for follow-up")
                    else:
                        print("   ❌ Should have identified need for follow-up")
                elif "doctor appointment on Friday 2pm for 30 minutes" in prompt:
                    if not parsed_data.get('needs_followup'):
                        print("   ✅ Correctly identified no follow-up needed")
                    else:
                        print("   ❌ Should not need follow-up")
                        
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_parsing() 