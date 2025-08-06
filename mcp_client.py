#!/usr/bin/env python3
"""
True MCP Client for Google Calendar Operations
Communicates with MCP server via JSON-RPC protocol.
"""

import json
import subprocess
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_client.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Client that communicates with MCP server via JSON-RPC."""
    
    def __init__(self, server_command: str = "python mcp_server.py"):
        """Initialize MCP client with server command."""
        self.server_command = server_command
        self.server_process = None
        self.request_id = 1
        
    def start_server(self):
        """Start the MCP server process."""
        try:
            logger.info(f"[MCP] Starting server with command: {self.server_command}")
            
            # Check if we're in a cloud environment
            is_cloud = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RENDER') or os.getenv('HEROKU')
            
            if is_cloud:
                logger.info("[MCP] Detected cloud environment, using cloud-optimized settings")
                # In cloud, use different approach
                self.server_process = subprocess.Popen(
                    ["python", "-u", "mcp_server.py"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0,
                    cwd=os.getcwd(),
                    env=dict(os.environ)  # Pass all environment variables
                )
            else:
                # Local development settings
                self.server_process = subprocess.Popen(
                    ["python", "-u", "mcp_server.py"],  # -u for unbuffered output
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0,  # No buffering
                    cwd=os.getcwd()  # Set working directory
                )
            
            # Wait a moment for the server to start
            import time
            wait_time = 3 if is_cloud else 2  # Longer wait for cloud
            time.sleep(wait_time)
            
            # Check if process is still alive
            if self.server_process.poll() is not None:
                # Process died, get error output
                try:
                    stderr_output = self.server_process.stderr.read()
                    logger.error(f"[ERROR] Server process died immediately: {stderr_output}")
                except:
                    logger.error("[ERROR] Server process died immediately (could not read stderr)")
                return False
            
            logger.info("[MCP] Server process started successfully")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server process."""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                logger.info("[MCP] Server process stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                logger.warning("[MCP] Server process killed forcefully")
            except Exception as e:
                logger.error(f"[ERROR] Error stopping server: {e}")
    
    def send_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send JSON-RPC request to server and get response."""
        if not self.server_process:
            logger.error("[ERROR] Server not running")
            return None
        
        try:
            # Create JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": method,
                "params": params
            }
            
            request_json = json.dumps(request)
            logger.info(f"[MCP] Sending request: {request_json}")
            
                        # Send request to server
            self.server_process.stdin.write(request_json + '\n')
            self.server_process.stdin.flush()
            
            # Read response from server with timeout protection
            import time
            start_time = time.time()
            timeout_seconds = 60  # 60 seconds for AI operations
            response_line = None
            
            # Try to read response with timeout (Windows-compatible)
            while time.time() - start_time < timeout_seconds:
                try:
                    # Use a simple blocking read with timeout
                    response_line = self.server_process.stdout.readline()
                    if response_line:
                        break
                    time.sleep(0.1)
                except Exception as e:
                    logger.error(f"[ERROR] Error reading from server: {e}")
                    break
            
            if not response_line:
                logger.error(f"[ERROR] Timeout waiting for server response after {timeout_seconds} seconds")
                # Check if server process is still alive
                if self.server_process.poll() is not None:
                    logger.error("[ERROR] Server process terminated unexpectedly")
                    # Get stderr output for debugging
                    try:
                        stderr_output = self.server_process.stderr.read()
                        if stderr_output:
                            logger.error(f"[ERROR] Server stderr: {stderr_output}")
                    except:
                        pass
                return None
            
            if not response_line:
                logger.error(f"[ERROR] Timeout waiting for server response after {timeout_seconds} seconds")
                return None
            
            response_line = response_line.strip()
            logger.info(f"[MCP] Received response: {response_line}")
            
            # Parse response
            response = json.loads(response_line)
            
            # Check for errors
            if 'error' in response:
                logger.error(f"[ERROR] Server error: {response['error']}")
                return None
            
            self.request_id += 1
            return response.get('result')
            
        except Exception as e:
            logger.error(f"[ERROR] Error communicating with server: {e}")
            # Get stderr output for debugging
            if self.server_process and self.server_process.stderr:
                try:
                    stderr_output = self.server_process.stderr.read()
                    if stderr_output:
                        logger.error(f"[ERROR] Server stderr: {stderr_output}")
                except:
                    pass
            return None
    
    def list_tools(self) -> Optional[Dict[str, Any]]:
        """Get list of available tools from server."""
        return self.send_request("tools/list", {})
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool on the server."""
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        result = self.send_request("tools/call", params)
        
        if result and 'content' in result:
            # Extract the actual result from the content
            content = result['content']
            if content and len(content) > 0:
                try:
                    return json.loads(content[0]['text'])
                except json.JSONDecodeError:
                    logger.error("[ERROR] Failed to parse tool result")
                    return None
        
        return result
    
    def add_calendar_event(self, prompt: str, user_id: str, chat_context: Optional[list] = None) -> Dict[str, Any]:
        """Add calendar event using MCP server."""
        logger.info(f"[MCP] Adding calendar event - Prompt: '{prompt}', User: {user_id}")
        
        arguments = {
            "prompt": prompt,
            "user_id": user_id
        }
        
        if chat_context:
            arguments["chat_context"] = chat_context
        
        result = self.call_tool("add_calendar_event", arguments)
        
        if result is None:
            return {
                'success': False,
                'error': 'Failed to communicate with MCP server'
            }
        
        return result
    
    def list_upcoming_events(self, user_id: str, max_results: int = 10) -> Dict[str, Any]:
        """List upcoming events using MCP server."""
        logger.info(f"[MCP] Listing upcoming events - User: {user_id}, Max: {max_results}")
        
        arguments = {
            "user_id": user_id,
            "max_results": max_results
        }
        
        result = self.call_tool("list_upcoming_events", arguments)
        
        if result is None:
            return {
                'success': False,
                'error': 'Failed to communicate with MCP server'
            }
        
        return result
    
    def add_calendar_event_with_duration(self, prompt: str, user_id: str, duration_minutes: int, chat_context: Optional[list] = None) -> Dict[str, Any]:
        """Add calendar event with specific duration using MCP server."""
        logger.info(f"[MCP] Adding calendar event with duration - Prompt: '{prompt}', Duration: {duration_minutes}, User: {user_id}")
        
        arguments = {
            "prompt": prompt,
            "user_id": user_id,
            "duration_minutes": duration_minutes
        }
        
        if chat_context:
            arguments["chat_context"] = chat_context
        
        result = self.call_tool("add_calendar_event_with_duration", arguments)
        
        if result is None:
            return {
                'success': False,
                'error': 'Failed to communicate with MCP server'
            }
        
        return result
    
    def handle_followup_response(self, original_prompt, followup_response, user_id, original_parsed_data):
        """Handle follow-up response using MCP server."""
        logger.info(f"[MCP] Handling followup response - Original: '{original_prompt}', Followup: '{followup_response}', User: {user_id}")
        
        arguments = {
            "original_prompt": original_prompt,
            "followup_response": followup_response,
            "user_id": user_id,
            "original_parsed_data": original_parsed_data
        }
        
        result = self.call_tool("handle_followup_response", arguments)
        
        if result is None:
            return {
                'success': False,
                'error': 'Failed to communicate with MCP server'
            }
        
        return result
    
    def __enter__(self):
        """Context manager entry."""
        if not self.start_server():
            raise RuntimeError("Failed to start MCP server")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_server()

# Convenience functions for easy use
def create_mcp_client() -> MCPClient:
    """Create and return an MCP client instance."""
    return MCPClient()

def test_mcp_connection():
    """Test MCP server connection."""
    try:
        with MCPClient() as client:
            # Test listing tools
            tools = client.list_tools()
            if tools:
                logger.info("[SUCCESS] MCP connection test passed")
                logger.info(f"Available tools: {[tool['name'] for tool in tools.get('tools', [])]}")
                return True
            else:
                logger.error("[ERROR] MCP connection test failed")
                return False
    except Exception as e:
        logger.error(f"[ERROR] MCP connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the MCP client
    if test_mcp_connection():
        print("✅ MCP client test passed!")
    else:
        print("❌ MCP client test failed!") 