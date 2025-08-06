#!/usr/bin/env python3
"""
Cloud-optimized startup script for Calendar Assistant
Handles true MCP client-server architecture for cloud environments
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for cloud
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("All required environment variables are set")
    return True

def test_mcp_server():
    """Test if MCP server can start properly."""
    try:
        from mcp_client import MCPClient
        
        logger.info("Testing MCP server startup...")
        client = MCPClient()
        
        if client.start_server():
            logger.info("✅ MCP server test successful")
            client.stop_server()
            return True
        else:
            logger.error("❌ MCP server test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ MCP server test error: {e}")
        return False

def main():
    """Main startup function."""
    logger.info("🚀 Starting Calendar Assistant with true MCP architecture...")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        sys.exit(1)
    
    # Test MCP server
    if not test_mcp_server():
        logger.error("MCP server test failed. Exiting.")
        sys.exit(1)
    
    # Start the Flask app
    logger.info("✅ All checks passed. Starting Flask app...")
    
    try:
        # Import and run Flask app
        from app import app
        
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting Flask app on port {port}")
        
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"❌ Failed to start Flask app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 