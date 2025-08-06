#!/usr/bin/env python3
"""
Cloud-optimized startup script for Calendar Assistant
Handles MCP server initialization for cloud environments
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

def main():
    """Main startup function."""
    logger.info("🚀 Starting Calendar Assistant in cloud mode...")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        sys.exit(1)
    
    # Start the Flask app directly (let it handle MCP internally)
    logger.info("✅ Environment check passed. Starting Flask app...")
    
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