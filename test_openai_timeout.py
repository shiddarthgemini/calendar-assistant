#!/usr/bin/env python3
"""
Test OpenAI API timeout and response
"""

import openai
import os
import time
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_api():
    """Test OpenAI API with the same prompt that's failing."""
    
    # Set up OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    client = openai.OpenAI(api_key=api_key)
    
    # Test prompt
    test_prompt = "team meeting tomorrow at 3pm"
    
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
                    - Current time is 14:40
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
        },
        {
            "role": "user",
            "content": test_prompt
        },
        {
            "role": "user",
            "content": f"Parse this calendar prompt: '{test_prompt}'"
        }
    ]
    
    print(f"Testing OpenAI API with prompt: '{test_prompt}'")
    print("=" * 60)
    
    try:
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
            timeout=30
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        content = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API responded in {duration:.2f} seconds")
        print(f"Response: {content}")
        
        # Try to parse the JSON
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                parsed_data = json.loads(content)
            
            print(f"✅ JSON parsed successfully: {json.dumps(parsed_data, indent=2)}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

if __name__ == "__main__":
    import re
    
    if test_openai_api():
        print("\n🎉 OpenAI API test passed!")
    else:
        print("\n❌ OpenAI API test failed!") 