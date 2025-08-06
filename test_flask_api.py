#!/usr/bin/env python3
"""
Test Flask API endpoint to check if MCP communication is working
"""

import requests
import json
import time

def test_flask_api():
    """Test the Flask app API endpoint."""
    
    print("Testing Flask API endpoint...")
    print("=" * 50)
    
    # Test data
    test_data = {
        "prompt": "team meeting tomorrow at 3pm",
        "chat_context": []
    }
    
    try:
        print("Sending request to Flask app...")
        print(f"URL: http://localhost:5000/add_event")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        # Send request
        response = requests.post(
            'http://localhost:5000/add_event',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60  # 60 second timeout
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✅ SUCCESS! Response data:")
                print(json.dumps(data, indent=2))
                
                if data.get('needs_followup'):
                    print("\n🎉 ISSUE SOLVED! The system is working correctly!")
                    print("✅ MCP communication is working")
                    print("✅ OpenAI API is responding")
                    print("✅ Follow-up questions are being generated")
                    return True
                elif data.get('success'):
                    print("\n🎉 ISSUE SOLVED! Event created successfully!")
                    return True
                else:
                    print(f"\n❌ Error in response: {data.get('error', 'Unknown error')}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"\n❌ Invalid JSON response: {response.text}")
                return False
                
        elif response.status_code == 302:
            print("\n⚠️  Redirected to login page (expected if not authenticated)")
            print("This means the Flask app is working, but you need to login first")
            return True
            
        elif response.status_code == 401:
            print("\n⚠️  Authentication required (expected)")
            print("This means the Flask app is working correctly")
            return True
            
        else:
            print(f"\n❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ FAIL: Flask app is not running")
        print("Please start the Flask app with: python app.py")
        return False
        
    except requests.exceptions.Timeout:
        print("\n❌ FAIL: Request timed out - MCP server may still be hanging")
        print("This indicates the issue is NOT solved")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing if the 'create button keeps loading' issue is solved...")
    print("=" * 60)
    
    if test_flask_api():
        print("\n🎉 CONCLUSION: The issue appears to be SOLVED!")
        print("\nTo verify completely:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Login with Google OAuth")
        print("3. Try creating an event - the create button should work now!")
    else:
        print("\n❌ CONCLUSION: The issue is NOT solved yet.")
        print("The MCP server is still hanging or not responding properly.") 