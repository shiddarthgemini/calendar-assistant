#!/usr/bin/env python3
"""
Test script to check MCP server hanging issue
"""

import subprocess
import json
import time
import os

def test_mcp_server():
    """Test MCP server directly to see if it hangs."""
    
    print("🚀 Starting MCP server test...")
    
    try:
        # Start MCP server
        server_process = subprocess.Popen(
            "python mcp_server.py",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            shell=True,
            cwd=os.getcwd()
        )
        
        print("✅ MCP server process started")
        time.sleep(2)  # Wait for server to start
        
        # Test 1: List tools
        print("\n📋 Test 1: Listing tools...")
        request1 = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        server_process.stdin.write(json.dumps(request1) + '\n')
        server_process.stdin.flush()
        
        # Read response with timeout
        import select
        ready, _, _ = select.select([server_process.stdout], [], [], 10)
        if ready:
            response1 = server_process.stdout.readline()
            print(f"✅ Response 1: {response1.strip()}")
        else:
            print("❌ Timeout waiting for response 1")
            return
        
        # Test 2: AI parsing (this is where it hangs)
        print("\n🤖 Test 2: AI parsing...")
        request2 = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "add_calendar_event",
                "arguments": {
                    "prompt": "test meeting tomorrow at 3pm",
                    "user_id": "test@example.com",
                    "chat_context": []
                }
            }
        }
        
        server_process.stdin.write(json.dumps(request2) + '\n')
        server_process.stdin.flush()
        
        # Read response with timeout
        ready, _, _ = select.select([server_process.stdout], [], [], 30)
        if ready:
            response2 = server_process.stdout.readline()
            print(f"✅ Response 2: {response2.strip()}")
        else:
            print("❌ Timeout waiting for response 2 - Server hung!")
            
            # Check if process is still alive
            if server_process.poll() is None:
                print("⚠️  Process is still alive but not responding")
                # Try to get stderr output
                try:
                    stderr_output = server_process.stderr.read()
                    if stderr_output:
                        print(f"🔍 Stderr: {stderr_output}")
                except:
                    pass
            else:
                print("💀 Process died")
                stderr_output = server_process.stderr.read()
                if stderr_output:
                    print(f"🔍 Stderr: {stderr_output}")
        
        # Cleanup
        server_process.terminate()
        server_process.wait(timeout=5)
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mcp_server() 