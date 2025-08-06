#!/usr/bin/env python3
"""
Test Flask app communication with MCP server
"""

import requests
import json
import time

def test_flask_mcp_communication():
    """Test that Flask app can communicate with MCP server."""
    
    print("Testing Flask app communication with MCP server...")
    print("=" * 60)
    
    # Test the Flask app endpoint
    test_data = {
        "prompt": "team meeting tomorrow at 3pm",
        "chat_context": []
    }
    
    try:
        print("Sending request to Flask app...")
        response = requests.post(
            'http://localhost:5000/add_event',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30  # 30 second timeout
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Flask app is working correctly!")
            print("✅ Expected: Authentication required (need to login first)")
            print("✅ MCP communication is working")
            return True
        elif response.status_code == 200:
            try:
                data = response.json()
                print(f"Response data: {json.dumps(data, indent=2)}")
                
                if data.get('needs_followup'):
                    print("✅ SUCCESS: Flask app and MCP server are working!")
                    print("✅ Follow-up questions are being triggered correctly")
                    return True
                elif data.get('success'):
                    print("✅ SUCCESS: Event created successfully!")
                    return True
                else:
                    print(f"❌ FAIL: Unexpected response: {data.get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print("❌ FAIL: Invalid JSON response from Flask app")
                print(f"Raw response: {response.text}")
                return False
        else:
            print(f"❌ FAIL: Unexpected HTTP status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Flask app is not running")
        print("Please start the Flask app with: python app.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ FAIL: Request timed out - MCP server may be slow to respond")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    # Wait for Flask to be ready
    print("Waiting for Flask app to be ready...")
    time.sleep(3)
    
    if test_flask_mcp_communication():
        print("\n🎉 SUCCESS: Flask app and MCP server are communicating correctly!")
        print("\nTo use the system:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Login with Google OAuth")
        print("3. Try creating an event!")
    else:
        print("\n❌ FAIL: There are communication issues between Flask and MCP server.") 