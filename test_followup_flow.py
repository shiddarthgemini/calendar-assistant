#!/usr/bin/env python3
"""
Test script to check the follow-up flow with incomplete information
"""

import json
import requests
from datetime import datetime

def test_followup_flow():
    """Test the follow-up flow with incomplete information."""
    
    # Test URL (replace with your actual deployed URL)
    base_url = "http://localhost:5000"  # Change this to your deployed URL
    
    print("🧪 Testing Follow-up Flow")
    print("=" * 50)
    
    # Test 1: Complete information (should work)
    print("\n📋 Test 1: Complete information")
    print("Prompt: 'doctor appointment on Friday 2pm for 30 minutes'")
    
    try:
        response = requests.post(f"{base_url}/add_event", 
                               json={
                                   "prompt": "doctor appointment on Friday 2pm for 30 minutes",
                                   "chat_context": []
                               },
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Incomplete information (should show follow-up)
    print("\n📋 Test 2: Incomplete information")
    print("Prompt: 'team meeting tomorrow at 3pm'")
    
    try:
        response = requests.post(f"{base_url}/add_event", 
                               json={
                                   "prompt": "team meeting tomorrow at 3pm",
                                   "chat_context": []
                               },
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if follow-up is needed
            if data.get('needs_followup'):
                print("✅ Follow-up flow working correctly!")
                print(f"Questions: {data.get('followup_questions', [])}")
            else:
                print("❌ Follow-up flow not working - should have needs_followup: true")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_followup_flow() 